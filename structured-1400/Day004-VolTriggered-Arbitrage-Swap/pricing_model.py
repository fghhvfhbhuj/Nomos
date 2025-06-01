import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import json
from arch import arch_model
from concurrent.futures import ProcessPoolExecutor
import logging

# 设置图表输出路径
current_dir = os.path.dirname(os.path.abspath(__file__))
simulation_charts_dir = os.path.join(current_dir, "simulation_charts")
tracks_dir = os.path.join(simulation_charts_dir, "tracks")
os.makedirs(simulation_charts_dir, exist_ok=True)
os.makedirs(tracks_dir, exist_ok=True)

# 基础参数设置
num_simulations = 10000  # 模拟路径数
num_tracks_to_save = 10  # 保存的示例轨迹数
simulation_days = 30     # 模拟天数
base_rate = 1.0
fee_per_trade = 0.001    # 每次交易手续费

# 多角套汇参数
currencies = ["USD", "JPY", "CNY", "GBP", "EUR"]  # 可选货币
path_length = 4          # 套汇路径长度，即n角套汇
total_fee = path_length * fee_per_trade

# 波动率触发参数
knock_in_threshold = 0.002   # 敲入阈值d
knock_out_threshold = 0.0005 # 敲出阈值z

# 远期汇率参数
interest_rates = {
    "USD": 0.0300,  # 美元年利率
    "JPY": 0.0010,  # 日元年利率
    "CNY": 0.0250,  # 人民币年利率
    "GBP": 0.0350,  # 英镑年利率
    "EUR": 0.0200   # 欧元年利率
}

# 货币对的波动率设置
volatilities = {
    ("USD", "JPY"): 0.0080,
    ("USD", "CNY"): 0.0060,
    ("USD", "GBP"): 0.0070,
    ("USD", "EUR"): 0.0065,
    ("JPY", "CNY"): 0.0085,
    ("JPY", "GBP"): 0.0090,
    ("JPY", "EUR"): 0.0075,
    ("CNY", "GBP"): 0.0095,
    ("CNY", "EUR"): 0.0080,
    ("GBP", "EUR"): 0.0065
}

# 初始汇率 (基于USD)
initial_rates = {
    ("USD", "USD"): 1.0000,
    ("USD", "JPY"): 110.0000,
    ("USD", "CNY"): 6.4500,
    ("USD", "GBP"): 0.7200,
    ("USD", "EUR"): 0.8400
}

# 计算所有货币对的初始汇率
for base in currencies:
    for quote in currencies:
        if base != quote and (base, quote) not in initial_rates:
            # 如果直接汇率不存在，通过USD交叉计算
            if (base, "USD") in initial_rates and ("USD", quote) in initial_rates:
                base_to_usd = initial_rates.get((base, "USD"), 1.0/initial_rates.get(("USD", base)))
                usd_to_quote = initial_rates.get(("USD", quote), 1.0)
                initial_rates[(base, quote)] = base_to_usd * usd_to_quote
            else:
                # 默认值
                initial_rates[(base, quote)] = 1.0

# 获取两种货币间的波动率，如果不存在则使用默认值
def get_volatility(from_currency, to_currency):
    if (from_currency, to_currency) in volatilities:
        return volatilities[(from_currency, to_currency)]
    elif (to_currency, from_currency) in volatilities:
        return volatilities[(to_currency, from_currency)]
    else:
        return 0.0080  # 默认波动率

# 获取两种货币间的初始汇率
def get_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return 1.0
    elif (from_currency, to_currency) in initial_rates:
        return initial_rates[(from_currency, to_currency)]
    elif (to_currency, from_currency) in initial_rates:
        return 1.0 / initial_rates[(to_currency, from_currency)]
    else:
        return 1.0  # 默认值

# 计算远期汇率
def calculate_forward_rate(spot_rate, from_currency, to_currency, days):
    r_domestic = interest_rates[from_currency]
    r_foreign = interest_rates[to_currency]
    t = days / 365.0  # 转换为年
    
    # 远期汇率 = 即期汇率 * (1 + r_domestic * t) / (1 + r_foreign * t)
    forward_rate = spot_rate * (1 + r_domestic * t) / (1 + r_foreign * t)
    return forward_rate

