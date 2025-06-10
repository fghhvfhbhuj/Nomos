# Day004: Volatility-Triggered Multi-Currency Arbitrage and Swap Extension Structure

This structured product is the fourth in the Structured-1400 series. It is a conditional-triggered structured derivative that monitors arbitrage opportunities based on "Volatility Triggered" mechanisms. By combining multi-currency path arbitrage and currency swap techniques, it extends the timing of arbitrage opportunities.

---

## 🔧 Structural Overview

* **Trigger Indicator**: Arbitrage yield volatility.
* **Knock-In Mechanism**: Automatically knocks in when arbitrage yield exceeds the threshold `d = 0.002`.
* **Execution Structure**: Select `n` currencies for closed-loop arbitrage (e.g., USD → JPY → CNY → GBP → USD).
* **Currency Swap Mechanism**: Extends arbitrage positions' timing and manages risks through currency swaps.
* **Knock-Out Mechanism**: Automatically knocks out when arbitrage yield compresses below the threshold `z = 0.0005`.
* **Pricing Simulation**: Monte Carlo path simulation based on Geometric Brownian Motion (GBM) with "national intervention resistance terms."

---

## 💰 Pricing Logic

The arbitrage space is represented by the following multiplicative path model:

$$
A(t) = \left(\prod S_{i \to i+1}(t) \right) \times (1 - \delta)^n - 1
$$

Where:

* $S_{i \to i+1}(t)$: Spot exchange rate for currency pair `i`.
* $\delta$: Transaction fee rate per jump, default is 0.001.
* $n$: Number of currencies in the arbitrage path, default is 4.

When $A(t) > d$, arbitrage is triggered; when $A(t) < z$, arbitrage opportunities are considered compressed, triggering knock-out.

---

## 🔁 Execution Conditions

This structure assumes the final executor possesses the following capabilities:

* Signed ISDA Master Agreement (qualified for currency swaps).
* Real-time access to FX execution platforms (e.g., Bloomberg FXGO, Refinitiv, EBS, Citadel).
* Automated infrastructure for exchange rate trading and swap execution.

Upon meeting arbitrage conditions, the product swiftly executes currency exchanges and swaps through pre-set paths, achieving arbitrage and delayed settlement.

---

## 🧠 Optimization Space Design

This structure supports intelligent optimization extensions:

1. **Multi-Factor Trigger Learning Mechanism**: Introduce multiple indicators such as volatility, interest rate spreads, and liquidity, using weighted learning to determine comprehensive trigger weights.
2. **Parameter Lifecycle Management**: Set finite validity periods for historical training results to avoid outdated market states affecting current models.
3. **Market Rolling Retraining**: Periodically update parameters based on rolling windows to enhance model robustness.
4. **Intelligent Arbitrage Path Selection**: Future versions may incorporate GARCH volatility models and RL algorithms to dynamically optimize arbitrage currency paths.

---

## 📁 Project File Structure

* `whitepaper.md`: Explanation of structural logic, motivations, and theoretical assumptions.
* `risk-disclosure.md`: Risk terms and extreme market scenario descriptions.
* `pricing_model.py`: Main pricing simulation program (automatically generates CSV and charts).
* `simulation_charts/`: Path image output directory.
* `trigger-engine.md`: Explanation of knock-in and knock-out mechanism principles.
* `pricingresult.csv`: Simulated output yield data (automatically generated).

---

© 2025 Structured-1400 Series
