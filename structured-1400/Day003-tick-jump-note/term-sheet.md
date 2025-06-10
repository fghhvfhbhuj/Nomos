# Term Sheet

## Product Name
Tick Jump Triggered Note

## Product Type
Structured Insurance Note (Discontinuous Volatility Risk Protection Structure)

## Underlying Asset
Gold Futures / CSI 300 Index / Micro Nasdaq Futures (optional)

## Investment Currency
Chinese Yuan (CNY) / US Dollar (USD)

## Contract Term
3 months / 6 months / 12 months (configurable)

## Minimum Investment Amount
¥10,000 (or equivalent in USD)

## Return Structure
- Client pays structure price `p` to purchase this insurance-type product
- Once a "tick jump liquidation" trigger event occurs → Client receives payout `a`
- If no trigger occurs by maturity, `p` is void and non-refundable

## Knock-In Clause
- Knock-in upon purchase
- Protection is considered effective once client pays the structure price

## Knock-Out Clause
- Payout is triggered when all of the following conditions are met:
  - The underlying asset experiences a continuous decline of t tick units
  - The account has not reached the liquidation threshold before the decline
  - The account directly falls below the liquidation threshold after the decline and triggers liquidation

## Payout Mechanism
- Once jump knock-out is triggered → Client receives fixed payout amount `a`
- The payout amount is agreed upon at contract signing and does not adjust with underlying asset movements

## Parameter Setting Recommendations
| Parameter | Default Value (Example) |
|-----------|-------------------------|
| `a` | ¥1,000 |
| `t` | 3 tick |
| `m` | Gold Futures |
| `p` | Estimated by pricing model (see whitepaper) |

## Risk Disclosure
- This structure does not protect against market risk itself, only pays out for specific jump structures
- No payout will be triggered if the market declines slowly and continuously or if volatility is insufficient
- Investors should fully understand the tick jump trigger mechanism and path dependency

## Project Status
Simulated design, for educational use, open-source code, suitable for structured finance learning and expression training scenarios.
Not a real trading product, does not constitute any offer or investment advice.

## Pricing Logic Update

The calculation formula for the structure price `p` is:

\{
    p = a \cdot \mathbb{P}[\text{Tick Jump Knock-Out}]
\}

Where:
- `a` is the fixed payout amount.
- \( \mathbb{P}[\text{Tick Jump Knock-Out}] \) is the probability of triggering the payout, derived from simulation results.

This logic ensures that the structure price reflects the risk and payout possibility under market conditions.
