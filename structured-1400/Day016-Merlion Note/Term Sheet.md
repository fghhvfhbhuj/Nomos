# 📃 Term Sheet – Merlion Adaptive Return Note v2

---

## 1. Product Summary

**Name**: Merlion Adaptive Return Note v2  
**Issuer**: [Private SPV – Singapore Registered]  
**Type**: Principal-Protected Structured Note with Conditional Volatility Overlay  
**Eligibility**: Accredited Investors only (SFA Section 275)  
**Currency**: SGD  
**Tenor**: 18 months  
**Status**: Private Placement (Non-Prospectus Exempted Issue)

---

## 2. Investment Objective

The Note aims to provide capital preservation while offering contingent returns linked to volatility-adjusted market indicators and systemic signal deviations. The structure is designed to adapt its return profile based on proxy-observed macro-market stress environments.

---

## 3. Key Components

| Component | Description |
|----------|-------------|
| **Volatility Index** | Custom REIT-based realized volatility composite |
| **Systemic Signal Index (FGEI)** | Proprietary governance-linked risk proxy |
| **Overlay Structure** | Triggered payout curve shift based on systemic regime classification |

---

## 4. Return Structure

**At Maturity**:

### math
VR = {
    0,                             if FGEI < K₁
    X₁ × (REITvol - σ₀),           if K₁ ≤ FGEI < K₂
    X₂ × (REITvol + FGEI offset),  if FGEI ≥ K₂
}
Principal: 100% Guaranteed

Return Range: 0–25% depending on volatility regime

No coupon, no interim payments

### 5. Redemption Conditions
Callable: Issuer may redeem after 12 months with market-adjusted compensation

Investor Exit: Redemption allowed if FGEI exceeds 3σ threshold for 5 consecutive days

### 6. Risk Factors Summary
Event-volatility driven structure may result in unpredictable return curves

FGEI index is a modeled proxy and may diverge from observable market stress

Discontinuous trigger zones may introduce nonlinear return gradients

For detailed risk statement, see risk-disclosure.md.

### 7. Disclosure & Use
This Note is intended solely for accredited investors under SFA Section 275. Not for public distribution. Full modeling details are available upon request under NDA.

8. Issuer Note
The product design includes conditional paths of behavior that may not be fully representable by classic delta/gamma models. Investors should interpret structural returns within the context of regime-based payout logic