# pricing_model.py
# Day002 — Credit-Triggered Redemption Note 定价模型（教学可视化版）

import numpy as np
import matplotlib.pyplot as plt
from math import exp
import os
import logging
import datetime

# === 初始化日志记录 ===
logging.basicConfig(
    filename='pricing_model.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === 参数设定（模块化） ===
def get_parameters():
    return {
        'principal': 100_000,
        'annual_discount_rate': 0.05,
        'risk_premium': 5_000,
        'observation_days': 15,
        'observation_compensation_rate': 0.05,
        'cash_flows': np.array([2_500, 2_500, 2_500, 102_500]),
        'times': np.array([0.25, 0.5, 0.75, 1.0]),
        'knockout_probs': np.linspace(0, 0.5, 100),
        'max_payout_ratio': 1.1
    }

# === 贴现函数 ===
def discount(value, time, rate):
    return value * exp(-rate * time)

# === 计算结构价值 ===
def calculate_values(params):
    principal = params['principal']
    annual_discount_rate = params['annual_discount_rate']
    risk_premium = params['risk_premium']
    observation_days = params['observation_days']
    observation_compensation_rate = params['observation_compensation_rate']
    cash_flows = params['cash_flows']
    times = params['times']
    knockout_probs = params['knockout_probs']
    max_payout_ratio = params['max_payout_ratio']

    T_obs = observation_days / 365
    V_normal = sum(discount(c, t, annual_discount_rate) for c, t in zip(cash_flows, times))
    V_obs = principal * (exp(observation_compensation_rate * T_obs) - 1)
    V_knockout = min(V_normal + risk_premium, principal * max_payout_ratio)

    expected_values = (1 - knockout_probs) * (V_normal + V_obs) + knockout_probs * V_knockout

    logging.info(f"V_normal: {V_normal}, V_obs: {V_obs}, V_knockout: {V_knockout}")
    return knockout_probs, expected_values, V_normal, V_obs, V_knockout

# === 可视化输出 ===
def visualize(knockout_probs, expected_values, principal):
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
    
    plt.figure(figsize=(12, 8))
    plt.plot(knockout_probs, expected_values, label='Structure Expected Value', linewidth=2.5, color='#2E86AB')
    plt.axhline(y=principal, color='#A23B72', linestyle='--', linewidth=2, label='Principal Baseline')
    
    # 添加更多信息到图表
    max_value = np.max(expected_values)
    min_value = np.min(expected_values)
    plt.axhline(y=max_value, color='#F18F01', linestyle=':', alpha=0.8, linewidth=1.5, label=f'Max Expected: {max_value:,.0f}')
    plt.axhline(y=min_value, color='#C73E1D', linestyle=':', alpha=0.8, linewidth=1.5, label=f'Min Expected: {min_value:,.0f}')
    
    # 填充区域
    plt.fill_between(knockout_probs, expected_values, principal, alpha=0.3, color='lightblue')
    
    plt.title('Day002: Knockout Probability vs Structure Note Expected Value', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Knockout Probability', fontsize=14)
    plt.ylabel('Structure Note Theoretical Pricing (Discounted)', fontsize=14)
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, 'ctn_pricing_visualization.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    logging.info(f"图像已保存至: {output_path}")
    print(f"📊 可视化图表已保存: {output_path}")
    plt.show()

# === 生成HTML报告功能 ===
def generate_html_report(knockout_probs, expected_values, principal, V_normal, V_obs, V_knockout):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Credit-Triggered Note Pricing Report</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 40px; 
                line-height: 1.7; 
                background-color: #f8f9fa;
                color: #2c3e50;
            }}
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            h1 {{ 
                color: #2c3e50; 
                border-bottom: 4px solid #3498db; 
                padding-bottom: 15px; 
                margin-bottom: 30px;
                font-size: 2.2em;
            }}
            h2 {{ 
                color: #34495e; 
                margin-top: 35px; 
                font-size: 1.5em;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }}
            .summary-box {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px; 
                border-radius: 10px; 
                margin: 25px 0; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .value {{ 
                font-weight: bold; 
                color: #e74c3c; 
                font-size: 1.1em;
            }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin: 25px 0; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            th, td {{ 
                padding: 15px; 
                text-align: left; 
            }}
            th {{ 
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white; 
                font-weight: 600;
            }}
            tr:nth-child(even) {{ 
                background-color: #f8f9fa; 
            }}
            tr:hover {{ 
                background-color: #e8f4f8; 
            }}
            .chart-container {{ 
                text-align: center; 
                margin: 40px 0; 
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
            }}
            .footer {{ 
                margin-top: 50px; 
                padding-top: 20px; 
                border-top: 2px solid #bdc3c7; 
                color: #7f8c8d; 
                text-align: center;
            }}
            .highlight {{ 
                background-color: #fff3cd; 
                padding: 15px; 
                border-radius: 5px; 
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
            .metric {{ 
                display: inline-block; 
                margin: 10px; 
                padding: 15px; 
                background: white; 
                border-radius: 8px; 
                text-align: center; 
                min-width: 150px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏦 信用触发式票据定价报告</h1>
            <p><strong>📅 生成时间:</strong> {current_time}</p>
            <p><strong>🏷️ 模型版本:</strong> Structured-1400 Day002</p>
            
            <div class="summary-box">
                <h2 style="color: white; border: none; margin-top: 0;">📊 核心参数总结</h2>
                <div style="display: flex; flex-wrap: wrap; justify-content: space-around;">
                    <div class="metric">
                        <div style="font-size: 1.5em; font-weight: bold;">¥{principal:,}</div>
                        <div>投资本金</div>
                    </div>
                    <div class="metric">
                        <div style="font-size: 1.5em; font-weight: bold; color: #27ae60;">¥{V_normal:,.0f}</div>
                        <div>正常路径价值</div>
                    </div>
                    <div class="metric">
                        <div style="font-size: 1.5em; font-weight: bold; color: #f39c12;">¥{V_obs:,.0f}</div>
                        <div>观察期补偿</div>
                    </div>
                    <div class="metric">
                        <div style="font-size: 1.5em; font-weight: bold; color: #e74c3c;">¥{V_knockout:,.0f}</div>
                        <div>敲出赔付价值</div>
                    </div>
                </div>
            </div>

            <h2>📈 敲出概率影响分析</h2>
            <table>
                <tr>
                    <th>敲出概率</th>
                    <th>期望价值 (¥)</th>
                    <th>相对本金收益率</th>
                    <th>风险等级</th>
                </tr>
    """
    
    # 添加关键概率点的数据
    key_probs = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    risk_levels = ["极低", "低", "中低", "中等", "中高", "高"]
    
    for i, prob in enumerate(key_probs):
        idx = int(prob * (len(knockout_probs) - 1))
        if idx < len(expected_values):
            expected_val = expected_values[idx]
            return_rate = (expected_val - principal) / principal * 100
            risk_level = risk_levels[i]
            
            # 根据收益率设置颜色
            color = "#27ae60" if return_rate > 5 else "#f39c12" if return_rate > 0 else "#e74c3c"
            
            html_content += f"""
            <tr>
                <td>{prob:.1%}</td>
                <td style="color: {color}; font-weight: bold;">¥{expected_val:,.2f}</td>
                <td style="color: {color}; font-weight: bold;">{return_rate:+.2f}%</td>
                <td>{risk_level}</td>
            </tr>
            """
    
    # 计算统计信息
    max_expected = np.max(expected_values)
    min_expected = np.min(expected_values)
    avg_expected = np.mean(expected_values)
    
    html_content += f"""
            </table>

            <div class="chart-container">
                <h2>📊 可视化分析图表</h2>
                <img src="ctn_pricing_visualization.png" alt="敲出概率vs期望价值图表" 
                     style="max-width: 100%; height: auto; border: 2px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            </div>

            <h2>📊 统计摘要</h2>
            <div class="highlight">
                <p><strong>📈 最大期望价值:</strong> ¥{max_expected:,.2f} (无敲出情况)</p>
                <p><strong>📉 最小期望价值:</strong> ¥{min_expected:,.2f} (最高敲出概率)</p>
                <p><strong>📊 平均期望价值:</strong> ¥{avg_expected:,.2f}</p>
                <p><strong>🛡️ 下行保护:</strong> {((min_expected/principal - 1) * 100):+.2f}% (相对本金)</p>
                <p><strong>📈 上行潜力:</strong> {((max_expected/principal - 1) * 100):+.2f}% (相对本金)</p>
            </div>

            <h2>💡 投资建议与风险提示</h2>
            <div class="summary-box">
                <h3 style="color: white; margin-top: 0;">✅ 产品优势</h3>
                <ul style="color: white;">
                    <li><strong>下行保护:</strong> 即使在最高敲出概率下，投资者仍能获得 ¥{min_expected:,.0f}，提供本金保护</li>
                    <li><strong>透明机制:</strong> 敲出条件明确，风险可控且可预测</li>
                    <li><strong>流动性管理:</strong> 观察期设计防止套利，提升结构稳定性</li>
                    <li><strong>收益补偿:</strong> 观察期补偿机制确保投资者时间价值</li>
                </ul>
                
                <h3 style="color: white;">⚠️ 风险提示</h3>
                <ul style="color: white;">
                    <li>本产品为结构化投资工具，存在信用风险和市场风险</li>
                    <li>敲出概率受多种因素影响，实际表现可能与预期不符</li>
                    <li>适合具有一定风险承受能力的投资者</li>
                    <li>建议作为投资组合的一部分，不宜集中投资</li>
                </ul>
            </div>

            <h2>🔧 模型参数设置</h2>
            <table>
                <tr><th>参数名称</th><th>当前值</th><th>说明</th></tr>
                <tr><td>年化贴现率</td><td>5.0%</td><td>用于计算现金流现值</td></tr>
                <tr><td>风险溢价</td><td>¥5,000</td><td>敲出时的额外补偿</td></tr>
                <tr><td>观察期</td><td>15天</td><td>初始冻结期，防止套利</td></tr>
                <tr><td>最大赔付比例</td><td>110%</td><td>敲出赔付的上限保护</td></tr>
            </table>

            <div class="footer">
                <p><em>📋 本报告由 Structured-1400 系列 Day002 定价模型自动生成</em></p>
                <p><em>🎓 仅用于教学和研究目的，实际投资决策请咨询专业金融顾问</em></p>
                <p><em>🔬 模型基于理论假设，实际市场表现可能存在差异</em></p>
            </div>
        </div>
    </body>
    </html>
    """

    output_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(output_dir, 'pricing_report.html')
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"HTML报告已生成: {report_path}")
        print(f"📝 HTML报告已生成: {report_path}")
        return True
    except Exception as e:
        logging.error(f"生成HTML报告失败: {str(e)}")
        print(f"❌ 生成HTML报告失败: {str(e)}")
        return False

# === 敏感性分析 ===
def sensitivity_analysis(base_params):
    print("\n🔍 正在进行敏感性分析...")
    
    sensitivity_results = {}
    base_knockout_prob = 0.2  # 固定敲出概率为20%
    
    # 测试不同的年化贴现率
    print("   📊 贴现率敏感性分析...")
    discount_rates = [0.03, 0.04, 0.05, 0.06, 0.07]
    
    for rate in discount_rates:
        test_params = base_params.copy()
        test_params['annual_discount_rate'] = rate
        _, expected_values, _, _, _ = calculate_values(test_params)
        
        idx = int(base_knockout_prob * (len(expected_values) - 1))
        sensitivity_results[f'贴现率{rate:.1%}'] = expected_values[idx]
    
    # 测试不同的风险溢价
    print("   💰 风险溢价敏感性分析...")
    risk_premiums = [3000, 4000, 5000, 6000, 7000]
    
    for premium in risk_premiums:
        test_params = base_params.copy()
        test_params['risk_premium'] = premium
        _, expected_values, _, _, _ = calculate_values(test_params)
        
        idx = int(base_knockout_prob * (len(expected_values) - 1))
        sensitivity_results[f'风险溢价¥{premium:,}'] = expected_values[idx]
    
    print("\n📊 敏感性分析结果 (20%敲出概率下):")
    print("-" * 50)
    for key, value in sensitivity_results.items():
        print(f"  {key}: ¥{value:,.2f}")
    
    return sensitivity_results

# === 主程序入口 ===
def main():
    print("🚀 开始运行信用触发式票据定价模型...")
    print("=" * 60)
    
    try:
        # 获取参数并计算
        params = get_parameters()
        print("📋 参数配置完成")
        
        knockout_probs, expected_values, V_normal, V_obs, V_knockout = calculate_values(params)
        print("🧮 价值计算完成")
        
        # 显示核心结果
        print(f"\n💰 核心计算结果:")
        print(f"  正常路径价值: ¥{V_normal:,.2f}")
        print(f"  观察期补偿:   ¥{V_obs:,.2f}")
        print(f"  敲出赔付价值: ¥{V_knockout:,.2f}")
        
        # 生成可视化
        print(f"\n📊 生成可视化图表...")
        visualize(knockout_probs, expected_values, params['principal'])
        
        # 生成HTML报告
        print(f"📝 生成详细HTML报告...")
        report_success = generate_html_report(knockout_probs, expected_values, params['principal'], V_normal, V_obs, V_knockout)
        
        # 敏感性分析
        sensitivity_results = sensitivity_analysis(params)
        
        print(f"\n🎉 所有任务完成!")
        print("=" * 60)
        print(f"📁 生成的文件:")
        print(f"  📊 ctn_pricing_visualization.png - 可视化图表")
        if report_success:
            print(f"  📝 pricing_report.html - 详细分析报告")
        print(f"  📋 pricing_model.log - 运行日志")
        
        # 快速统计
        max_expected = np.max(expected_values)
        min_expected = np.min(expected_values)
        print(f"\n📈 快速统计:")
        print(f"  最大期望价值: ¥{max_expected:,.2f}")
        print(f"  最小期望价值: ¥{min_expected:,.2f}")
        print(f"  收益保护范围: {((min_expected/params['principal'] - 1) * 100):+.2f}% ~ {((max_expected/params['principal'] - 1) * 100):+.2f}%")
        
    except Exception as e:
        error_msg = f"程序运行出错: {str(e)}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ 程序执行成功! 请查看生成的文件。")
    else:
        print(f"\n❌ 程序执行失败，请检查错误信息。")
