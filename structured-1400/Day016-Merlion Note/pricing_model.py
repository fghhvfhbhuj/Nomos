import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import datetime, timedelta

class MerlionShieldPricer:
    """
    Merlion Shield - 本金保障型波动率票据
    
    定价逻辑基于：
    - FGEI (Financial Governance Event Index) 指数值
    - REITvol (REIT波动率指数)
    """
    
    def __init__(self, principal=100.0, tenor=18, 
                 k1=0.7, k2=1.2, 
                 lambda1=3.0, lambda2=5.5, 
                 sigma0=0.125):
        """
        初始化 Merlion Shield 定价器
        
        参数:
            principal: 本金金额
            tenor: 期限(月)
            k1: FGEI 第一阈值
            k2: FGEI 第二阈值
            lambda1: 第一区间的乘数
            lambda2: 第二区间的乘数
            sigma0: REITvol 基准波动率
        """
        self.principal = principal
        self.tenor = tenor
        self.k1 = k1
        self.k2 = k2
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.sigma0 = sigma0
        
    def calculate_return(self, fgei, reit_vol):
        """
        计算回报率
        
        参数:
            fgei: 金融治理事件指数值
            reit_vol: REIT波动率
            
        返回:
            回报率 (0-25%)
        """
        if fgei < self.k1:
            return 0.0
        elif fgei < self.k2:
            return self.lambda1 * (reit_vol - self.sigma0)
        else:
            # 在高压力区域添加FGEI偏移
            fgei_offset = 0.05 * (fgei - self.k2)  # 5%的FGEI偏移系数
            return self.lambda2 * (reit_vol + fgei_offset)
    
    def price(self, fgei, reit_vol):
        """
        定价 Merlion Shield 票据
        
        参数:
            fgei: 金融治理事件指数值
            reit_vol: REIT波动率
            
        返回:
            票据价格
        """
        return_rate = self.calculate_return(fgei, reit_vol)
        # 限制最大回报率为25%
        return_rate = min(0.25, max(0, return_rate))
        
        # 本金保障型票据，最低价值等于本金
        price = self.principal * (1 + return_rate)
        return price
    
    def generate_pricing_surface(self, fgei_range=None, reit_vol_range=None):
        """
        生成定价曲面
        
        参数:
            fgei_range: FGEI范围数组
            reit_vol_range: REIT波动率范围数组
            
        返回:
            fgei_grid, reit_vol_grid, price_surface
        """
        if fgei_range is None:
            fgei_range = np.linspace(0.0, 2.0, 50)
        if reit_vol_range is None:
            reit_vol_range = np.linspace(0.05, 0.30, 50)
            
        fgei_grid, reit_vol_grid = np.meshgrid(fgei_range, reit_vol_range)
        price_surface = np.zeros_like(fgei_grid)
        
        for i in range(len(reit_vol_range)):
            for j in range(len(fgei_range)):
                price_surface[i, j] = self.price(fgei_grid[i, j], reit_vol_grid[i, j])
                
        return fgei_grid, reit_vol_grid, price_surface
    
    def plot_pricing_surface(self, fgei_range=None, reit_vol_range=None):
        """绘制定价曲面"""
        fgei_grid, reit_vol_grid, price_surface = self.generate_pricing_surface(
            fgei_range, reit_vol_range
        )
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(fgei_grid, reit_vol_grid, price_surface, 
                               cmap='viridis', alpha=0.8)
        
        # 标记阈值平面
        max_vol = reit_vol_grid.max()
        min_vol = reit_vol_grid.min()
        
        # K1平面
        x1 = np.array([self.k1, self.k1])
        y1 = np.array([min_vol, max_vol])
        z1 = np.array([[self.principal, self.principal], 
                       [self.price(self.k1, max_vol), self.price(self.k1, max_vol)]])
        ax.plot_surface(x1[:, np.newaxis], y1[:, np.newaxis], z1, 
                        alpha=0.3, color='red')
        
        # K2平面
        x2 = np.array([self.k2, self.k2])
        y2 = np.array([min_vol, max_vol])
        z2 = np.array([[self.price(self.k2, min_vol), self.price(self.k2, min_vol)], 
                       [self.price(self.k2, max_vol), self.price(self.k2, max_vol)]])
        ax.plot_surface(x2[:, np.newaxis], y2[:, np.newaxis], z2, 
                        alpha=0.3, color='green')
        
        ax.set_xlabel('FGEI')
        ax.set_ylabel('REIT Volatility')
        ax.set_zlabel('Price')
        ax.set_title('Merlion Shield Pricing Surface')
        
        # 添加颜色条
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        return fig, ax


