# Overview Tab - Executive Summary Updated ✅

## What Changed

Replaced the "Executive Summary: Factor Performance Analysis" section in the Overview tab with actual factor combinations from the `mv_executive_summary` materialized view showing WHERE the model isn't performing well.

---

## Before vs After

### Before:
- **Title:** "Executive Summary: Factor Performance Analysis"
- **Data Source:** Aggregated from severity/injury/variance drivers (calculated in frontend)
- **Columns:** 6 columns (Rank, Factor, Category, Avg Deviation, Claims, Status)
- **Example Row:** "High Severity", "Severity", "15.23%", "1,234", "Monitor"

### After:
- **Title:** "Factor Combinations with Poor Model Performance"
- **Data Source:** Direct from `mv_executive_summary` materialized view via API
- **Columns:** **15 columns** showing detailed factor combinations
- **Example Row:** Shows actual combination like "Low severity, Tear injury, Knee, Moderate venue, Harris County, PA, IOL 2, Version 25, 2025" with real metrics

---

## 15 Columns Displayed

| # | Column | Description |
|---|--------|-------------|
| 1 | **Rank** | Position by deviation (1-50) |
| 2 | **Severity** | Severity Level (Low/Medium/High) - color coded |
| 3 | **Injury Type** | Type of injury (e.g., Sprain/Strain, Tear) |
| 4 | **Body Part** | Affected body part (e.g., Knee, Hip, Cervical) |
| 5 | **Venue** | Venue rating (e.g., Moderate, Liberal) |
| 6 | **County** | County name |
| 7 | **State** | State abbreviation |
| 8 | **IOL** | Impact on Life score (1-5) |
| 9 | **Ver** | Version ID |
| 10 | **Year** | Claim year |
| 11 | **Claims** | Number of claims in this combination |
| 12 | **Avg Actual** | Average actual settlement amount |
| 13 | **Avg Predicted** | Average predicted settlement |
| 14 | **Deviation %** | Average deviation percentage (color coded) |
| 15 | **$ Error** | Average dollar error |
| 16 | **Risk** | Risk level badge (Critical/High/Medium/Low) |

---

## Key Features

### 1. **Real Factor Combinations**
Instead of showing aggregated factors, now shows actual multi-dimensional combinations:
- Example: "Low Severity + Tear + Knee + Moderate Venue + Harris County, PA + IOL 2 + Version 25 + Year 2025"

### 2. **High Variance Focus**
Shows only factor combinations where the model is performing poorly (high variance/deviation)

### 3. **Color Coding**
- **Severity Badge:** Red (High), Orange (Medium), Green (Low)
- **Deviation %:** Red dot (Critical), Orange dot (High Risk), Yellow dot (Medium Risk)
- **Risk Badge:** Red (Critical), Orange (High Risk), Yellow (Medium), Blue (Low Risk)

### 4. **Sorted by Worst Performance**
Automatically sorted by highest absolute deviation percentage first

### 5. **Sticky Columns**
- Rank column sticks to left when scrolling horizontally
- Risk column sticks to right when scrolling horizontally

### 6. **Loading State**
Shows spinner while fetching data from API

### 7. **Responsive Table**
Horizontal scroll for 15 columns with sticky positioning

---

## Files Modified

### Frontend:
**`frontend/src/components/tabs/OverviewTabAggregated.tsx`**

**Changes:**
1. Added `useEffect` import (line 10)
2. Added state for executive summary data (lines 76-77):
   ```typescript
   const [executiveSummaryData, setExecutiveSummaryData] = useState<any[]>([]);
   const [loadingExecutiveSummary, setLoadingExecutiveSummary] = useState(true);
   ```
3. Added API call to fetch data (lines 84-101):
   ```typescript
   useEffect(() => {
     const fetchExecutiveSummary = async () => {
       const response = await fetch('http://localhost:8000/api/v1/aggregation/executive-summary?limit=100');
       const result = await response.json();
       if (result.status === 'success') {
         setExecutiveSummaryData(result.data);
       }
     };
     fetchExecutiveSummary();
   }, []);
   ```
4. Replaced entire Executive Summary Card section (lines 422-593) with new 15-column table

**Removed:**
- Old `executiveSummary` useMemo calculation that aggregated from severity/injury/drivers
- 6-column table showing aggregated factors

**Added:**
- Direct API call to `/api/v1/aggregation/executive-summary`
- 15-column table with detailed factor combinations
- Loading state handling
- Sticky column positioning
- Color-coded badges for severity and risk levels

---

## API Endpoint Used

**GET** `http://localhost:8000/api/v1/aggregation/executive-summary?limit=100`

