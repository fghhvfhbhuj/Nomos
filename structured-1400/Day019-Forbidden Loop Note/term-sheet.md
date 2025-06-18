## 📑 Term Sheet (Preliminary Draft)

**Issuer:** Confidential — Available on request  
**Product Name:** Forbidden Loop Note (Structure No.29)  
**Underlying Asset:** Equity Index Basket or Synthetic ETF Proxy  
**Notional Amount:** Customizable by client tranche (min. CNY 1,000,000)  
**Currency:** CNY  
**Tenor:** 12 months  
**Participation Rate:** Up to 150% (conditional)  
**Barrier Level:** Sup \( S_t > K_1 \), custom-defined (path-dependent)  
**Volatility Trigger:** Sup \( \sigma_t > \theta \), real-time IV monitoring  
**Payoff Structure:**
- If both triggers are met: Lookback Call on path-minimum strike
- If only one trigger is met: Fixed coupon (e.g., 4–6%)
- If neither is met: Zero or partial capital return, per tranche

**Early Redemption:** None (strictly held to maturity)  
**Liquidity:** Non-transferable, OTC bilateral settlement  
**Secondary Market:** None guaranteed  
**Replication:** Prohibited; structure includes non-replicable payoff mechanics  
**Arbitrage Risk:** None, due to regulatory path interruption  
**Pricing Model:** Proprietary; not based on classical risk-neutral valuation  
**Documentation:** Custom ISDA/CSA annexes, full legal opinion upon request

---

## 📈 Future Extensions

- 📊 Build a replicability testing engine (Python-based)
- 🔬 Implement an expression-depth detector for auditing structured products
- 🧩 Register this structure as a "non-replicable module" in the RFPM system
- 🏦 Apply the design to construct sell-side structures with embedded pricing power

---

## ✅ Conclusion

Structure No.19: **Forbidden Loop Note** uses **regulatory arbitrage barriers** and **expression-depth proof of non-replicability** to create a robust structured product that cannot be replicated using any combination of 10 known legal instruments in China. This design establishes a new paradigm for **legally-controlled asymmetric pricing**, ideal for sell-side structuring in markets with regulatory tool constraints.