# 计算CIP基差偏离
def calculate_cip_basis(spot_rate, forward_rate, from_currency, to_currency, days):
    r_domestic = interest_rates[from_currency]
    r_foreign = interest_rates[to_currency]
    t = days / 365.0
    
    implied_foreign_rate = r_domestic - ((forward_rate / spot_rate) - 1) / t
    cip_basis = implied_foreign_rate - r_foreign
    return cip_basis

# 生成货币兑换路径
def generate_currency_path(start_currency, length):
    path = [start_currency]
    available = [c for c in currencies if c != start_currency]
    
    # 确保路径上不会有重复货币
    for _ in range(length - 1):
        if not available:
            break
        next_curr = np.random.choice(available)
        path.append(next_curr)
        available = [c for c in available if c != next_curr]
    
    # 确保路径闭环回到起始货币
    path.append(start_currency)
    return path

# 模拟单条汇率路径
def simulate_rate_path(from_currency, to_currency, days, include_forward=False):
    spot_rate = get_rate(from_currency, to_currency)
    volatility = get_volatility(from_currency, to_currency)
    drift = 0.0  # 假设无漂移
    
    # 添加国家干预阻力项 - 当汇率极端变动时阻碍继续变动
    # 简化模型：使用 tanh 函数来限制极端移动
    
    dt = 1.0 / 252  # 假设252个交易日/年
    rate_path = [spot_rate]
    
    for _ in range(days):
        last_rate = rate_path[-1]
        # 国家干预阻力 - 偏离初始值越大，阻力越大
        deviation = (last_rate - spot_rate) / spot_rate
        intervention = -0.01 * np.tanh(deviation * 10)  # 国家干预阻力
        
        # 随机波动
        random_factor = np.random.normal(0, 1)
        
        # 带阻力项的几何布朗运动
        new_rate = last_rate * np.exp((drift + intervention) * dt + volatility * np.sqrt(dt) * random_factor)
        rate_path.append(new_rate)
    
    # 如果需要包含远期汇率
    if include_forward:
        forward_rates = []
        for day in range(days + 1):
            remaining_days = days - day
            if remaining_days > 0:
                forward = calculate_forward_rate(rate_path[day], from_currency, to_currency, remaining_days)
            else:
                forward = rate_path[day]  # 最后一天远期等于即期
            forward_rates.append(forward)
        return rate_path, forward_rates
    
    return rate_path

# 引入GARCH模型以生成波动率路径，并修改模拟汇率路径函数以使用动态波动率路径
def simulate_garch_volatility(initial_volatility, days):
    # 使用GARCH(1,1)模型生成波动率路径
    garch = arch_model(np.zeros(days), vol='Garch', p=1, q=1)
    garch_fit = garch.fit(disp='off')
    simulated_volatility = garch_fit.simulate(params=garch_fit.params, nobs=days)
    return simulated_volatility['volatility']

# 修改模拟汇率路径函数以使用GARCH波动率

def simulate_rate_path_with_garch(from_currency, to_currency, days, include_forward=False):
    spot_rate = get_rate(from_currency, to_currency)
    initial_volatility = get_volatility(from_currency, to_currency)
    drift = 0.0  # 假设无漂移

    # 使用GARCH模型生成波动率路径
    volatility_path = simulate_garch_volatility(initial_volatility, days)

    dt = 1.0 / 252  # 假设252个交易日/年
    rate_path = [spot_rate]

    for day in range(days):
        last_rate = rate_path[-1]
        deviation = (last_rate - spot_rate) / spot_rate
        intervention = -0.01 * np.tanh(deviation * 10)  # 国家干预阻力

        random_factor = np.random.normal(0, 1)
        new_rate = last_rate * np.exp((drift + intervention) * dt + volatility_path[day] * np.sqrt(dt) * random_factor)
        rate_path.append(new_rate)

    if include_forward:
        forward_rates = []
        for day in range(days + 1):
            remaining_days = days - day
            if remaining_days > 0:
                forward = calculate_forward_rate(rate_path[day], from_currency, to_currency, remaining_days)
            else:
                forward = rate_path[day]
            forward_rates.append(forward)
        return rate_path, forward_rates

    return rate_path

