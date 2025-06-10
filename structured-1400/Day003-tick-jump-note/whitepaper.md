# Whitepaper

## Day003 - Tick Jump Triggered Note

---

## 1. Product Background and Design Motivation

In actual trading, market price movements are not continuous but rather constitute a jump process composed of minimum price units (ticks).  
For leveraged users, these jumps may **directly breach the liquidation threshold**, causing substantial losses through "jump liquidation" even when users might still have margin call opportunities in a continuous model.

This structure uses this as a trigger basis, designing a **structured insurance note targeting inherent market mechanism deficiencies**, specifically to counter non-continuous price risks at the tick level.

---

## 2. Product Structure and Logical Definition

### 2.1 Basic Product Structure

| Item | Description |
|------|-------------|
| Product Type | Discontinuous Volatility Structured Insurance Note |
| Structure Price | `p` (one-time insurance premium paid by the user) |
| Payout Amount | `a` (one-time payout upon satisfaction of trigger conditions) |
| Contract Term | `T` (typically 1-12 months) |
| Knock-In Condition | User's purchase of the structured product is considered knock-in |
| Knock-Out Condition | Satisfaction of the tick jump mechanism triggering liquidation |

---

### 2.2 Trigger Logic Explanation

The knock-out condition is defined as the simultaneous satisfaction of the following three criteria:

1. The underlying asset experiences a continuous decline of `t` ticks;
2. At the `t-1` tick, the user's equity has not crossed the liquidation threshold (`liquidation not triggered`);
3. At the `t` tick, the user's equity directly falls below the liquidation threshold, triggering system liquidation;

At this point, it is determined that the loss was caused by **jump variation rather than user judgment error**, triggering the structural payout.

---

## 3. Mathematical Expression and Pricing Logic

### 3.1 Parameter Definition

| Parameter | Meaning |
|-----------|---------|
| `a` | Payout amount |
| `t` | Number of consecutive downward ticks |
| `m` | Underlying asset class (affects tick unit) |
| `p` | Structure price |

### 3.2 Basic Pricing Principles

The structure price `p` should equal the payout amount `a` × probability `Pr(trigger)`, i.e.:

\{
p = a \cdot \mathbb{P}[\text{Tick Jump Knock-Out}]
\}

The trigger probability can be estimated through the following methods:

- Using Monte Carlo to generate price paths
- Analyzing each path on a tick-by-tick basis
- Counting instances where "tick jump causes liquidation"
- Estimating probability using count / total simulated paths

This pricing model provides a reasonable insurance premium rate under no-arbitrage conditions.

---

## Mathematical Modeling and Simulation Methods

The pricing model implements probability calculations for the tick jump trigger mechanism through the following steps:

1. Using the GBM model to generate price paths.
2. Analyzing whether there are time periods in each path that satisfy the trigger logic.
3. Using the proportion of trigger paths as the payout probability.
4. Calculating the structure price `p = a \cdot \mathbb{P}[\text{Tick Jump Knock-Out}]`.

Simulation results validate the logic's reasonability and provide payout probability estimates under market conditions.

---

## 4. Example Paths and Demonstration

Please refer to `scenario.md` and `simulation_charts/price_jump_demo.png`  
These include the following three types of paths:

- ✅ **Normal Gradual Loss**: Will not trigger payout
- ✅ **Significant Gap Triggering Liquidation**: But not from the liquidation threshold edge, does not trigger
- ✅ **Consecutive Edge Jump Liquidation**: Satisfies the definition, triggers payout `a`

---

## 5. Pricing Model Implementation (Brief)

See `pricing_model.py` for details:

- Using the GBM model to generate intraday price sequences;
- Determining whether time periods satisfying the trigger logic exist in the path;
- Outputting the proportion of all trigger paths as the payout probability;
- Returning `p = a × trigger ratio`

Example results (using gold futures as an example):

| Simulation Count | Payout Amount `a` | Trigger Ratio | Structure Price `p` |
|------------------|-------------------|---------------|---------------------|
| 10,000 | 1,000 yuan | 4.25% | 42.5 yuan |

---

## 6. Risk Disclosure and Considerations

- This structure only compensates for "liquidation losses caused by price jumps";
- It does not compensate for liquidation due to high volatility, continuous losses, or strategy errors;
- The structural payout is a fixed amount `a`, not equivalent to the actual loss;
- If market volatility is insufficient, trigger events become extremely rare, and the structure price becomes extremely low;
- This note should not be used for "trading error exemption" or non-insurance purpose arbitrage.

---

## 7. Extension Directions and Structure Combination Recommendations

- ✅ Combination with Day001 Margin Replenishment Structure → Multi-round Jump Repair Structure;
- ✅ Combination with Day002 Credit Trigger Note → Credit + Jump Dual-factor Payout;
- ✅ Setting up multi-level tick judgment mechanisms → tick-sensitivity options;
- ✅ Automated graphical structure generation → for educational platforms, derivatives DSL engines;

---

## 8. Conclusion

The Tick Jump Triggered Note is a structural response to market mechanism deficiencies, implementing microscopic risk protection for high-leverage traders through precisely defined "jump knock-out" conditions. This product can be used in investor education scenarios, trading simulation platforms, structural combination language research, and can also serve as a prototype for additional clauses in real notes.

> 🎯 It is not a judgment on price trends, but rather a **structural modeling** of the market mechanism itself.

---
