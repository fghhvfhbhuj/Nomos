#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lag-Arb Note 定价模型

本模型用于模拟一级结构（欧式期权）的Delta值随时间变化，
并计算基于Delta滞后性的二级结构（Lag-Arb Note）的触发收益。
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import scipy.stats as stats
from scipy.stats import norm

# 确保输出目录存在
if not os.path.exists('simulation_charts'):
    os.makedirs('simulation_charts')

class LagArbNote:
    """Lag-Arb Note定价模型类"""
    
    def __init__(self, 
                 S0=100,                # 初始标的价格
                 K=100,                 # 行权价格
                 r=0.03,                # 无风险利率
                 sigma=0.2,             # 波动率
                 T=60/252,              # 到期日(年)
                 tau=2/252,             # 延迟窗口(年)
                 epsilon=0.1,           # Delta变化阈值
                 payout=0.05,           # 触发收益率
                 num_simulations=1000,  # 模拟路径数
                 num_steps=60,          # 模拟步数
                 seed=42):              # 随机种子
        
        self.S0 = S0
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.tau_days = int(tau * 252)  # 转换为天数
        self.epsilon = epsilon
        self.payout = payout
        self.num_simulations = num_simulations
        self.num_steps = num_steps
        self.dt = T / num_steps
        self.seed = seed
        
        # 设置随机种子
        np.random.seed(seed)
        
        # 存储模拟结果
        self.simulated_prices = None
        self.simulated_deltas = None
        self.delta_changes = None
        self.triggers = None
        self.results_df = None
        
    def black_scholes_delta(self, S, t):
        """计算Black-Scholes欧式看涨期权的Delta"""
        if t >= self.T:
            return 0.0
        
        tau = self.T - t
        if tau <= 0:
            return 0.0
            
        d1 = (np.log(S / self.K) + (self.r + 0.5 * self.sigma**2) * tau) / (self.sigma * np.sqrt(tau))
        return norm.cdf(d1)
    
    def simulate_price_paths(self):
        """模拟标的资产价格路径"""
        dt = self.dt
        prices = np.zeros((self.num_simulations, self.num_steps + 1))
        prices[:, 0] = self.S0
        
        for i in range(self.num_simulations):
            for t in range(1, self.num_steps + 1):
                z = np.random.standard_normal()
                prices[i, t] = prices[i, t-1] * np.exp((self.r - 0.5 * self.sigma**2) * dt + 
                                                       self.sigma * np.sqrt(dt) * z)
                
        self.simulated_prices = prices
        return prices
    
    def calculate_deltas(self):
        """计算每个价格路径对应的Delta值"""
        if self.simulated_prices is None:
            self.simulate_price_paths()
            
        deltas = np.zeros_like(self.simulated_prices)
        
        for i in range(self.num_simulations):
            for t in range(self.num_steps + 1):
                time_to_expiry = t * self.dt
                deltas[i, t] = self.black_scholes_delta(self.simulated_prices[i, t], time_to_expiry)
                
        self.simulated_deltas = deltas
        return deltas
    
    def calculate_delta_changes(self):
        """计算Delta变化"""
        if self.simulated_deltas is None:
            self.calculate_deltas()
            
        # 计算滞后delta变化
        delta_changes = np.zeros((self.num_simulations, self.num_steps + 1 - self.tau_days))
        
        for i in range(self.num_simulations):
            for t in range(self.num_steps + 1 - self.tau_days):
                delta_changes[i, t] = self.simulated_deltas[i, t + self.tau_days] - self.simulated_deltas[i, t]
                
        self.delta_changes = delta_changes
        return delta_changes
    
    def check_triggers(self):
        """检查是否触发收益条件"""
        if self.delta_changes is None:
            self.calculate_delta_changes()
            
        # 检查触发条件: |delta变化| > epsilon
        triggers = np.abs(self.delta_changes) > self.epsilon
        self.triggers = triggers
        return triggers
    
    def calculate_payouts(self):
        """计算每个路径的收益"""
        if self.triggers is None:
            self.check_triggers()
            
        # 每个路径是否在任何时间点触发
        path_triggers = np.any(self.triggers, axis=1)
        
        # 计算收益
        payouts = path_triggers * self.payout
        
        return payouts, path_triggers
    
    def run_simulation(self):
        """运行完整模拟并返回结果"""
        self.simulate_price_paths()
        self.calculate_deltas()
        self.calculate_delta_changes()
        self.check_triggers()
        payouts, path_triggers = self.calculate_payouts()
        
        # 计算每个时间点的触发概率
        trigger_probs = np.mean(self.triggers, axis=0)
        
        # 计算总体触发概率
        total_trigger_prob = np.mean(path_triggers)
        
        # 期望收益
        expected_payout = np.mean(payouts)
        
        # 创建结果数据框
        days = np.arange(self.num_steps + 1 - self.tau_days)
        
        results = {
            '总体触发概率': total_trigger_prob,
            '期望收益': expected_payout,
            '参数设置': {
                '初始价格': self.S0,
                '行权价格': self.K,
                '无风险利率': self.r,
                '波动率': self.sigma,
                '到期日(交易日)': int(self.T * 252),
                '延迟窗口(交易日)': self.tau_days,
                'Delta变化阈值': self.epsilon,
                '触发收益率': self.payout
            }
        }
        
        # 创建路径结果的数据框
        path_results = []
        for i in range(self.num_simulations):
            # 记录每条路径的最大Delta变化和是否触发
            max_delta_change = np.max(np.abs(self.delta_changes[i]))
            path_data = {
                '路径ID': i,
                '最大Delta变化': max_delta_change,
                '是否触发': path_triggers[i],
                '收益': payouts[i]
            }
            path_results.append(path_data)
        
        self.results_df = pd.DataFrame(path_results)
        
        return results, self.results_df, trigger_probs
    
    def save_results(self, filename="lag_arb_simulation_results.csv"):
        """保存模拟结果到CSV文件"""
        if self.results_df is None:
            _, self.results_df, _ = self.run_simulation()
        
        self.results_df.to_csv(filename, index=False)
        print(f"结果已保存到 {filename}")
    
    def plot_sample_paths(self, num_paths=5):
        """绘制样本价格路径图"""
        if self.simulated_prices is None:
            self.simulate_price_paths()
            
        plt.figure(figsize=(12, 6))
        
        for i in range(min(num_paths, self.num_simulations)):
            plt.plot(self.simulated_prices[i], label=f'路径 {i+1}')
            
        plt.axhline(y=self.K, color='r', linestyle='--', label='行权价格')
        plt.title('标的资产价格路径模拟')
        plt.xlabel('时间步数')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True)
        plt.savefig('simulation_charts/price_paths.png')
        plt.close()
    
    def plot_sample_deltas(self, num_paths=5):
        """绘制样本Delta路径图"""
        if self.simulated_deltas is None:
            self.calculate_deltas()
            
        plt.figure(figsize=(12, 6))
        
        for i in range(min(num_paths, self.num_simulations)):
            plt.plot(self.simulated_deltas[i], label=f'路径 {i+1}')
            
        plt.title('期权Delta值路径模拟')
        plt.xlabel('时间步数')
        plt.ylabel('Delta值')
        plt.legend()
        plt.grid(True)
        plt.savefig('simulation_charts/delta_paths.png')
        plt.close()
    
    def plot_delta_changes(self, num_paths=5):
        """绘制样本Delta变化图"""
        if self.delta_changes is None:
            self.calculate_delta_changes()
            
        plt.figure(figsize=(12, 6))
        
        for i in range(min(num_paths, self.num_simulations)):
            plt.plot(self.delta_changes[i], label=f'路径 {i+1}')
            
        plt.axhline(y=self.epsilon, color='r', linestyle='--', label=f'上阈值 (+{self.epsilon})')
        plt.axhline(y=-self.epsilon, color='r', linestyle='--', label=f'下阈值 (-{self.epsilon})')
        plt.title(f'Delta滞后变化 (τ = {self.tau_days}天)')
        plt.xlabel('时间步数')
        plt.ylabel('Delta变化')
        plt.legend()
        plt.grid(True)
        plt.savefig('simulation_charts/delta_changes.png')
        plt.close()
    
    def plot_trigger_probability(self):
        """绘制触发概率图"""
        if self.triggers is None:
            self.check_triggers()
            
        # 计算每个时间点的触发概率
        trigger_probs = np.mean(self.triggers, axis=0)
        
        plt.figure(figsize=(12, 6))
        plt.plot(trigger_probs, 'b-', linewidth=2)
        plt.title('Lag-Arb Note 触发概率随时间变化')
        plt.xlabel('时间步数')
        plt.ylabel('触发概率')
        plt.grid(True)
        plt.savefig('simulation_charts/trigger_probability.png')
        plt.close()
    
    def plot_payout_distribution(self):
        """绘制收益分布图"""
        _, path_triggers = self.calculate_payouts()
        
        plt.figure(figsize=(10, 6))
        plt.hist(path_triggers, bins=[0, 0.5, 1], rwidth=0.8, align='mid')
        plt.xticks([0.25, 0.75], ['未触发', '触发'])
        plt.title('Lag-Arb Note 收益分布')
        plt.ylabel('路径数量')
        plt.grid(True, axis='y')
        plt.savefig('simulation_charts/payout_distribution.png')
        plt.close()
    
    def plot_delta_change_distribution(self):
        """绘制Delta变化分布图"""
        if self.delta_changes is None:
            self.calculate_delta_changes()
            
        # 每条路径的最大Delta变化
        max_delta_changes = np.max(np.abs(self.delta_changes), axis=1)
        
        plt.figure(figsize=(12, 6))
        plt.hist(max_delta_changes, bins=20, alpha=0.7)
        plt.axvline(x=self.epsilon, color='r', linestyle='--', 
                   label=f'触发阈值 (ε = {self.epsilon})')
        plt.title('最大Delta变化分布')
        plt.xlabel('|Delta变化|最大值')
        plt.ylabel('频率')
        plt.legend()
        plt.grid(True)
        plt.savefig('simulation_charts/max_delta_change_distribution.png')
        plt.close()
        
    def generate_all_charts(self):
        """生成所有图表"""
        self.plot_sample_paths()
        self.plot_sample_deltas()
        self.plot_delta_changes()
        self.plot_trigger_probability()
        self.plot_payout_distribution()
        self.plot_delta_change_distribution()

