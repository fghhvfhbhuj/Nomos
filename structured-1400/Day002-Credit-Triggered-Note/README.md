# Credit-Triggered Redemption Note

## 📘 Project Overview

This project is part of the Structured-1400 series, specifically the second structured product, designed to create a **credit-event-triggered automatic payout structured note**. It aims to provide an educational, customizable, and visualized demonstration of the complete process of structured financial product design, from logical construction to pricing modeling.

The project adopts a modular design, supports sensitivity analysis, and generates professional-grade reports, making it suitable for financial engineering education, research, and real-world product development.

---

## 📌 Core Structural Logic

* Upon purchasing the structured note, clients enter an **observation period** (default: 15 days). During this period, no returns are accrued, but funds receive **discount compensation** (annualized interest discount) if the structure does not knock out.
* If no knock-out event occurs after the observation period, the structure transitions to the main return path, ultimately delivering principal and agreed returns (including observation period compensation).
* If the **risk-control knock-out mechanism** is triggered at any point, the structure terminates immediately, paying:

$$
\text{Discounted Future Cash Flows} + \text{Credit Risk Premium (Insurance)}
$$

**Latest Model Results:**
- Normal Path Value: ¥104,816.22
- Observation Period Compensation: ¥205.69
- Knock-Out Payout Value: ¥109,816.22

---

## 🧠 Educational Objectives

This project is tailored for learners focusing on structured product design, covering the following objectives:

* Learn how to construct path-triggered structured product logic (observation period + risk-control knock-out + payout structure).
* Understand how to embed **risk management logic** and "anti-arbitrage design" into contracts.
* Demonstrate how to use Python to develop **pricing models and probability sensitivity analysis** for structured notes.
* Provide a pluggable risk-scoring function template for users to customize trigger mechanisms.
* Showcase professional-grade financial modeling and report generation capabilities.

---

## 🗂 File Description

### Core Documents
* `README.md`: Project overview and usage instructions.
* `term-sheet.md`: Structured terms sheet (formal contract language).
* `whitepaper.md`: Design principle whitepaper, including structural logic, model design, and replaceable function structures.
* `scenario-example.md`: Scenario examples: normal maturity / risk-control knock-out paths.

### Code Files
* `pricing_model.py`: **Core Pricing Model**, featuring modular parameter settings, sensitivity analysis, and professional visualization.
* `risk_score_func_demo.py`: Enhanced credit scoring function supporting machine learning and anomaly detection.

### Output Files
* `ctn_pricing_visualization.png`: **High-quality visualization chart** (knock-out probability vs expected value relationship).
* `pricing_report.html`: **Professional analysis report**, including detailed statistics, risk analysis, and investment recommendations.
* `pricing_model.log`: Execution log recording all calculation processes and results.

---

## 🚀 Quick Start

### Run the Pricing Model
```bash
python pricing_model.py
```

### Model Features
- ✅ **Modular Design**: Flexible parameter configuration.
- ✅ **Sensitivity Analysis**: Automatic analysis of key parameter impacts.
- ✅ **Professional Visualization**: High-quality chart generation.
- ✅ **Detailed Reporting**: HTML-format professional analysis reports.
- ✅ **Log Tracking**: Comprehensive execution process tracking.

---

## 🧩 Project Positioning and Usage

This product is intended for education, research, and structured modeling demonstrations, particularly suitable for:

- **Financial Engineering** students' course projects and theses.
- **Quantitative Finance** researchers' product prototype development.
- **Structured Product** design teams' concept validation.
- **Risk Management** departments' stress testing and scenario analysis.

For practical use, it is recommended to integrate with actual risk engines, regulatory frameworks, and legal systems for customized deployment.

---

## 📊 Technical Highlights

* **Mathematical Modeling**: Rigorous pricing framework based on stochastic processes and probability theory.
* **Risk Control**: Multi-layered risk management mechanisms (observation period + knock-out + cap).
* **Visualization Analysis**: Professional-grade charts and interactive reports.
* **Code Quality**: Modular, extensible, and well-documented Python implementation.

---

> This project is part of the Structured-1400 series · Day002 Structured Note  
> Creator: User / GitHub Copilot  
> Type: Structured Note · Credit-Triggered · Risk-Control Knock-Out  
> Applicable Scenarios: Educational Research · Product Prototyping · Risk Modeling
