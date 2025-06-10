# Term Sheet

## Product Name  
Credit-Triggered Redemption Note

## Product Type  
Structured Credit Protection Note (Path-Dependent + Automatic Knock-Out Payout + Educational Replaceable Model)

## Underlying Asset  
Publicly traded corporate bonds / REITs / High-risk corporate receivables (to be specified separately)

## Investment Currency  
Chinese Yuan (CNY) / US Dollar (USD)

## Investment Term  
12 months (structure can set observation period + main structure duration)

## Minimum Investment Amount  
¥100,000 minimum (or equivalent in USD)

## Yield Structure  
- If no credit risk event occurs:  
  - Fixed coupon + Principal at maturity  
  - Frozen observation period compensation released at structure conclusion  
- If knock-out occurs (i.e., credit score falls below threshold):  
  - Immediate termination of structure  
  - Payout: Discounted total of future cash flows + Credit risk premium (insurance premium)

## Initial Observation Period  
- Duration: 15 days  
- Function: Prevents risk control arbitrage, no yield calculation or knock-out triggers during structure freeze period  
- Discount compensation for observation period paid at maturity (based on current model: ¥205.69)

## Knock-Out Trigger Conditions  
- Uses educational risk scoring function `risk_score_func()` to calculate company credit score  
- If score is below 50 for 3 consecutive days, knock-out is triggered  
- This function is replaceable, model structure is transparent, suitable for educational or actual deployment scenarios
- **Enhanced functionality**: Support for machine learning models and anomaly detection algorithms

## Knock-Out Payout Structure  
- Payout amount =  
  - Discounted value of all remaining future cash flows (based on current model: ¥104,816.22)
  - + Credit risk premium (default: ¥5,000)
  - = Total payout value: ¥109,816.22
- Overall payout capped at 110% of note issuance price

## Normal Redemption Structure  
- If structure is not knocked out, users receive:  
  - All earned cash flows (¥104,816.22)
  - + Initial observation period discount compensation (¥205.69)
  - = Total expected value: ¥105,021.91

## Model Mechanism  
- Structure default uses logistic regression scoring function to estimate default probability  
- All scoring inputs, thresholds, and behavior paths are replaceable  
- System estimates expected value under different knock-out probabilities through path simulation
- **New addition**: Sensitivity analysis and professional report generation

## Pricing Method  
- Structured note issuance price = Normal discounted value + Risk premium  
- Uses law of large numbers to drive risk control structure rationality, allowing reverse pricing equation solving in educational settings  
- **Professional feature**: High-quality visualization output: Knock-out probability vs. Theoretical structure value
- **Automated reporting**: Generates detailed analysis reports in HTML format

## Technical Specifications
- **Calculation Engine**: Python numerical computation framework
- **Visualization**: matplotlib professional chart generation
- **Reporting System**: HTML automated report generation
- **Logging**: Complete runtime process tracking
- **Modular Design**: Supports dynamic parameter configuration and function extension

## Risk Disclosure (Educational Version)  
- This note is a structured risk educational tool  
- Non-capital guaranteed structure, with potential for knock-out payouts and pricing deviations  
- Please adjust trigger mechanisms according to regulatory compliance frameworks and risk appetite in actual deployment
- **Investment recommendation**: Suitable for risk-averse investors, recommended as part of an investment portfolio

## Applicable Scenarios  
- Financial education / Derivatives research / Credit risk modeling practice  
- High-risk note protection structure prototype / Investor behavior testing design
- **New addition**: Professional financial engineering projects and academic research

## Technical Support and Documentation
- Complete code documentation and user instructions
- Professional-grade visualization charts and analysis reports
- Modular design supports secondary development
- Open-source code, supports academic research and educational use

---