# 主函数，运行模拟
def main():
    # 创建三种不同市场情景的模拟
    scenarios = [
        {
            'name': '基准情景',
            'params': {
                'S0': 100,
                'K': 100,
                'r': 0.03,
                'sigma': 0.2,
                'T': 60/252,
                'tau': 2/252,
                'epsilon': 0.1,
                'payout': 0.05,
                'num_simulations': 1000
            }
        },
        {
            'name': '高波动情景',
            'params': {
                'S0': 100,
                'K': 100,
                'r': 0.03,
                'sigma': 0.3,
                'T': 60/252,
                'tau': 2/252,
                'epsilon': 0.1,
                'payout': 0.05,
                'num_simulations': 1000
            }
        },
        {
            'name': '低波动情景',
            'params': {
                'S0': 100,
                'K': 100,
                'r': 0.03,
                'sigma': 0.1,
                'T': 60/252,
                'tau': 2/252,
                'epsilon': 0.1,
                'payout': 0.05,
                'num_simulations': 1000
            }
        }
    ]
    
    # 存储所有情景的结果
    all_results = []
    
    for scenario in scenarios:
        print(f"运行 {scenario['name']} 模拟...")
        model = LagArbNote(**scenario['params'])
        results, results_df, trigger_probs = model.run_simulation()
        
        # 为每个情景生成图表
        print(f"为 {scenario['name']} 生成图表...")
        model.generate_all_charts()
        
        # 保存CSV结果
        results_df['情景'] = scenario['name']
        all_results.append(results_df)
        
        # 打印结果摘要
        print(f"\n{scenario['name']}结果摘要:")
        print(f"总体触发概率: {results['总体触发概率']:.4f}")
        print(f"期望收益: {results['期望收益']:.4f}")
        print("-" * 50)
    
    # 合并所有情景结果并保存
    combined_results = pd.concat(all_results, ignore_index=True)
    combined_results.to_csv('lag_arb_simulation_results.csv', index=False)
    print("\n所有模拟结果已保存到 lag_arb_simulation_results.csv")
    
    # 生成情景对比图
    print("生成情景对比图...")
    plot_scenario_comparison(combined_results)
    
def plot_scenario_comparison(combined_results):
    """生成不同情景对比图"""
    # 计算每个情景的触发率
    trigger_rates = combined_results.groupby('情景')['是否触发'].mean()
    
    # 绘制情景对比图
    plt.figure(figsize=(10, 6))
    bars = plt.bar(trigger_rates.index, trigger_rates.values, color=['blue', 'orange', 'green'])
    plt.title('不同情景下的Lag-Arb Note触发率对比')
    plt.ylabel('触发率')
    plt.ylim(0, 1)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.2f}', ha='center', va='bottom')
    
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.savefig('simulation_charts/scenario_comparison.png')
    plt.close()

if __name__ == "__main__":
    main()