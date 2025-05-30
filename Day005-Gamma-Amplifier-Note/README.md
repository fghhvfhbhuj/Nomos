# Day005 – Gamma Amplifier Note（GAN）

## 📌 概述
Gamma Amplifier Note 是一款用于放大 Gamma 敏感度而无需融资杠杆的结构衍生品。其设计通过让渡路径精度换取局部敏感放大，适合震荡性行情策略。

## 📈 特点
- 无融资杠杆
- 高 Gamma 暴露
- Delta 中性结构
- 局部激活式收益结构
- 成本较低，风险非对称

## 📂 文件结构
- `whitepaper.md`：理论与结构设计
- `term-sheet.md`：术语与结构参数
- `scenario-examples.md`：情景模拟
- `risk-disclosure.md`：风险披露
- `pricing_model.py`：模拟模型
- `README.md`：项目说明

## ▶ 使用说明

```bash
pip install numpy pandas matplotlib
python pricing_model.py
