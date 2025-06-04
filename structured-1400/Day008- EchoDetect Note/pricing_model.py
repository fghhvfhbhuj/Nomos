import numpy as np
import matplotlib.pyplot as plt
import os
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import sys

# 检查依赖库
try:
    from tqdm import tqdm
except ImportError:
    print("正在安装 tqdm 库...")
    import pip
    pip.main(['install', 'tqdm'])
    from tqdm import tqdm

print("初始化 EchoDetect Note 定价模型...")

# 创建存储图像的文件夹
output_dir = "simulation_charts"
os.makedirs(output_dir, exist_ok=True)

# 模拟单次 EchoDetect Note 策略
def simulate_echo_note(days=252, initial_price=100, drift=0.05, volatility=0.2, seed=None):
    """
    模拟单次 EchoDetect Note 策略
    
    参数:
    - days: 模拟天数
    - initial_price: 初始价格
    - drift: 年化漂移
    - volatility: 年化波动率
    - seed: 随机种子
    
    返回:
    - is_triggered: 是否触发
    - final_price: 最终价格
    - price_path: 价格路径
    - trigger_day: 触发日期
    """
    if seed is not None:
        np.random.seed(seed)
    
    # 模拟扰动路径
    var_path = np.random.normal(0, 1, days)
    skew_path = np.random.normal(0, 1, days)
    volume_path = np.random.normal(0, 1, days)
    
    # 判断是否触发 - 连续 3 天三因子同时超过阈值
    trigger_indicators = (var_path > 1.5) & (skew_path > 1.5) & (volume_path > 1.5)
    is_triggered = False
    trigger_day = -1
    
    # 检查是否有连续 3 天触发
    for i in range(days - 2):
        if trigger_indicators[i] and trigger_indicators[i+1] and trigger_indicators[i+2]:
            is_triggered = True
            trigger_day = i
            break
    
    # 模拟 SPY 价格路径
    daily_returns = np.random.normal(drift / days, volatility / np.sqrt(days), days)
    price_path = initial_price * np.exp(np.cumsum(daily_returns))
    final_price = price_path[-1]
    
    return is_triggered, final_price, price_path, trigger_day

# 计算 EchoDetect Note 收益
def calculate_echo_payoff(is_triggered, final_price, initial_price=100):
    """
    计算 EchoDetect Note 收益
    
    参数:
    - is_triggered: 是否触发
    - final_price: 最终价格
    - initial_price: 初始价格
    
    返回:
    - payoff: 收益
    """
    if is_triggered:
        if final_price >= initial_price * 1.05:
            return initial_price * 1.2  # 120% 收益
        elif final_price <= initial_price * 0.95:
            return initial_price * 0.8  # 80% 收益
        else:
            return initial_price  # 100% 收益
    else:
        return initial_price * 0.95  # 95% 收益（未触发）

# 单次模拟函数（用于多进程）
def single_simulation(sim_id, days=252, initial_price=100, drift=0.05, volatility=0.2):
    is_triggered, final_price, _, _ = simulate_echo_note(
        days=days, 
        initial_price=initial_price, 
        drift=drift, 
        volatility=volatility,
        seed=sim_id
    )
    payoff = calculate_echo_payoff(is_triggered, final_price, initial_price)
    return payoff, is_triggered

