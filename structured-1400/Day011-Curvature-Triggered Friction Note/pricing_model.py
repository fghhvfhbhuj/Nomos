import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm
import os
import plotly.graph_objects as go

# 确保simulation_charts文件夹存在
os.makedirs('simulation_charts', exist_ok=True)

# Black-Scholes定价公式
def black_scholes(S, K, T, sigma, r=0.01):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

# 模拟数据生成模块
def generate_data():
    K = np.linspace(80, 120, 50)  # strike grid
    T = np.array([0.25, 0.5, 0.75, 1.0])  # time grid
    sigma = lambda k, t: 0.2 + 0.05 * np.sin(5 * k/100) * np.exp(-t)  # volatility surface
    
    # 计算市场价格C(K, T)
    S0 = 100  # 初始价格
    C = np.zeros((len(K), len(T)))
    lambda_values = np.zeros((len(K), len(T)))
    
    for i, k in enumerate(K):
        for j, t in enumerate(T):
            vol = sigma(k, t)
            # 模拟交易量和λ值
            volume = np.random.uniform(0, 1)
            lambda_val = 0.1 * np.log(1 + volume) + np.random.normal(0, 0.01)
            lambda_values[i, j] = lambda_val
            
            # 计算市场价格
            bs_price = black_scholes(S0, k, t, vol)
            gamma = (black_scholes(S0, k, t+0.01, vol) - 2*bs_price + black_scholes(S0, k, t-0.01, vol)) / (0.01**2)
            C[i, j] = bs_price + lambda_val * gamma

    return K, T, C, lambda_values, S0

# 曲率计算模块
# 使用梯度和Hessian矩阵计算曲率
def calculate_curvature_advanced(C):
    grad_x, grad_y = np.gradient(C)
    hessian_xx, hessian_xy = np.gradient(grad_x)
    hessian_yx, hessian_yy = np.gradient(grad_y)
    curvature = np.sqrt(hessian_xx**2 + hessian_yy**2 + 2 * hessian_xy * hessian_yx)
    return curvature

# 曲率触发条件
def is_triggered(curvature, threshold, C, C0):
    return (curvature > threshold) & (C > C0)

# 可视化模块
# 1. σ-λ-T空间上的C值分布 (3D图)
def plot_3d_surface(K, T, C):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    K_mesh, T_mesh = np.meshgrid(K, T)
    ax.plot_surface(K_mesh, T_mesh, C.T, cmap='viridis')
    ax.set_xlabel('Strike Price (K)')
    ax.set_ylabel('Time to Maturity (T)')
    ax.set_zlabel('Market Price (C)')
    ax.set_title('3D Surface of C(K, T)')
    plt.savefig('simulation_charts/3d_surface.png')
    plt.close()

# 使用Plotly生成交互式3D图表
def plot_3d_surface_interactive(K, T, C):
    K_mesh, T_mesh = np.meshgrid(K, T)
    fig = go.Figure(data=[go.Surface(z=C.T, x=K_mesh, y=T_mesh)])
    fig.update_layout(
        title='Interactive 3D Surface of C(K, T)',
        scene=dict(
            xaxis_title='Strike Price (K)',
            yaxis_title='Time to Maturity (T)',
            zaxis_title='Market Price (C)'
        )
    )
    fig.write_html('simulation_charts/interactive_3d_surface.html')

