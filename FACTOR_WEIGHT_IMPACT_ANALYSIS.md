# Factor Weight Impact Analyzer - User Guide

## Overview

The **Factor Weight Impact Analyzer** is a powerful tool that allows you to see how changing **individual factor weights** impacts DOLLARAMOUNTHIGH predictions while keeping **everything else constant**.

This is exactly what you requested: analyzing how a particular factor weight impacts predictions on recent data without changing the existing equation.

---

## Location

Navigate to: **Recalibration Tab → Factor Analyzer** (first tab)

---

## Key Features

### 1. **Isolated Impact Analysis**
- Change ONE factor weight at a time
- All other 51 factors remain at baseline (base_weight)
- See direct impact on DOLLARAMOUNTHIGH prediction accuracy

### 2. **Recent Data Focus**
- Toggle between:
  - **Recent (2024-2025)**: Focuses on most recent claims
  - **All Data (2023-2025)**: Complete historical dataset
- Shows claim count for transparency

### 3. **Interactive Weight Testing**
- Select any of the 52 factors from dropdown (organized by category)
- Use slider to test different weight values (min to max)
- See real-time impact as you adjust

### 4. **Comprehensive Metrics**
- **Avg Error Change**: How much prediction error improves/degrades
- **RMSE Impact**: Root Mean Square Error improvement percentage
- **Improved Claims**: Count and percentage of claims with better predictions
- **Degraded Claims**: Count and percentage of claims with worse predictions

---

## How to Use

### Step 1: Select a Factor
1. Click the "Select Factor to Analyze" dropdown
2. Factors are organized by category:
   - **Causation** (12 factors)
   - **Severity** (8 factors)
   - **Treatment** (15 factors)
   - **Clinical** (12 factors)
   - **Disability** (5 factors)
3. Choose any factor (e.g., "Surgical_Intervention", "Head_Trauma", etc.)

### Step 2: Adjust Weight
- Use the slider to test different weight values
- **Min**: Minimum allowed weight from weights.csv
- **Base**: Current baseline weight (shown in red on chart)
- **Max**: Maximum allowed weight from weights.csv
- Current test value shown in green on chart

### Step 3: Choose Data Range
- **Recent (2024-2025)**: Best for understanding current trends
- **All Data**: More comprehensive, larger sample size

### Step 4: Interpret Results

#### Metrics Cards
```
┌─────────────────────────────────────────────────┐
│ Avg Error Change: +5.23%                        │
│ 15.8% → 10.57% (improvement = positive)         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ RMSE Impact: +8.15%                             │
│ $42.3K → $38.9K (lower = better)                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Improved Claims: 87                             │
│ 68.5% of 127 claims                             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Degraded Claims: 32                             │
│ 25.2% of 127 claims                             │
└─────────────────────────────────────────────────┘
```

---

## Charts Explained

### 1. Weight Sensitivity Curve (Left)

**What it shows:**
- X-axis: Weight value (from min to max)
- Y-axis: Average prediction error %
- Blue line: How error changes as weight changes

