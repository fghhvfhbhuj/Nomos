import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import os

class EnhancedCreditShockSimulator:
    def __init__(self, leverage=2.5):
        # 初始化变量 - 扩展了资产种类
        self.variables = {
            "Issuer A Stock": 40,
            "VIX": 18,
            "Gold ETF": 190,
            "Sector ETF": 120,
            "High Yield ETF": 72,
            "US Bond ETF": 100,
            "CDS Spread": 150,     # 基点
            "Volatility Swap": 22,
            "Commodity Futures": 85,
            "Credit Index": 95
        }
        
        # 设置杠杆倍数
        self.leverage = leverage
        
        # 更复杂的冲击规则 - 考虑极端情景
        self.shock_rules = {
            "Issuer A Stock": lambda x: x * 0.55,  # 更严重的股价下跌
            "VIX": lambda x: x * 2.5,              # 波动率暴涨
            "Gold ETF": lambda x: x * 1.15,        # 避险资产上涨
            "Sector ETF": lambda x: x * 0.8,       # 行业ETF下跌
            "High Yield ETF": lambda x: x * 0.75,  # 高收益债下跌更多
            "US Bond ETF": lambda x: x * 1.12,     # 国债避险上涨
            "CDS Spread": lambda x: x * 3.5,       # CDS大幅走阔
            "Volatility Swap": lambda x: x * 2.2,  # 波动率掉期上涨
            "Commodity Futures": lambda x: x * 0.9,# 商品期货小幅下跌
            "Credit Index": lambda x: x * 0.7      # 信用指数下跌
        }
        
        # 资产相关性矩阵
        self.correlation_matrix = pd.DataFrame({
            "Issuer A Stock": [1.0, -0.7, -0.3, 0.8, 0.6, -0.4, 0.7, -0.6, 0.5, 0.7],
            "VIX": [-0.7, 1.0, 0.4, -0.6, -0.5, 0.3, -0.8, 0.8, -0.3, -0.6],
            "Gold ETF": [-0.3, 0.4, 1.0, -0.2, -0.3, 0.6, -0.4, 0.3, 0.1, -0.3],
            "Sector ETF": [0.8, -0.6, -0.2, 1.0, 0.7, -0.3, 0.6, -0.5, 0.4, 0.8],
            "High Yield ETF": [0.6, -0.5, -0.3, 0.7, 1.0, -0.2, 0.7, -0.5, 0.3, 0.8],
            "US Bond ETF": [-0.4, 0.3, 0.6, -0.3, -0.2, 1.0, -0.5, 0.2, -0.1, -0.4],
            "CDS Spread": [0.7, -0.8, -0.4, 0.6, 0.7, -0.5, 1.0, -0.7, 0.4, 0.8],
            "Volatility Swap": [-0.6, 0.8, 0.3, -0.5, -0.5, 0.2, -0.7, 1.0, -0.3, -0.6],
            "Commodity Futures": [0.5, -0.3, 0.1, 0.4, 0.3, -0.1, 0.4, -0.3, 1.0, 0.4],
            "Credit Index": [0.7, -0.6, -0.3, 0.8, 0.8, -0.4, 0.8, -0.6, 0.4, 1.0]
        }, index=list(self.variables.keys()))
        
        # 初始化动态权重
        self.base_weights = self._initialize_weights()
        
        # 确保simulation_charts文件夹存在
        if not os.path.exists("simulation_charts"):
            os.makedirs("simulation_charts")

    def _initialize_weights(self):
        # 初始化基础权重 - 会在优化过程中调整
        return {
            "Issuer A Stock": 0.15,
            "VIX": 0.20,
            "Gold ETF": 0.10,
            "Sector ETF": 0.05,
            "High Yield ETF": 0.10,
            "US Bond ETF": 0.05,
            "CDS Spread": 0.15,
            "Volatility Swap": 0.10,
            "Commodity Futures": 0.05,
            "Credit Index": 0.05
        }

    def optimize_weights(self, shocked_values):
        """使用蒙特卡洛模拟优化权重配置"""
        best_return = 0
        best_weights = self.base_weights.copy()
        
        # 运行1000次模拟以找到最优权重
        for _ in range(1000):
            # 随机生成权重并归一化
            weights = np.random.random(len(self.variables))
            weights = weights / np.sum(weights)
            
            # 计算该权重下的收益
            test_weights = dict(zip(self.variables.keys(), weights))
            test_return = self._calculate_return(shocked_values, test_weights)
            
            if test_return > best_return:
                best_return = test_return
                best_weights = test_weights
        
        return best_weights, best_return

    def _calculate_return(self, shocked_values, weights):
        """计算给定权重下的收益"""
        hedge_values = []
        for var in self.variables:
            # 计算资产价值变化
            value_change = shocked_values[var] - self.variables[var]
            # 根据资产特性判断是否为正向对冲
            is_positive_hedge = (var in ["VIX", "Gold ETF", "US Bond ETF", "CDS Spread", "Volatility Swap"])
            
            if is_positive_hedge:
                hedge_value = max(value_change, 0)
            else:
                # 对于预期下跌的资产，做空获利
                hedge_value = max(-value_change, 0)
            
            hedge_values.append(hedge_value)
        
        # 应用权重并考虑杠杆
        return sum(w * h * self.leverage for w, h in zip(weights.values(), hedge_values))

    def simulate_jump(self):
        """模拟市场跳变 - 添加随机性以模拟不同程度的违约事件"""
        shocked_values = {}
        
        # 生成相关的随机冲击
        random_shocks = self._generate_correlated_shocks()
        
        for i, (var, value) in enumerate(self.variables.items()):
            # 基础冲击规则
            base_shock = self.shock_rules[var](value)
            # 添加随机性，使情景更加真实
            shock_multiplier = 1.0 + random_shocks[i] * 0.2  # 上下浮动20%
            shocked_values[var] = base_shock * shock_multiplier
            
        return shocked_values

    def _generate_correlated_shocks(self):
        """生成相关性的随机冲击"""
        # 使用Cholesky分解生成相关的随机数
        L = np.linalg.cholesky(self.correlation_matrix.values)
        uncorrelated = np.random.standard_normal(len(self.variables))
        correlated = np.dot(L, uncorrelated)
        return correlated

    def evaluate_hedge(self, shocked_values, optimized_weights=None):
        """评估对冲策略效果"""
        if optimized_weights is None:
            weights = self.base_weights
        else:
            weights = optimized_weights
            
        return self._calculate_return(shocked_values, weights)

    def calculate_total(self, shocked_values):
        """计算总体结果，包括多策略组合"""
        # 基本情景 - 标准违约
        RR = 0.3  # 降低回收率以反映更糟糕的情况
        L = (1 - RR) * 100
        
        # 优化权重
        optimized_weights, _ = self.optimize_weights(shocked_values)
        
        # 评估基础对冲策略
        base_hedge_benefit = self.evaluate_hedge(shocked_values)
        
        # 评估优化后的对冲策略
        optimized_hedge_benefit = self.evaluate_hedge(shocked_values, optimized_weights)
        
        # 额外添加信用事件触发的特殊策略收益
        special_strategy_benefit = self._calculate_special_strategies(shocked_values)
        
        # 计算净收益
        total_hedge_benefit = optimized_hedge_benefit + special_strategy_benefit
        net_gain = total_hedge_benefit - L
        
        return {
            "Total Loss": -L,  # 显示为负数
            "Base Hedge Benefit": base_hedge_benefit,
            "Optimized Hedge": optimized_hedge_benefit,
            "Special Strategies": special_strategy_benefit,
            "Total Hedge Benefit": total_hedge_benefit,
            "Net Profit/Loss": net_gain
        }
    
    def _calculate_special_strategies(self, shocked_values):
        """计算特殊策略的额外收益"""
        # 1. CDS触发收益
        cds_benefit = max(0, shocked_values["CDS Spread"] - self.variables["CDS Spread"]) * 0.3
        
        # 2. 波动率策略收益
        vol_benefit = max(0, shocked_values["VIX"] - self.variables["VIX"]) * 0.5
        
        # 3. 信用违约掉期组合收益
        credit_arbitrage = max(0, self.variables["Credit Index"] - shocked_values["Credit Index"]) * 0.4
        
        # 4. 债券-CDS基差交易
        bond_cds_basis = abs(shocked_values["US Bond ETF"] - self.variables["US Bond ETF"]) * 0.3
        
        return cds_benefit + vol_benefit + credit_arbitrage + bond_cds_basis

    def plot_results(self, results):
        """改进的可视化，显示更多细节"""
        plt.figure(figsize=(12, 10))
        
        # 创建柱状图
        labels = list(results.keys())
        values = list(results.values())
        
        # 设置颜色
        colors = ['red', 'green', 'blue', 'purple', 'orange', 'black']
        if len(colors) < len(values):
            colors = colors * (len(values) // len(colors) + 1)
        
        # 绘制主图
        bars = plt.bar(labels, values, color=colors[:len(values)])
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.title("Enhanced Credit Default Arbitrage Results", fontsize=16)
        plt.ylabel("Profit/Loss Value", fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 保存结果
        plt.tight_layout()
        plt.savefig("simulation_charts/enhanced_arbitrage_results.png")
        
        # 绘制优化前后对比图
        self._plot_optimization_comparison(results)
        
        # 绘制各资产贡献图
        self._plot_asset_contributions(results)
        
        plt.show()
    
    def _plot_optimization_comparison(self, results):
        """绘制优化前后的对比图"""
        plt.figure(figsize=(10, 6))
        
        # 提取相关数据
        categories = ['Base Strategy', 'Optimized Strategy']
        values = [results['Base Hedge Benefit'], results['Optimized Hedge']]
        
        plt.bar(categories, values, color=['lightblue', 'darkblue'])
        plt.title("Strategy Optimization Comparison")
        plt.ylabel("Hedge Benefit")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加提升百分比标签
        improvement = ((values[1] - values[0]) / values[0]) * 100
        plt.text(1, values[1], f"+{improvement:.1f}%", ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig("simulation_charts/optimization_comparison.png")
    
    def _plot_asset_contributions(self, results):
        """绘制各资产对总收益的贡献"""
        shocked_values = self.simulate_jump()
        optimized_weights, _ = self.optimize_weights(shocked_values)
        
        # 计算各资产贡献
        contributions = []
        assets = []
        
        for var in self.variables:
            value_change = shocked_values[var] - self.variables[var]
            is_positive_hedge = (var in ["VIX", "Gold ETF", "US Bond ETF", "CDS Spread", "Volatility Swap"])
            
            if is_positive_hedge:
                hedge_value = max(value_change, 0)
            else:
                hedge_value = max(-value_change, 0)
                
            contribution = hedge_value * optimized_weights[var] * self.leverage
            if contribution > 0:  # 只显示有正向贡献的资产
                contributions.append(contribution)
                assets.append(var)
        
        # 绘制饼图
        plt.figure(figsize=(10, 8))
        plt.pie(contributions, labels=assets, autopct='%1.1f%%', startangle=90, shadow=True)
        plt.axis('equal')
        plt.title("Asset Contributions to Total Hedge Benefit")
        plt.tight_layout()
        plt.savefig("simulation_charts/asset_contributions.png")

    def run_monte_carlo(self, num_simulations=1000):
        """运行蒙特卡洛模拟，评估策略在不同情景下的表现"""
        results = []
        
        for _ in range(num_simulations):
            shocked_values = self.simulate_jump()
            sim_result = self.calculate_total(shocked_values)
            results.append(sim_result["Net Profit/Loss"])
        
        # 计算统计数据
        mean_result = np.mean(results)
        median_result = np.median(results)
        std_dev = np.std(results)
        min_result = np.min(results)
        max_result = np.max(results)
        
        # 计算VaR和CVaR
        var_95 = np.percentile(results, 5)  # 5% VaR (95% confidence)
        cvar_95 = np.mean([r for r in results if r <= var_95])
        
        # 绘制分布图
        plt.figure(figsize=(10, 6))
        plt.hist(results, bins=30, alpha=0.7, color='blue', edgecolor='black')
        plt.axvline(mean_result, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_result:.2f}')
        plt.axvline(var_95, color='g', linestyle='dashed', linewidth=2, label=f'5% VaR: {var_95:.2f}')
        
        plt.title("Monte Carlo Simulation of Net Profit/Loss")
        plt.xlabel("Net Profit/Loss")
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("simulation_charts/monte_carlo_distribution.png")
        
        # 返回统计数据
        stats_data = {
            "Mean": mean_result,
            "Median": median_result,
            "Std Dev": std_dev,
            "Min": min_result,
            "Max": max_result,
            "5% VaR": var_95,
            "5% CVaR": cvar_95
        }
        
        return stats_data

if __name__ == "__main__":
    # 创建增强版信用违约套利引擎
    simulator = EnhancedCreditShockSimulator(leverage=3.0)
    
    # 模拟市场跳变
    shocked_values = simulator.simulate_jump()
    
    # 计算结果
    results = simulator.calculate_total(shocked_values)
    
    # 可视化结果
    simulator.plot_results(results)
    
    # 运行蒙特卡洛模拟
    mc_stats = simulator.run_monte_carlo(1000)
    
    # 打印结果
    print("\n=== 信用违约套利结果 ===")
    for key, value in results.items():
        print(f"{key}: {value:.2f}")
    
    print("\n=== 蒙特卡洛模拟统计 ===")
    for key, value in mc_stats.items():
        print(f"{key}: {value:.2f}")