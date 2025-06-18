# 📘 README — Structure No.19: Forbidden Loop Note

## Overview

**Structure No.19: Forbidden Loop Note** is a theoretical structured product designed as part of the Structure1400 project (Day 19). The product explores a pricing framework that intentionally embeds an arbitrage path which becomes **legally unexecutable** within China’s domestic financial system.

By combining advanced payoff architecture with market regulatory constraints, this note achieves a unique outcome: **pricing without risk-neutral assumptions**, while **still being immune to arbitrage** in practical execution.

---

## Key Features

* ✅ **Nested payoff architecture** (Lookback-on-Digital-on-Volatility)
* ❌ **Non-replicable** using any of the 10 known legal derivative instruments in China
* 🔒 **Arbitrage path interruption** through forbidden financial tool dependencies
* 🧠 **Theoretical arbitrage exists**, but cannot be executed in any regulated or accessible market path
* 📑 **Custom Term Sheet** with compliance-aware design language

---

## Core Mechanism

### Target Payoff Function

$$
V(S, \sigma) = \mathbb{1}_{\{\sup S_t > K_1\}} \cdot \mathbb{1}_{\{\sup \sigma_t > \theta\}} \cdot \text{LookbackCall}(S)
$$

### Triggers:

* **Price Barrier:** Path maximum crosses a fixed strike
* **Volatility Barrier:** Volatility surface crosses threshold $\theta$
* **Final Payoff:** Lookback call on minimum price, conditional on both triggers

### Tool Dependency Set:

* Tool set $\mathcal{D}_{10}$: 10 legal derivatives (vanilla options, digital, barrier, IRS, autocallable, etc.)
* Expression level of $V$: $> 3$; expression level of $\mathcal{D}_{10}$: $\leq 2$
* ⛔ Cannot be replicated by linear or nonlinear combination of legal tools

---

## Non-Replicability Theorem

> Because the payoff structure exceeds the maximum expression depth of China’s legal derivative tools (i.e. requires Option-on-Digital-on-Volatility), it is provably outside the legal replication space.

Thus:

$$
V \notin \text{span}(\mathcal{D}_{10})
$$

⇒ The structure is **theoretically arbitrageable but operationally protected**.

---

## Term Sheet (Highlights)

| Term                 | Value                                                           |
| -------------------- | --------------------------------------------------------------- |
| **Issuer**           | Confidential (via OTC)                                          |
| **Tenor**            | 12 months                                                       |
| **Currency**         | CNY                                                             |
| **Triggers**         | Path barrier $S_t > K_1$, Volatility $\sigma_t > \theta$        |
| **Payoff**           | Lookback Call if dual-triggered, fixed coupon or zero otherwise |
| **Early Redemption** | None                                                            |
| **Secondary Market** | Not available                                                   |
| **Pricing**          | Non-risk-neutral, proprietary framework                         |
| **Arbitrage**        | Disabled via legal constraint trap                              |

---

## Risk Disclosure

> This product contains embedded triggers and payout logic that are **not replicable** under the current Chinese regulatory framework. Replication or arbitrage would require access to financial instruments that are either **legally prohibited** or **market-inaccessible**.

> Therefore, the product is not subject to classical risk-neutral valuation and should be evaluated accordingly.

---

## Project Goals & Applications

* 🧩 Demonstrate **structure-controlled pricing via regulatory constraints**
* 💡 Provide a **template for non-replicable structured notes** under constrained environments
* ⚙️ Serve as a module within the RFPM system for expression-depth classification

---

## Authors & Contact

Created by: **沈翰 (Han Shen)**
Structure1400 Research Project — Day 19
GitHub: [github.com/fghhvfhbhuj/Nomos](https://github.com/fghhvfhbhuj/Nomos)

---

## License

©️ 2025 Structure1400 Research. All rights reserved. For academic and educational use only.

---

**Note:** This document serves as a theoretical and structural demonstration of financial architecture under constrained regulatory settings. It does not represent an offer to sell, nor solicitation to buy any financial instrument.
