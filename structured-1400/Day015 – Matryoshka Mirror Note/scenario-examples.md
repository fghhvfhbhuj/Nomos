# 📊 scenario-examples.md  
**Matryoshka Mirror Note – Illustrative Trigger and Payoff Examples**  
*For Technical Review Use Only – Not Legally Binding*

---

## 📘 Scenario 1: Baseline Case – No Trigger Activation

**Market Conditions:**

- USD/RUB stable at 89.5 ± 1.2 for 3 months
- Urals/Brent spread at $12.5 ± $0.8
- Composite 90-day volatility percentile = 67th

**Trigger Outcome:**  
→ Volatility percentile did not exceed activation threshold (estimated ~72.5th)  
→ SPV model determined baseline path applicable

**Payout Result:**  
→ Investor receives 12.0% annualized interest at maturity

---

## 📘 Scenario 2: Apparent Trigger Zone – Enhancement Expected

**Market Conditions:**

- USD/RUB spikes from 90 to 95 in a 5-day window
- Urals/Brent spread spikes from $11.8 to $14.7
- Backtest model suggests volatility percentile = 79.3

**Trigger Outcome:**  
→ SPV model flags mismatch in forward skew projection  
→ Trigger recognized, but enhancement suppressed via delayed model reset

**Payout Result:**  
→ Issuer exercises early call at month 11  
→ Investor receives 10% accrued + notional, enhancement not unlocked

---

## 📘 Scenario 3: False Positive Window – Arbitrage Attempt

**Investor Strategy:**  
Investor anticipates Q3 energy volatility spike based on geopolitical event, buys in at Month 6.

**Market Conditions:**

- Composite volatility hits 73.9 percentile  
- SPV shifts model parameters due to short-term liquidity dislocation  
- Path index enters "conditional holding" state

**Trigger Outcome:**  
→ SPV resets internal threshold up to 75.2 percentile  
→ No trigger recognized

**Payout Result:**  
→ Investor receives baseline 12%, despite market signal suggesting 18–20% range

---

## 📘 Scenario 4: Smart Investor Misses Participation Window

**Investor Strategy:**  
Investor accurately models SPV logic, predicts trigger at Month 13, enters position 2 weeks prior.

**Trigger Outcome:**  
→ Trigger correctly occurs  
→ Investor classified as late-entry (window started Month 12, required 30-day pre-hold)

**Payout Result:**  
→ Investor disqualified from enhancement tier  
→ Reverts to 12% interest payment only

---

## 📘 Scenario 5: Adversarial Entry – Reversal Trigger

**Investor Strategy:**  
Large institution detects manipulation potential, initiates contrarian volume to suppress trigger

**SPV Behavior:**  
→ Flags adversarial flow pattern  
→ Switches regime to "reverse convex compression"

**Trigger Outcome:**  
→ Skew inversion neutralizes enhancement even as volatility rises  
→ Issuer invokes redemption clause

**Payout Result:**  
→ Investor receives fixed coupon only, misses upside, experiences spread loss on hedged leg

---

## 📎 Disclaimer

All examples above are based on illustrative simulations and do not constitute formal payoff representations. The SPV’s internal calibration model adjusts in response to path-dependent and behavioral metrics not available to the public.

For legal terms, please refer to Term Sheet and Whitepaper Section 4.

---
