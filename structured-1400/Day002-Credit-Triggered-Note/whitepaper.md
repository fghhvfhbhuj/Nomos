# Whitepaper — Credit-Triggered Redemption Note

## 📘 Project Positioning

This product represents Structure No. 002 (Day002) in the Structured-1400 series, designed as a **credit event-driven contingent redemption structured note**. It combines risk management logic, path contract language, and educational visualization models to simulate the complete process from structural conceptualization to model pricing of derivatives.

**Model Technical Upgrade**: The latest version adopts a modular architecture, supporting sensitivity analysis, professional-grade visualization, and automated report generation, significantly enhancing the model's practicality and educational value.

---

## 🎯 Core Structural Design Philosophy

* Utilizing "observation period + risk control trigger + capped payout" mechanisms to achieve **structured repackaging of high-risk underlyings**
* Embedding "insurance-type payouts" into the structure path, enabling the structured note to **automatically respond to credit deterioration events**
* Leveraging the **law of large numbers** to control expected payouts, achieving positive returns through structural average returns
* **New addition**: Multi-level risk management and real-time sensitivity monitoring

---

## 🧱 Structural Path Logic

### 1. Investment Path Structure

* After initial principal investment, the structure enters an observation period (default 15 days)
* Funds are frozen during the observation period, ultimately releasing discount compensation (similar to zero-coupon bond discounting)
* If no knock-out is triggered during the observation period, the structure transitions to the main path, generating periodic coupon cash flows
* If knock-out is triggered, the structure terminates and pays "future discounted cash flows + premium"

**Calculation Example** (based on current model):
- Observation period compensation: ¥205.69
- Normal path total value: ¥104,816.22
- Knock-out redemption value: ¥109,816.22

### 2. Knock-Out Mechanism Design

* Utilizes a replaceable credit scoring function `risk_score_func()` to determine knock-out conditions
* Default scoring rules as follows:

  $$
  \text{Score} = w_1 \cdot \text{Interest Coverage Ratio} + w_2 \cdot \text{Current Ratio} + w_3 \cdot \text{Credit Rating Score} + w_4 \cdot \text{Market Value/Par Value Ratio}
  $$
* Three consecutive days below the score threshold (default 50 points) triggers knock-out
* **Enhanced functionality**: Support for machine learning models and anomaly detection algorithms

### 3. Payout Cap Logic

* Knock-out payout amount = All remaining discounted cash flows + premium π
* Configurable cap ratio (default not exceeding 110% of note price) to control maximum loss
* **Risk control**: Multiple safety mechanisms ensure payout reasonability

---

## 💰 Profit Structure and Pricing Logic

The structure price consists of the following two components:

$$
P = V_{\text{Normal Discounting}} + \pi
$$

Where:

* $V_{\text{Normal Discounting}}$: Total discounted cash flow value under normal return path (¥104,816.22)
* $\pi$: Credit risk premium (i.e., "premium", default ¥5,000), used to cover expected payouts

The issuer's profit model satisfies:

$$
\pi > \mathbb{E}[\text{Payout Cost}] \quad \Rightarrow \quad \text{Structural System Profit > 0}
$$

**Sensitivity Analysis**: The model automatically tests profit stability under different parameter combinations.

---

## 🔄 Interchangeable Module Design

To accommodate teaching, simulation, and actual model deployment, this structure supports the following module replacements:

| Module | File | Description | New Features |
|--------|------|-------------|--------------|
| Credit Scoring Function | `risk_score_func_demo.py` | Replaceable with any risk control scoring logic | Supports ML models and anomaly detection |
| Knock-Out Judgment Strategy | Conditional logic in `pricing_model.py` | Can be modified to output AI model risk levels | Dynamic parameter configuration |
| Payout Path | Knock-out path branch in `pricing_model.py` | Can be set to multi-level payouts (mild/severe) | Cap mechanism optimization |
| Parameter Settings | Constants area in `pricing_model.py` | Premium π, discount rate r, etc. can be modified | Modular parameter management |
| Report Generation | New HTML report functionality | Automatically generates professional analysis reports | Completely new addition |

---

## 📈 Model Visualization and Path Simulation

* The structural pricing model provides knock-out probability $p$ and expected value function graphs:

  $$
  \text{Expected Value} = (1 - p) \cdot V_{\text{Normal}} + p \cdot V_{\text{Knock-out}}
  $$

* **Professional Visualization**: High-quality chart generation, including statistical information and risk interval annotations
* **Interactive Reports**: Detailed analysis reports in HTML format, including:
  - Core parameter summary
  - Knock-out probability impact analysis
  - Statistical summary and risk indicators
  - Investment recommendations and risk alerts
* **Sensitivity Analysis**: Automatic testing of the impact of key parameter changes on structure value

---

## 📦 Project Extension Directions

* The scoring function can be connected to real-time quotations, corporate financial reports, or natural language processing (NLP) modules
* "Credit improvement reward clauses" or "termination and reissuance mechanisms" can be added to the structure
* Can be combined with on-chain smart contract systems to achieve transparency in structural contracts and risk control scoring
* **New Directions**: Machine learning enhancement, professional reporting systems, multi-asset portfolio optimization

---

## 🧠 Conclusion

This structured note aims to demonstrate how structural language can be used to implement automatic responses and risk control for complex credit events.
It is not just a product, but a prototype of a structural design language that can be nested, evolved, simulated, and deployed.

**Technical Achievement**: Through modular design and professional implementation, this project has achieved dual standards for financial engineering education and practical application.

> Structured-1400 · Day002 Product  
> Construction Objective: Credit Event Structural Response Prototype + Premium-Driven Risk System  
> Authors: User / GitHub Copilot Joint Structural Engineers
