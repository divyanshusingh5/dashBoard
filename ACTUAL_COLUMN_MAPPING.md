# Actual dat.csv Column Mapping

## Your Actual Data Structure (851,118 rows, 80 columns)

### Key Differences from Current Code:

| Current Code Expects | Your Actual dat.csv | Type | Notes |
|---------------------|-------------------|------|-------|
| `claim_id` | `CLAIMID` | int64 | Not string! |
| `claim_date` | `CLAIMCLOSEDDATE` | object (datetime string) | ✅ Already fixed |
| `predicted_pain_suffering` | `CAUSATION_HIGH_RECOMMENDATION` | float64 | ✅ Already fixed |
| `adjuster` | `ADJUSTERNAME` | object | ✅ Already fixed |
| `variance_pct` | **MISSING!** | - | Need to calculate |
| `VERSIONNAME` | **MISSING!** | - | Only have VERSIONID |
| `INJURY_GROUP_CODE` | `PRIMARY_INJURYGROUP_CODE` | object | Different name |
| `VENUE_RATING` | `VENUERATING` | object | Different name |
| `CAUTION_LEVEL` | **MISSING!** | - | Need to derive |
| `SEVERITY_SCORE` | **MISSING!** | - | Need to calculate |
| `IMPACT` | `IOL` | int64 | Different name |

### New Columns You Have:

| Column | Type | Non-Null Count | Sample Value |
|--------|------|----------------|--------------|
| `EXPSR_NBR` | object | 851,118 | 27-07J4-70V-0/02 |
| `INCIDENTDATE` | object | 851,118 | 2020-05-28 |
| `SETTLEMENTAMOUNT` | int64 | 851,118 | 0 |
| `HASATTORNEY` | int64 | 851,118 | 1 |
| `GENERALS` | float64 | 851,118 | 5900.0 |
| `AGE` | int64 | 851,118 | 42 |
| `GENDER` | int64 | 851,118 | 1 |
| `OCCUPATION_AVAILABLE` | int64 | 851,118 | 0 |
| `BODY_REGION` | object | 851,118 | Spine |
| `SETTLEMENT_SPEED_CATEGORY` | object | 851,118 | Within 5 years |
| `VENUERATINGTEXT` | object | 851,097 | Moderate |
| `VENUERATINGPOINT` | float64 | 851,097 | 2.0 |
| `VULNERABLECLAIMANT` | object | 395,831 | nan |

### Missing Columns (Need to Calculate):

1. **`variance_pct`** - Calculate as:
   ```python
   variance_pct = ((SETTLEMENTAMOUNT - CAUSATION_HIGH_RECOMMENDATION) / CAUSATION_HIGH_RECOMMENDATION) * 100
   ```

2. **`SEVERITY_SCORE`** - Can derive from DOLLARAMOUNTHIGH or GENERALS

3. **`CAUTION_LEVEL`** - Can derive from:
   - Low: DOLLARAMOUNTHIGH < 10000
   - Medium: 10000 <= DOLLARAMOUNTHIGH < 50000
   - High: DOLLARAMOUNTHIGH >= 50000

---

## Complete Column List (80 columns):

```
1.  CLAIMID                        (int64)
2.  EXPSR_NBR                      (object)
3.  CLAIMCLOSEDDATE                (object - datetime)
4.  CAUSATION_HIGH_RECOMMENDATION  (float64)
5.  INCIDENTDATE                   (object - datetime)
6.  SETTLEMENTAMOUNT               (int64)
7.  VERSIONID                      (int64)
8.  DURATIONTOREPORT               (int64)
9.  ADJUSTERNAME                   (object)
10. HASATTORNEY                    (int64)
11. GENERALS                       (float64)
12. DOLLARAMOUNTHIGH               (float64)
13. AGE                            (int64)
14. GENDER                         (int64)
15. OCCUPATION_AVAILABLE           (int64)
16. OCCUPATION                     (float64 - all NaN)
17. ALL_BODYPARTS                  (object)
18. ALL_INJURIES                   (object)
19. ALL_INJURYGROUP_CODES          (object)
20. ALL_INJURYGROUP_TEXTS          (object)
21. PRIMARY_INJURY                 (object)
22. PRIMARY_BODYPART               (object)
23. PRIMARY_INJURYGROUP_CODE       (object)
24. INJURY_COUNT                   (int64)
25. BODYPART_COUNT                 (int64)
26. INJURYGROUP_COUNT              (int64)
27. BODY_REGION                    (object)
28. SETTLEMENT_DAYS                (int64)
29. SETTLEMENT_MONTHS              (int64)
30. SETTLEMENT_YEARS               (float64)
31. SETTLEMENT_SPEED_CATEGORY      (object)
32. IOL                            (int64)
33. COUNTYNAME                     (object)
34. VENUESTATE                     (object)
35. VENUERATINGTEXT                (object)
36. VENUERATINGPOINT               (float64)
37. RATINGWEIGHT                   (float64)
38. VENUERATING                    (object)
39. VULNERABLECLAIMANT             (object)
40-80. Feature columns (Advanced_Pain_Treatment, etc.)
```

---

## Required Changes:

### 1. Schema Changes (schema.py):
- Change `claim_id` from String to Integer
- Add `CLAIMID` column
- Add `EXPSR_NBR` column
- Add `INCIDENTDATE` column
- Add `SETTLEMENTAMOUNT` column
- Add `HASATTORNEY`, `GENERALS`, `AGE`, `GENDER`
- Add calculated `variance_pct` column
- Rename `INJURY_GROUP_CODE` → `PRIMARY_INJURYGROUP_CODE`
- Rename `VENUE_RATING` → `VENUERATING`
- Add `IOL` column
- Add `BODY_REGION`, `SETTLEMENT_SPEED_CATEGORY`
- Add `VENUERATINGTEXT`, `VENUERATINGPOINT`, `VULNERABLECLAIMANT`

### 2. Migration Changes (migrate_csv_to_sqlite.py):
- Map `CLAIMID` → `claim_id`
- Calculate `variance_pct` during migration
- Calculate `SEVERITY_SCORE` from DOLLARAMOUNTHIGH
- Calculate `CAUTION_LEVEL` from DOLLARAMOUNTHIGH
- Handle all 80 columns from actual data

---

## Next Step:

Do you want me to:
1. ✅ **Update schema.py to match your actual 80 columns**
2. ✅ **Update migration script to handle your actual dat.csv**
3. ✅ **Add calculated columns (variance_pct, SEVERITY_SCORE, CAUTION_LEVEL)**
4. ✅ **Test with your actual 851,118 row dataset**

Confirm and I'll make all the changes!
