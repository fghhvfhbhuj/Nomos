# Day003 - Tick Jump Triggered Note

## 📘 Project Overview

This structured product addresses the forced liquidation risks caused by non-continuous price movements (tick jumps) in financial markets, offering a protective mechanism through structured insurance.

As the third product in the Structured-1400 series, this design extracts priceable structural features from micro-market mechanisms. The structure is entirely original, linearly independent, and can serve as a foundational module for composite systems.

---

## File Structure

```
Day003-Tick-Jump-Note/
├── README.md                  # Current file
├── term-sheet.md              # Formal terms sheet
├── whitepaper.md              # Product mechanism explanation (whitepaper)
├── scenario.md                # Scenario illustrations
├── pricing_model.py           # Python pricing simulation code
├── simulation_charts/         # Simulation image folder
│   ├── price_jump_demo.png    # Jump trigger demonstration
│   └── ...
├── LICENSE.md                 # License (optional)
```

---

## Core Mechanism Overview

### 🎯 Product Objectives
- Provide insurance-like payout structures for users affected by forced liquidation due to market price jumps.
- Utilize the non-continuous characteristics of ticks to construct risk determination logic.

### ⚙️ Structural Trigger Logic
- A user holds an underlying asset at a certain time point, experiencing a consecutive drop of `t` units in price.
- Loss before the jump does not exceed the forced liquidation threshold, but the jump causes immediate liquidation.
- Determined as a "jump trigger" → Knock-out → Fixed payout of `a` units.

### 📦 Contract Structural Features
- Structure Price: `p` units (insurance purchase price).
- Knock-In: Effective upon purchase.
- Knock-Out: Triggered by jump conditions, resulting in a fixed payout of `a`.
- If untriggered, `p` expires worthless.

### 🔧 Parameter Description
- `a`: Payout amount (insurance value).
- `t`: Consecutive drop tick count (sensitivity).
- `m`: Underlying asset (affects tick units, slippage, etc.).
- `p = f(a, t, m)`: Arbitrage-free structure price expression (details in whitepaper).

---

## 🔍 Example Path Demonstration

- Images located in `simulation_charts/`.
- Illustrates differences between normal sliding and jump-through scenarios.
- Demonstrates payout trigger determination logic.

---

## 💬 Project Disclaimer
This project is intended for educational and research purposes only and does not constitute real investment advice.
The structural logic is entirely original and can be used for composite structure demonstrations, structural language research, educational projects, and financial programming.