class HydraFangPricer:
    """
    Hydra Fang - 触发事件期权
    
    在 FGEI > K₂ 时激活，与REIT波动率和方向性空头敞口相关
    """
    
    def __init__(self, notional=100.0, tenor=18, k2=1.2, 
                 beta=7.0, gamma=2.5, reit_base_price=100.0):
        """
        初始化 Hydra Fang 定价器
        
        参数:
            notional: 名义本金
            tenor: 期限(月)
            k2: FGEI 触发阈值
            beta: 波动率敏感度
            gamma: REIT价格敏感度
            reit_base_price: REIT指数基准价格
        """
        self.notional = notional
        self.tenor = tenor
        self.k2 = k2
        self.beta = beta
        self.gamma = gamma
        self.reit_base_price = reit_base_price
        
    def calculate_payoff(self, fgei, reit_vol, reit_price):
        """
        计算期权收益
        
        参数:
            fgei: 金融治理事件指数值
            reit_vol: REIT波动率
            reit_price: 当前REIT指数价格
            
        返回:
            期权收益
        """
        # 如果FGEI低于触发阈值，期权无价值
        if fgei < self.k2:
            return 0.0
        
        # 波动率组件：高波动率导致更高收益
        vol_component = self.beta * (reit_vol - 0.1)  # 假设0.1为基准波动率
        
        # 价格组件：REIT价格下跌导致更高收益(做空敞口)
        price_component = self.gamma * max(0, (self.reit_base_price - reit_price) / self.reit_base_price)
        
        # FGEI超额组件：FGEI超过阈值越多，收益越高
        fgei_excess = (fgei - self.k2) * 2.0
        
        # 综合计算收益
        payoff = self.notional * (vol_component + price_component) * fgei_excess
        return max(0, payoff)  # 期权收益不能为负
    
    def price(self, fgei, reit_vol, reit_price, risk_free_rate=0.03, days_to_maturity=None):
        """
        定价 Hydra Fang 期权
        
        参数:
            fgei: 金融治理事件指数值
            reit_vol: REIT波动率
            reit_price: 当前REIT指数价格
            risk_free_rate: 无风险利率
            days_to_maturity: 到期天数(如果为None，使用tenor计算)
            
        返回:
            期权价格
        """
        if days_to_maturity is None:
            days_to_maturity = self.tenor * 30  # 简化计算，每月30天
        
        # 计算即期收益
        immediate_payoff = self.calculate_payoff(fgei, reit_vol, reit_price)
        
        # 如果FGEI已经高于触发阈值，使用即期收益
        if fgei >= self.k2:
            # 折现到当前
            time_to_maturity = days_to_maturity / 365.0  # 转换为年
            price = immediate_payoff * np.exp(-risk_free_rate * time_to_maturity)
            return price
        
        # 如果FGEI低于触发阈值，使用概率模型估计未来触发可能性
        # 简化模型：假设FGEI遵循正态分布
        fgei_std = 0.3  # FGEI的标准差(根据历史数据估计)
        time_to_maturity = days_to_maturity / 365.0  # 转换为年
        
        # 计算FGEI到达触发阈值的概率
        prob_trigger = 1 - norm.cdf((self.k2 - fgei) / (fgei_std * np.sqrt(time_to_maturity)))
        
        # 估计触发后的平均收益
        expected_fgei_if_triggered = fgei + fgei_std * np.sqrt(time_to_maturity) * norm.pdf(
            (self.k2 - fgei) / (fgei_std * np.sqrt(time_to_maturity))) / prob_trigger
        expected_payoff = self.calculate_payoff(expected_fgei_if_triggered, reit_vol, reit_price)
        
        # 期权价格 = 触发概率 * 预期收益的现值
        price = prob_trigger * expected_payoff * np.exp(-risk_free_rate * time_to_maturity)
        return price
    
    def generate_pricing_surface(self, fgei_range=None, reit_price_range=None, reit_vol=0.15):
        """
        生成定价曲面
        
        参数:
            fgei_range: FGEI范围数组
            reit_price_range: REIT价格范围数组
            reit_vol: 固定的REIT波动率
            
        返回:
            fgei_grid, reit_price_grid, price_surface
        """
        if fgei_range is None:
            fgei_range = np.linspace(0.5, 2.0, 50)
        if reit_price_range is None:
            reit_price_range = np.linspace(70, 130, 50)
            
        fgei_grid, reit_price_grid = np.meshgrid(fgei_range, reit_price_range)
        price_surface = np.zeros_like(fgei_grid)
        
        for i in range(len(reit_price_range)):
            for j in range(len(fgei_range)):
                price_surface[i, j] = self.price(
                    fgei_grid[i, j], reit_vol, reit_price_grid[i, j]
                )
                
        return fgei_grid, reit_price_grid, price_surface
    
    def plot_pricing_surface(self, fgei_range=None, reit_price_range=None, reit_vol=0.15):
        """绘制定价曲面"""
        fgei_grid, reit_price_grid, price_surface = self.generate_pricing_surface(
            fgei_range, reit_price_range, reit_vol
        )
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(fgei_grid, reit_price_grid, price_surface, 
                               cmap='plasma', alpha=0.8)
        
        # 标记阈值平面
        max_price = reit_price_grid.max()
        min_price = reit_price_grid.min()
        
        # K2触发平面
        x2 = np.array([self.k2, self.k2])
        y2 = np.array([min_price, max_price])
        z_min = self.price(self.k2, reit_vol, min_price)
        z_max = self.price(self.k2, reit_vol, max_price)
        z2 = np.array([[z_min, z_min], [z_max, z_max]])
        ax.plot_surface(x2[:, np.newaxis], y2[:, np.newaxis], z2, 
                        alpha=0.3, color='red')
        
        ax.set_xlabel('FGEI')
        ax.set_ylabel('REIT Price')
        ax.set_zlabel('Option Price')
        ax.set_title(f'Hydra Fang Option Pricing Surface (REIT Vol: {reit_vol:.2f})')
        
        # 添加颜色条
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        return fig, ax


