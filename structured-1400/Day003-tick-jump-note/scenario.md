# Scenario

## Day003 - Tick Jump Triggered Note  
Scenario Illustration and Trigger Path Explanation

---

## 📉 Background

This structured product is designed to address the following situation:

> During continuous gradual price declines, users still have opportunities to add margin to avoid liquidation;  
> However, due to market price jumps (tick jumps) directly breaching the liquidation threshold,  
> Users experience **non-strategic liquidation**.

Therefore, we construct a payout mechanism based on "jump triggers" as a micro-insurance for traders.

---

## 🧩 Scenario Path Explanation

### ✅ Example A: Normal Gradual Loss (Not Triggered)

- User holds gold futures
- Market experiences continuous small declines
- Never crosses the liquidation threshold
- User eventually closes position actively or profits
- ✅ No payout triggered

---

### ✅ Example B: Direct Large Gap Crossing (No Payout)

- Market experiences a one-time crash crossing the liquidation threshold
- Not a "continuous step-by-step" decline to the edge
- Already reached the liquidation threshold (or worse) before the jump
- ✅ No payout triggered (not a micro-level misfire)

---

### ✅ Example C: Precise Jump Breaching Liquidation (Payout)

- User's account is still normal at `t-1` tick
- Market decline at the `t` tick exactly triggers liquidation
- Also meets the criteria of continuous `t` tick decline
- ✅ Payout mechanism triggered, client receives compensation `a`

---

## 📊 Image Example

Image located at `simulation_charts/price_jump_demo.png`, where:

- Blue line represents the price path
- Red dotted line represents the liquidation threshold
- Clearly visible in a certain time period, price directly crosses downward from the liquidation edge

---

## 🧠 Teaching Suggestions

- Can be used for classroom or project demonstrations, guiding students to consider the impact of micro-market mechanisms on trading outcomes
- Encourage users to draw their own geometric models of tick step size, liquidation boundaries, and payout zone triggers
- Can be combined with `whitepaper.md` and `pricing_model.py` to simulate logic verification for intuitive understanding

---

## 🧩 Extended Discussion

- Are there more complex market jump behaviors that can be summarized with similar trigger logic?
- How can "non-strategic risks" be identified without affecting market fairness?
- Could similar structures be used for exchange design of "compensatory repo" mechanisms?

---

## Simulation Results and Path Examples

According to the simulation results from `pricing_model.py`, here are specific tick jump scenarios:

- **Trigger Path**: Continuous tick decline leading to liquidation triggering the payout mechanism.
- **Non-Trigger Path**: Price remains above the liquidation threshold or does not meet the tick threshold.

The visualization results of these paths are stored in `simulation_charts/price_jump_demo.png`, demonstrating the logic of the tick jump trigger mechanism.

