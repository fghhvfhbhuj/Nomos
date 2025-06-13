# Internal Strategy Note – Merlion Adaptive Return Note v2

## 📌 Structure Code
`Structure1400-Day016-MerlionNote-v2`

## 🎯 Strategic Objective
To create a capital-preserving, volatility-linked product with embedded regulatory arbitrage behavior. The structure is designed to simulate a market-compliant instrument while embedding a latent conditional payout that exploits predictable policy-triggered mispricings in the Singapore financial market.

The primary goal is to design a system that:
- Remains undetected by regulatory signal models during normal operation;
- Triggers structured profit exposure upon MAS-aligned intervention signals;
- Simultaneously activates the paired Hydra structure for asymmetric market advantage.

---

## ⚙️ Structural Architecture

### 1. Core Product (`Merlion Shield`)
- Type: Principal-Protected Volatility Note
- Underlying: SGX REIT Vol Index (customized), SGD short-rate spread proxy
- Payout: Tiered structure activated by FGEI index value at maturity
- Features: Callable, with path-dependent overlay

### 2. Linked Structure (`Hydra Fang`)
- Type: Trigger Event Option (Non-linear derivative structure)
- Activation: Triggered if `FGEI > K₂`
- Function: Initiates payout engine tied to short REIT volatility and directional short exposure

---

## 🧪 Trigger System

### Event Proxy: FGEI (Financial Governance Event Index)
Defined as:

### math
FGEI = α * vol_CDS + β * skew_IR + γ * Δspread_policy
Where:

vol_CDS: 5-day realized vol of iTraxx Singapore financials

skew_IR: implied skew of 1M–3M SGD rate caps

Δspread_policy: deviation between SIBOR/CNH forward-implied spread vs realized forward basis

Thresholds:

K₁ = 0.7 (mild stress)

K₂ = 1.2 (regulatory stress zone)

### 💥 Pricing Logic Summary
// ...existing code...
### 💥 Pricing Logic Summary

$$
VR = 
\begin{cases}
0 & \text{if } FGEI < K_1 \\
\lambda_1 \cdot (REITvol - \sigma_0) & \text{if } K_1 \leq FGEI < K_2 \\
\lambda_2 \cdot (REITvol + FGEI_{offset}) & \text{if } FGEI \geq K_2
\end{cases}
$$

Assumptions:

REITvol baseline σ₀ = 12.5%

λ₁ = 3.0, λ₂ = 5.5
// ...existing code...


### 🧬 Intentional Non-Martingality Window
Between T = [t₁, t₂] (~Policy Week / SG liquidity reform rumors), the model intentionally shifts to a path-dependent, non-martingale overlay via conditional event expectation shift. This window provides structured deviation from risk-neutral equilibrium enabling statistical arbitrage through Hydra Fang.

### 🧠 Risk Disclosure Preparation Notes
Use dual-path phrasing for FGEI (e.g., "governance-linked volatility proxy")

Do not define Δspread_policy explicitly in public documents

Avoid all references to “regulatory arbitrage” or “latent exploit”

Label trigger band as “systemic deviation zones” in white paper

### 📚 Reference Models
Implied vol proxy: SGX REIT skew basket via bootstrapped caplet inversion

Jump proxy: modeled as Lévy perturbation over vol path

Market stress replication: 2018 MAS warning, 2023 SORA shock

### 🔚 Expected Use
Internal only. Foundation for:

Term Sheet section 2–3

Risk Disclosure paragraph 2–4

Modeling notebook pricing_model.py