**How to read it:**
- **Downward slope** = Increasing weight **reduces** error (good!)
- **Upward slope** = Increasing weight **increases** error (bad!)
- **Flat line** = Weight has minimal impact
- **U-shape** = There's an optimal weight in the middle
- **Red marker**: Base weight (current)
- **Green marker**: Test weight (what you're testing)

**Example interpretation:**
```
If the curve goes down as weight increases:
→ This factor is UNDERWEIGHTED
→ Increasing its weight will improve predictions
→ Consider raising it toward the max

If the curve goes up as weight increases:
→ This factor is OVERWEIGHTED
→ Decreasing its weight will improve predictions
→ Consider lowering it toward the min
```

### 2. Factor Value vs Impact (Right)

**What it shows:**
- X-axis: Factor's normalized value (0-1) in each claim
- Y-axis: Improvement % for that claim
- Each dot = one claim

**How to read it:**
- **Dots above zero line**: Claims that improved
- **Dots below zero line**: Claims that degraded
- **Clustering patterns**:
  - High factor values → High improvement = Strong positive relationship
  - High factor values → High degradation = Inverse relationship

**Example interpretation:**
```
If dots cluster in upper-right (high value, high improvement):
→ Claims with high values of this factor benefit from weight increase
→ This factor is predictive and should have higher weight

If dots scatter randomly:
→ Factor impact is inconsistent
→ May not be a good predictor
→ Consider keeping weight low
```

---

## Claim-Level Details

### Top 10 Most Improved Claims
Shows which specific claims benefited most from the weight change.

Example:
```
Claim ID        Actual      Improvement
CLM-2024-001    $71.0K      +12.34%
CLM-2025-015    $114.5K     +9.87%
CLM-2024-023    $104.1K     +8.45%
```

### Top 10 Most Degraded Claims
Shows which claims got worse predictions.

Use this to understand:
- Are degraded claims outliers?
- Do they share common characteristics?
- Is the trade-off worth it?

---

## Practical Example Walkthrough

### Scenario: Analyzing "Surgical_Intervention"

1. **Select Factor**: Choose "Surgical_Intervention" from dropdown
2. **View Baseline**:
   - Base weight: 0.120
   - Min: 0.06, Max: 0.22
3. **Test Higher Weight**: Move slider to 0.18 (50% increase)
4. **Results**:
   - Avg Error Change: **+6.5%** (improvement)
   - RMSE Impact: **+4.2%** (improvement)
   - 95 claims improved, 28 degraded
5. **Sensitivity Curve**: Downward slope = higher weight is better
6. **Scatter Plot**: Dots cluster upper-right = strong positive relationship

**Conclusion**: Surgical_Intervention is underweighted. Increasing from 0.12 → 0.18 improves predictions by ~6.5%. Recommend applying this change.

---

## Understanding the Equation (Kept Constant)

The tool uses your **existing recalibration equation** without modification:

```typescript
1. Baseline Score = Σ(factor_value × base_weight) / total_weight
2. Test Score = Σ(factor_value × test_weight) / total_weight
   // Only ONE weight changes; all others stay at base_weight

3. Score Differential = Test Score - Baseline Score

4. Recalibrated Prediction = Original Prediction × (1 + Score Differential)

5. Error = |Recalibrated Prediction - DOLLARAMOUNTHIGH|

6. Improvement = (Baseline Error - Test Error) / Baseline Error × 100
```

**Key Point**: The equation itself is NOT changed. We're only adjusting weights within the existing formula.

---

## Best Practices

### When to Use This Tool

✅ **DO use when:**
- Testing impact of a single factor before committing changes
- Understanding which factors have the most leverage
- Validating recommendations from other tabs
- Explaining weight changes to stakeholders
- Analyzing recent data trends (2024-2025 filter)

❌ **DON'T use when:**
- You want to optimize ALL weights simultaneously → Use "Auto-Optimize" tab
- You want to see before/after comparisons → Use "Before/After" tab
- You want multiple recommendations → Use "Recommendations" tab

### Recommended Workflow

1. **Start with High-Impact Factors**
   - Go to "Factor Impact" tab
   - Note the top 10 factors by weighted impact
   - Return to "Factor Analyzer" and test each one

2. **Test Weight Ranges**
   - Start at base weight
   - Move slider to max
   - Observe sensitivity curve
   - Find the "sweet spot" where error is minimized

3. **Focus on Recent Data**
   - Use "Recent (2024-2025)" filter
   - Recent claims are more predictive of future performance
   - Historical data may have different patterns

4. **Validate with Multiple Factors**
   - Test top 5-10 factors individually
   - Document which ones show clear improvement
   - Apply changes to those factors only

5. **Check for Trade-offs**
   - Review degraded claims table
   - Ensure you're not hurting too many claims
   - Aim for >60% improved rate

---

## Interpreting Common Patterns

### Pattern 1: Clear U-Shape Curve
```
Error
  │    ╱╲
  │   ╱  ╲
  │  ╱    ╲
  │ ╱      ╲
  └─────────── Weight
  min    opt    max
```
**Meaning**: There's an optimal weight in the middle
**Action**: Set weight to the bottom of the U

### Pattern 2: Downward Slope
```
Error
  │╲
  │ ╲
  │  ╲
  │   ╲
  └─────── Weight
  min    max
```
**Meaning**: Higher weight is better (underweighted)
**Action**: Increase weight toward max

### Pattern 3: Upward Slope
```
Error
  │    ╱
  │   ╱
  │  ╱
  │ ╱
  └─────── Weight
  min    max
```
**Meaning**: Lower weight is better (overweighted)
**Action**: Decrease weight toward min

### Pattern 4: Flat Line
```
Error
  │─────────
  │
  │
  └─────── Weight
  min    max
```
**Meaning**: Weight has minimal impact
**Action**: Keep at base or reduce to min

---

## Tips for Optimal Results

### 1. Focus on Recent Data
- Recent claims (2024-2025) better predict future performance
- Use "All Data" only for statistical significance

### 2. Look for Consistency
- If scatter plot shows random dots → Factor is inconsistent
- If scatter plot shows clear pattern → Factor is predictive

### 3. Don't Over-Optimize
- Aim for 60-80% improved rate
- Some claims will always degrade (outliers)
- Perfect optimization may overfit

### 4. Consider Magnitude
- A 2% improvement on 100 claims is better than 5% on 20 claims
- Check both percentage AND absolute claim counts

### 5. Test Edge Cases
- Move slider to min: Does error increase?
- Move slider to max: Does error decrease?
- Find the inflection point

---

## Integration with Other Tabs

### Use Factor Analyzer to validate:

**Recommendations Tab**
- "Recommendations" suggests weights based on correlation
- "Factor Analyzer" lets you TEST those suggestions
- Verify recommended weights actually improve predictions

**Auto-Optimize Tab**
- Auto-optimize finds mathematical optimum
- Factor Analyzer shows you WHY it works
- Understand the relationship, not just the number

**Before/After Tab**
- Shows aggregate results
- Factor Analyzer shows which FACTORS drove improvement
- Drill down into root causes

---

## Troubleshooting

### "No improvement shown"
- Try wider weight range (min to max)
- Check if factor has low impact (see "Factor Impact" tab)
- May need to adjust multiple factors simultaneously

### "Results inconsistent"
- Check claim count (need >30 for statistical significance)
- Try "All Data" instead of "Recent"
- Factor may be noisy/unreliable

### "Curve is flat"
- Factor has minimal predictive power
- Consider removing or reducing weight
- Focus on high-impact factors instead

### "Too many degraded claims"
- Weight change may be too extreme
- Test smaller increments
- Check if degraded claims are outliers (very high/low DOLLARAMOUNTHIGH)

---

## Technical Details

### Data Filtering
- **Recent**: `claim_date >= 2024-01-01`
- Filters applied at query time, not in chart rendering
- Claim count displayed for transparency

### Calculations
- Predictions recalculated for each weight test value
- 20 steps tested for sensitivity curve (min to max)
- Baseline comparison uses `base_weight` from weights.csv

### Performance
- Client-side calculation (fast for <1000 claims)
- Results cached per factor selection
- Charts re-render only when factor/weight/filter changes

---

## Summary

The **Factor Weight Impact Analyzer** gives you precise control to:

✅ Test individual factor weights in isolation
✅ Use recent data (2024-2025) for current trends
✅ Keep the existing equation constant
✅ See direct impact on DOLLARAMOUNTHIGH predictions
✅ Understand which factors have the most leverage
✅ Make data-driven weight adjustment decisions

**Use this tool BEFORE making weight changes to validate your assumptions!**

---

## Questions?

If you need help interpreting results or have questions about specific factors, refer to:
- [weights.csv](d:\Repositories\dashBoard\backend\data\weights.csv) - Factor definitions and bounds
- "Factor Impact" tab - Overall impact rankings
- "Recommendations" tab - Data-driven suggestions
- "Sensitivity" tab - Multi-factor sensitivity analysis
