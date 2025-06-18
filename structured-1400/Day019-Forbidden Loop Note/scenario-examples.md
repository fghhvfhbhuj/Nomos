# 📊 Scenario Examples — Structure No.19: Forbidden Loop Note

## 🔍 Scenario 1: Passive Retail Investor

**Profile:** Individual client investing in structured notes via private bank, no derivatives trading capability.

**Trigger Path:**

* Equity index (e.g. CSI 300) experiences a brief spike above the predefined barrier $K_1$.
* Market volatility rises sharply following a central bank announcement (exceeds $\theta$).

**Outcome:**

* Both triggers activated → Receives payoff based on Lookback Call.
* Client unaware of embedded arbitrage logic.

**Insight:**
Investor gains exposure to path-dependent upside without realizing product’s defensive pricing design.

---

## 🔍 Scenario 2: Domestic Hedge Fund (Seeking Arbitrage)

**Profile:** Sophisticated investor with access to vanilla/barrier/digital OTC options, but restricted by PRC regulation from using offshore NDFs or volatility derivatives.

**Attempted Strategy:**

* Constructs synthetic hedge using vanilla + digital + barrier legs.
* Attempts dynamic delta-hedging via implied vol proxies.

**Barrier:**

* Cannot simulate or access the Option-on-Digital-on-Volatility structure.
* No legal access to volatility-surface-dependent triggers.

**Outcome:**

* Hedge fails to fully replicate structure.
* Fund either accepts tracking error or withdraws.

**Insight:**
Product survives theoretical arbitrage attempt by leveraging regulatory infeasibility.

---

## 🔍 Scenario 3: Cross-Border SPV Arbitrage Strategy

**Profile:** Offshore entity (Hong Kong-based) attempts to construct synthetic replication via SPV issuing option-on-volatility instruments.

**Approach:**

* SPV sets up in Singapore to issue exotic derivatives.
* Domestic investor seeks cash flow swap to indirectly access foreign tool.

**Constraint:**

* Cross-border derivative linkage violates SAFE rules or CSRC capital controls.
* Domestic counterparty cannot legally clear the required contracts.

**Outcome:**

* Structure considered incomplete.
* Replication collapses at the cash flow transmission level.

**Insight:**
Even international counterparties cannot fully overcome regulatory loop constraints embedded in product.

---

## 🔍 Scenario 4: Sell-Side Structurer Perspective

**Profile:** Bank or trust structurer issuing the Forbidden Loop Note.

**Strategy:**

* Sells product with non-risk-neutral pricing (adds 2–4% internal spread).
* Knows no one can hedge or challenge price via known market instruments.

**Risk Control:**

* Only needs to delta hedge basic components.
* No full replication required due to structural arbitrage shield.

**Insight:**
Issuer benefits from pricing asymmetry and built-in defensibility, especially for capital preservation clients.

---

## Summary Table

| Scenario         | Entity Type      | Can Replicate? | Why Not?                                  | Outcome                 |
| ---------------- | ---------------- | -------------- | ----------------------------------------- | ----------------------- |
| 1. Retail Client | Individual       | ❌              | No tools, no knowledge                    | Receives payoff blindly |
| 2. Domestic Fund | Hedge Fund       | ❌              | Cannot access volatility path trigger     | Cannot hedge fully      |
| 3. Offshore SPV  | Cross-border Arb | ❌              | Cannot transmit cash flow legally         | Replication breaks      |
| 4. Issuer        | Structuring Bank | ✅ (partial)    | Knows how to hedge internal exposure only | Profits from asymmetry  |

---

**Conclusion:**
These scenarios demonstrate how Forbidden Loop Note maintains its structural uniqueness and pricing integrity by embedding a replication trap at the intersection of market tools and regulatory boundaries. The product is therefore viable under strategic distribution but remains fundamentally protected from arbitrage-based pressure.