# 计算套利路径的综合收益
def calculate_arbitrage_profit(currency_path, day, rates_dict, include_fees=True):
    profit_factor = 1.0
    
    for i in range(len(currency_path) - 1):
        from_curr = currency_path[i]
        to_curr = currency_path[i+1]
        
        # 使用当天的汇率
        if (from_curr, to_curr) in rates_dict:
            rate = rates_dict[(from_curr, to_curr)][day]
        else:
            rate = 1.0 / rates_dict[(to_curr, from_curr)][day]
        
        profit_factor *= rate
        
        # 考虑交易手续费
        if include_fees:
            profit_factor *= (1 - fee_per_trade)
    
    # 返回百分比收益率
    return profit_factor - 1.0

# 创建模拟类
class ArbitrageSimulation:
    def __init__(self, start_currency="USD", path_length=4, days=30):
        self.start_currency = start_currency
        self.path_length = path_length
        self.days = days
        self.currency_path = generate_currency_path(start_currency, path_length)
        self.rates_dict = {}
        self.forward_rates_dict = {}
        self.cip_basis_dict = {}
        self.daily_profits = []
        self.is_triggered = False
        self.trigger_day = -1
        self.exit_day = -1
    
    def simulate(self):
        # 初始化汇率字典
        for i in range(len(self.currency_path) - 1):
            from_curr = self.currency_path[i]
            to_curr = self.currency_path[i+1]
            
            if (from_curr, to_curr) not in self.rates_dict and (to_curr, from_curr) not in self.rates_dict:
                # 模拟汇率路径
                spot_rates, forward_rates = simulate_rate_path(from_curr, to_curr, self.days, include_forward=True)
                self.rates_dict[(from_curr, to_curr)] = spot_rates
                self.forward_rates_dict[(from_curr, to_curr)] = forward_rates
                
                # 计算每日CIP基差
                cip_basis = []
                for day in range(self.days + 1):
                    remaining_days = self.days - day
                    if remaining_days > 0:
                        basis = calculate_cip_basis(
                            spot_rates[day], 
                            forward_rates[day], 
                            from_curr, to_curr, 
                            remaining_days
                        )
                        cip_basis.append(basis)
                    else:
                        cip_basis.append(0)  # 最后一天没有远期
                self.cip_basis_dict[(from_curr, to_curr)] = cip_basis
        
        # 计算每日套利收益
        for day in range(self.days + 1):
            profit = calculate_arbitrage_profit(self.currency_path, day, self.rates_dict)
            self.daily_profits.append(profit)
            
            # 检查触发条件 - 波动率触发
            if not self.is_triggered and profit > knock_in_threshold:
                self.is_triggered = True
                self.trigger_day = day
            
            # 检查退出条件 - 当收益低于阈值
            if self.is_triggered and self.exit_day == -1 and profit < knock_out_threshold:
                self.exit_day = day
    
    def get_results(self):
        return {
            "currency_path": self.currency_path,
            "daily_profits": self.daily_profits,
            "is_triggered": self.is_triggered,
            "trigger_day": self.trigger_day,
            "exit_day": self.exit_day,
            "max_profit": max(self.daily_profits) if self.daily_profits else 0,
            "final_profit": self.daily_profits[-1] if self.daily_profits else 0
        }
    
    def plot_profit_path(self, save_path):
        plt.figure(figsize=(12, 6))
        days = list(range(len(self.daily_profits)))
        
        plt.plot(days, self.daily_profits, 'b-', linewidth=2)
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axhline(y=knock_in_threshold, color='g', linestyle='--', label=f'Knock-in threshold ({knock_in_threshold:.4f})')
        plt.axhline(y=knock_out_threshold, color='r', linestyle='--', label=f'Knock-out threshold ({knock_out_threshold:.4f})')
        
        # 标记触发和退出点
        if self.is_triggered:
            plt.axvline(x=self.trigger_day, color='g', linestyle=':', label=f'Triggered on day {self.trigger_day}')
        
        if self.exit_day != -1:
            plt.axvline(x=self.exit_day, color='r', linestyle=':', label=f'Exited on day {self.exit_day}')
        
        # 显示货币路径
        path_str = " → ".join(self.currency_path)
        plt.title(f'Multi-Currency Arbitrage Profit Path\n{path_str}')
        plt.xlabel('Days')
        plt.ylabel('Profit Rate')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.savefig(save_path)
        plt.close()