def calculate_fgei(vol_cds, skew_ir, delta_spread_policy, alpha=0.4, beta=0.3, gamma=0.3):
    """
    计算 FGEI (Financial Governance Event Index)
    
    FGEI = α * vol_CDS + β * skew_IR + γ * Δspread_policy
    
    参数:
        vol_cds: iTraxx新加坡金融CDS的5日实现波动率
        skew_ir: 1M-3M新加坡元利率上限的隐含偏斜
        delta_spread_policy: SIBOR/CNH远期隐含价差与实现远期基差之间的偏差
        alpha, beta, gamma: 各组件的权重
        
    返回:
        FGEI值
    """
    return alpha * vol_cds + beta * skew_ir + gamma * delta_spread_policy


# 示例使用
if __name__ == "__main__":
    # 创建Merlion Shield定价器
    merlion_shield = MerlionShieldPricer()
    
    # 创建Hydra Fang定价器
    hydra_fang = HydraFangPricer()
    
    # 当前市场参数
    fgei = 0.8  # 当前FGEI值
    reit_vol = 0.14  # 当前REIT波动率
    reit_price = 95.0  # 当前REIT价格
    
    # 计算票据价格
    merlion_price = merlion_shield.price(fgei, reit_vol)
    hydra_price = hydra_fang.price(fgei, reit_vol, reit_price)
    
    print(f"当前市场参数:")
    print(f"  FGEI: {fgei:.2f}")
    print(f"  REIT波动率: {reit_vol:.2f}")
    print(f"  REIT价格: {reit_price:.2f}")
    print()
    print(f"Merlion Shield价格: {merlion_price:.2f}")
    print(f"Hydra Fang期权价格: {hydra_price:.2f}")
    
    # 绘制定价曲面
    merlion_fig, _ = merlion_shield.plot_pricing_surface()
    hydra_fig, _ = hydra_fang.plot_pricing_surface()
    
    plt.show()