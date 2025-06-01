# 📊 自适应保证金控制票据 (Adaptive Margin-Control Note)

[![Stars](https://img.shields.io/github/stars/yourusername/structured-1400?style=social)](https://github.com/yourusername/structured-1400)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/yourusername/structured-1400)

<p align="center">
  <img src="./simulation_charts/payout_distribution.png" alt="收益分布图" width="70%">
</p>

## 🌟 项目简介

自适应保证金控制票据 (AMCN) 是一种创新型结构化衍生品，结合了路径依赖特性、资金池机制和动态保证金控制系统，为投资者提供:

- 💹 **上行市场参与**：保留对市场上涨的显著参与度
- 🛡️ **下行风险缓冲**：通过独特的资金池机制提供风险保护
- 🔄 **自适应风险控制**：根据市场走势自动调整风险敞口
- 🎮 **用户可控机制**：投资者可干预和管理风险

该产品特别适合高波动率市场环境，通过智能结构设计在保留上行收益潜力的同时，提供下行风险管理功能。

## 🔍 核心机制

### 敲入与收益封顶
当标的资产回报率超过20%时，触发收益封顶机制(30%)，将超额收益转入资金池。

### 资金池保护
资金池存储超额收益，在账户权益下跌时自动或按用户要求进行补仓，防止强制平仓。

### 保证金控制系统
设置初始保证金(10%)和维持保证金(5%)，当权益低于维持线且资金池耗尽时触发敲出。

<details>
<summary><b>查看详细产品结构图</b></summary>
<p align="center">
  <img src="./simulation_charts/scenario1_price_path.png" alt="产品结构示例" width="80%">
</p>
</details>

## 📈 模拟结果

使用高级蒙特卡洛模拟（10,000路径，包含跳跃扩散与随机波动率）的主要发现:

| 指标 | 数值 |
|------|------|
| 理论票据价值 | ¥-1.38 |
| 初始本金 | ¥100.00 |
| 收益封顶 | 30% |
| 敲入阈值 | 20% |
| 维持保证金线 | 5% |
| 95% 风险价值(VaR) | -32.38 |
| 99% 风险价值(VaR) | -42.74 |
| 条件风险价值(CVaR) | -38.78 |
| 平均最大回撤 | 27.64% |
| 敲入概率 | 33.43% |
| 强平概率 | 0% |

### 性能亮点

- 在市场温和上涨环境中提供稳定收益
- 在高波动市场中显著降低极端亏损风险
- 资金池机制有效缓冲市场突变冲击
- 随机波动率模型更准确反映真实市场条件
- 为投资者提供干预和调整的灵活性

## 📚 项目文档

- [📄 **条款说明书 (Term Sheet)**](./term-sheet.md)：完整产品条款与规格
- [📋 **白皮书 (Whitepaper)**](./whitepaper.md)：详细的产品设计理念与机制
- [⚠️ **风险揭示说明**](./risk-disclosure.md)：产品风险点与适用性说明
- [📊 **情景示例**](./scenario-examples.md)：不同市场环境下的产品表现

## 💻 技术实现

该项目使用Python实现，核心技术包括:

```python
# 核心定价逻辑示例
for i in tqdm(range(n_paths)):
    prices = [S0]
    volatilities = [sigma_base]
    current_sigma = sigma_base
    pool = 0
    knocked_in = False
    
    for t in range(N):
        # 更新随机波动率 (Heston-like)
        vol_shock = np.random.normal(0, 1)
        current_sigma = max(0.05, current_sigma + vol_mean_reversion * (vol_long_run_mean - current_sigma) * dt + 
                        vol_vol * np.sqrt(current_sigma * dt) * vol_shock)
        
        # 价格扩散与跳跃
        z = np.random.normal()
        dS_diffusion = prices[-1] * (mu * dt + current_sigma * np.sqrt(dt) * z)
        
        jump_occurs = np.random.poisson(jump_intensity * dt)
        dS_jump = 0
        if jump_occurs > 0:
            jump_size = np.random.normal(jump_mean, jump_std, jump_occurs)
            dS_jump = prices[-1] * np.sum(jump_size)
        
        # ...敲入判断与风险控制逻辑...
```

完整代码详见 [pricing_model.py](./pricing_model.py)

## 🚀 如何使用

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/structured-1400.git
   cd structured-1400/Day001-Adaptive-Margin-Control-Note
   ```

2. **安装依赖**
   ```bash
   pip install numpy matplotlib pandas tqdm
   ```

3. **运行模拟**
   ```bash
   python pricing_model.py
   ```

4. **查看结果**
   - 模拟图表将保存在 `simulation_charts/` 目录
   - 定价结果将保存为 `pricing_result.csv`

## 🔗 相关资源

- [结构化产品设计系列](https://github.com/yourusername/structured-1400)
- [金融衍生品设计指南](https://github.com/yourusername/structured-1400)
- [量化金融工具集](https://github.com/yourusername/structured-1400)

## 👨‍💼 作者

该项目是结构化衍生品设计系列的一部分，旨在展示现代金融工程的创新应用。欢迎用于:

- 🎓 衍生品教学与学习
- 📝 金融工程案例研究
- 💼 面试作品集展示
- 🧪 结构化产品设计实验

## 📄 许可证

本项目采用 [MIT 许可证](./LICENSE.md)。您可以自由使用、修改和分发本代码，但请保留原作者署名。

---

<p align="center">
  <i>这是 structured-1400 结构化衍生品设计系列的一部分</i><br>
  <a href="https://github.com/yourusername/structured-1400">探索更多创新金融结构 →</a>
</p>
