# Single Injury Recalibration - User Guide

## Overview

This tool is specifically designed for **single injury claims** using your actual equation:

```
y = e^(C0 + C1·S + C2·I + C3·S·I + C4·I² + C5·I³ + C6·S²) × (1 + RatingWeight) × (1 + 0.1·CausationSum)
```

Where:
- **y** = DOLLARAMOUNTHIGH (predicted settlement amount)
- **e** = Euler's number (≈ 2.71828) - exponential function
- **C0-C6** = Coefficients you can calibrate
- **S** = Sum of all severity scores
- **I** = Impact of life score (1-4)
- **RatingWeight** = Venue rating weight (from RATINGWEIGHT field)
- **CausationSum** = Sum of all causation factors

---

## Location

Navigate to: **Recalibration Tab → Single Injury** (first tab)

---

## How It Works

### 1. **Claim Filtering**
The tool automatically filters to show only **single injury claims**:
- Claims where `INJURY_COUNT === 1`
- OR claims where `Injury_Count === 'Single'`

You can further filter by date:
- **Recent (2024-2025)**: Only claims from 2024 onwards
- **All Data**: All single injury claims in your dataset

### 2. **Variable Calculation**

#### **S (Severity Sum)**
Automatically calculates by summing:
- `SEVERITY_SCORE` field (if available)
- All `severity_*` factors:
  - `severity_allowed_tx_period`
  - `severity_initial_tx`
  - `severity_injections`
  - `severity_objective_findings`
  - `severity_pain_mgmt`
  - `severity_type_tx`
  - `severity_injury_site`
  - `severity_code`

#### **I (Impact Score)**
Extracted from the `IMPACT` field in your data:
- Values: 1, 2, 3, or 4
- Represents impact on life (1 = minimal, 4 = severe)
- If missing, defaults to 2 (medium impact)

#### **RatingWeight**
Taken directly from `RATINGWEIGHT` field:
- Positive value = Plaintiff-friendly venue
- Negative value = Defense-friendly venue
- Zero = Neutral venue

#### **CausationSum**
Automatically calculates by summing:
- `causation_probability`
- `causation_tx_delay`
- `causation_tx_gaps`
- `causation_compliance`

---

## Using the Tool

### Step 1: Select Data Range

Click one of the buttons:
- **Recent (2024-2025)**: Focus on recent trends
- **All Data**: Maximum sample size

The tool shows: "**X Single Injury Claims**" badge

### Step 2: Adjust Coefficients

In the blue box labeled "Adjust Coefficients", you'll see 7 input fields:

| Coefficient | Default | Represents |
|-------------|---------|------------|
| **C0** | 10.5 | Base constant (intercept) |
| **C1** | 0.15 | Linear effect of severity |
| **C2** | 0.25 | Linear effect of impact |
| **C3** | 0.05 | Interaction between severity & impact |
| **C4** | -0.1 | Quadratic effect of impact (I²) |
| **C5** | 0.02 | Cubic effect of impact (I³) |
| **C6** | -0.01 | Quadratic effect of severity (S²) |

**How to adjust:**
1. Type a new value in any coefficient field
2. Results update in real-time
3. Watch the metrics cards and charts change

**Tips:**
- **Increase C1**: Severity has more influence
- **Increase C2**: Impact has more influence
- **Increase C3**: Interaction effect is stronger
- **Negative C4/C6**: Diminishing returns (common for polynomial terms)

### Step 3: Interpret Results

#### **Metrics Cards (Top Row)**

```
┌─────────────────────────────────────────────────┐
│ Avg Error Change: +5.23%                        │
│ Shows if predictions got better (+ = good)      │
│ Baseline: 15.8% → Test: 10.57%                  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ RMSE Impact: +8.15%                             │
│ Root Mean Square Error improvement              │
│ Lower RMSE = better                             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ R² Score: 0.842                                 │
│ How well model fits data (0-1)                  │
│ Higher = better (>0.8 is very good)             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Improved: 87 claims                             │
│ Number of claims with better predictions        │
│ Aim for >60%                                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Degraded: 32 claims                             │
│ Number of claims with worse predictions         │
│ Some degradation is normal                      │
└─────────────────────────────────────────────────┘
```

#### **Charts**

**1. Actual vs Predicted Values (Left Chart)**
- **X-axis**: Actual DOLLARAMOUNTHIGH from settlement
- **Y-axis**: Predicted value from equation
- **Diagonal line**: Perfect predictions
- **Green dots**: Test predictions (with your coefficients)
- **Red dots**: Baseline predictions (with default coefficients)

**How to read:**
- Dots close to diagonal line = accurate predictions
- Dots above line = over-prediction
- Dots below line = under-prediction
- Green dots closer to line than red = improvement!

**2. Error Distribution (Right Chart)**
- Shows how many claims fall into each error percentage range
- **Red bars**: Baseline errors
- **Green bars**: Test errors

**Goal:**
- More green bars in "0-10%" and "10-20%" ranges
- Fewer green bars in ">50%" range