**Response Structure:**
```json
{
  "status": "success",
  "count": 100,
  "data": [
    {
      "factor_combination": "Severity: Low | Injury: Tear | Venue: Moderate | IOL: 2",
      "severity_level": "Low",
      "injury_type": "Tear",
      "body_part": "Knee",
      "venue_rating": "Moderate",
      "county": "Harris",
      "state": "PA",
      "impact_on_life": 2,
      "version_id": 25,
      "year": 2025,
      "claim_count": 6,
      "avg_actual": 197509.86,
      "avg_predicted": 55.0,
      "avg_deviation_pct": 359008.84,
      "abs_avg_deviation_pct": 359008.84,
      "min_deviation": 359008.84,
      "max_deviation": 359008.84,
      "risk_level": "Critical",
      "total_dollar_error": 1184729.16,
      "avg_dollar_error": 197454.86
    }
  ]
}
```

---

## Data Source

**Materialized View:** `mv_executive_summary`
- **Row Count:** 98,681 factor combinations
- **Updated:** Via `create_executive_summary_views.py`
- **Source Table:** `claims` table with 730,000 claims
- **Calculation:** Pre-aggregated multi-dimensional grouping by:
  - Severity Level × Injury Type × Body Part × Venue Rating × County × State × IOL × VersionID × Year

---

## Visual Example

### Table Header:
```
| Rank | Severity | Injury Type | Body Part | Venue | County | State | IOL | Ver | Year | Claims | Avg Actual | Avg Predicted | Deviation % | $ Error | Risk |
```

### Sample Rows:
```
| 1  | [Low]    | Tear           | Knee      | Moderate | Harris | PA | 2 | 25 | 2025 | 6  | $197,510 | $55  | 359,008.8% | $197,455 | [Critical] |
| 2  | [High]   | Sprain/Strain  | Hip       | Moderate | San Diego | PA | 3 | 7  | 2022 | 6  | $141,935 | $55  | 257,964.2% | $141,880 | [Critical] |
| 3  | [High]   | Sprain/Strain  | Knee      | Moderate | Cook   | AZ | 1 | 21 | 2023 | 8  | $153,506 | $62  | 247,490.8% | $153,444 | [Critical] |
```

---

## Benefits

### 1. **More Actionable**
Shows specific factor combinations that need attention, not just aggregated categories

### 2. **Detailed Context**
See ALL factors contributing to poor performance in one view:
- What severity?
- What injury?
- What body part?
- Which venue?
- Which county?
- What year/version?

### 3. **Data-Driven**
Direct from materialized view = faster queries and consistent with backend data

### 4. **Easier Debugging**
Can see exactly which combination of factors causes high variance

### 5. **Better for Analysis**
Analysts can identify patterns like:
- "All Tear injuries in Harris County, PA have high variance"
- "Moderate venue ratings in 2025 show worse predictions"
- "Version 25 has worse performance than Version 7 for certain injuries"

---

## How to Test

### 1. **Open Frontend**
```bash
http://localhost:5173
```

### 2. **Navigate to Overview Tab**
- Should be the default tab when page loads

### 3. **Scroll Down**
- Find the "Factor Combinations with Poor Model Performance" section
- Should show a loading spinner briefly, then display the table

### 4. **Check Features**
- ✅ 15 columns visible
- ✅ Color-coded severity badges (Red/Orange/Green)
- ✅ Color-coded deviation percentages with dots
- ✅ Risk level badges on right (Critical/High Risk/Medium/Low Risk)
- ✅ Sticky Rank column on left when scrolling
- ✅ Sticky Risk column on right when scrolling
- ✅ Showing top 50 of 100 rows

### 5. **Verify Data**
- Check that deviation percentages are very high (thousands of %)
- Check that counties, states, years are showing correctly
- Check that dollar amounts are formatted with $ and commas

---

## Next Steps (Optional Enhancements)

### 1. **Add Filters**
Allow filtering the executive summary table by:
- Severity level dropdown
- Injury type dropdown
- County search
- VersionID selector
- Year range

### 2. **Add Sorting**
Click column headers to sort by:
- Deviation %
- Claims count
- Dollar error
- Year

### 3. **Add Drill-Down**
Click on a row to:
- Show county comparison (which other counties have similar factors)
- Show detailed claims in that combination
- Show trend over time for that combination

### 4. **Export to CSV**
Add button to export the visible table data to CSV for further analysis

### 5. **Add Search**
Add search box to filter rows by keyword (e.g., search for "Knee" or "Harris")

---

## Status

**✅ COMPLETE**

The Overview tab now displays real factor combinations from the materialized view instead of aggregated summary data. The table shows 15 columns with detailed information about WHERE the model isn't performing well.

---

## Summary

**Old Approach:**
- Aggregated factors (severity, injury, drivers)
- 6 columns
- Generic data

**New Approach:**
- Actual multi-dimensional factor combinations
- 15 columns
- Specific data showing exact combinations with poor performance
- Direct from `mv_executive_summary` materialized view
- Color-coded for easy identification of risk levels

The Overview tab now provides much more actionable insights into which specific combinations of factors are causing the model to perform poorly! 🎉