def run_simulations_in_parallel(num_simulations, simulation_days, currencies):
    def run_single_simulation(sim_id):
        start_currency = np.random.choice(currencies)
        path_len = np.random.randint(3, min(len(currencies), 6))
        sim = ArbitrageSimulation(start_currency, path_len, simulation_days)
        sim.simulate()
        sim_results = sim.get_results()
        return {
            "sim_id": sim_id,
            "currency_path": "→".join(sim_results["currency_path"]),
            "path_length": len(sim_results["currency_path"]) - 1,
            "is_triggered": sim_results["is_triggered"],
            "trigger_day": sim_results["trigger_day"] if sim_results["is_triggered"] else -1,
            "exit_day": sim_results["exit_day"],
            "max_profit": sim_results["max_profit"],
            "final_profit": sim_results["final_profit"],
            "holding_period": sim_results["exit_day"] - sim_results["trigger_day"] if sim_results["exit_day"] != -1 and sim_results["is_triggered"] else (simulation_days - sim_results["trigger_day"] if sim_results["is_triggered"] else 0)
        }

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(run_single_simulation, range(num_simulations)))

    return results

# 运行多条模拟
print("开始模拟多角套汇和远期货币交换...")
logging.basicConfig(
    filename=os.path.join(current_dir, "simulation.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("开始模拟多角套汇和远期货币交换...")
logging.info(f"模拟参数: num_simulations={num_simulations}, simulation_days={simulation_days}, currencies={currencies}")

results = run_simulations_in_parallel(num_simulations, simulation_days, currencies)

# 创建数据框并保存CSV
df = pd.DataFrame(results)
csv_path = os.path.join(os.path.dirname(current_dir), "pricingresult.csv")  # 保存到根目录
df.to_csv(csv_path, index=False)

# 分析并绘制触发率图表
trigger_rate = df["is_triggered"].mean()
avg_holding_period = df[df["is_triggered"]]["holding_period"].mean()
avg_max_profit = df[df["is_triggered"]]["max_profit"].mean()

plt.figure(figsize=(12, 8))
plt.subplot(2, 2, 1)
df["path_length"].value_counts().sort_index().plot(kind='bar')
plt.title('Path Length Distribution')
plt.xlabel('Number of Currency Pairs')
plt.ylabel('Count')

plt.subplot(2, 2, 2)
plt.hist(df["max_profit"], bins=50, alpha=0.7, color='skyblue')
plt.axvline(knock_in_threshold, color='r', linestyle='--')
plt.title(f'Max Profit Distribution\nKnock-in Threshold: {knock_in_threshold}')
plt.xlabel('Max Profit Rate')
plt.ylabel('Frequency')

plt.subplot(2, 2, 3)
triggered_df = df[df["is_triggered"]]
if not triggered_df.empty:
    plt.hist(triggered_df["holding_period"], bins=30, alpha=0.7, color='lightgreen')
    plt.title(f'Holding Period Distribution\nAvg: {avg_holding_period:.2f} days')
    plt.xlabel('Days')
    plt.ylabel('Frequency')
else:
    plt.text(0.5, 0.5, 'No triggered scenarios', horizontalalignment='center', verticalalignment='center')

plt.subplot(2, 2, 4)
labels = ['Triggered', 'Not Triggered']
sizes = [trigger_rate, 1 - trigger_rate]
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
plt.title(f'Trigger Rate: {trigger_rate:.2%}')

plt.tight_layout()
plt.savefig(os.path.join(simulation_charts_dir, "payoff_distribution.png"))
plt.close()

# 保存示例轨迹图
for i, sim in enumerate(track_sims):
    if i < num_tracks_to_save:
        sim.plot_profit_path(os.path.join(tracks_dir, f"track_{i}.png"))

logging.info("模拟完成！")
logging.info(f"总共模拟了 {num_simulations} 条路径")
logging.info(f"触发率: {trigger_rate:.2%}")
logging.info(f"平均持有期: {avg_holding_period:.2f} 天")
logging.info(f"平均最大收益: {avg_max_profit:.4f}")
logging.info(f"CSV保存到: {csv_path}")
logging.info(f"图表保存到: {simulation_charts_dir}")

print(f"模拟完成！")
print(f"总共模拟了 {num_simulations} 条路径")
print(f"触发率: {trigger_rate:.2%}")
print(f"平均持有期: {avg_holding_period:.2f} 天")
print(f"平均最大收益: {avg_max_profit:.4f}")
print(f"CSV保存到: {csv_path}")
print(f"图表保存到: {simulation_charts_dir}")
