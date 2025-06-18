# 📄 Structure No.19: Forbidden Loop Note (Whitepaper)

## 🧠 Product Design Rationale

In the Chinese mainland financial market, the set of available derivatives is limited and strictly regulated. This creates a natural structural boundary that can be exploited to build products with **asymmetric pricing advantages**. The core idea of this note is:

> **Construct a theoretical arbitrage path embedded in the product's structure that depends on a financial instrument explicitly forbidden by regulation—thus achieving de facto no-arbitrage, while legally allowing non-risk-neutral pricing.**

As Day 19 of the Structure1400 project, this product explores "regulatory embedded arbitrage interruption" as a design principle, contributing to the development of a structured finance language framework with provable non-replicability.

---

## 🔧 Derivative Tool Set \( \mathcal{D}_{10} \)

Ten representative instruments currently available in China's domestic derivatives market are selected to form the replication space:

| ID | Instrument | Expression Level | Description |
|----|------------|------------------|-------------|
| D1 | Vanilla Call/Put | 1 | Exchange-traded options (ETF/Index) |
| D2 | Digital Option | 1 | One-touch options, OTC by banks |
| D3 | Barrier Option | 1 | Knock-in/Knock-out, OTC structures |
| D4 | Autocallable | 2 | Callable structured note, early redemption |
| D5 | Lookback Option | 2 | Path-dependent minimum/maximum payoff |
| D6 | Asian Option | 2 | Average price option, commodity-linked |
| D7 | Interest Rate Swap (IRS) | 1 | Interbank rates market instrument |
| D8 | CMS Coupon | 2 | Coupon linked to CMS rate spread |
| D9 | Callable Bond | 2 | Fixed income early redemption structure |
| D10 | Equity Index Option | 1 | Standardized index option (e.g. CSI 300) |

Defined tool set expression power: \( \text{ExprLevel}(\mathcal{D}_{10}) = 2 \)

---

## 🎯 Target Structure Function \( V \)

The structure’s payoff function is defined as:

\[
V(S, \sigma) = \mathbb{1}_{\{\sup S_t > K_1\}} \cdot \mathbb{1}_{\{\sup \sigma_t > \theta\}} \cdot \text{LookbackCall}(S)
\]

Where:
- \( \mathbb{1}_{\{\sup S_t > K_1\}} \): price barrier trigger (path-dependent)
- \( \mathbb{1}_{\{\sup \sigma_t > \theta\}} \): volatility surface jump trigger
- \( \text{LookbackCall}(S) \): call option on the path minimum

This is a **Lookback-on-Digital-on-Volatility** structure with nested logic.

Expression depth: \( \text{ExprLevel}(V) = 3+ \)

---

## ❌ Non-Replicability Proof

The tool set \( \mathcal{D}_{10} \) spans a structural space:

\[
\mathcal{R}_{10} = \text{span}_{\text{linear}}\left\{ D_1, D_2, \dots, D_{10} \right\}, \text{ with } \text{ExprLevel} \leq 2
\]

Since \( \text{ExprLevel}(V) > \text{ExprLevel}(\mathcal{R}_{10}) \), it follows:

\[
V \notin \mathcal{R}_{10}
\]

\( \blacksquare \) Q.E.D.

---

## 🔒 Arbitrage Path Interruption via Regulatory Constraints

Theoretical arbitrage path:

\[
\text{Sell}(V) \to \text{Buy Option-on-Digital} \to \text{Hedge via vol-surface triggers} \to \text{Construct Lookback hedge}
\]

But the core node "Option-on-Digital-on-Volatility" is:
- ❌ Untradable
- ❌ Unhedgeable in practice
- ❌ Forbidden by Chinese regulations
- ❌ Not recognized in OTC clearing standards

Hence, the arbitrage path cannot be executed in any legal or practical manner.

---

## 📘 Suggested Risk Disclosure (Term Sheet Language)

> The structure’s payoff is designed based on theoretically replicable arbitrage paths, but the replication chain includes financial instruments that are **explicitly prohibited or unavailable** in the Chinese domestic market.

> Therefore, this product is considered **non-replicable in practice**, and **risk-neutral pricing assumptions are not required**. Despite theoretical arbitrage, **no operational arbitrage opportunity exists**, making the structure valid under market no-arbitrage conditions.

---

## 📈 Future Extensions

- 📊 Build a replicability testing engine (Python-based)
- 🔬 Implement an expression-depth detector for auditing structured products
- 🧩 Register this structure as a "non-replicable module" in the RFPM system
- 🏦 Apply the design to construct sell-side structures with embedded pricing power

---

## ✅ Conclusion

Structure No.19: **Forbidden Loop Note** uses **regulatory arbitrage barriers** and **expression-depth proof of non-replicability** to create a robust structured product that cannot be replicated using any combination of 10 known legal instruments in China. This design establishes a new paradigm for **legally-controlled asymmetric pricing**, ideal for sell-side structuring in markets with regulatory tool constraints.