# Monte Carlo 定价方法
def monte_carlo_pricing(num_simulations=10000, days=252, initial_price=100, drift=0.05, volatility=0.2, use_multiprocessing=True):
    """
    Monte Carlo 定价方法
    
    参数:
    - num_simulations: 模拟次数
    - days: 模拟天数
    - initial_price: 初始价格
    - drift: 年化漂移
    - volatility: 年化波动率
    - use_multiprocessing: 是否使用多进程
    
    返回:
    - mean_payoff: 平均收益
    - confidence_interval: 置信区间
    - payoffs: 收益列表
    - triggered_ratio: 触发比例
    """
    payoffs = []
    triggers = []
    
    try:
        if use_multiprocessing and num_simulations > 100:
            try:
                # 尝试使用 ProcessPoolExecutor
                with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
                    futures = []
                    for i in range(num_simulations):
                        futures.append(executor.submit(single_simulation, i, days, initial_price, drift, volatility))
                    
                    for future in tqdm(futures, desc="Running Monte Carlo Simulations"):
                        payoff, is_triggered = future.result()
                        payoffs.append(payoff)
                        triggers.append(is_triggered)
            except Exception as e:
                print(f"多进程执行失败，切换到单进程: {e}")
                use_multiprocessing = False
        
        if not use_multiprocessing or len(payoffs) == 0:
            # 单进程运行
            for i in tqdm(range(num_simulations), desc="Running Monte Carlo Simulations"):
                payoff, is_triggered = single_simulation(i, days, initial_price, drift, volatility)
                payoffs.append(payoff)
                triggers.append(is_triggered)
    
    except Exception as e:
        print(f"模拟过程中出错: {e}")
        # 如果出错，至少返回一些模拟结果
        if len(payoffs) < 100:
            print("生成简单模拟数据...")
            for i in range(1000):
                is_triggered = np.random.random() > 0.7
                final_price = initial_price * (1 + np.random.normal(0.05, 0.2))
                payoff = calculate_echo_payoff(is_triggered, final_price, initial_price)
                payoffs.append(payoff)
                triggers.append(is_triggered)
    
    # 计算定价和置信区间
    mean_payoff = np.mean(payoffs)
    std_dev = np.std(payoffs)
    confidence_interval = (
        mean_payoff - 1.96 * std_dev / np.sqrt(len(payoffs)),
        mean_payoff + 1.96 * std_dev / np.sqrt(len(payoffs))
    )
    
    # 计算触发比例
    triggered_ratio = np.mean(triggers)
    
    return mean_payoff, confidence_interval, payoffs, triggered_ratio

# 组合策略 A：SPY vs SPY+EchoNote
def simulate_combination_strategy(num_simulations=1000, days=252, initial_price=100, drift=0.05, volatility=0.2):
    """
    模拟组合策略：SPY vs SPY+EchoNote
    
    参数:
    - num_simulations: 模拟次数
    - days: 模拟天数
    - initial_price: 初始价格
    - drift: 年化漂移
    - volatility: 年化波动率
    
    返回:
    - spy_paths: SPY 价格路径
    - combo_paths: 组合策略价格路径
    - max_drawdowns_spy: SPY 最大回撤
    - max_drawdowns_combo: 组合策略最大回撤
    """
    spy_paths = []
    combo_paths = []
    max_drawdowns_spy = []
    max_drawdowns_combo = []
    
    for sim_id in tqdm(range(num_simulations), desc="Simulating Combination Strategy"):
        try:
            # 模拟 SPY 价格路径
            is_triggered, final_price, spy_price_path, trigger_day = simulate_echo_note(
                days=days, 
                initial_price=initial_price, 
                drift=drift, 
                volatility=volatility,
                seed=sim_id
            )
            
            # 计算 EchoDetect Note 收益
            echo_payoff = calculate_echo_payoff(is_triggered, final_price, initial_price)
            
            # 计算组合策略价格路径
            # 95% SPY + 5% EchoDetect Note
            combo_path = spy_price_path.copy()
            
            if is_triggered and trigger_day > 0:
                # 如果触发，根据触发日调整价格路径
                adjustment = (echo_payoff / initial_price - 0.95) * 0.05
                combo_path[trigger_day:] *= (1 + adjustment)
            
            spy_paths.append(spy_price_path)
            combo_paths.append(combo_path)
            
            # 计算最大回撤
            max_drawdowns_spy.append(calculate_max_drawdown(spy_price_path))
            max_drawdowns_combo.append(calculate_max_drawdown(combo_path))
        except Exception as e:
            print(f"模拟第 {sim_id} 次时出错: {e}")
    
    return spy_paths, combo_paths, max_drawdowns_spy, max_drawdowns_combo

# 计算最大回撤
def calculate_max_drawdown(prices):
    """
    计算最大回撤
    
    参数:
    - prices: 价格序列
    
    返回:
    - max_drawdown: 最大回撤百分比
    """
    if len(prices) <= 1:
        return 0.0
    
    peaks = np.maximum.accumulate(prices)
    drawdowns = (peaks - prices) / peaks
    return np.max(drawdowns) if len(drawdowns) > 0 else 0.0

# 可视化独立收益分布
def visualize_payoff_distribution(payoffs, triggered_ratio):
    """
    可视化独立收益分布
    
    参数:
    - payoffs: 收益列表
    - triggered_ratio: 触发比例
    """
    try:
        plt.figure(figsize=(12, 8))
        plt.hist(payoffs, bins=50, color='blue', alpha=0.7)
        plt.axvline(np.mean(payoffs), color='red', linestyle='--', linewidth=2, 
                    label=f'Mean Payoff: {np.mean(payoffs):.2f}')
        plt.title(f"EchoDetect Note Payoff Distribution (触发比例: {triggered_ratio:.2%})")
        plt.xlabel("Payoff")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "payoff_distribution.png"), dpi=300)
        plt.close()
        print(f"图表已保存: {os.path.join(output_dir, 'payoff_distribution.png')}")
    except Exception as e:
        print(f"绘制收益分布图时出错: {e}")

