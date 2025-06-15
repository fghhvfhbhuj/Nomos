# 📄 Term Sheet – Stoa Note (Structure No.18)

**Product Name:** Stoa Note
**Structure ID:** SN-18
**Type:** Anchored Friction Derivative
**Issuer:** \[To be determined – demo structure]
**Designer:** Shen Han

---

## 🔧 Underlying

* **Effective Fee Index (EFI):** Aggregated index of market execution costs including gas fees, slippage, and platform transaction charges.
* **Anchoring Variable:** External real-world benchmark (e.g., ETH gas base fee, multi-exchange liquidity depth index)
* **Anchoring Sensitivity (λ):** 0.65 (configurable)
* **Adjusted Fee Index (f\_adj):** `EFI - λ × Anchor`

---

## 🧮 Payout Function

Let `μ` be the payout center, `ε` the friction band, `δ` the compression offset:

```math
P(f_adj) =
    α₁ · (f_adj - μ - ε - δ), if f_adj > μ + ε + δ
    α₂ · (μ - f_adj - ε - δ), if f_adj < μ - ε - δ
    0, otherwise
```

* **Recommended Values:**

  * μ = 0.22%
  * ε = 0.05%
  * δ = 0.01%
  * α₁ = 12x, α₂ = 8x (example asymmetry)

---

## 📅 Term

* **Tenor:** 7 days (renewable)
* **Settlement:** ETH or USDT cash-settled
* **Valuation Frequency:** Daily close + on-demand spike detection

---

## 🔐 Embedded Protections

* **Zone Compression:** f\_adj must exceed μ ± (ε + δ) to trigger payout
* **Anti-Arbitrage:** Requires minimum notional > \$5000 and 4h smoothing window
* **Mirror Note Pairing:** Optional twin structure for full risk neutrality

---

## 🧠 Use Case Profiles

* Market makers hedging gas and slippage risk
* Fee arbitrage traders seeking edge across platforms
* DAO treasury risk overlays tied to execution costs
* ESG/climate applications using weather or social friction proxies

---

## 📜 Legal Notes

* This structure is experimental and not a registered security or regulated derivative.
* Use is restricted to simulated environments unless proper jurisdictional compliance is obtained.

---

## Contact

Designed by **Shen Han**

🔗 GitHub: [fghhvfhbhuj/Nomos](https://github.com/fghhvfhbhuj/Nomos)