#### **Claim Tables (Bottom)**

**Most Improved Claims:**
- Shows which claims benefited most from coefficient changes
- Columns:
  - **S**: Severity sum for that claim
  - **I**: Impact score (1-4)
  - **Actual**: Real settlement amount
  - **Improve**: % improvement in prediction accuracy

**Most Degraded Claims:**
- Shows which claims got worse predictions
- Use to identify patterns (are they outliers?)

---

## Understanding the Equation

### **Why This Equation?**

Your equation is a **polynomial regression with exponential transformation**:

1. **Polynomial terms** (I², I³, S²) capture non-linear relationships
   - Linear relationship: double severity → double payout
   - Non-linear: severe injuries have exponentially higher payouts

2. **Interaction term** (S·I) captures combined effects
   - High severity + high impact = more than sum of parts
   - Example: severe injury with major life impact costs more than expected

3. **Exponential function** (e^x) ensures positive predictions
   - Prevents negative settlement amounts
   - Models exponential growth in severe cases

4. **Multipliers** (RatingWeight, CausationSum) adjust for external factors
   - Plaintiff-friendly venue → higher settlement
   - Strong causation → higher settlement

### **Coefficient Interpretation**

**C0 (Base Constant)**
- Starting point when S=0 and I=0
- Typical range: 8-12
- Higher = higher baseline settlements across the board

**C1 (Severity Linear)**
- How much each unit of severity increases the exponent
- Positive = more severity = higher payout (expected)
- Typical range: 0.1 - 0.3

**C2 (Impact Linear)**
- How much each impact level increases the exponent
- Positive = higher impact = higher payout (expected)
- Typical range: 0.2 - 0.5

**C3 (Severity × Impact Interaction)**
- Captures synergy between severity and impact
- Positive = combined effect > individual effects
- Typical range: 0.01 - 0.1

**C4 (Impact Quadratic)**
- Captures diminishing or accelerating returns from impact
- Negative = diminishing returns (common)
- Typical range: -0.2 to 0

**C5 (Impact Cubic)**
- Captures complex non-linear patterns
- Small values typical
- Typical range: -0.05 to 0.05

**C6 (Severity Quadratic)**
- Captures diminishing or accelerating returns from severity
- Negative = diminishing returns (common)
- Typical range: -0.05 to 0

---

## Practical Examples

### Example 1: Increase Impact Weight

**Goal**: Make impact score more influential

**Action**:
1. Change C2 from 0.25 → 0.35
2. Observe results

**Expected outcome**:
- Claims with I=3 or I=4 will have higher predictions
- Claims with I=1 will have lower predictions
- If actual high-impact claims were under-predicted, this should improve them

### Example 2: Add Severity Interaction

**Goal**: Capture that severe injuries with high impact cost disproportionately more

**Action**:
1. Change C3 from 0.05 → 0.10
2. Observe results

**Expected outcome**:
- Claims with both high S and high I will increase significantly
- Claims with high S but low I won't change much
- Claims with low S but high I won't change much

### Example 3: Adjust Quadratic Terms

**Goal**: Model diminishing returns for very severe injuries

**Action**:
1. Change C6 from -0.01 → -0.05
2. Observe results

**Expected outcome**:
- Very high severity claims will have slightly lower predictions
- Medium severity claims won't change much
- Models the reality that beyond a certain point, severity has less impact

---

## Best Practices

### 1. Start with One Coefficient at a Time
- Change C1, see result
- Reset, change C2, see result
- This helps understand each coefficient's individual effect

### 2. Use Recent Data First
- Recent claims (2024-2025) are most relevant for future predictions
- Once calibrated on recent, test on "All Data"

### 3. Watch R² Score
- Target: R² > 0.75 (good fit)
- R² > 0.85 (excellent fit)
- If R² drops, revert the change

### 4. Balance Improved vs Degraded
- Aim for >60% improved claims
- <20% degraded claims is acceptable
- If 50/50 split, coefficients aren't helping

### 5. Look for Patterns in Degraded Claims
- Are they all high severity? Adjust C1 or C6
- Are they all low impact? Adjust C2 or C4
- Are they outliers? May need different equation

### 6. Test Extreme Cases
- Find a claim with S=1, I=1 (minimal)
- Find a claim with S=10, I=4 (severe)
- Ensure predictions make sense at extremes

### 7. Don't Overfit
- If you achieve 99% improved, you're probably overfitting
- Model should generalize to new data
- Cross-validate on different time periods

---

## Common Scenarios

### Scenario 1: Predictions Too Low for Severe Cases

**Symptoms:**
- High severity claims (S > 5) under-predicted
- Most degraded claims have high S values

**Solution:**
1. Increase C1 (severity linear effect)
   - Try C1 = 0.15 → 0.20
2. OR make C6 less negative (reduce diminishing returns)
   - Try C6 = -0.01 → -0.005

### Scenario 2: Impact Not Influential Enough

**Symptoms:**
- Claims with I=4 aren't predicted much higher than I=2
- Impact doesn't seem to matter in results