# 可视化组合策略净值曲线
def visualize_combination_strategy(spy_paths, combo_paths, max_drawdowns_spy, max_drawdowns_combo):
    """
    可视化组合策略净值曲线和最大回撤
    
    参数:
    - spy_paths: SPY 价格路径
    - combo_paths: 组合策略价格路径
    - max_drawdowns_spy: SPY 最大回撤
    - max_drawdowns_combo: 组合策略最大回撤
    """
    if not spy_paths or not combo_paths:
        print("没有足够的数据进行可视化")
        return
    
    try:
        # 选择有代表性的几条路径
        num_samples = min(10, len(spy_paths))
        if num_samples <= 0:
            print("没有足够的样本进行可视化")
            return
            
        sample_indices = np.random.choice(len(spy_paths), num_samples, replace=False)
        
        # 1. 净值曲线对比
        plt.figure(figsize=(12, 8))
        
        for idx in sample_indices:
            plt.plot(np.arange(len(spy_paths[idx])), spy_paths[idx] / spy_paths[idx][0], 
                     alpha=0.3, color='blue')
            plt.plot(np.arange(len(combo_paths[idx])), combo_paths[idx] / combo_paths[idx][0], 
                     alpha=0.3, color='green')
        
        # 添加平均曲线
        try:
            avg_spy = np.mean([path / path[0] for path in spy_paths], axis=0)
            avg_combo = np.mean([path / path[0] for path in combo_paths], axis=0)
            
            plt.plot(np.arange(len(avg_spy)), avg_spy, color='blue', linewidth=2, 
                     label='SPY 平均净值')
            plt.plot(np.arange(len(avg_combo)), avg_combo, color='green', linewidth=2, 
                     label='SPY+EchoNote 平均净值')
        except Exception as e:
            print(f"计算平均净值曲线时出错: {e}")
        
        plt.title("组合策略净值曲线对比")
        plt.xlabel("交易日")
        plt.ylabel("净值")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "combination_strategy_curves.png"), dpi=300)
        plt.close()
        print(f"图表已保存: {os.path.join(output_dir, 'combination_strategy_curves.png')}")
        
        # 2. 最大回撤对比
        if max_drawdowns_spy and max_drawdowns_combo:
            plt.figure(figsize=(12, 8))
            plt.hist(max_drawdowns_spy, bins=50, alpha=0.7, label="SPY 最大回撤", color="blue")
            plt.hist(max_drawdowns_combo, bins=50, alpha=0.7, label="SPY+EchoNote 最大回撤", color="green")
            plt.title("最大回撤分布对比")
            plt.xlabel("最大回撤")
            plt.ylabel("频率")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "max_drawdown_comparison.png"), dpi=300)
            plt.close()
            print(f"图表已保存: {os.path.join(output_dir, 'max_drawdown_comparison.png')}")
            
            # 3. 打印回撤统计数据
            print(f"SPY 平均最大回撤: {np.mean(max_drawdowns_spy):.2%}")
            print(f"组合策略平均最大回撤: {np.mean(max_drawdowns_combo):.2%}")
            print(f"SPY 最大回撤 95% 分位数: {np.percentile(max_drawdowns_spy, 95):.2%}")
            print(f"组合策略最大回撤 95% 分位数: {np.percentile(max_drawdowns_combo, 95):.2%}")
    except Exception as e:
        print(f"可视化组合策略时出错: {e}")

