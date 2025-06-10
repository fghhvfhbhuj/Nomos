# Derivative Structure Day004 Term Sheet

This document serves as the standard term sheet for the Day004 Volatility-Triggered Multi-Leg Arbitrage Currency Swap Structured Derivative, intended for potential buyers, sales teams, and compliance personnel as a formal summary for understanding product structure and liability boundaries.

---

## I. Basic Terms

| Term Item | Description |
| ------ | ----------------------------------- |
| Product Name | Volatility-Triggered Multi-Leg Currency Arbitrage Swap Structure (Day004) |
| Product Type | Structured Derivative / Multi-Currency Arbitrage Product |
| Notional Principal | Customizable |
| Initial Price p | Determined by pricing model output, simulated prices in `pricingresult.csv` |
| Knock-In Condition | Arbitrage yield exceeds knock-in threshold d = 0.002, triggering arbitrage path execution |
| Knock-Out Condition | Expected arbitrage path yield falls below knock-out threshold z = 0.0005, triggering exit |
| Underlying Assets | Foreign exchange currency pairs (currently supporting USD, JPY, CNY, GBP, EUR) |
| Trading Path | n-leg multi-currency circular path (default n = 4, optional) |
| Contract Term | Maximum 30 days after knock-in or until knock-out occurs (whichever comes first) |
| Profit Mechanism | Utilizes multi-currency arbitrage deviation + currency swap to extend arbitrage time |
| Swap Mechanism | After knock-in, user initiates currency swap, locking arbitrage profits at future currency return nodes |

---

## II. Parameter Settings

| Parameter | Meaning | Default Value | Notes |
| ---------- | ----------- | ------ | ----------- |
| d | Knock-in deviation threshold | 0.002 | Knock-in triggered when arbitrage yield exceeds this value |
| z | Knock-out yield lower bound | 0.0005 | Knock-out triggered when arbitrage yield falls below this value |
| n | Currency path length | 4 | Expandable to any valid path |
| τ_max | Maximum arbitrage position holding time (days) | 30 | Avoids long-term position liquidity risk |
| fee_per_trade | Transaction fee per trade | 0.001 | Affects overall arbitrage yield |
| σ_control | Simulation process resistance factor | Adaptive | Suppresses probability of extreme directional changes |

---

## III. Pricing Method (Brief)

* Using Geometric Brownian Motion to simulate currency exchange ratio fluctuation process:
  $dS_t = \mu S_t dt + \sigma S_t dW_t$

* Adding resistance term to control simulation trajectory distribution density, simulating national intervention:
  $\text{drift} = \mu - k \cdot \tanh(deviation \cdot 10)$

* Using Monte Carlo method to simulate 10,000 arbitrage paths, filtering path yields relative to knock-in/knock-out thresholds

---

## IV. Volatility Model

* Basic volatility settings: Volatility for various currency pairs ranges between 0.0060 and 0.0095
* GARCH model enhancement: Option to use GARCH(1,1) model to generate dynamic volatility paths
* Interest rate differential settings: Major currency annual interest rates from 0.0010 (JPY) to 0.0350 (GBP)

---

## V. Risk Disclosure (Summary)

* This product does not guarantee arbitrage opportunities will always exist
* Exchange rate fluctuations and execution delays may lead to arbitrage failure
* If users cannot initiate currency swaps in a timely manner, the arbitrage window may close
* In highly volatile market conditions, this product may remain in cash position for extended periods

For complete risk disclosure, see `risk-disclosure.md`

---

## VI. Suitable Users and Applications

* Advanced investment institutions for demonstrating foreign exchange arbitrage research capabilities
* Corporate internal fund management teams for custom structure design
* Not recommended for direct participation by retail investors

---

## VII. Associated Documentation

| Filename | Function Description |
| ------------------- | --------------- |
| `README.md` | Overview file, describing background and logical structure |
| `whitepaper.md` | Whitepaper, comprehensive introduction to design motivation and theory |
| `trigger-engine.md` | Trigger logic and parameter settings |
| `risk-disclosure.md` | Risk disclosure document |
| `pricing_model.py` | Python main pricing model |
| `pricingresult.csv` | Simulated price output |
| `simulation_charts/` | Path simulation image output folder |

---

## VIII. Copyright and Usage Restrictions

This structure is the author's original design, intended only to demonstrate derivative structure construction and financial engineering capabilities, not as investment advice or sales material.
