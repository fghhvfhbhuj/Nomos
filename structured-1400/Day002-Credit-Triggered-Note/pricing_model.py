# pricing_model.py
# Day002 — Credit-Triggered Redemption Note 定价模型（教学可视化版）

import numpy as np
import matplotlib.pyplot as plt
from math import exp
import os

# === 参数设定（可根据实际结构调整） ===

principal = 100_000               # 本金（例如 10万元）
annual_discount_rate = 0.05      # 年贴现率（5%）
risk_premium = 5_000             # 保费 π（结构中的盈利空间）
observation_days = 15            # 观察期（天数）
observation_compensation_rate = annual_discount_rate  # 默认同贴现率
T_obs = observation_days / 365   # 观察期时间（年）

# 假设每季度票息 2.5%，共四期，最后一期含本金返还
cash_flows = np.array([2_500, 2_500, 2_500, 102_500])
times = np.array([0.25, 0.5, 0.75, 1.0])

# === 贴现函数 ===
def discount(value, time, rate=annual_discount_rate):
    return value * exp(-rate * time)

# === 正常结构收益计算 ===
V_normal = sum(discount(c, t) for c, t in zip(cash_flows, times))
V_obs = principal * (exp(observation_compensation_rate * T_obs) - 1)  # 观察期贴现补偿

# === 敲出路径赔付值 ===
V_knockout = V_normal + risk_premium
# 可选：封顶赔付比例，例如 110%
V_knockout = min(V_knockout, principal * 1.1)

# === 敲出概率模拟与结构定价 ===
knockout_probs = np.linspace(0, 0.5, 100)  # 敲出概率从0到50%
expected_values = (1 - knockout_probs) * (V_normal + V_obs) + knockout_probs * V_knockout

# === 可视化输出 ===
plt.figure(figsize=(10, 6))
plt.plot(knockout_probs, expected_values, label='结构期望价值')
plt.axhline(y=principal, color='red', linestyle='--', label='本金基准线')
plt.title('Day002: 敲出概率 vs 结构票据期望价值')
plt.xlabel('敲出概率')
plt.ylabel('结构票据理论定价（含贴现）')
plt.legend()
plt.grid(True)
plt.tight_layout()

# 保存图像到本地目录
output_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
output_path = os.path.join(output_dir, 'ctn_pricing_visualization.png')
plt.savefig(output_path, dpi=300)
print(f"图像已保存至: {output_path}")

# 显示图像
plt.show()
