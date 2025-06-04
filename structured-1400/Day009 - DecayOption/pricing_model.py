import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import norm

def ensure_directory_exists(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

# Step 1: Generate CDS sequence - 修复导数计算方法
def generate_CDS_sequence(S, delta_S, V):
    """生成高阶导数贡献序列
    使用有限差分法计算高阶导数
    """
    CDS_sequence = []
    for n in range(2, 6):
        # 使用中心差分法计算n阶导数
        if n == 2:  # 二阶导数
            second_deriv = np.gradient(np.gradient(V, S), S)
            CDS_sequence.append(np.abs(second_deriv) * (delta_S ** n))
        elif n == 3:  # 三阶导数
            third_deriv = np.gradient(np.gradient(np.gradient(V, S), S), S)
            CDS_sequence.append(np.abs(third_deriv) * (delta_S ** n))
        elif n == 4:  # 四阶导数
            fourth_deriv = np.gradient(np.gradient(np.gradient(np.gradient(V, S), S), S), S)
            CDS_sequence.append(np.abs(fourth_deriv) * (delta_S ** n))
        elif n == 5:  # 五阶导数
            fifth_deriv = np.gradient(np.gradient(np.gradient(np.gradient(np.gradient(V, S), S), S), S), S)
            CDS_sequence.append(np.abs(fifth_deriv) * (delta_S ** n))
    
    return CDS_sequence

# Step 2: Compute DecayIndex - 修复点积计算
def compute_decay_index(CDS_sequence, threshold):
    """计算DecayIndex并判断是否触发"""
    weights = [1 / (n ** 2) for n in range(2, 6)]
    # 手动计算加权和，避免维度不匹配问题
    decay_index = sum(w * np.mean(cds) for w, cds in zip(weights, CDS_sequence))
    return decay_index, decay_index <= threshold

# Step 3: Simulate structure failure
def simulate_structure_failure(triggered, VAR, threshold_VAR):
    """模拟结构爆发场景"""
    return 10000 if triggered and VAR > threshold_VAR else 0

# Step 4: Monte Carlo pricing
def monte_carlo_pricing(S, delta_S, V, threshold, VAR, threshold_VAR, num_simulations):
    """Monte Carlo定价"""
    # 预先计算CDS序列和DecayIndex，避免重复计算
    CDS_sequence = generate_CDS_sequence(S, delta_S, V)
    decay_index, triggered = compute_decay_index(CDS_sequence, threshold)
    
    # 根据触发条件和VAR模拟多次
    payoffs = []
    for _ in range(num_simulations):
        # 随机模拟VAR波动
        simulated_VAR = VAR * (1 + 0.2 * np.random.randn())
        payoff = simulate_structure_failure(triggered, simulated_VAR, threshold_VAR)
        payoffs.append(payoff)
    
    # 折现计算期望收益
    return np.mean(payoffs) * np.exp(-0.05)

# Visualization and saving to simulation_charts
def visualize_and_save(S, V, CDS_sequence, decay_index, threshold, payoffs):
    """生成并保存多种图表"""
    try:
        # 确保目录存在，使用绝对路径
        charts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation_charts")
        ensure_directory_exists(charts_dir)
        
        # 图1: 原始价值函数
        plt.figure(figsize=(10, 6))
        plt.plot(S, V)
        plt.title("Value Function")
        plt.xlabel("Underlying Price")
        plt.ylabel("Value")
        plt.grid(True)
        plt.savefig(os.path.join(charts_dir, "value_function.png"))
        plt.close()
        
        # 图2: CDS序列各阶贡献
        plt.figure(figsize=(10, 6))
        for i, cds in enumerate(CDS_sequence):
            plt.plot(S, cds, label=f"{i+2}阶导数贡献")
        plt.title("CDS Sequence Contributions")
        plt.xlabel("Underlying Price")
        plt.ylabel("Contribution")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(charts_dir, "cds_contributions.png"))
        plt.close()
        
        # 图3: DecayIndex与阈值对比
        plt.figure(figsize=(10, 6))
        plt.axhline(y=threshold, color='r', linestyle='--', label=f"Threshold: {threshold}")
        plt.axhline(y=decay_index, color='g', label=f"DecayIndex: {decay_index:.4f}")
        plt.title(f"DecayIndex vs Threshold (Triggered: {'Yes' if decay_index <= threshold else 'No'})")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(charts_dir, "decay_index.png"))
        plt.close()
        
        # 图4: 蒙特卡洛模拟结果
        plt.figure(figsize=(10, 6))
        plt.hist(payoffs, bins=20)
        plt.title("Monte Carlo Simulation Payoffs")
        plt.xlabel("Payoff")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.savefig(os.path.join(charts_dir, "monte_carlo_payoffs.png"))
        plt.close()
        
        print(f"所有图表已保存到: {charts_dir}")
    except Exception as e:
        print(f"生成图表时出错: {e}")

# Example usage
if __name__ == "__main__":
    # 基础参数设置
    S = np.linspace(100, 200, 100)  # 标的价格范围
    delta_S = 1  # 价格扰动
    
    # 构造一个更复杂的价值函数示例 (含有期权特性)
    K = 150  # 行权价
    sigma = 0.2  # 波动率
    T = 1.0  # 到期时间
    r = 0.05  # 无风险利率
    
    # Black-Scholes call option value
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    V = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    
    # 如果没有scipy的norm，可以使用简化的期权模型
    # V = np.maximum(S - K, 0) + 5 * np.sin(S/20)  # 简化的价值函数
    
    threshold = 0.1  # DecayIndex阈值
    VAR = 0.6  # 风险价值
    threshold_VAR = 0.5  # VAR阈值
    num_simulations = 1000  # 模拟次数
    
    # 计算CDS序列和DecayIndex
    CDS_sequence = generate_CDS_sequence(S, delta_S, V)
    decay_index, triggered = compute_decay_index(CDS_sequence, threshold)
    
    # 进行Monte Carlo模拟
    payoffs = [simulate_structure_failure(triggered, 
                                         VAR * (1 + 0.2 * np.random.randn()), 
                                         threshold_VAR) for _ in range(num_simulations)]
    expected_payoff = np.mean(payoffs) * np.exp(-r * T)
    
    print(f"DecayIndex: {decay_index:.4f}")
    print(f"Triggered: {'Yes' if triggered else 'No'}")
    print(f"Expected Payoff: {expected_payoff:.2f}")
    
    # 生成可视化图表
    visualize_and_save(S, V, CDS_sequence, decay_index, threshold, payoffs)