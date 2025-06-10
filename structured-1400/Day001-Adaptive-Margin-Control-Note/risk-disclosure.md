# Risk Disclosure — Adaptive Margin-Control Note

---

## 1. Product Risk Level Assessment

- This product is a structured derivative involving leverage mechanisms, classified as a high-risk financial instrument.
- Suitable only for qualified investors with professional investment experience and risk tolerance.
- Investors should independently decide whether to participate after fully understanding the product mechanism and risks.

---

## 2. Key Risk Types

### 1. Market Risk
- Price fluctuations of the underlying asset may cause significant equity volatility.
- If prices drop sharply, causing equity to fall below the maintenance margin line, and the fund pool cannot replenish, forced termination may occur, potentially leading to severe principal losses.

### 2. Leverage Risk
- The product introduces high leverage (e.g., 10x) through structured positions, amplifying the impact of market fluctuations on principal.
- Minor market changes can result in significant gains or losses, especially during sudden volatility shifts.

### 3. Fund Pool Dependency Risk
- The product's risk-buffering capability relies on the "protection fund pool" generated after knock-in events.
- If knock-in is not triggered or the pool is insufficient, the ability to replenish margins is lost, increasing forced liquidation risk.

### 4. Operational Errors and Delay Risk
- If clients do not set up automatic margin replenishment mechanisms, manual operations are required to inject funds into the pool.
- Execution delays, errors, or system issues may lead to replenishment failure, triggering forced liquidation.

### 5. Tail Risk and Extreme Market Events
- The product employs an enhanced risk model, including jump diffusion processes and stochastic volatility simulations, to better assess the impact of extreme market events.
- Jump Risk: Sudden market events may cause abrupt price changes, leading to margin insufficiency and forced liquidation. The model anticipates five jumps per year, with an average jump size of -1% and a standard deviation of 3%.
- Volatility Clustering: During turbulent periods, high volatility tends to persist and may intensify further. The stochastic volatility model (mean reversion speed 3.0, long-term mean 20%, volatility of volatility 30%) captures this phenomenon.
- Conditional Value at Risk (CVaR): Model calculations indicate that in the worst 5% of cases, average losses may reach -38.78%. Refer to pricing results for CVaR metrics.
- Maximum Drawdown Risk: During the investment period, the product may experience significant temporary losses (average maximum drawdown of 27.64%), even if final returns are positive.

### 6. Risk Management Recommendations
Based on enhanced model analysis, we recommend investors:
1. Set risk alerts: Establish multi-level alert thresholds based on equity changes, not limited to the maintenance margin line.
2. Prepare additional funds: In addition to initial investments, prepare extra funds equivalent to 10-20% of the principal to address potential replenishment needs.
3. Monitor volatility changes: Regularly observe market volatility levels and remain vigilant during significant volatility increases.
4. Develop fund pool usage strategies: Pre-determine how to utilize the fund pool under different market scenarios to avoid emotional decisions under market pressure.
5. Set stop-loss levels: Despite built-in risk controls, investors should consider setting personal maximum loss levels.

### 7. Risk Indicator Interpretation
The product pricing model provides the following key risk indicators, which investors should understand:

| Risk Indicator | Explanation | Application | Current Value |
|----------------|-------------|-------------|---------------|
| 95% VaR       | Maximum potential loss at 95% confidence level | Assess risk exposure under general market conditions | -32.38% |
| 99% VaR       | Maximum potential loss at 99% confidence level | Assess risk exposure under extreme market conditions | -42.74% |
| CVaR/Expected Loss | Average loss beyond VaR | Understand the severity of tail risks | -38.78% |
| Average Maximum Drawdown | Potential maximum temporary loss during the investment period | Assess psychological pressure during holding | 27.64% |
| Knock-In Probability | Likelihood of triggering yield cap mechanism | Understand the probability of achieving maximum returns | 33.43% |
| Forced Liquidation Probability | Likelihood of triggering forced liquidation | Assess risk of premature termination | 0% |

### 8. Volatility Sensitivity
Product performance is highly sensitive to market volatility. Sensitivity analysis indicates:
- As volatility increases, knock-in probability rises, but forced liquidation risk also increases.
- Moderate volatility environments (15%-25%) are typically optimal for product performance.
- Extremely high volatility environments (>35%) may reduce the effectiveness of the fund pool mechanism.
- Sudden volatility changes may lead to margin insufficiency, even if price movements appear mild.

Investors should regularly review the latest volatility sensitivity analysis results to understand the potential impact of current market conditions on the product.

---

## 3. Disclaimer and Scope of Application

- This product is a structured financial instrument example, currently designed for simulation purposes only, intended for education, modeling, and structural development demonstrations.
- It does not constitute any sales advice, guaranteed returns, or investment recommendations.
- If used for market issuance, compliance reviews, risk assessments, legal document preparation, and regulatory filings should be conducted by licensed financial institutions.

---

**Invest at your own risk. Exercise caution.**