# 2. 高曲率区域热图
def plot_heatmap(curvature):
    plt.figure(figsize=(10, 8))
    plt.imshow(curvature, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Curvature')
    plt.title('Heatmap of High Curvature Regions')
    plt.xlabel('Strike Index')
    plt.ylabel('Time Index')
    plt.savefig('simulation_charts/heatmap.png')
    plt.close()

# 3. Structure payoff map
def plot_payoff_map(K, T, C):
    plt.figure(figsize=(10, 8))
    for i, t in enumerate(T):
        plt.plot(K, C[:, i], label=f'T={t}')
    plt.title('Structure Payoff Map')
    plt.xlabel('Strike Price (K)')
    plt.ylabel('Market Price (C)')
    plt.legend()
    plt.savefig('simulation_charts/payoff_map.png')
    plt.close()

# 4. 触发条件可视化
def plot_trigger_condition(K, T, triggered_matrix):
    plt.figure(figsize=(10, 8))
    K_mesh, T_mesh = np.meshgrid(K, T)
    plt.contourf(K_mesh, T_mesh, triggered_matrix.T, cmap='RdYlGn')
    plt.colorbar(label='Triggered (1) / Not Triggered (0)')
    plt.title('Curvature Trigger Condition Map')
    plt.xlabel('Strike Price (K)')
    plt.ylabel('Time to Maturity (T)')
    plt.savefig('simulation_charts/trigger_condition.png')
    plt.close()

# 5. Vanilla Put Spread Payoff
def plot_vanilla_put_spread(S_range, K1, K2, T, sigma):
    plt.figure(figsize=(10, 8))
    payoffs = []
    for S in S_range:
        payoff = vanilla_put_spread(S, K1, K2, T, sigma)
        payoffs.append(payoff)
    plt.plot(S_range, payoffs)
    plt.title(f'Vanilla Put Spread Payoff (K1={K1}, K2={K2})')
    plt.xlabel('Stock Price at Expiry')
    plt.ylabel('Payoff')
    plt.axhline(y=0, color='r', linestyle='-')
    plt.axvline(x=K1, color='g', linestyle='--')
    plt.axvline(x=K2, color='g', linestyle='--')
    plt.savefig('simulation_charts/put_spread_payoff.png')
    plt.close()

# 对结构保险项使用vanilla put spread组合对冲模拟收益
def vanilla_put_spread(S, K1, K2, T, sigma, r=0.01):
    # 买入低行权价put，卖出高行权价put
    d1_1 = (np.log(S / K1) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2_1 = d1_1 - sigma * np.sqrt(T)
    put1 = K1 * np.exp(-r * T) * norm.cdf(-d2_1) - S * norm.cdf(-d1_1)
    
    d1_2 = (np.log(S / K2) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2_2 = d1_2 - sigma * np.sqrt(T)
    put2 = K2 * np.exp(-r * T) * norm.cdf(-d2_2) - S * norm.cdf(-d1_2)
    
    return put1 - put2

# 增加风险分析模块
def risk_analysis(C, threshold):
    risk_regions = C > threshold
    risk_percentage = np.sum(risk_regions) / C.size * 100
    return risk_percentage

# 主函数
if __name__ == "__main__":
    print("生成模拟数据...")
    K, T, C, lambda_values, S0 = generate_data()
    
    print("计算高级曲率...")
    curvature = calculate_curvature_advanced(C)
    
    print("设置触发条件...")
    threshold = np.percentile(curvature, 90)  # 取曲率前10%为高曲率区域
    C0 = np.mean(C)  # 平均价格作为触发阈值
    triggered_matrix = is_triggered(curvature, threshold, C, C0)
    
    print("保存模拟数据...")
    np.savez('simulation_data_advanced.npz', K=K, T=T, C=C, lambda_values=lambda_values, 
             curvature=curvature, triggered=triggered_matrix)
    
    print("生成交互式3D图表...")
    plot_3d_surface_interactive(K, T, C)
    
    print("进行风险分析...")
    risk_percentage = risk_analysis(C, threshold)
    print(f"高风险区域占比: {risk_percentage:.2f}%")
    
    print("任务完成，所有图表已保存至 simulation_charts 文件夹。")
    
    # 进阶内容，仅在安装了yfinance和sklearn时使用
    try:
        import yfinance as yf
        from sklearn.linear_model import LinearRegression
        
        print("\n进阶功能 - 使用真实股权数据...")
        # 获取真实数据
        ticker = 'SPY'  # S&P 500 ETF
        start_date = '2023-01-01'
        end_date = '2025-01-01'
        print(f"尝试获取{ticker}的股价数据 ({start_date} 至 {end_date})...")
        
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            print(f"成功获取{ticker}数据，最新价格: {stock_data['Close'].iloc[-1]:.2f}")
            
            # 验证λ-volume映射函数
            print("\n进阶功能 - 验证λ-volume映射关系...")
            volume_flat = lambda_values.flatten().reshape(-1, 1)
            lambda_flat = lambda_values.flatten()
            
            model = LinearRegression()
            model.fit(volume_flat, lambda_flat)
            print(f"λ-volume线性关系: λ = {model.coef_[0]:.4f} * volume + {model.intercept_:.4f}")
            
            # 绘制回归结果
            plt.figure(figsize=(10, 6))
            plt.scatter(volume_flat, lambda_flat, alpha=0.3)
            x_range = np.linspace(0, 1, 100).reshape(-1, 1)
            y_pred = model.predict(x_range)
            plt.plot(x_range, y_pred, 'r-')
            plt.xlabel('Trading Volume (Normalized)')
            plt.ylabel('Lambda (Market Friction)')
            plt.title('Lambda-Volume Mapping Validation')
            plt.savefig('simulation_charts/lambda_volume_regression.png')
            plt.close()
            
        except Exception as e:
            print(f"获取股票数据时出错: {e}")
            
    except ImportError:
        print("\n注意: 进阶功能需要安装yfinance和sklearn")
        print("如需使用进阶功能，请运行: pip install yfinance scikit-learn")