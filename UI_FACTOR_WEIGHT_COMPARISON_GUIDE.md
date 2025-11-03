# UI Factor Weight Comparison - Complete Guide

## Overview

You now have a **Factor Analysis** tab that shows you **existing weights vs suggested weights with impact** for individual severity and causation factors!

---

## What You'll See on the UI

### Navigation Path
1. Go to **Weight Recalibration** tab
2. Click **"Single Injury"** (first tab)
3. Adjust coefficients (C0-C6) in the blue box
4. Click the **"Factor Analysis"** tab (next to "Performance Charts")

---

## UI Layout - Factor Analysis Tab

### **Section 1: Coefficient Changes Impact** (Top Card)

Shows how your coefficient adjustments affect the model overall:

```
┌─────────────────────────────────────────────────────────────┐
│ Coefficient Changes Impact                                   │
│ How your coefficient adjustments affect the model            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ C1 (Severity Linear)                                         │
│ 0.150 → 0.200  [+0.050]                                      │
│ Severity factors have MORE influence                         │
│                                                               │
│ C2 (Impact Linear)                                           │
│ 0.250 → 0.350  [+0.100]                                      │
│ Impact score has MORE influence                              │
│                                                               │
│ C6 (Severity Quadratic)                                      │
│ -0.010 → -0.050  [-0.040]                                    │
│ MORE diminishing returns for high severity                   │
└─────────────────────────────────────────────────────────────┘
```

**What this means:**
- Shows which coefficients you've changed
- Current → New value with delta badge
- Plain English explanation of the impact

---

### **Section 2: Severity Factors Weight Analysis** (Main Table)

Shows individual severity factors with their contributions:

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Severity Factors Weight Analysis                                          │
│ Individual severity factors and their contribution to predictions          │
│ (affected by C1 and C6)                                                   │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ Factor                  | Avg Value | Current  | New      | Impact | Dir │
│                         |           | Contrib  | Contrib  |        |     │
│ ──────────────────────────────────────────────────────────────────────────│
│ Injections              | 0.847     | 0.1271   | 0.1687   | +8.2%  | ↑   │
│ Objective Findings      | 0.623     | 0.0935   | 0.1243   | +7.5%  | ↑   │
│ Initial Treatment       | 0.512     | 0.0768   | 0.1021   | +6.9%  | ↑   │
│ Type of Treatment       | 0.489     | 0.0734   | 0.0975   | +6.2%  | ↑   │
│ Pain Management         | 0.445     | 0.0668   | 0.0887   | +5.8%  | ↑   │
│ Severity Code           | 0.398     | 0.0597   | 0.0793   | +5.1%  | ↑   │
│ Allowed Treat Period    | 0.365     | 0.0548   | 0.0727   | +4.9%  | ↑   │
│ Injury Site             | 0.312     | 0.0468   | 0.0622   | +4.2%  | ↑   │
└───────────────────────────────────────────────────────────────────────────┘

Understanding Severity Contributions:
• Avg Value: Average value of this factor across all claims
• Current Contribution: How much this factor contributes to exponent
  with baseline coefficients (C1×value + C6×value²)
• New Contribution: How much with your adjusted coefficients
• Impact: Percentage change in contribution (positive = more influential)
```

**Column Breakdown:**

| Column | What It Shows | Example |
|--------|---------------|---------|
| **Factor** | Name of severity factor | "Injections" |
| **Avg Value** | Average across all claims | 0.847 (most claims have high injection values) |
| **Current Contribution** | Baseline equation: C1×0.847 + C6×0.847² | 0.1271 |
| **New Contribution** | With your coefficients | 0.1687 |
| **Impact** | % change | +8.2% (now more influential) |
| **Direction** | Arrow showing trend | ↑ (increase), ↓ (decrease), − (stable) |

---

### **Section 3: Causation Factors Analysis** (Second Table)

Shows individual causation factors and their multiplier effects:

```
┌───────────────────────────────────────────────────────────────────┐
│ Causation Factors Analysis                                         │
│ Individual causation factors and their multiplier effect           │
│ (fixed at 0.1× factor value)                                      │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Factor                | Avg Value | Current     | Impact if +10%  │
│                       |           | Multiplier  |                 │
│ ──────────────────────────────────────────────────────────────────│
│ Causation Probability | 0.623     | 1.0623×     | +$6.2K          │
│ Treatment Delay       | 0.489     | 1.0489×     | +$4.9K          │
│ Treatment Gaps        | 0.412     | 1.0412×     | +$4.1K          │
│ Compliance            | 0.387     | 1.0387×     | +$3.9K          │
└───────────────────────────────────────────────────────────────────┘

Understanding Causation Impact:
• Avg Value: Average value of this factor across all claims
• Current Multiplier: Prediction multiplier: (1 + 0.1 × value)
• Impact if +10%: How much predictions would increase if this factor's
  value increased by 10%
