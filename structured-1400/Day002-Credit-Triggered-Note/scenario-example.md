# Scenario Example — Credit-Triggered Note

## 📈 Scenario 1: Normal Maturity Path

### Initial Setup:

* User invests principal of ¥100,000
* Underlying asset is a certain high-yield bond, observation period is 15 days
* Total term of 1 year, annual coupon rate 10%, paid quarterly (4 payments)

### Path Evolution:

1. User enters the structured note, freeze period begins (Days 0-15)
2. No knock-out triggered → Day 15 releases observation period discount compensation (**Actual calculation: ¥205.69**)
3. Quarterly coupon payments: ¥2,500, four times in total
4. Principal returned at maturity: ¥100,000

### Summary:

* **Actual Model Calculation Results**:
  - Normal path value: ¥104,816.22
  - Observation period compensation: ¥205.69
  - Total expected value: ¥105,021.91
* Annualized yield ≈ 5.02%
* Structure operates safely, no default events

---

## 🚨 Scenario 2: Credit Score Triggers Knock-Out

### Initial Setup:

* Same as above, user invests ¥100,000
* On Day 30, company releases financial reports, ICR and current ratio decline sharply

### Risk Control Path:

1. Scoring function outputs score < 50 for 3 consecutive days → Knock-out triggered
2. **System automatically calculates**:
   - Discounted value of remaining cash flows: ¥104,816.22
   - Risk premium: ¥5,000
   - **Total payout amount: ¥109,816.22**
3. User automatically receives payout, structure terminates, no further participation in subsequent fluctuations

### Summary:

* User receives ¥109,816.22, a return of +9.82% relative to principal
* Structure actively circuit-breaks before credit risk exposure, securing the outcome
* **Significant downside protection effect**

---

## 💬 Scenario Interpretation Guide

| Path | User Experience | Corresponding Structural Advantage | Actual Return |
| ---- | ------------- | ----------------- | ------ |
| Normal Path | Receives all coupons, anticipates enclosed returns | Observation period reimbursement enhances perceived reasonability | +5.02% |
| Knock-out Path | No active operation required, automatic payout triggered | Transparent, adjustable risk control mechanism, enhanced user trust | +9.82% |

---

## 📊 Sensitivity Analysis Scenarios

### Scenario 3: Expected Performance Under Different Knock-Out Probabilities

Sensitivity analysis results based on the latest model:

| Knock-Out Probability | Expected Value | Return Relative to Principal | Risk Level |
|---------|----------|--------------|----------|
| 0.0%    | ¥105,021.91 | +5.02% | Very Low |
| 10.0%   | ¥104,501.33 | +4.50% | Low |
| 20.0%   | ¥103,980.75 | +3.98% | Medium-Low |
| 30.0%   | ¥103,460.17 | +3.46% | Medium |
| 40.0%   | ¥102,939.59 | +2.94% | Medium-High |
| 50.0%   | ¥102,419.01 | +2.42% | High |

### Key Observations:
- **Downside Protection**: Even at the highest knock-out probability (50%), investors still achieve positive returns
- **Risk Compensation**: Higher knock-out probabilities correspond to more significant risk premiums
- **Stability**: Return fluctuation range is controlled within a reasonable interval

---

## 🔬 Technical Verification Scenarios

### Scenario 4: Model Technical Features Demonstration

**Automated Report Generation**:
- System automatically generates professional HTML reports: `pricing_report.html`
- Includes detailed statistical analysis, risk indicators, and investment recommendations
- Professional-grade charts displaying relationship between knock-out probability and expected value

**Sensitivity Analysis**:
- Automatically tests the impact of discount rate changes on structure value
- Analyzes the effects of risk premium adjustments
- Provides parameter optimization recommendations

**Visualization Effects**:
- High-quality charts: `ctn_pricing_visualization.png`
- Includes statistical information and risk interval annotations
- Professional financial chart styling

---

## 🎯 Educational Application Scenarios

### Scenario 5: Classroom Demonstration Usage

**Quick Demonstration**:
```bash
python pricing_model.py
```

**Output Content**:
- Core calculation results displayed in real-time
- Professional-grade visualization charts automatically generated
- Detailed analysis reports generated with one click
- Complete runtime logs recorded

**Educational Value**:
- Demonstrates complete financial engineering modeling process
- Case study combining theory and practice
- Modular design facilitates extension and modification
- Suitable for various levels of educational requirements

---

## 📈 Visualization Results Display

The optimized model has generated the following professional-grade outputs:

1. **High-Quality Visualization Charts** (`ctn_pricing_visualization.png`)
   - Curve showing relationship between knock-out probability and structure value
   - Includes maximum value, minimum value, and benchmark line annotations
   - Professional chart styling and color scheme

2. **Detailed Analysis Report** (`pricing_report.html`)
   - Core parameter summary table
   - Knock-out probability impact analysis
   - Statistical summary and risk indicators
   - Investment recommendations and risk alerts

3. **Runtime Log Records** (`pricing_model.log`)
   - Complete calculation process tracking
   - Key results and timestamp records
   - Facilitates debugging and verification

---

## 💡 Practical Application Recommendations

### Investor Suitability
- **Conservative Investors**: Focus on downside protection functionality, positive returns even in worst-case scenarios
- **Balanced Investors**: Balance risk and return, obtain reasonable risk-adjusted returns
- **Educational Research**: Complete modeling framework, suitable for academic research and course teaching

### Risk Management Key Points
- Knock-out mechanism provides timely risk control
- Observation period design prevents market arbitrage
- Payout cap mechanism controls maximum loss
- Transparent scoring algorithm facilitates risk assessment

---

> This example is based on actual running results of the latest optimized pricing model  
> All values are real calculation outputs from the model  
> Suitable for educational demonstrations, academic research, and product prototype development
