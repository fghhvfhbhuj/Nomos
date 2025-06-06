# 白皮书

## 技术背景
曲率触发摩擦票据模型结合了Black-Scholes定价理论和市场摩擦因子的动态调整，旨在探索市场微观结构对衍生品定价的影响。

## 数学模型
1. **波动率曲面**：
   \[
   \sigma(K, T) = 0.2 + 0.05 \cdot \sin(5K) \cdot e^{-T}
   \]
2. **摩擦因子**：
   \[
   \lambda(K,T) = \eta \cdot \log(1 + V(K,T)) + \epsilon
   \]
3. **市场价格**：
   \[
   C(K, T) = BS(S_0, K, T, \sigma) + \lambda \cdot \Gamma
   \]

## 实现细节
- 使用Python实现数据模拟和定价逻辑。
- 通过梯度和Hessian矩阵计算曲率。
- 提供多种可视化图表以分析结果。