• Note: Causation multiplier coefficient (0.1) is fixed in the equation
```

**What This Tells You:**

Example: **Causation Probability** has avg value 0.623
- Current multiplier: 1.0623 (predictions are 6.23% higher)
- If value increases 10% (0.623 → 0.685):
  - New multiplier: 1.0685
  - Predictions increase by ~$6,200 on average

**Key Insight:** Causation factors work as **multipliers**, not additive terms. Higher causation values = proportionally higher settlements.

---

### **Section 4: Key Insights** (Bottom Cards)

Automatically generated insights based on your data:

```
┌───────────────────────────────────────────────────────────────┐
│ Most Influential Severity Factor                              │
│ Injections has the highest average value (0.847).             │
│ This factor has the most weight in determining severity scores│
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│ Most Influential Causation Factor                             │
│ Causation Probability has the highest average value (0.623).  │
│ Improving this factor by 10% would increase predictions by    │
│ $6.2K on average.                                             │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│ No Coefficient Changes                                        │
│ You're currently using default coefficients. Try adjusting    │
│ C1 (severity influence) or C2 (impact influence) to see how   │
│ it affects individual factors.                                │
└───────────────────────────────────────────────────────────────┘
```

---

## How to Use This View

### **Workflow:**

1. **Start with Default Coefficients**
   - Look at the Severity Factors table
   - Note which factors have highest "Avg Value"
   - These are the most important factors in your data

2. **Adjust C1 (Severity Linear)**
   - Go back to coefficient inputs
   - Change C1 from 0.150 → 0.200 (+33% increase)
   - Return to Factor Analysis tab

3. **Observe Changes**
   - "Coefficient Changes Impact" card will show the change
   - Severity Factors table will update:
     - "New Contribution" column increases
     - "Impact" column shows positive %
     - Direction arrows point up ↑

4. **Understand Impact**
   - Positive impact % = factor is now MORE influential
   - Negative impact % = factor is now LESS influential
   - ~0% = no meaningful change

---

## Real-World Examples

### Example 1: Increase Severity Influence

**Scenario:** You notice high-severity claims are under-predicted

**Action:**
```
C1: 0.150 → 0.200 (increase severity weight)
```

**What You'll See:**
```
Severity Factors Table:
┌─────────────────────────────────────────────────────┐
│ Factor       | Avg Value | Current | New    | Impact │
├─────────────────────────────────────────────────────┤
│ Injections   | 0.847     | 0.1271  | 0.1694 | +33.3% │
│ Findings     | 0.623     | 0.0935  | 0.1246 | +33.3% │
└─────────────────────────────────────────────────────┘
```

**Interpretation:**
- ALL severity factors now have 33.3% more influence
- Claims with high injection counts will have significantly higher predictions
- This uniformly increases the weight of severity in your model

---

### Example 2: Add Diminishing Returns

**Scenario:** Very severe cases seem over-predicted

**Action:**
```
C6: -0.010 → -0.050 (more negative = stronger diminishing returns)
```

**What You'll See:**
```
Coefficient Changes Impact:
C6 (Severity Quadratic): -0.010 → -0.050 [-0.040]
MORE diminishing returns for high severity

Severity Factors Table:
┌─────────────────────────────────────────────────────┐
│ Factor       | Avg Value | Current | New    | Impact │
├─────────────────────────────────────────────────────┤
│ Injections   | 0.847     | 0.1271  | 0.1200 | -5.6%  │
│ Findings     | 0.623     | 0.0935  | 0.0901 | -3.6%  │
└─────────────────────────────────────────────────────┘
```

**Interpretation:**
- Factors with HIGH values (like Injections at 0.847) are now LESS influential
- The quadratic term C6×value² becomes more negative for high values
- This "caps" the influence of extreme severity values
- Lower-value factors barely affected (smaller quadratic effect)

---

### Example 3: Understand Causation Impact

**Scenario:** You want to know which causation factor matters most

**Look At:**
```
Causation Factors Table:
┌──────────────────────────────────────────────────────┐
│ Factor                | Avg   | Impact if +10%       │
├──────────────────────────────────────────────────────┤
│ Causation Probability | 0.623 | +$6.2K               │
│ Treatment Delay       | 0.489 | +$4.9K               │
│ Treatment Gaps        | 0.412 | +$4.1K               │
│ Compliance            | 0.387 | +$3.9K               │
└──────────────────────────────────────────────────────┘
```

**Interpretation:**
- **Causation Probability** has highest average (0.623)
- Also has highest impact: +$6.2K if it increases 10%
- **Actionable insight:** Focus on improving causation documentation
- Better causation evidence → higher multiplier → higher settlements

**Business Decision:**
- Invest in better medical records review
- Improve causation analysis process
- This could increase predicted settlements by thousands per claim

---

## Understanding the Math

### **Severity Contribution Formula:**
```
Contribution = (C1 × value) + (C6 × value²)
```

**Example: Injections factor**
- Avg value: 0.847
- Default C1 = 0.150, C6 = -0.010

**Current:**
```
Contribution = (0.150 × 0.847) + (-0.010 × 0.847²)
             = 0.12705 + (-0.00717)
             = 0.1199
