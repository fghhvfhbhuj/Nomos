# risk_score_func_demo.py
# 教学用信用评分函数模板（用于结构票据敲出触发）

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
import os

class CreditRiskModel:
    """增强版信用风险评分模型，包含机器学习和异常检测功能"""
    
    def __init__(self, use_ml=True, anomaly_detection=True):
        self.use_ml = use_ml  # 是否使用机器学习增强模型
        self.anomaly_detection = anomaly_detection  # 是否使用异常检测
        self.weights = {
            'interest_coverage': 0.30,
            'current_ratio': 0.25,
            'credit_rating': 0.25,
            'market_to_book': 0.20
        }
        self.rf_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        
        # 创建输出目录
        os.makedirs("./model_outputs", exist_ok=True)
    
    def fit(self, historical_data):
        """使用历史数据训练模型"""
        if not self.use_ml:
            return
            
        # 准备训练数据
        X = historical_data[['interest_coverage', 'current_ratio', 
                            'credit_rating', 'market_to_book']]
        y = historical_data['default_flag']  # 假设有一个违约标记列
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练随机森林模型
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.3, random_state=42)
        
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf_model.fit(X_train, y_train)
        
        # 评估模型
        y_pred_proba = self.rf_model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        # 训练异常检测器
        if self.anomaly_detection:
            self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
            self.anomaly_detector.fit(X_scaled)
        
        # 绘制ROC曲线
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC曲线 (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlabel('假阳性率')
        plt.ylabel('真阳性率')
        plt.title('信用风险模型ROC曲线')
        plt.legend(loc='lower right')
        plt.savefig('./model_outputs/roc_curve.png')
        plt.close()
        
        # 特征重要性
        if self.rf_model:
            importance = self.rf_model.feature_importances_
            feature_names = X.columns
            
            # 根据机器学习模型自动调整权重
            total_importance = sum(importance)
            for i, feat in enumerate(feature_names):
                self.weights[feat] = importance[i] / total_importance
                
            # 绘制特征重要性
            plt.figure(figsize=(10, 6))
            plt.bar(feature_names, importance)
            plt.title('特征重要性')
            plt.xlabel('特征')
            plt.ylabel('重要性')
            plt.savefig('./model_outputs/feature_importance.png')
            plt.close()
    
    def detect_anomalies(self, data):
        """检测异常值"""
        if not self.anomaly_detection or self.anomaly_detector is None:
            return np.zeros(len(data), dtype=int)
            
        X = data[['interest_coverage', 'current_ratio', 
                 'credit_rating', 'market_to_book']]
        X_scaled = self.scaler.transform(X)
        
        # -1表示异常，1表示正常
        return self.anomaly_detector.predict(X_scaled)
    
    def risk_score_func(self, interest_coverage, current_ratio, 
                       credit_rating, market_to_book, additional_factors=None):
        """
        计算信用风险评分
        
        参数:
        - interest_coverage: 利息覆盖倍数 (EBIT/利息支出)
        - current_ratio: 流动比率 (流动资产/流动负债)
        - credit_rating: 信用评级分数 (例如：AAA=90, AA=80, A=70...)
        - market_to_book: 市值账面比 (市值/账面价值)
        - additional_factors: 可选的额外因素字典，用于扩展模型
        
        返回:
        - 风险评分 (0-100，越高越安全)
        """
        # 基础数据收集
        data = {
            'interest_coverage': max(0, min(interest_coverage, 10)),  # 限制在0-10范围内
            'current_ratio': max(0, min(current_ratio, 5)),           # 限制在0-5范围内
            'credit_rating': max(0, min(credit_rating, 100)),         # 限制在0-100范围内
            'market_to_book': max(0, min(market_to_book, 10))         # 限制在0-10范围内
        }
        
        # 处理额外因素
        if additional_factors and isinstance(additional_factors, dict):
            for key, value in additional_factors.items():
                data[key] = value
        
        # 标准化数据
        data_df = pd.DataFrame([data])
        X = data_df[['interest_coverage', 'current_ratio', 
                     'credit_rating', 'market_to_book']]
        
        # 检测是否为异常值
        is_anomaly = False
        if self.anomaly_detection and self.anomaly_detector is not None:
            X_scaled = self.scaler.transform(X)
            anomaly_result = self.anomaly_detector.predict(X_scaled)[0]
            is_anomaly = (anomaly_result == -1)
        
        # 基于ML模型的评分
        ml_score = 0
        if self.use_ml and self.rf_model is not None:
            X_scaled = self.scaler.transform(X)
            # 获取违约概率
            default_prob = self.rf_model.predict_proba(X_scaled)[0, 1]
            ml_score = 100 * (1 - default_prob)
        
        # 传统评分计算（作为备份或混合使用）
        # 规范化各指标，使它们在0-100范围内
        normalized = {
            'interest_coverage': min(100, data['interest_coverage'] * 10),  # 0-10 -> 0-100
            'current_ratio': min(100, data['current_ratio'] * 20),          # 0-5 -> 0-100
            'credit_rating': data['credit_rating'],                         # 已经在0-100范围
            'market_to_book': min(100, data['market_to_book'] * 10)         # 0-10 -> 0-100
        }
        
        # 计算加权得分
        traditional_score = sum(normalized[k] * self.weights[k] for k in self.weights)
        
        # 混合ML和传统评分
        if self.use_ml and self.rf_model is not None:
            final_score = 0.7 * ml_score + 0.3 * traditional_score
        else:
            final_score = traditional_score
        
        # 如果检测到异常，降低评分
        if is_anomaly:
            final_score *= 0.7  # 异常情况下降低30%的评分
        
        return round(final_score, 2)

# 演示函数
def demo_risk_score():
    # 创建模型实例
    model = CreditRiskModel(use_ml=False, anomaly_detection=False)
    
    # 打印一些样例评分
    test_cases = [
        # 利息覆盖率, 流动比率, 信用评级, 市值账面比
        (5.0, 2.0, 80, 2.5),    # 良好的财务状况
        (3.0, 1.5, 65, 1.8),    # 中等的财务状况
        (1.2, 0.9, 40, 0.7),    # 较差的财务状况
        (0.5, 0.6, 25, 0.3)     # 危险的财务状况
    ]
    
    print("信用风险评分示例 (传统模型):")
    print("-" * 60)
    print(f"{'利息覆盖率':<12} {'流动比率':<10} {'信用评级':<10} {'市值账面比':<12} {'风险评分':<10}")
    print("-" * 60)
    
    for case in test_cases:
        score = model.risk_score_func(*case)
        print(f"{case[0]:<12.1f} {case[1]:<10.1f} {case[2]:<10.0f} {case[3]:<12.1f} {score:<10.2f}")
    
    # 创建一些模拟历史数据来演示ML功能
    np.random.seed(42)
    n_samples = 1000
    
    # 生成随机特征
    interest_coverage = np.random.normal(3, 2, n_samples)
    current_ratio = np.random.normal(1.5, 0.7, n_samples)
    credit_rating = np.random.normal(60, 15, n_samples)
    market_to_book = np.random.normal(1.5, 0.8, n_samples)
    
    # 生成目标变量 (根据特征的线性组合加噪声)
    latent = (0.3 * interest_coverage + 
              0.25 * current_ratio + 
              0.25 * credit_rating/100 + 
              0.2 * market_to_book + 
              np.random.normal(0, 0.5, n_samples))
    
    # 转换为二元违约标记
    default_threshold = np.percentile(latent, 15)  # 假设15%的违约率
    default_flag = (latent < default_threshold).astype(int)
    
    # 创建数据框
    historical_data = pd.DataFrame({
        'interest_coverage': np.clip(interest_coverage, 0, 10),
        'current_ratio': np.clip(current_ratio, 0, 5),
        'credit_rating': np.clip(credit_rating, 0, 100),
        'market_to_book': np.clip(market_to_book, 0, 10),
        'default_flag': default_flag
    })
    
    # 创建并训练ML模型
    ml_model = CreditRiskModel(use_ml=True, anomaly_detection=True)
    ml_model.fit(historical_data)
    
    # 测试ML模型
    print("\n信用风险评分示例 (ML增强模型):")
    print("-" * 60)
    print(f"{'利息覆盖率':<12} {'流动比率':<10} {'信用评级':<10} {'市值账面比':<12} {'风险评分':<10}")
    print("-" * 60)
    
    for case in test_cases:
        score = ml_model.risk_score_func(*case)
        print(f"{case[0]:<12.1f} {case[1]:<10.1f} {case[2]:<10.0f} {case[3]:<12.1f} {score:<10.2f}")
    
    # 创建风险评分可视化
    test_interest = np.linspace(0, 10, 20)
    test_current = np.linspace(0, 5, 20)
    
    # 对利息覆盖率的敏感性
    ic_scores = []
    for ic in test_interest:
        score = model.risk_score_func(ic, 1.5, 60, 1.5)
        ic_scores.append(score)
    
    # 对流动比率的敏感性
    cr_scores = []
    for cr in test_current:
        score = model.risk_score_func(3.0, cr, 60, 1.5)
        cr_scores.append(score)
    
    # 绘制敏感性曲线
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 利息覆盖率敏感性
    ax1.plot(test_interest, ic_scores, 'b-', linewidth=2)
    ax1.set_title('利息覆盖率对风险评分的影响')
    ax1.set_xlabel('利息覆盖率')
    ax1.set_ylabel('风险评分')
    ax1.grid(True)
    
    # 流动比率敏感性
    ax2.plot(test_current, cr_scores, 'r-', linewidth=2)
    ax2.set_title('流动比率对风险评分的影响')
    ax2.set_xlabel('流动比率')
    ax2.set_ylabel('风险评分')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('./model_outputs/risk_score_sensitivity.png')
    plt.close()
    
    print("\n风险评分敏感性分析图表已生成：./model_outputs/risk_score_sensitivity.png")
    print("机器学习模型评估图表已生成：./model_outputs/roc_curve.png")
    print("特征重要性图表已生成：./model_outputs/feature_importance.png")

if __name__ == "__main__":
    demo_risk_score()
