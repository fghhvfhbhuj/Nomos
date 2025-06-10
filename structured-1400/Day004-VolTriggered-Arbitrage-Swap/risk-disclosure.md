# Derivative Structure Day004 Risk Disclosure Statement

This document systematically outlines the main risk categories, specific causes, mitigation strategies, and sensitivity analyses that may be encountered in the design, execution, and trading process of this structured derivative. It aims to ensure that investors and institutional users have a clear and comprehensive awareness of potential risks when using this product.

---

## I. Market Risk

### 1️⃣ Exchange Rate Volatility Risk

* **Description**: Although geometric Brownian motion of exchange rates tends to exhibit mean reversion, rates may still deviate significantly due to geopolitical events, economic policies, and other unexpected factors.
* **Mitigation**:
  * Implementation of a national intervention "resistance term" $intervention = -0.01 \cdot \tanh(deviation \cdot 10)$ to suppress extreme volatility probability
  * Utilization of GARCH volatility models to more accurately capture volatility clustering effects
  * Calibration of volatility parameters (0.0060 ~ 0.0095) using high-frequency data during design

### 2️⃣ Interest Rate Fluctuation Risk

* **Description**: Interest rate changes directly affect forward exchange rate calculations and currency swap pricing.
* **Mitigation**: Dynamic acquisition of risk-free rates, setting tolerance intervals, or dynamically updating trigger thresholds.
* **Current model interest rates**:
  * USD: 0.0300
  * JPY: 0.0010
  * CNY: 0.0250
  * GBP: 0.0350
  * EUR: 0.0200

### 3️⃣ Arbitrage Yield Risk

* **Description**: Arbitrage yields may rapidly diminish due to market volatility, liquidity changes, and other factors.
* **Mitigation**: Implementation of multi-factor confirmation mechanisms and timely exit through knock-out threshold z = 0.0005.

---

## II. Liquidity Risk

### 1️⃣ Counterparty Risk

* **Description**: If any currency in the swap or path exchange lacks counterparties at a specific point in time, execution will fail.
* **Mitigation**:
  * Establishment of market maker connections and automated quoting mechanisms
  * Use of slippage models to estimate execution difficulty in advance and preset tolerance ranges
  * Prioritization of major currency pairs (USD, JPY, CNY, GBP, EUR) for arbitrage

### 2️⃣ Insufficient Market Depth

* **Description**: Particularly when executing n-angle paths, some minor currencies may have insufficient trading depth, affecting arbitrage feasibility.
* **Mitigation**:
  * Execution limited to highly liquid currency combinations
  * Dynamic filtering of low-feasibility combinations through credit scoring of paths
  * Adjustment of arbitrage margins through fee parameters (fee_per_trade = 0.001)

---

## III. Model Risk

### 1️⃣ GBM Modeling Errors

* **Description**: Geometric Brownian motion only approximates real market behavior and fails particularly during jumps and extreme volatility events.
* **Mitigation**:
  * Correction through the "resistance function" $intervention$
  * Generation of dynamic volatility paths using GARCH(1,1) models
  * Potential future improvements through jump-diffusion process modeling

### 2️⃣ Inappropriate Parameter Settings

* **Description**: Trigger threshold d = 0.002, knock-out threshold z = 0.0005, and simulation path quantity significantly impact performance.
* **Mitigation**:
  * Provision of default trained parameters with customization options and lifecycle management for enterprise users
  * Validation of parameter robustness through 10,000 simulated paths

### 3️⃣ Insufficient Monte Carlo Sampling

* **Description**: Too few sample paths will lead to valuation bias.
* **Mitigation**: Default simulation of over 10,000 iterations, providing error confidence intervals for reference.

---

## IV. Legal & Operational Risk

### 1️⃣ Compliance Risk

* **Description**: Different countries have varying regulations for cross-currency transactions and currency swaps.
* **Mitigation**: Users must comply with local regulations; this product serves only as a structural demonstration, not investment advice.

### 2️⃣ Execution Delay or Failure

* **Description**: If system response lags behind the arbitrage opportunity window, the strategy becomes ineffective.
* **Mitigation**: Implementation of high-frequency real-time monitoring, deployed on nodes close to exchange servers.

### 3️⃣ Data Delay or Error

* **Description**: Delayed or erroneous underlying data will lead to misjudgment of trigger points.
* **Mitigation**: Use of high-quality data sources and backtesting against historical performance.

---

## V. Sensitivity Analysis

| Variable | Impact Direction | Impact Level (High/Medium/Low) | Notes |
| ------ | ----------- | ----------- | ------------- |
| Exchange Rate Volatility | Determines path return distribution | High | Higher volatility more easily triggers arbitrage opportunities |
| Interest Rate Differential | Alters forward exchange rates | Medium | Narrowing differentials compress arbitrage space |
| Fee Changes | Reduces arbitrage feasibility probability | Medium | Per-trade fee is 0.001 |
| N-angle Path Quantity | Increases structural complexity and potential returns | High | Default path length is 4 |
| National Intervention Intensity | Suppresses extreme scenarios | Medium | Implemented through tanh function |

---

## VI. GARCH Volatility Model Related Risks

### 1️⃣ Model Fitting Risk

* **Description**: GARCH parameter estimation may contain errors, leading to inaccurate volatility predictions.
* **Mitigation**: Regular re-estimation of model parameters and validation of model fit using historical data.

### 2️⃣ Model Complexity Risk

* **Description**: Overly complex GARCH models may lead to overfitting.
* **Mitigation**: Adoption of the simpler GARCH(1,1) model, balancing fitting effectiveness and model complexity.

---

## VII. Conclusion

While Day004 derivative structure possesses high controllability and originality in its design, its successful execution heavily depends on market conditions and system deployment efficiency. Users must strictly control model parameters, data quality, and trading interface responsiveness to fully leverage its structural advantages and avoid significant risks.

This risk disclosure statement forms an important component of all portfolio structure documentation and serves as a crucial reference for subsequent structural iterations, simulation testing, and external presentations.

— Derivative Structure Designer
