import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import pandas as pd

# 设置图像保存路径
output_dir = "./simulation_charts"
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory created/confirmed at: {os.path.abspath(output_dir)}")

# 模拟参数
S0 = 100                  # 初始价格
mu = 0.05                 # 年化期望收益
sigma = 0.2               # 年化波动率
T = 1                     # 投资期限1年
dt = 1 / 252              # 日度步长
N = int(T / dt)           # 步数
n_paths = 10000           # 模拟路径数
principal = 100           # 本金

# 产品参数
cap_return = 0.30                     # 收益封顶
knock_in_return = 0.20                # 敲入阈值
initial_margin = 0.10 * principal     # 初始保证金
maintenance_margin = 0.05 * principal # 维持保证金

# 存储模拟结果
final_payouts = []
example_paths = []
example_pools = []

# 蒙特卡洛模拟
for i in tqdm(range(n_paths)):
    prices = [S0]
    for _ in range(N):
        z = np.random.normal()
        dS = prices[-1] * (mu * dt + sigma * np.sqrt(dt) * z)
        prices.append(prices[-1] + dS)

    S_T = prices[-1]
    R_T = (S_T - S0) / S0
    payout = 0
    pool = 0

    # 敲入判断
    if R_T > knock_in_return:
        if R_T > cap_return:
            payout = cap_return * principal
            pool = (R_T - cap_return) * principal
        else:
            payout = R_T * principal
    else:
        payout = R_T * principal

    # 路径中最低权益判断是否触发敲出
    min_price = min(prices)
    min_equity = principal * (min_price / S0)

    if min_equity < maintenance_margin:
        if pool > 0:
            needed = maintenance_margin - min_equity
            refill = min(pool, needed)
            min_equity += refill
            pool -= refill

    if min_equity < maintenance_margin and pool == 0:
        final_payouts.append(min_equity)
    else:
        final_payouts.append(payout)

    # 保存前4条路径做可视化
    if i < 4:
        example_paths.append(prices)
        example_pools.append(pool)

# 计算期望价值 - 移到这里，在画图前计算
expected_value = np.mean(final_payouts)

# 可视化生成
print(f"生成{len(example_paths)}条示例路径可视化...")
for i, path in enumerate(example_paths):
    fig, ax = plt.subplots()
    ax.plot(path, label='Price Path', color='blue')
    ax.axhline(S0 * (1 + knock_in_return), color='orange', linestyle='--', label='Knock-In')
    ax.axhline(S0 * (1 + cap_return), color='green', linestyle='--', label='Cap')
    ax.set_title(f'Scenario {i+1} - Price Path')
    ax.set_xlabel('Days')
    ax.set_ylabel('Price')
    ax.legend()
    plt.tight_layout()
    
    # Save with absolute path for clarity
    save_path = os.path.abspath(f"{output_dir}/scenario{i+1}_price_path.png")
    plt.savefig(save_path)
    print(f"Saved visualization to: {save_path}")
    plt.close()

# 添加所有收益的汇总可视化
plt.figure(figsize=(10, 6))
plt.hist(final_payouts, bins=50, alpha=0.7, color='blue')
plt.axvline(expected_value, color='red', linestyle='--', label=f'期望值: {expected_value:.2f}')
plt.axvline(principal, color='green', linestyle='--', label=f'初始本金: {principal}')
plt.title('最终收益分布')
plt.xlabel('收益值')
plt.ylabel('频率')
plt.legend()
plt.tight_layout()
summary_path = os.path.abspath(f"{output_dir}/payout_distribution.png")
plt.savefig(summary_path)
print(f"收益分布图已保存至: {summary_path}")
plt.close()

# 保存结果为CSV（可选）
result_df = pd.DataFrame({
    '模拟次数': [n_paths],
    '票据理论价值': [expected_value],
    '初始本金': [principal],
    '收益封顶': [cap_return],
    '敲入阈值': [knock_in_return],
    '维持保证金线': [maintenance_margin]
})

result_df.to_csv("./pricing_result.csv", index=False)
print(result_df)