```

**After C1 increase to 0.200:**
```
Contribution = (0.200 × 0.847) + (-0.010 × 0.847²)
             = 0.1694 + (-0.00717)
             = 0.1622
```

**Impact:**
```
(0.1622 - 0.1199) / 0.1199 × 100 = +35.3%
```

### **Causation Multiplier Formula:**
```
Multiplier = 1 + (0.1 × factor_value)
```

**Example: Causation Probability**
- Current value: 0.623
- Multiplier: 1 + (0.1 × 0.623) = 1.0623

**If value increases 10%:**
- New value: 0.623 × 1.1 = 0.6853
- New multiplier: 1 + (0.1 × 0.6853) = 1.06853
- Impact: (1.06853 - 1.0623) / 1.0623 = +0.587%

**On $100K base prediction:**
- Current: $100K × 1.0623 = $106,230
- New: $100K × 1.06853 = $106,853
- Increase: +$623 (or +$6.2K on average across claims)

---

## Use Cases

### **Use Case 1: Identify Underweighted Factors**

**Steps:**
1. Go to Severity Factors table
2. Sort by "Avg Value" (factors with high values are most common)
3. Look at "Current Contribution"
4. If a common factor has low contribution, it's underweighted

**Example:**
```
Injections: Avg 0.847 (very high) but Contribution 0.127 (only 12.7% of exponent)
→ Severity might be underweighted overall
→ Try increasing C1
```

---

### **Use Case 2: Validate Coefficient Changes**

**Steps:**
1. Adjust C1 or C2
2. Go to Factor Analysis tab
3. Check "Coefficient Changes Impact" card
4. Verify it matches your intent

**Example:**
```
You increased C2 (Impact) to make impact more influential
✓ Card shows: "Impact score has MORE influence"
✓ Severity factors unchanged (correct - C2 only affects impact)
```

---

### **Use Case 3: Find Data Quality Issues**

**Steps:**
1. Look at "Avg Value" column
2. Check if values make sense

**Red Flags:**
```
❌ All severity factors ~0.1 or lower → Factors not populated
❌ One factor is 0.999 → Possible data error
❌ Causation probability = 0.05 → Very low, check data quality
```

---

### **Use Case 4: Prioritize Data Collection**

**Steps:**
1. Look at Causation table
2. Identify high-impact factors
3. Focus on improving those

**Example:**
```
Causation Probability impact: +$6.2K if improved 10%
Treatment Delay impact: +$4.9K if improved 10%

→ Prioritize improving causation documentation over treatment delay tracking
→ 27% more impactful ($6.2K vs $4.9K)
```

---

## FAQ

**Q: Why do all severity factors have the same % impact?**
A: When you change C1 (linear coefficient), it affects all factors proportionally. To have different impacts, adjust C6 (quadratic) which affects high-value factors more.

**Q: Can I change the causation multiplier (0.1)?**
A: No, it's fixed in the equation. You'd need to modify the equation itself in the code.

**Q: What if "Current Contribution" and "New Contribution" are the same?**
A: You haven't adjusted the relevant coefficient (C1 or C6 for severity factors).

**Q: Why are some "Impact" values negative?**
A: You decreased a coefficient (e.g., made C6 more negative), reducing that factor's influence.

**Q: What's a "good" contribution value?**
A: It depends on your data. Typically:
- Contribution of 0.10-0.20 for important factors (10-20% of exponent)
- Contribution of 0.05-0.10 for moderate factors
- Contribution < 0.05 for minor factors

**Q: The causation "Impact if +10%" seems small. Is that normal?**
A: Yes! Causation works as a multiplier (1.06×), not additive. Even small percentage increases compound across many claims and add up significantly.

---

## Technical Details

### Data Source
- Severity factors: From `severity_*` fields in your claims data
- Causation factors: From `causation_*` fields in your claims data
- Calculations done in: [FactorWeightComparison.tsx](d:\Repositories\dashBoard\frontend\src\components\recalibration\FactorWeightComparison.tsx)

### Update Frequency
- Real-time: Changes immediately when you adjust coefficients
- Recalculates on every coefficient change
- Uses React useMemo for performance

### Accuracy
- Averages calculated across ALL single injury claims in the filtered set
- Contributions calculated using actual equation from your model
- Impact percentages are relative to current contribution

---

## Summary

The **Factor Analysis** tab gives you:

✅ **Coefficient-level insights** - See how C0-C6 changes affect the model
✅ **Factor-level breakdown** - Understand individual severity/causation factors
✅ **Current vs New comparison** - See exact contribution changes
✅ **Impact percentages** - Quantify how much influence changed
✅ **Visual indicators** - Arrows show direction (↑ increase, ↓ decrease)
✅ **Actionable insights** - Identify most influential factors
✅ **Business value** - Prioritize data collection efforts

**This view answers:**
- "Which severity factors matter most?"
- "How does changing C1 affect individual factors?"
- "Which causation factor should we improve?"
- "Are my coefficient changes working as intended?"

**Use it to make data-driven decisions about weight calibration!**
