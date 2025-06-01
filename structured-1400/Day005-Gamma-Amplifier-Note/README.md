# Day005 – Gamma Amplifier Note（GAN）

## 📌 概述
Gamma Amplifier Note (GAN) 是一款用于放大 Gamma 敏感度而无需融资杠杆的结构衍生品。其设计通过让渡路径精度换取局部敏感放大，适合震荡性行情策略。基于我们开发的定价模型和回测结果，GAN在特定市场环境下能够提供比传统策略更高的收益潜力。

## 📈 特点与性能
- **无融资杠杆**：通过结构设计而非资金杠杆实现敏感度放大
- **高 Gamma 暴露**：在激活区间[K-δ, K+δ]内提供强烈的Gamma敞口
- **Delta 中性结构**：整体方向性敞口中性，降低单边市场风险
- **局部激活式收益**：在特定价格区间内提供放大效应
- **回测表现**：在震荡市场中表现优异，收益放大倍数平均可达1.5-3倍
- **风险特征**：非线性收益分布，在特定路径下可实现高收益

## 📊 回测结果摘要
根据我们的定价模型（pricing_model.py）运行的1000条路径模拟，GAN产品展现以下特性：
- 在价格波动穿越激活区间的情况下，GAN收益明显优于普通策略
- 价格区间越大，实现波动率越高，GAN收益越显著
- 激活带宽(δ)的选择对GAN收益有显著影响，我们的模型支持优化此参数
- 回测结果显示，GAN在大多数路径中能保持较低风险，同时在特定路径下获得超额收益

## 📂 文件结构
- `whitepaper.md`：理论与结构设计详解
- `term-sheet.md`：产品条款与参数规格
- `scenario-examples.md`：市场情景分析与收益模式
- `risk-disclosure.md`：风险披露与管理策略
- `pricing_model.py`：GAN定价与回测模型实现
- `pricing_result.csv`：完整回测数据结果
- `simulation_charts/`：可视化分析图表
- `README.md`：项目总览

## 🔧 使用说明

### 运行定价模型
```bash
pip install numpy pandas matplotlib scipy seaborn tqdm
python pricing_model.py
```

### 主要输出
- `pricing_result.csv`：详细回测数据，包含GAN与普通策略的对比结果
- `simulation_charts/`目录：包含收益分布、敏感性分析、典型路径等多种分析图表

## 📈 模型参数说明
当前模型使用以下默认参数：
- 初始价格(S0): 100
- 激活中心(K): 100
- 激活带宽(δ): 2
- 期限(T): 30天
- 无风险利率(r): 3%
- 波动率(σ): 20%
- Gamma放大系数: 2.5
- 结构成本因子: 5%

这些参数可在`pricing_model.py`文件的main函数中调整以适应不同市场环境。
