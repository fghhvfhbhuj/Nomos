# risk_score_func_demo.py
# 教学用信用评分函数模板（用于结构票据敲出触发）

import numpy as np

def risk_score_func(ICR, LR, rating_score, price_to_par):
    """
    教学型信用评分函数（打分范围 0 ~ 100）

    参数解释：
    ICR: Interest Coverage Ratio（利息覆盖倍数）
    LR: Liquidity Ratio（流动比率）
    rating_score: 信用评级分数（如 AAA=90，BBB=70，CCC=30）
    price_to_par: 当前债券价格 / 面值 比值（例如：0.85）

    返回值：
    score: 信用分数（float，范围 0~100）
    """
    # 权重设定（可自定义）
    w_icr = 25
    w_lr = 20
    w_rating = 40
    w_price = 15

    # 分数缩放（防止极端值）
    ICR = min(ICR, 5)
    LR = min(LR, 5)
    rating_score = min(max(rating_score, 0), 100)
    price_to_par = min(max(price_to_par, 0), 2)

    # 打分计算
    score = (
        w_icr * (ICR / 5) +
        w_lr * (LR / 5) +
        w_rating * (rating_score / 100) +
        w_price * price_to_par
    )

    return round(score, 2)

# 示例调用
if __name__ == "__main__":
    sample = risk_score_func(ICR=2.5, LR=1.8, rating_score=65, price_to_par=0.87)
    print("示例公司信用评分：", sample)

    # 敲出判断建议：若 score < 50 连续 3 日，则结构自动敲出
