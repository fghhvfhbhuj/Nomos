import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import defaultdict
import os

#########################
# 1. 路径模拟器 (Path Simulator)
#########################

def simulate_correlated_paths(assets, dt, steps, n_paths, correlation_matrix=None):
    """
    使用GBM和Cholesky分解模拟相关资产价格路径。
    
    参数:
    - assets: 标的资产列表
    - dt: 时间步长
    - steps: 模拟步数
    - n_paths: 模拟路径数量
    - correlation_matrix: 资产间的相关性矩阵，如果为None则生成随机相关性
    
    返回:
    - prices: 形状为(n_paths, steps, n_assets)的价格矩阵
    """
    n_assets = len(assets)
    prices = np.zeros((n_paths, steps, n_assets))
    
    # 初始化第一个时间点的价格
    for i, asset in enumerate(assets):
        prices[:, 0, i] = asset['S0']
    
    # 如果没有提供相关性矩阵，则生成随机相关性
    if correlation_matrix is None:
        # 生成一个保证正定的相关性矩阵
        random_matrix = np.random.rand(n_assets, n_assets)
        # 确保对称
        random_matrix = (random_matrix + random_matrix.T) / 2
        # 添加对角线优势确保正定性
        random_matrix = random_matrix + n_assets * np.eye(n_assets)
        # 转化为相关系数矩阵(对角线为1)
        d = np.sqrt(np.diag(random_matrix))
        correlation_matrix = random_matrix / np.outer(d, d)
        np.fill_diagonal(correlation_matrix, 1.0)
    
    try:
        # Cholesky分解
        cholesky_matrix = np.linalg.cholesky(correlation_matrix)
        
        # 模拟价格路径
        for t in range(1, steps):
            # 生成标准正态随机数
            random_numbers = np.random.normal(0, 1, (n_paths, n_assets))
            # 应用相关性
            correlated_random = np.dot(random_numbers, cholesky_matrix.T)
            
            for i, asset in enumerate(assets):
                mu, sigma = asset['mu'], asset['sigma']
                # GBM公式
                drift = (mu - 0.5 * sigma**2) * dt
                diffusion = sigma * np.sqrt(dt) * correlated_random[:, i]
                prices[:, t, i] = prices[:, t-1, i] * np.exp(drift + diffusion)
    
    except np.linalg.LinAlgError:
        # 如果Cholesky分解失败，退回到简单的无相关性模拟
        print("警告: 相关性矩阵不是正定的，退回到无相关性模拟")
        
        for t in range(1, steps):
            for i, asset in enumerate(assets):
                mu, sigma = asset['mu'], asset['sigma']
                # 独立GBM模拟
                drift = (mu - 0.5 * sigma**2) * dt
                diffusion = sigma * np.sqrt(dt) * np.random.normal(0, 1, n_paths)
                prices[:, t, i] = prices[:, t-1, i] * np.exp(drift + diffusion)
    
    return prices

#########################
# 2. 结构依赖图 (Structure DAG)
#########################

def build_dependency_graph(options):
    """
    构建期权之间的依赖关系图。
    
    参数:
    - options: 期权列表
    
    返回:
    - graph: NetworkX DiGraph对象
    """
    graph = nx.DiGraph()
    
    # 添加所有期权作为节点
    for option in options:
        graph.add_node(option['id'], **option)
    
    # 添加依赖关系作为边
    for option in options:
        for dependency in option.get('dependencies', []):
            dependency_type = dependency['type']
            
            if dependency_type == 'triggered_by':
                # A触发后启用B: 从source到当前option的边
                source = dependency['source']
                if source in graph:  # 确保source存在
                    graph.add_edge(source, option['id'], type=dependency_type)
            
            elif dependency_type == 'disables':
                # A触发后禁用B: 从当前option到target的边
                target = dependency['target']
                if target in graph:  # 确保target存在
                    graph.add_edge(option['id'], target, type=dependency_type)
            
            elif dependency_type == 'bundle':
                # A+B必须同步执行: 双向边
                target = dependency['target']
                if target in graph:  # 确保target存在
                    graph.add_edge(option['id'], target, type=dependency_type)
                    graph.add_edge(target, option['id'], type=dependency_type)
    
    return graph