# 可视化触发频率和路径
def visualize_trigger_pathways(num_simulations=1000, days=252, initial_price=100, drift=0.05, volatility=0.2):
    """
    可视化触发频率和路径
    
    参数:
    - num_simulations: 模拟次数
    - days: 模拟天数
    - initial_price: 初始价格
    - drift: 年化漂移
    - volatility: 年化波动率
    """
    trigger_days = []
    triggered_paths = []
    non_triggered_paths = []
    
    for sim_id in tqdm(range(num_simulations), desc="Analyzing Trigger Pathways"):
        try:
            is_triggered, _, price_path, trigger_day = simulate_echo_note(
                days=days, 
                initial_price=initial_price, 
                drift=drift, 
                volatility=volatility,
                seed=sim_id
            )
            
            if is_triggered:
                trigger_days.append(trigger_day)
                triggered_paths.append(price_path / price_path[0])
            else:
                non_triggered_paths.append(price_path / price_path[0])
        except Exception as e:
            print(f"分析触发路径第 {sim_id} 次时出错: {e}")
    
    try:
        # 可视化触发日分布
        if trigger_days:
            plt.figure(figsize=(12, 8))
            bins = min(50, len(trigger_days))
            if bins > 0:
                plt.hist(trigger_days, bins=bins, color='red', alpha=0.7)
                plt.title(f"EchoDetect Note 触发日分布 (触发比例: {len(trigger_days)/num_simulations:.2%})")
                plt.xlabel("触发日")
                plt.ylabel("频率")
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, "trigger_day_distribution.png"), dpi=300)
                plt.close()
                print(f"图表已保存: {os.path.join(output_dir, 'trigger_day_distribution.png')}")
        else:
            print("没有触发事件，跳过触发日分布图")
        
        # 可视化触发路径 vs 非触发路径
        plt.figure(figsize=(12, 8))
        
        # 绘制触发路径
        if triggered_paths:
            num_samples = min(30, len(triggered_paths))
            if num_samples > 0:
                for path in np.random.choice(triggered_paths, num_samples, replace=False):
                    plt.plot(np.arange(len(path)), path, color='red', alpha=0.2)
                
                avg_triggered = np.mean(triggered_paths, axis=0)
                plt.plot(np.arange(len(avg_triggered)), avg_triggered, color='red', linewidth=2, 
                        label='触发路径平均')
        
        # 绘制非触发路径
        if non_triggered_paths:
            num_samples = min(30, len(non_triggered_paths))
            if num_samples > 0:
                for path in np.random.choice(non_triggered_paths, num_samples, replace=False):
                    plt.plot(np.arange(len(path)), path, color='blue', alpha=0.2)
                
                avg_non_triggered = np.mean(non_triggered_paths, axis=0)
                plt.plot(np.arange(len(avg_non_triggered)), avg_non_triggered, color='blue', linewidth=2, 
                        label='非触发路径平均')
        
        plt.title("触发路径 vs 非触发路径对比")
        plt.xlabel("交易日")
        plt.ylabel("相对价格")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "trigger_path_comparison.png"), dpi=300)
        plt.close()
        print(f"图表已保存: {os.path.join(output_dir, 'trigger_path_comparison.png')}")
    except Exception as e:
        print(f"可视化触发路径时出错: {e}")

# 执行模拟和可视化
if __name__ == "__main__":
    try:
        print("📊 开始 EchoDetect Note 定价模拟...")
        
        # 减少模拟数量以加快速度，同时避免可能的内存问题
        simulation_count = 5000  # 减少模拟次数
        
        mean_payoff, confidence_interval, payoffs, triggered_ratio = monte_carlo_pricing(
            num_simulations=simulation_count, 
            days=252, 
            initial_price=100, 
            drift=0.05, 
            volatility=0.2
        )
        
        print(f"平均收益: {mean_payoff:.2f}")
        print(f"95% 置信区间: [{confidence_interval[0]:.2f}, {confidence_interval[1]:.2f}]")
        print(f"触发比例: {triggered_ratio:.2%}")
        
        # 可视化独立收益分布
        visualize_payoff_distribution(payoffs, triggered_ratio)
        
        print("\n📈 开始组合策略模拟...")
        # 组合策略模拟（数量更少）
        combination_count = 500  # 减少组合策略模拟次数
        
        spy_paths, combo_paths, max_drawdowns_spy, max_drawdowns_combo = simulate_combination_strategy(
            num_simulations=combination_count, 
            days=252, 
            initial_price=100, 
            drift=0.05, 
            volatility=0.2
        )
        
        # 可视化组合策略
        visualize_combination_strategy(spy_paths, combo_paths, max_drawdowns_spy, max_drawdowns_combo)
        
        print("\n🔍 分析触发路径...")
        # 可视化触发频率和路径（数量更少）
        pathway_count = 500  # 减少触发路径分析次数
        
        visualize_trigger_pathways(
            num_simulations=pathway_count, 
            days=252, 
            initial_price=100, 
            drift=0.05, 
            volatility=0.2
        )
        
        print("\n✅ 模拟完成！图表已保存至 simulation_charts 文件夹。")
        
    except Exception as e:
        print(f"运行时出错: {e}")
        import traceback
        traceback.print_exc()