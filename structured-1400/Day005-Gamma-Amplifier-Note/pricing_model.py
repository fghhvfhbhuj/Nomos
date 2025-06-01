#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gamma Amplifier Note (GAN) 定价模型与回测模拟
============================================

本模型实现了GAN结构性产品的定价和回测功能，具体包括：
1. 标的资产价格路径模拟
2. GAN产品定价算法实现
3. 多场景回测与性能评估
4. 结果可视化与分析
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import datetime as dt
from matplotlib.ticker import PercentFormatter
import seaborn as sns
from tqdm import tqdm
import math

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

# 创建保存图表的目录
if not os.path.exists('simulation_charts'):
    os.makedirs('simulation_charts')

class GammaAmplifierNote:
    """Gamma Amplifier Note (GAN) 定价模型类"""
    
    def __init__(self, S0, K, delta, T, r, sigma, steps_per_day=10, 
                 amplification_factor=2.5, cost_factor=0.05):
        """
        初始化GAN模型参数
        
        参数:
            S0 (float): 标的资产初始价格
            K (float): 激活中心点价格
            delta (float): 激活带宽
            T (float): 到期时间（年）
            r (float): 无风险利率
            sigma (float): 标的资产波动率
            steps_per_day (int): 每天模拟步数
            amplification_factor (float): Gamma放大系数
            cost_factor (float): 结构成本因子
        """
        self.S0 = S0
        self.K = K
        self.delta = delta
        self.T = T
        self.r = r
        self.sigma = sigma
        self.steps_per_day = steps_per_day
        self.amplification_factor = amplification_factor
        self.cost_factor = cost_factor
        self.total_steps = int(self.T * 365 * steps_per_day)
        self.dt = self.T / self.total_steps
        
        # 激活区间
        self.activation_low = K - delta
        self.activation_high = K + delta

    def simulate_price_path(self, num_paths=1, random_seed=None):
        """
        模拟标的资产价格路径
        
        参数:
            num_paths (int): 模拟路径数量
            random_seed (int): 随机数种子，用于复现结果
            
        返回:
            numpy.ndarray: 价格路径矩阵，形状为(num_paths, total_steps+1)
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # 初始化价格矩阵
        price_paths = np.zeros((num_paths, self.total_steps + 1))
        price_paths[:, 0] = self.S0
        
        # 生成随机价格路径
        for i in range(num_paths):
            for t in range(1, self.total_steps + 1):
                z = np.random.normal(0, 1)
                price_paths[i, t] = price_paths[i, t-1] * np.exp(
                    (self.r - 0.5 * self.sigma**2) * self.dt + 
                    self.sigma * np.sqrt(self.dt) * z
                )
        
        return price_paths
    
    def is_activated(self, price):
        """
        判断价格是否在激活区间内
        
        参数:
            price (float): 当前价格
            
        返回:
            bool: 是否在激活区间
        """
        return self.activation_low <= price <= self.activation_high
    
    def calculate_gamma(self, S, t):
        """
        计算在价格S和时间t下的Gamma值
        
        参数:
            S (float): 当前价格
            t (float): 当前时间（距离到期的时间）
            
        返回:
            float: Gamma值
        """
        # 计算ATM期权的Gamma
        tau = max(self.T - t, 1e-10)  # 避免除以0
        d1 = (np.log(S / self.K) + (self.r + 0.5 * self.sigma**2) * tau) / (self.sigma * np.sqrt(tau))
        gamma = np.exp(-d1**2 / 2) / (S * self.sigma * np.sqrt(2 * np.pi * tau))
        return gamma
    
    def calculate_gan_payoff(self, price_path):
        """
        计算GAN产品在给定价格路径下的收益
        
        参数:
            price_path (numpy.ndarray): 单条价格路径
            
        返回:
            float: GAN产品的收益率
        """
        payoff = 0
        activated = False
        gamma_contribution = 0
        price_changes = []
        
        # 记录每一步的价格变动和是否在激活区间
        for t in range(1, len(price_path)):
            current_time = t * self.dt
            current_price = price_path[t]
            previous_price = price_path[t-1]
            
            # 判断是否在激活区间
            is_active = self.is_activated(current_price)
            
            if is_active:
                activated = True
                # 计算价格变动的平方（用于Gamma收益）
                price_change = (current_price - previous_price) / previous_price
                price_changes.append(price_change)
                
                # 计算Gamma贡献
                gamma = self.calculate_gamma(current_price, current_time)
                # Gamma收益与价格变动平方成正比
                gamma_contribution += gamma * self.amplification_factor * price_change**2
        
        # 如果价格从未进入激活区间，则只有成本损失
        if not activated:
            return -self.cost_factor
        
        # 计算最终收益率
        # 1. 基础Gamma贡献（放大后）
        # 2. 减去结构成本
        payoff = gamma_contribution - self.cost_factor
        
        return payoff
    
    def calculate_vanilla_straddle_payoff(self, price_path):
        """
        计算普通跨式组合(Long Straddle)在给定价格路径下的收益
        
        参数:
            price_path (numpy.ndarray): 单条价格路径
            
        返回:
            float: 普通跨式组合的收益率
        """
        # 计算期权定价参数
        final_price = price_path[-1]
        call_payoff = max(0, final_price - self.K)
        put_payoff = max(0, self.K - final_price)
        
        # 计算期权初始价格
        d1 = (np.log(self.S0 / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        
        call_price = self.S0 * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S0 * norm.cdf(-d1)
        
        initial_cost = call_price + put_price
        final_value = call_payoff + put_payoff
        
        # 计算收益率
        return (final_value - initial_cost) / initial_cost
    
    def price_gan(self, num_simulations=10000):
        """
        通过蒙特卡洛模拟为GAN产品定价
        
        参数:
            num_simulations (int): 模拟次数
            
        返回:
            float: GAN产品价格
        """
        total_payoff = 0
        
        for _ in range(num_simulations):
            price_path = self.simulate_price_path(1)[0]
            payoff = self.calculate_gan_payoff(price_path)
            total_payoff += payoff
        
        # 平均收益率
        average_payoff = total_payoff / num_simulations
        
        # GAN初始价格 = 标的资产价格 * 期望收益折现
        gan_price = self.S0 * np.exp(-self.r * self.T) * average_payoff
        
        return gan_price
    
    def run_backtest(self, num_paths=1000, output_file="pricing_result.csv"):
        """
        运行回测模拟并生成结果
        
        参数:
            num_paths (int): 模拟路径数量
            output_file (str): 结果输出文件名
            
        返回:
            pandas.DataFrame: 回测结果数据框
        """
        # 初始化结果列表
        results = []
        
        # 执行多路径模拟
        price_paths = self.simulate_price_path(num_paths)
        
        # 计算每条路径的GAN收益和普通策略收益
        for i in tqdm(range(num_paths), desc="模拟回测进度"):
            path = price_paths[i]
            
            # 计算GAN产品收益
            gan_payoff = self.calculate_gan_payoff(path)
            
            # 计算普通策略收益
            vanilla_payoff = self.calculate_vanilla_straddle_payoff(path)
            
            # 记录路径中价格是否曾进入激活区间
            ever_activated = any(self.is_activated(p) for p in path)
            
            # 计算价格路径统计量
            price_volatility = np.std(np.diff(path) / path[:-1])
            final_price = path[-1]
            max_price = np.max(path)
            min_price = np.min(path)
            price_range = max_price - min_price
            
            # 保存结果
            results.append({
                '路径ID': i,
                'GAN收益率': gan_payoff,
                '普通策略收益率': vanilla_payoff,
                '收益放大倍数': gan_payoff / vanilla_payoff if vanilla_payoff != 0 else float('nan'),
                '是否曾激活': ever_activated,
                '最终价格': final_price,
                '最高价格': max_price,
                '最低价格': min_price,
                '价格区间': price_range,
                '实现波动率': price_volatility,
                '初始价格': self.S0,
                '激活中心': self.K,
                '激活带宽': self.delta
            })
        
        # 转换为DataFrame
        results_df = pd.DataFrame(results)
        
        # 保存结果到CSV
        results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 生成分析图表
        self.generate_analysis_charts(results_df)
        
        return results_df
    
    def generate_analysis_charts(self, results_df):
        """
        生成分析图表
        
        参数:
            results_df (pandas.DataFrame): 回测结果数据框
        """
        # 设置图表风格
        sns.set(style="whitegrid")
        
        # 1. GAN vs 普通策略收益对比直方图
        plt.figure(figsize=(12, 8))
        sns.histplot(data=results_df, x='GAN收益率', color='red', alpha=0.5, label='GAN收益率', kde=True)
        sns.histplot(data=results_df, x='普通策略收益率', color='blue', alpha=0.5, label='普通策略收益率', kde=True)
        plt.title('GAN vs 普通策略收益分布对比', fontsize=15)
        plt.xlabel('收益率', fontsize=12)
        plt.ylabel('频率', fontsize=12)
        plt.legend()
        plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
        plt.savefig('simulation_charts/收益分布对比.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 收益与价格波动范围的关系散点图
        plt.figure(figsize=(12, 8))
        plt.scatter(results_df['价格区间'], results_df['GAN收益率'], alpha=0.6, label='GAN收益率')
        plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        z = np.polyfit(results_df['价格区间'], results_df['GAN收益率'], 1)
        p = np.poly1d(z)
        plt.plot(results_df['价格区间'], p(results_df['价格区间']), "r--", alpha=0.8)
        plt.title('GAN收益率与价格波动范围关系', fontsize=15)
        plt.xlabel('价格波动范围', fontsize=12)
        plt.ylabel('GAN收益率', fontsize=12)
        plt.legend()
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        plt.savefig('simulation_charts/收益与波动范围关系.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 价格是否曾进入激活区间的收益对比箱线图
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='是否曾激活', y='GAN收益率', data=results_df)
        plt.title('是否激活对GAN收益的影响', fontsize=15)
        plt.xlabel('是否曾进入激活区间', fontsize=12)
        plt.ylabel('GAN收益率', fontsize=12)
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        plt.savefig('simulation_charts/激活状态与收益关系.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. 收益放大倍数分布直方图
        plt.figure(figsize=(12, 8))
        # 过滤掉无效值和极端值
        valid_multiples = results_df['收益放大倍数']
        valid_multiples = valid_multiples[~np.isnan(valid_multiples)]
        valid_multiples = valid_multiples[np.abs(valid_multiples) < 10]  # 过滤极端值
        
        if len(valid_multiples) > 0:  # 确保有有效数据
            sns.histplot(valid_multiples, bins=30, kde=True)
            plt.axvline(x=1, color='r', linestyle='--', alpha=0.7)
            plt.title('GAN收益放大倍数分布', fontsize=15)
            plt.xlabel('收益放大倍数', fontsize=12)
            plt.ylabel('频率', fontsize=12)
            plt.savefig('simulation_charts/收益放大倍数分布.png', dpi=300, bbox_inches='tight')
        else:
            print("警告: 没有有效的收益放大倍数数据可以绘制")
        plt.close()
        
        # 5. 实现波动率与GAN收益关系图
        plt.figure(figsize=(12, 8))
        plt.scatter(results_df['实现波动率'], results_df['GAN收益率'], alpha=0.6)
        plt.title('实现波动率与GAN收益关系', fontsize=15)
        plt.xlabel('实现波动率', fontsize=12)
        plt.ylabel('GAN收益率', fontsize=12)
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        
        # 添加趋势线 - 确保有足够的数据点
        if len(results_df) > 2:
            try:
                z = np.polyfit(results_df['实现波动率'], results_df['GAN收益率'], 2)
                p = np.poly1d(z)
                x_range = np.linspace(min(results_df['实现波动率']), max(results_df['实现波动率']), 100)
                plt.plot(x_range, p(x_range), "r--", alpha=0.8)
            except np.linalg.LinAlgError:
                print("警告: 无法拟合趋势线，可能是因为数据点太少或共线性问题")
        
        plt.savefig('simulation_charts/波动率与收益关系.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 6. 不同激活带宽对收益的影响模拟
        delta_range = np.linspace(0.5, 5, 10)
        avg_payoffs = []
        
        for delta in delta_range:
            temp_gan = GammaAmplifierNote(
                S0=self.S0, 
                K=self.K, 
                delta=delta, 
                T=self.T, 
                r=self.r, 
                sigma=self.sigma
            )
            
            # 模拟较少条路径以加快速度
            paths = temp_gan.simulate_price_path(50)
            payoffs = [temp_gan.calculate_gan_payoff(path) for path in paths]
            avg_payoffs.append(np.mean(payoffs))
        
        plt.figure(figsize=(12, 8))
        plt.plot(delta_range, avg_payoffs, marker='o')
        plt.title('激活带宽δ对GAN平均收益的影响', fontsize=15)
        plt.xlabel('激活带宽δ', fontsize=12)
        plt.ylabel('平均GAN收益率', fontsize=12)
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        plt.grid(True, alpha=0.3)
        plt.savefig('simulation_charts/带宽对收益影响.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 7. 典型价格路径及其收益示例
        # 选择最高收益和中等收益的路径进行展示
        if len(results_df) > 0:
            top_path_idx = results_df['GAN收益率'].idxmax()
            
            # 安全地选择中等收益路径
            try:
                mid_path_idx = results_df['GAN收益率'].rank(pct=True).sub(0.5).abs().idxmin()
            except:
                # 如果中位数选择失败，选择第一个路径作为备选
                mid_path_idx = results_df.index[0] if len(results_df) > 0 else top_path_idx
            
            selected_paths = [top_path_idx, mid_path_idx]
            path_labels = ['最高收益路径', '中等收益路径']
            path_colors = ['green', 'blue']
            
            # 重新生成相同的路径，确保一致性
            try:
                price_paths = self.simulate_price_path(num_paths=max(selected_paths) + 1, random_seed=42)
                
                plt.figure(figsize=(14, 10))
                
                for i, path_idx in enumerate(selected_paths):
                    if path_idx < len(price_paths):
                        path = price_paths[path_idx]
                        time_points = np.linspace(0, self.T * 365, len(path))
                        
                        plt.plot(time_points, path, 
                                label=f"{path_labels[i]} (收益率: {results_df.loc[path_idx, 'GAN收益率']:.2%})", 
                                color=path_colors[i], alpha=0.8)
                
                # 标记激活区间
                plt.axhline(y=self.activation_low, color='red', linestyle='--', alpha=0.5)
                plt.axhline(y=self.activation_high, color='red', linestyle='--', alpha=0.5)
                plt.fill_between(time_points, self.activation_low, self.activation_high, 
                                color='red', alpha=0.1, label='激活区间')
                
                plt.title('典型价格路径示例', fontsize=15)
                plt.xlabel('时间 (天)', fontsize=12)
                plt.ylabel('价格', fontsize=12)
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.savefig('simulation_charts/典型价格路径.png', dpi=300, bbox_inches='tight')
            except Exception as e:
                print(f"绘制典型价格路径时出错: {str(e)}")
            
            plt.close()
        else:
            print("警告: 没有足够的路径数据来绘制典型价格路径")


def main():
    """
    主函数，用于运行GAN定价模型和回测模拟
    """
    print("开始Gamma Amplifier Note (GAN)定价和回测模拟...")
    
    # 设置模型参数
    S0 = 100  # 初始价格
    K = 100   # 激活中心点
    delta = 2  # 激活带宽
    T = 30/365  # 30天到期
    r = 0.03  # 无风险利率
    sigma = 0.2  # 波动率
    
    # 初始化GAN模型
    gan_model = GammaAmplifierNote(
        S0=S0, 
        K=K, 
        delta=delta, 
        T=T, 
        r=r, 
        sigma=sigma,
        steps_per_day=10,  # 每天10个步长
        amplification_factor=2.5,  # Gamma放大系数
        cost_factor=0.05  # 结构成本因子
    )
    
    # 计算GAN价格
    try:
        gan_price = gan_model.price_gan(num_simulations=500)  # 减少模拟次数以加快运行
        print(f"GAN定价结果: {gan_price:.4f}")
    except Exception as e:
        print(f"GAN定价计算出错: {str(e)}")
    
    # 运行回测模拟
    print("开始回测模拟...")
    try:
        results = gan_model.run_backtest(num_paths=500, output_file="pricing_result.csv")  # 减少路径数量以加快运行
        
        # 输出摘要统计信息
        print("\n===== GAN回测统计摘要 =====")
        print(f"平均GAN收益率: {results['GAN收益率'].mean():.2%}")
        print(f"GAN收益率标准差: {results['GAN收益率'].std():.2%}")
        print(f"最大GAN收益率: {results['GAN收益率'].max():.2%}")
        print(f"最小GAN收益率: {results['GAN收益率'].min():.2%}")
        print(f"激活路径比例: {results['是否曾激活'].mean():.2%}")
        
        print(f"\n平均普通策略收益率: {results['普通策略收益率'].mean():.2%}")
        print(f"普通策略收益率标准差: {results['普通策略收益率'].std():.2%}")
        
        # 安全计算平均收益放大倍数
        valid_multiples = results['收益放大倍数'].dropna()
        valid_multiples = valid_multiples[np.abs(valid_multiples) < 10]  # 过滤极端值
        if len(valid_multiples) > 0:
            print(f"\n平均收益放大倍数: {valid_multiples.mean():.2f}")
        else:
            print("\n没有有效的收益放大倍数数据")
        
        print("\n模拟回测完成！结果已保存到pricing_result.csv")
        print("分析图表已保存到simulation_charts文件夹")
    except Exception as e:
        print(f"回测模拟过程中出错: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序执行过程中出现错误: {str(e)}")