def check_graph_validity(graph):
    """
    检查依赖图的有效性，包括检测循环依赖。
    
    参数:
    - graph: NetworkX DiGraph对象
    
    返回:
    - valid: 布尔值，表示图是否有效
    - message: 如果无效，提供原因
    """
    # 检查是否有循环
    try:
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            return False, f"依赖图中存在循环: {cycles}"
    except:
        pass
    
    # 检查其他有效性条件
    # ...
    
    return True, "依赖图有效"

#########################
# 3. 行点树搜索器 (Structure Execution Tree)
#########################

def calculate_option_payoff(option, asset_price, time_to_expiry):
    """
    计算期权的收益。
    
    参数:
    - option: 期权数据
    - asset_price: 标的资产当前价格
    - time_to_expiry: 到期剩余时间
    
    返回:
    - payoff: 期权收益
    """
    option_type = option['type']
    strike_price = option['K']
    quantity = option['quantity']
    
    if option_type == 'call':
        payoff = max(0, asset_price - strike_price) * quantity
    else:  # put
        payoff = max(0, strike_price - asset_price) * quantity
    
    return payoff

def search_execution_tree(options, graph, asset_prices, dt):
    """
    使用回溯法搜索最优执行序列。
    
    参数:
    - options: 期权列表
    - graph: 依赖关系图
    - asset_prices: 资产价格路径
    - dt: 时间步长
    
    返回:
    - best_executions: 每条路径的最优执行序列
    """
    n_paths = asset_prices.shape[0]
    steps = asset_prices.shape[1]
    best_executions = []
    
    for path_idx in range(n_paths):
        # 记录此路径上的最优执行序列
        path_executions = []
        
        # 可用期权集合(初始时所有期权都可用)
        available_options = set(option['id'] for option in options)
        disabled_options = set()
        
        # 已执行的期权
        executed_options = set()
        
        # 当前总收益
        total_payoff = 0
        
        # 对每个时间步进行回溯搜索
        best_sequence, best_payoff = backtrack(
            0, graph, options, asset_prices[path_idx], 
            available_options, disabled_options, executed_options,
            total_payoff, steps, dt, path_executions
        )
        
        best_executions.append(best_sequence)
    
    return best_executions

def backtrack(time_step, graph, options, asset_prices, available_options, 
              disabled_options, executed_options, current_payoff, 
              total_steps, dt, current_sequence):
    """
    回溯法寻找最优执行序列。
    
    参数:
    - time_step: 当前时间步
    - graph: 依赖关系图
    - options: 期权列表
    - asset_prices: 当前路径的资产价格
    - available_options: 可用期权集合
    - disabled_options: 禁用期权集合
    - executed_options: 已执行期权集合
    - current_payoff: 当前总收益
    - total_steps: 总时间步数
    - dt: 时间步长
    - current_sequence: 当前执行序列
    
    返回:
    - best_sequence: 最优执行序列
    - best_payoff: 最优总收益
    """
    # 如果达到终止条件(所有时间步处理完毕)
    if time_step >= total_steps:
        return current_sequence, current_payoff
    
    # 复制当前状态用于尝试不同选择
    best_sequence = current_sequence.copy()
    best_payoff = current_payoff
    
    # 尝试执行当前可用的期权
    for option_id in list(available_options - disabled_options):
        option = None
        for opt in options:
            if opt['id'] == option_id:
                option = opt
                break
        
        if option is None:
            continue
        
        # 检查期权类型和执行条件
        can_execute = False
        option_style = option['style']
        
        # 欧式期权只能在到期日执行
        if option_style == 'european':
            time_to_expiry = option['T'] - time_step * dt
            can_execute = abs(time_to_expiry) < dt  # 接近到期日
        # 美式期权可以在任何时间执行
        else:  # american
            can_execute = True
        
        if can_execute:
            # 找到对应的资产索引
            asset_idx = 0  # 默认值，实际应该根据option['underlying']查找
            for i, asset_id in enumerate([f"Asset{i+1}" for i in range(len(asset_prices[0]))]):
                if asset_id == option['underlying']:
                    asset_idx = i
                    break
            
            # 计算执行收益
            time_to_expiry = option['T'] - time_step * dt
            asset_price = asset_prices[time_step, asset_idx]
            payoff = calculate_option_payoff(option, asset_price, time_to_expiry)
            
            # 如果有收益，则考虑执行
            if payoff > 0:
                # 记录执行
                execution = {
                    "option_id": option_id,
                    "time_step": time_step,
                    "payoff": payoff
                }
                
                # 更新状态
                new_available = available_options.copy()
                new_disabled = disabled_options.copy()
                new_executed = executed_options.copy()
                
                # 标记当前期权为已执行
                new_executed.add(option_id)
                new_available.remove(option_id)
                
                # 处理依赖关系
                for successor in graph.successors(option_id):
                    edge_data = graph.get_edge_data(option_id, successor)
                    edge_type = edge_data.get('type', '')
                    
                    if edge_type == 'disables':
                        new_disabled.add(successor)
                    elif edge_type == 'triggered_by':
                        if successor in new_available and successor not in new_disabled:
                            new_available.add(successor)
                
                # 继续回溯
                new_sequence = current_sequence + [execution]
                next_sequence, next_payoff = backtrack(
                    time_step + 1, graph, options, asset_prices, 
                    new_available, new_disabled, new_executed,
                    current_payoff + payoff, total_steps, dt, new_sequence
                )
                
                # 更新最优结果
                if next_payoff > best_payoff:
                    best_sequence = next_sequence
                    best_payoff = next_payoff
        
    # 尝试不执行任何期权，直接进入下一时间步
    next_sequence, next_payoff = backtrack(
        time_step + 1, graph, options, asset_prices, 
        available_options, disabled_options, executed_options,
        current_payoff, total_steps, dt, current_sequence
    )
    
    if next_payoff > best_payoff:
        best_sequence = next_sequence
        best_payoff = next_payoff
    
    return best_sequence, best_payoff

