import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from tqdm import tqdm

# 输出路径
output_dir = './simulation_charts'
os.makedirs(output_dir, exist_ok=True)

# 参数设定
S0 = 100              # 初始价格
mu = 0.02             # 年化收益率
sigma = 0.3           # 年化波动率
T = 1 / 12            # 合约期限（1个月）
dt = 1 / 252          # 时间步长（每日）
N = int(T / dt)       # 步数
M = 10000             # 模拟路径数
tick_size = 0.5       # Tick 单位
margin_ratio = 0.1    # 强平线：初始价格的10%亏损
initial_equity = 10000
strong_line = initial_equity * (1 - margin_ratio)

# 产品参数
payout = 1000         # 赔付金额 a
tick_threshold = 3    # 连续跌 tick 次数 t

# 函数：判断某路径是否满足“跳跃式强平”
def is_jump_triggered(price_path):
    for i in range(tick_threshold, len(price_path)):
        ticks = price_path[i - tick_threshold:i]
        deltas = np.diff(ticks)
        if np.all(deltas < -tick_size):  # 连续下跌
            pre_equity = initial_equity * (ticks[-2] / S0)
            now_equity = initial_equity * (ticks[-1] / S0)
            if pre_equity > strong_line and now_equity < strong_line:
                return True
    return False

# 模拟与判断
triggered_count = 0
results = []
example_trigger = None

for _ in tqdm(range(M)):
    Z = np.random.normal(size=N)
    price_path = S0 * np.exp(np.cumsum((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z))
    if is_jump_triggered(price_path):
        triggered_count += 1
        if example_trigger is None:
            example_trigger = price_path
    results.append(price_path)

# 定价与输出
trigger_prob = triggered_count / M
price = payout * trigger_prob

print("模拟次数\t赔付金额\t触发比例\t结构价格")
print(f"{M}\t{payout}\t{trigger_prob:.4f}\t{price:.2f}")

# 图像保存
if example_trigger is not None:
    plt.figure(figsize=(10, 4))
    plt.plot(example_trigger, label='示例路径')
    plt.axhline(S0 * (1 - margin_ratio), linestyle='--', color='red', label='强平线')
    plt.title('Day003: Tick Jump Path Example')
    plt.xlabel('时间')
    plt.ylabel('价格')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'price_jump_demo.png'))
    plt.close()

# 可选：保存结果数据 CSV
mean_path = np.mean(results, axis=0)
df = pd.DataFrame({'time': np.arange(N), 'mean_price': mean_path})
df.to_csv('pricing_result_day003.csv', index=False)