**Solution:**
1. Increase C2 (impact linear effect)
   - Try C2 = 0.25 → 0.40
2. Increase C3 (interaction)
   - Try C3 = 0.05 → 0.08

### Scenario 3: All Predictions Too High

**Symptoms:**
- Most predictions > actual values
- Many claims in degraded list

**Solution:**
1. Decrease C0 (base constant)
   - Try C0 = 10.5 → 10.0
2. This shifts entire curve down

### Scenario 4: All Predictions Too Low

**Symptoms:**
- Most predictions < actual values
- Underestimating settlements across the board

**Solution:**
1. Increase C0 (base constant)
   - Try C0 = 10.5 → 11.0
2. This shifts entire curve up

### Scenario 5: Good for Most, Bad for Extremes

**Symptoms:**
- Middle-range claims accurate
- Very low or very high claims way off

**Solution:**
1. Adjust quadratic/cubic terms (C4, C5, C6)
2. These control curvature at extremes
3. May need more complex equation for true extremes

---

## Validation Checklist

Before applying new coefficients to production:

- [ ] R² score > 0.75
- [ ] Improved claims > 60%
- [ ] Degraded claims < 25%
- [ ] Predictions reasonable at extremes (check scatter plot)
- [ ] No negative predictions (shouldn't happen with exponential)
- [ ] Tested on both recent and historical data
- [ ] Predictions align with domain expertise
- [ ] Outliers investigated (check degraded claims table)

---

## Mathematical Details

### Full Equation Breakdown

```
Step 1: Calculate the exponent
exponent = C0 + C1·S + C2·I + C3·S·I + C4·I² + C5·I³ + C6·S²

Step 2: Apply exponential
basePrediction = e^exponent

Step 3: Apply multipliers
finalPrediction = basePrediction × (1 + RatingWeight) × (1 + 0.1·CausationSum)
```

### Example Calculation

**Given:**
- S = 3.5 (severity sum)
- I = 3 (impact score)
- RatingWeight = 0.15 (plaintiff-friendly venue)
- CausationSum = 2.0

**Using default coefficients:**
```
exponent = 10.5 + (0.15×3.5) + (0.25×3) + (0.05×3.5×3) + (-0.1×3²) + (0.02×3³) + (-0.01×3.5²)
         = 10.5 + 0.525 + 0.75 + 0.525 + (-0.9) + 0.54 + (-0.1225)
         = 11.8175

basePrediction = e^11.8175
               = 135,622

finalPrediction = 135,622 × (1 + 0.15) × (1 + 0.1×2.0)
                = 135,622 × 1.15 × 1.2
                = 187,160
```

So this claim would be predicted at **$187,160**.

---

## Troubleshooting

### "0 Single Injury Claims" Message

**Cause:** No claims match the single injury filter

**Solutions:**
1. Click "All Data" instead of "Recent"
2. Check if your data has `INJURY_COUNT` field
3. Verify claims have the field populated
4. May need to adjust filter logic in code

### Metrics Don't Update

**Cause:** Frontend hasn't recompiled

**Solution:**
1. Hard refresh browser (Ctrl + Shift + R)
2. Check console for errors (F12)
3. Restart frontend dev server

### Predictions Seem Wrong

**Cause:** Missing or incorrect data fields

**Solutions:**
1. Check `IMPACT` field exists and has values 1-4
2. Check severity factors are populated
3. Verify `DOLLARAMOUNTHIGH` is the actual settlement
4. Check for data quality issues (nulls, zeros)

### Can't See Charts

**Cause:** Not enough data or all errors

**Solutions:**
1. Need at least 10 claims for meaningful charts
2. Check browser console for JavaScript errors
3. Ensure Recharts library is installed

---

## Export Results

To save your optimized coefficients:

1. Take a screenshot of the coefficient box (blue section)
2. Or manually record values in a spreadsheet
3. Apply to production model once validated

**Future enhancement:** Export to CSV or JSON (can be added if needed)

---

## Summary

The **Single Injury Recalibration** tool lets you:

✅ Use your **actual equation** (exponential polynomial regression)
✅ Adjust **7 coefficients** (C0-C6) in real-time
✅ See immediate impact on prediction accuracy
✅ Focus on **single injury claims** only
✅ Filter by **recent data** (2024-2025)
✅ Visualize with **scatter plots** and **error distributions**
✅ Identify **specific claims** that improve or degrade

**Use this to calibrate your model for optimal DOLLARAMOUNTHIGH predictions!**

---

## Questions?

Common questions:

**Q: Why exponential function?**
A: Ensures positive predictions and models exponential growth in severe cases.

**Q: Why polynomial terms (I², I³)?**
A: Captures non-linear relationships - severe cases don't scale linearly.

**Q: What if I have multiple injuries?**
A: Use the "Multi-Factor" tab (different equation for multi-injury claims).

**Q: How often should I recalibrate?**
A: Every 6-12 months, or when performance degrades, or after major legal changes.

**Q: Can I use this for all claims?**
A: No, only single injury claims. Multi-injury needs different equation.