#########################
# 4. 结果输出 (Result Aggregation)
#########################

def aggregate_results(executions, asset_prices, options):
    """
    汇总各路径的执行结果。
    
    参数:
    - executions: 各路径的执行序列
    - asset_prices: 资产价格路径
    - options: 期权列表
    
    返回:
    - results: 汇总结果
    """
    n_paths = len(executions)
    
    # 统计结果
    results = {
        "total_payoffs": [],
        "option_stats": defaultdict(lambda: {
            "payoffs": [],
            "execution_times": [],
            "execution_count": 0
        })
    }
    
    for path_idx, sequence in enumerate(executions):
        path_payoff = 0
        
        for execution in sequence:
            option_id = execution["option_id"]
            time_step = execution["time_step"]
            payoff = execution["payoff"]
            
            path_payoff += payoff
            
            # 更新期权统计
            results["option_stats"][option_id]["payoffs"].append(payoff)
            results["option_stats"][option_id]["execution_times"].append(time_step)
            results["option_stats"][option_id]["execution_count"] += 1
        
        results["total_payoffs"].append(path_payoff)
    
    # 计算平均值和其他统计量
    avg_total_payoff = sum(results["total_payoffs"]) / n_paths if n_paths > 0 else 0
    results["avg_total_payoff"] = avg_total_payoff
    
    for option_id, stats in results["option_stats"].items():
        count = stats["execution_count"]
        if count > 0:
            stats["avg_payoff"] = sum(stats["payoffs"]) / count
            stats["avg_execution_time"] = sum(stats["execution_times"]) / count
            stats["execution_frequency"] = count / n_paths
        else:
            stats["avg_payoff"] = 0
            stats["avg_execution_time"] = 0
            stats["execution_frequency"] = 0
    
    print(f"平均总收益: {avg_total_payoff:.2f}")
    print(f"路径数量: {n_paths}")
    
    # 输出每个期权的统计信息
    print("\n期权统计信息:")
    for option_id, stats in results["option_stats"].items():
        if stats["execution_count"] > 0:
            print(f"  {option_id}:")
            print(f"    平均收益: {stats['avg_payoff']:.2f}")
            print(f"    平均执行时间: {stats['avg_execution_time']:.2f}")
            print(f"    执行频率: {stats['execution_frequency']:.2%}")
    
    return results

#########################
# 5. 可视化模块 (Visualization)
#########################

