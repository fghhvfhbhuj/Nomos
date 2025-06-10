# Adaptive Margin-Control Note

## Term Sheet

### Product Name

Adaptive Margin-Control Note

### Product Type

Structured Derivative Note (Path-Dependent + Embedded Fund Pool + User-Controlled Margin Replenishment)

### Underlying Assets

CSI 300 Index / Gold Futures / Copper Futures (select one, specified in the product details)

### Investment Currency

Chinese Yuan (CNY) / US Dollar (USD)

### Investment Term

12 months (T = 1 year)

### Minimum Investment Amount

¥100,000 (or equivalent in USD)

### Yield Structure

* Underlying asset growth $R_t$ = $(S_t - S_0)/S_0$
* If $R_t < 20%$, linear distribution based on actual growth
* If $R_t \geq 20%$, knock-in is triggered:
  * Yield cap set at 30%
  * Excess beyond 30% is allocated to the Protection Pool

### Knock-In Clause

* Trigger Condition: Cumulative growth of the underlying asset exceeds 20%
* Effect: Automatically activates the yield cap mechanism (30%)
* Excess returns are transferred to the fund pool for subsequent margin replenishment

### Protection Pool Mechanism

* Initially empty
* Excess returns post-knock-in are transferred to the pool
* Clients can choose:
  * No utilization
  * One-time injection into the margin account
  * Partial withdrawal for "lifeline" purposes

### Margin Mechanism and Automatic Replenishment

* Initial margin is 10% of the investment principal
* Maintenance margin line is 5% of the principal
* If account equity falls below the maintenance margin line:
  * The system automatically utilizes the fund pool for margin replenishment
  * If the fund pool is insufficient, replenishment is performed to the maximum extent possible
  * If equity remains below the maintenance line post-replenishment, knock-out is triggered

### Knock-Out Clause

* Trigger Condition: Equity falls below the maintenance margin line and the fund pool is empty
* Effect: Product terminates, remaining equity is returned upon settlement

### User Control Rights

* Users can access the system platform or designated interface to:
  * View fund pool balance
  * Initiate injection requests
  * Configure automatic or manual margin replenishment strategies

### Risk Disclosure (Summary)

* This product is not capital-guaranteed. Based on model analysis, the Value at Risk (VaR) at a 95% confidence level is -32.38%
* In extreme cases, the VaR at a 99% confidence level can reach -42.74%
* Average maximum drawdown is 27.64%, knock-in probability is 33.43%
* Involves leverage mechanisms, futures-based underlying assets, and dynamic fund pool structures
* Investors must possess derivative investment experience and risk tolerance

### Pricing Methodology

* Monte Carlo simulation (10,000 paths) is used to simulate the underlying asset paths
* Jump diffusion model (jump frequency λ=5, average jump size=-1%, standard deviation=3%)
* Combined with stochastic volatility model (mean reversion speed κ=3.0, long-term mean θ=0.2, volatility of volatility ξ=0.3)
* Final yield expectation is calculated as a reference for theoretical issuance price
* Current theoretical value is -1.38 (based on simulation parameters)

### Example Scenarios (Optional Diagrams)

1. Normal growth → Knock-in → Yield cap + Fund pool filled
2. Market reversal → Approaching forced liquidation → Client initiates or automatic margin replenishment
3. Market fluctuation → Final holding until maturity → Settlement based on actual path

### Project Status

Simulation design for structured product demonstration and GitHub project release.
Not a real issuance product, intended for educational and research purposes only.

---

(This Term Sheet can be submitted alongside the whitepaper, pricing model, and risk disclosure.)
