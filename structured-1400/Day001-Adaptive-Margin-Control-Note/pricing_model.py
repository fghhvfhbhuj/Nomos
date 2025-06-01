import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import pandas as pd
from scipy import stats

# 设置图像保存路径
output_dir = "./simulation_charts"
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory created/confirmed at: {os.path.abspath(output_dir)}")

# 模拟参数
S0 = 100                  # 初始价格
mu = 0.05                 # 年化期望收益
sigma_base = 0.2          # 基础年化波动率
T = 1                     # 投资期限1年
dt = 1 / 252              # 日度步长
N = int(T / dt)           # 步数
n_paths = 10000           # 模拟路径数
principal = 100           # 本金

# 跳跃扩散模型参数
jump_intensity = 5        # 每年跳跃次数期望
jump_mean = -0.01         # 跳跃大小均值
jump_std = 0.03           # 跳跃大小标准差

# 随机波动率模型参数
vol_mean_reversion = 3.0  # 波动率均值回归速度
vol_long_run_mean = 0.2   # 长期波动率均值
vol_vol = 0.3             # 波动率的波动率

# 产品参数
cap_return = 0.30                     # 收益封顶
knock_in_return = 0.20                # 敲入阈值
initial_margin = 0.10 * principal     # 初始保证金
maintenance_margin = 0.05 * principal # 维持保证金
max_leverage = 10                     # 最大杠杆倍数

# 存储模拟结果
final_payouts = []
example_paths = []
example_pools = []
example_volatilities = []
knocked_in_count = 0
knocked_out_count = 0

# 风险度量指标
var_95 = 0
var_99 = 0
expected_shortfall = 0
max_drawdowns = []

# 蒙特卡洛模拟
for i in tqdm(range(n_paths)):
    prices = [S0]
    volatilities = [sigma_base]
    current_sigma = sigma_base
    pool = 0
    knocked_in = False
    max_price = S0
    min_equity = principal
    
    for t in range(N):
        # 更新随机波动率 (Heston-like)
        vol_shock = np.random.normal(0, 1)
        current_sigma = max(0.05, current_sigma + vol_mean_reversion * (vol_long_run_mean - current_sigma) * dt + 
                        vol_vol * np.sqrt(current_sigma * dt) * vol_shock)
        volatilities.append(current_sigma)
        
        # 价格扩散
        z = np.random.normal()
        dS_diffusion = prices[-1] * (mu * dt + current_sigma * np.sqrt(dt) * z)
        
        # 跳跃过程
        jump_occurs = np.random.poisson(jump_intensity * dt)
        dS_jump = 0
        if jump_occurs > 0:
            jump_size = np.random.normal(jump_mean, jump_std, jump_occurs)
            dS_jump = prices[-1] * np.sum(jump_size)
        
        # 总价格变动
        new_price = prices[-1] + dS_diffusion + dS_jump
        prices.append(max(0.01, new_price))  # 防止价格为负
        
        # 追踪最高价格（用于计算回撤）
        max_price = max(max_price, prices[-1])
        
        # 计算当前权益价值
        current_return = (prices[-1] - S0) / S0
        current_equity = principal * (1 + current_return)
        
        # 敲入检查（只在第一次超过阈值时触发）
        if not knocked_in and current_return > knock_in_return:
            knocked_in = True
            knocked_in_count += 1
            
            # 如果立即超过封顶，将超额部分转入资金池
            if current_return > cap_return:
                excess = (current_return - cap_return) * principal
                pool += excess
        
        # 更新最低权益
        min_equity = min(min_equity, current_equity)
        
        # 检查是否触发维持保证金补充
        if current_equity < maintenance_margin and pool > 0:
            needed = maintenance_margin - current_equity
            refill = min(pool, needed)
            current_equity += refill
            pool -= refill
            min_equity = current_equity  # 更新最低权益
        
        # 检查是否触发敲出（强制平仓）
        if current_equity < maintenance_margin and pool == 0:
            knocked_out_count += 1
            break  # 提前终止此路径模拟

    # 计算最终收益
    S_T = prices[-1]
    R_T = (S_T - S0) / S0
    
    # 根据敲入状态计算最终收益
    if knocked_in:
        if R_T > cap_return:
            payout = cap_return * principal
            # 已在路径中将超额收益转入资金池
        else:
            payout = min(R_T, cap_return) * principal
    else:
        payout = R_T * principal
    
    # 如果触发了强平，最终收益为最低权益
    if min_equity < maintenance_margin and pool == 0:
        payout = min_equity
    
    # 计算最大回撤
    max_drawdown = (max_price - min(prices)) / max_price
    max_drawdowns.append(max_drawdown)
    
    final_payouts.append(payout)
    
    # 保存前4条路径做可视化
    if i < 4:
        example_paths.append(prices)
        example_pools.append(pool)
        example_volatilities.append(volatilities)

# 计算风险指标
final_payouts = np.array(final_payouts)
expected_value = np.mean(final_payouts)
var_95 = np.percentile(final_payouts, 5)  # 95% VaR
var_99 = np.percentile(final_payouts, 1)  # 99% VaR
expected_shortfall = np.mean(final_payouts[final_payouts <= var_95])  # 条件风险价值(CVaR)
avg_max_drawdown = np.mean(max_drawdowns)
knock_in_probability = knocked_in_count / n_paths
knock_out_probability = knocked_out_count / n_paths