def visualize_dependency_graph(graph):
    """
    可视化依赖关系图。
    
    参数:
    - graph: NetworkX DiGraph对象
    """
    plt.figure(figsize=(12, 10))
    
    # 使用spring布局
    pos = nx.spring_layout(graph, seed=42)
    
    # 绘制节点
    nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color="lightblue", alpha=0.8)
    
    # 绘制边，根据类型使用不同颜色
    edge_colors = []
    for u, v, data in graph.edges(data=True):
        if data.get('type') == 'triggered_by':
            edge_colors.append('green')
        elif data.get('type') == 'disables':
            edge_colors.append('red')
        elif data.get('type') == 'bundle':
            edge_colors.append('blue')
        else:
            edge_colors.append('gray')
    
    nx.draw_networkx_edges(graph, pos, width=2, alpha=0.7, edge_color=edge_colors, 
                           arrowsize=20, connectionstyle='arc3,rad=0.1')
    
    # 绘制标签
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold')
    
    # 添加图例
    plt.plot([0], [0], color='green', label='触发 (Triggered By)')
    plt.plot([0], [0], color='red', label='禁用 (Disables)')
    plt.plot([0], [0], color='blue', label='捆绑 (Bundle)')
    plt.legend()
    
    plt.title("期权依赖关系图")
    plt.axis('off')
    plt.tight_layout()
    
    # 确保输出目录存在
    output_dir = "simulation_charts"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "dependency_graph.png"))
    
    plt.show()

def visualize_payoff_distribution(results):
    """
    可视化收益分布。
    
    参数:
    - results: 汇总结果
    """
    plt.figure(figsize=(10, 6))
    
    plt.hist(results["total_payoffs"], bins=30, alpha=0.7, color='blue')
    plt.axvline(results["avg_total_payoff"], color='red', linestyle='dashed', linewidth=2, 
                label=f'平均收益: {results["avg_total_payoff"]:.2f}')
    
    plt.title("总收益分布")
    plt.xlabel("收益")
    plt.ylabel("频率")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

def visualize_execution_frequency(results):
    """
    可视化期权执行频率。
    
    参数:
    - results: 汇总结果
    """
    option_ids = []
    frequencies = []
    
    for option_id, stats in results["option_stats"].items():
        if stats["execution_count"] > 0:
            option_ids.append(option_id)
            frequencies.append(stats["execution_frequency"])
    
    # 按频率排序
    sorted_indices = np.argsort(frequencies)[::-1]
    sorted_option_ids = [option_ids[i] for i in sorted_indices]
    sorted_frequencies = [frequencies[i] for i in sorted_indices]
    
    plt.figure(figsize=(12, 8))
    
    plt.bar(sorted_option_ids[:20], sorted_frequencies[:20], alpha=0.7, color='skyblue')
    
    plt.title("期权执行频率 (前20名)")
    plt.xlabel("期权ID")
    plt.ylabel("执行频率")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

def save_visualizations(results, graph):
    """
    保存所有可视化图表到指定文件夹。
    :param results: 汇总结果
    :param graph: 依赖关系图
    """
    output_dir = "simulation_charts"
    os.makedirs(output_dir, exist_ok=True)

    # 保存依赖关系图
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(graph, seed=42)
    nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color="lightblue", alpha=0.8)
    edge_colors = []
    for u, v, data in graph.edges(data=True):
        if data.get('type') == 'triggered_by':
            edge_colors.append('green')
        elif data.get('type') == 'disables':
            edge_colors.append('red')
        elif data.get('type') == 'bundle':
            edge_colors.append('blue')
        else:
            edge_colors.append('gray')
    nx.draw_networkx_edges(graph, pos, width=2, alpha=0.7, edge_color=edge_colors, 
                           arrowsize=20, connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold')
    plt.title("期权依赖关系图")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "dependency_graph.png"))
    plt.close()

    # 保存收益分布图
    plt.figure(figsize=(10, 6))
    plt.hist(results["total_payoffs"], bins=30, alpha=0.7, color='blue')
    plt.axvline(results["avg_total_payoff"], color='red', linestyle='dashed', linewidth=2, 
                label=f'平均收益: {results["avg_total_payoff"]:.2f}')
    plt.title("总收益分布")
    plt.xlabel("收益")
    plt.ylabel("频率")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "payoff_distribution.png"))
    plt.close()

    # 保存执行频率图
    option_ids = []
    frequencies = []
    for option_id, stats in results["option_stats"].items():
        if stats["execution_count"] > 0:
            option_ids.append(option_id)
            frequencies.append(stats["execution_frequency"])
    sorted_indices = np.argsort(frequencies)[::-1]
    sorted_option_ids = [option_ids[i] for i in sorted_indices]
    sorted_frequencies = [frequencies[i] for i in sorted_indices]
    plt.figure(figsize=(12, 8))
    plt.bar(sorted_option_ids[:20], sorted_frequencies[:20], alpha=0.7, color='skyblue')
    plt.title("期权执行频率 (前20名)")
    plt.xlabel("期权ID")
    plt.ylabel("执行频率")
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "execution_frequency.png"))
    plt.close()

