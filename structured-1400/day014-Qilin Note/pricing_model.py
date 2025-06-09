import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Ensure the simulation_charts directory exists
output_dir = "simulation_charts"
os.makedirs(output_dir, exist_ok=True)

# Monte Carlo Simulation for Qilin Note Pricing
def simulate_qilin_note(num_simulations=10000, years=1):
    """
    更复杂的Qilin Note定价模拟：引入随机波动率、相关性、极端事件和非线性触发。
    :param num_simulations: Number of Monte Carlo simulations
    :param years: Number of years for the simulation
    :return: Simulated annualized returns
    """
    # Parameters
    exchange_rate_mean = 0.0  # Mean exchange rate change (%)
    exchange_rate_std = 1.5  # Standard deviation of exchange rate change (%)
    stock_market_mean = 0.0  # Mean stock market change (%)
    stock_market_std = 10.0  # Standard deviation of stock market change (%)
    corr = 0.35  # 汇率与股市的相关性
    # 随机波动率
    vol_of_vol = 0.5
    # 极端事件概率
    tail_event_prob = 0.03
    tail_event_impact = -20

    # 相关性协方差矩阵
    cov = [[exchange_rate_std ** 2, corr * exchange_rate_std * stock_market_std],
           [corr * exchange_rate_std * stock_market_std, stock_market_std ** 2]]

    # 蒙特卡洛模拟
    returns = []
    for _ in range(num_simulations):
        # 随机波动率
        sigma_er = abs(np.random.normal(exchange_rate_std, vol_of_vol))
        sigma_sm = abs(np.random.normal(stock_market_std, vol_of_vol * 10))
        cov_sim = [[sigma_er ** 2, corr * sigma_er * sigma_sm],
                   [corr * sigma_er * sigma_sm, sigma_sm ** 2]]
        # 联合正态采样
        er, sm = np.random.multivariate_normal([exchange_rate_mean, stock_market_mean], cov_sim)
        # 极端事件
        if np.random.rand() < tail_event_prob:
            sm += tail_event_impact * np.random.beta(2, 5)
        # 复杂非线性触发
        base = 4.0
        if abs(er) < 0.5 and abs(sm) < 3:
            enhanced = 3.0
        elif er > 1.5 or sm > 10:
            enhanced = 3.0 + 0.5 * np.tanh(sm / 10)
        elif er < -1.5 or sm < -15:
            enhanced = 4.0 + 0.5 * np.tanh(-sm / 10)
        else:
            enhanced = 0.5 * np.sin(er) + 0.5 * np.cos(sm / 10)
        # 触发提前赎回
        if sm > 20 or er > 3:
            total = base + enhanced - 1.5  # 提前赎回惩罚
        else:
            total = base + enhanced
        returns.append(total)
    return np.array(returns)

# Run simulation
simulated_returns = simulate_qilin_note()

# Plot results
plt.figure(figsize=(8,5))
plt.hist(simulated_returns, bins=60, color='navy', alpha=0.75, density=True, label='模拟分布')
# 拟合正态分布
mu, std = np.mean(simulated_returns), np.std(simulated_returns)
x = np.linspace(mu-3*std, mu+3*std, 200)
plt.plot(x, stats.norm.pdf(x, mu, std), 'r--', label='正态拟合')
plt.title('Qilin Note模拟年化收益分布（大师版）')
plt.xlabel('年化收益率(%)')
plt.ylabel('概率密度')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
# 保存图片
output_path = os.path.join(output_dir, "simulated_annualized_returns_masterpiece.png")
plt.savefig(output_path)
plt.close()

print(f"大师版模拟图表已保存到 {output_path}")