# 可视化生成
print(f"生成{len(example_paths)}条示例路径可视化...")
for i, (path, vols) in enumerate(zip(example_paths, example_volatilities)):
    # 价格路径图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 价格路径
    ax1.plot(path, label='价格路径', color='blue')
    ax1.axhline(S0 * (1 + knock_in_return), color='orange', linestyle='--', label='敲入线')
    ax1.axhline(S0 * (1 + cap_return), color='green', linestyle='--', label='封顶线')
    ax1.set_title(f'情景 {i+1} - 价格路径与波动率')
    ax1.set_ylabel('价格')
    ax1.legend()
    
    # 波动率路径
    ax2.plot(vols, label='波动率', color='red')
    ax2.set_xlabel('交易日')
    ax2.set_ylabel('波动率')
    ax2.legend()
    
    plt.tight_layout()
    save_path = os.path.abspath(f"{output_dir}/scenario{i+1}_price_path.png")
    plt.savefig(save_path)
    print(f"Saved visualization to: {save_path}")
    plt.close()

# 添加收益分布可视化
plt.figure(figsize=(10, 6))
plt.hist(final_payouts, bins=50, alpha=0.7, color='blue', density=True)
plt.axvline(expected_value, color='red', linestyle='--', label=f'期望值: {expected_value:.2f}')
plt.axvline(principal, color='green', linestyle='--', label=f'初始本金: {principal}')
plt.axvline(var_95, color='orange', linestyle='--', label=f'95% VaR: {var_95:.2f}')
plt.axvline(var_99, color='purple', linestyle='--', label=f'99% VaR: {var_99:.2f}')

# 添加密度曲线
x = np.linspace(min(final_payouts), max(final_payouts), 1000)
kde = stats.gaussian_kde(final_payouts)
plt.plot(x, kde(x), 'r-', label='密度估计')

plt.title('最终收益分布')
plt.xlabel('收益值')
plt.ylabel('频率密度')
plt.legend()
plt.tight_layout()
summary_path = os.path.abspath(f"{output_dir}/payout_distribution.png")
plt.savefig(summary_path)
print(f"收益分布图已保存至: {summary_path}")
plt.close()

# 添加回撤分布可视化
plt.figure(figsize=(10, 6))
plt.hist(max_drawdowns, bins=30, alpha=0.7, color='red')
plt.axvline(avg_max_drawdown, color='black', linestyle='--', label=f'平均最大回撤: {avg_max_drawdown:.2%}')
plt.title('最大回撤分布')
plt.xlabel('回撤比例')
plt.ylabel('频率')
plt.legend()
plt.tight_layout()
drawdown_path = os.path.abspath(f"{output_dir}/max_drawdown_distribution.png")
plt.savefig(drawdown_path)
print(f"回撤分布图已保存至: {drawdown_path}")
plt.close()

# 保存结果为CSV
result_df = pd.DataFrame({
    '模拟次数': [n_paths],
    '票据理论价值': [expected_value],
    '初始本金': [principal],
    '收益封顶': [cap_return],
    '敲入阈值': [knock_in_return],
    '维持保证金线': [maintenance_margin],
    '95%风险价值(VaR)': [var_95],
    '99%风险价值(VaR)': [var_99],
    '条件风险价值(CVaR)': [expected_shortfall],
    '平均最大回撤': [avg_max_drawdown],
    '敲入概率': [knock_in_probability],
    '强平概率': [knock_out_probability]
})

result_df.to_csv("./pricing_result.csv", index=False)
print("模拟结果摘要:")
print(result_df)

# 增加敏感性分析
print("\n开始进行敏感性分析...")

# 波动率敏感性分析
volatilities = [0.15, 0.20, 0.25, 0.30, 0.35]
vol_expected_values = []
vol_var95_values = []

for vol in tqdm(volatilities, desc="波动率敏感性"):
    # 简化版模拟，仅计算期望值
    sim_payouts = []
    for _ in range(1000):  # 减少模拟次数以加快敏感性分析
        prices = [S0]
        for t in range(N):
            z = np.random.normal()
            dS = prices[-1] * (mu * dt + vol * np.sqrt(dt) * z)
            prices.append(max(0.01, prices[-1] + dS))
            
        S_T = prices[-1]
        R_T = (S_T - S0) / S0
        
        if R_T > knock_in_return:
            payout = min(R_T, cap_return) * principal
        else:
            payout = R_T * principal
            
        sim_payouts.append(payout)
    
    vol_expected_values.append(np.mean(sim_payouts))
    vol_var95_values.append(np.percentile(sim_payouts, 5))

# 绘制波动率敏感性分析
plt.figure(figsize=(10, 6))
plt.plot(volatilities, vol_expected_values, 'b-o', label='期望收益')
plt.plot(volatilities, vol_var95_values, 'r-o', label='95% VaR')
plt.axhline(principal, color='green', linestyle='--', label='初始本金')
plt.title('波动率敏感性分析')
plt.xlabel('波动率')
plt.ylabel('收益值')
plt.legend()
plt.grid(True)
plt.tight_layout()
vol_sensitivity_path = os.path.abspath(f"{output_dir}/volatility_sensitivity.png")
plt.savefig(vol_sensitivity_path)
print(f"波动率敏感性分析图已保存至: {vol_sensitivity_path}")
plt.close()

print("模型优化和分析完成!")