#########################
# 6. 主函数和数据生成
#########################

def generate_assets_and_options(n_assets):
    """
    生成嵌套或互相关的标的资产及其对应的期权。
    
    参数:
    - n_assets: 资产数量
    
    返回:
    - assets: 资产列表
    - options: 期权列表
    """
    assets = []
    options = []
    
    # 生成资产
    for i in range(n_assets):
        asset_id = f"Asset{i+1}"
        assets.append({
            "id": asset_id,
            "S0": random.uniform(80, 120),  # 初始价格
            "mu": random.uniform(0.01, 0.08),  # 年化漂移率
            "sigma": random.uniform(0.15, 0.35)  # 年化波动率
        })
    
    # 生成期权及其依赖关系
    for i in range(n_assets):
        option_id = f"Option{i+1}"
        option_type = random.choice(["call", "put"])
        option_style = random.choice(["american", "european"])
        
        # 生成依赖关系
        dependencies = []
        
        # 每个期权有30%概率有依赖关系
        if i > 0 and random.random() < 0.3:
            dependency_type = random.choice(["triggered_by", "disables"])
            # 随机选择一个已存在的期权作为依赖
            source_idx = random.randint(0, i-1)
            
            if dependency_type == "triggered_by":
                dependencies.append({
                    "type": dependency_type,
                    "source": f"Option{source_idx+1}"
                })
            else:  # disables
                dependencies.append({
                    "type": dependency_type,
                    "target": f"Option{source_idx+1}"
                })
        
        options.append({
            "id": option_id,
            "type": option_type,
            "style": option_style,
            "underlying": f"Asset{i+1}",  # 每个期权对应一个资产
            "K": assets[i]["S0"] * random.uniform(0.9, 1.1),  # 执行价格在当前价格附近
            "T": random.uniform(0.5, 2.0),  # 到期时间
            "sigma": assets[i]["sigma"],  # 波动率
            "quantity": random.randint(1, 10),  # 数量
            "dependencies": dependencies
        })
    
    return assets, options

def main():
    """
    主函数：运行整个模拟和优化过程。
    """
    # 参数设置 - 使用极小的数据集，仅用于作品集展示
    n_assets = 5   # 从10减少到5
    dt = 1/252     # 日度时间步长
    steps = 15     # 从30减少到15
    n_paths = 5    # 从10减少到5
    
    print("生成资产和期权数据...")
    assets, options = generate_assets_and_options(n_assets)
    print(f"生成了 {len(assets)} 个资产和 {len(options)} 个期权")
    
    print("\n模拟资产价格路径...")
    asset_prices = simulate_correlated_paths(assets, dt, steps, n_paths)
    print(f"模拟了 {n_paths} 条路径，每条路径 {steps} 个时间步")
    
    print("\n构建依赖关系图...")
    graph = build_dependency_graph(options)
    valid, message = check_graph_validity(graph)
    print(message)
    
    if valid:
        print("\n搜索最优执行序列...")
        executions = search_execution_tree(options, graph, asset_prices, dt)
        print(f"为 {n_paths} 条路径生成了执行序列")
        
        print("\n汇总结果...")
        results = aggregate_results(executions, asset_prices, options)
        
        print("\n生成可视化...")
        visualize_dependency_graph(graph)
        visualize_payoff_distribution(results)
        visualize_execution_frequency(results)
        
        print("\n保存可视化图表...")
        save_visualizations(results, graph)
        print(f"图表已保存到 {os.path.abspath('simulation_charts')} 文件夹")
    else:
        print("依赖图无效，无法继续执行")

if __name__ == "__main__":
    main()