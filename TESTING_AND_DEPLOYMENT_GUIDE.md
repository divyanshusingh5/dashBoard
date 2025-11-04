# Testing and Deployment Guide

## What Was Changed

### ✅ Completed Updates

#### Backend
1. **CSV Files** - Both `dat.csv` and `weights.csv` now have 80 columns matching actual data structure
2. **Database Schema** ([schema.py](backend/app/db/schema.py)) - All columns added/updated
3. **Data Service** ([data_service.py](backend/app/services/data_service.py)) - Updated column references
4. **Aggregation API** ([aggregation.py](backend/app/api/endpoints/aggregation.py)) - Fixed column names
5. **Database Loaded** - 1,000 claims successfully loaded into SQLite

#### Frontend
1. **Types** ([claims.ts](frontend/src/types/claims.ts)) - Updated ClaimData interface
2. **Data Hook** ([useClaimsData.ts](frontend/src/hooks/useClaimsData.ts)) - Updated column mappings
3. **Filters** - FilterSidebar already uses correct structure

## How to Test

### Step 1: Test Backend API

#### Start Backend Server
```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

#### Test Endpoints

**1. Test Full Claims Data**
```bash
# Open browser or use curl
http://localhost:8000/api/v1/claims/claims/full
```
Expected: JSON array of claims with 80+ columns including `CLAIMID`, `CAUSATION_HIGH_RECOMMENDATION`, `DOLLARAMOUNTHIGH`, `PRIMARY_INJURYGROUP_CODE`, `IOL`, `VENUERATING`, etc.

**2. Test Aggregated Data**
```bash
http://localhost:8000/api/v1/aggregated?use_fast=false
```
Expected: JSON with aggregated data for dashboard (yearSeverity, countyYear, injuryGroup, adjusterPerformance, venueAnalysis)

**3. Test Filter Options**
```bash
http://localhost:8000/api/v1/claims/filters
```
Expected: JSON with arrays of:
- `injury_groups` (PRIMARY_INJURYGROUP_CODE values)
- `adjusters` (ADJUSTERNAME values)
- `states` (VENUESTATE values)
- `counties` (COUNTYNAME values)
- `years` (extracted from CLAIMCLOSEDDATE)

#### Check for Errors
- ✅ No "column not found" errors
- ✅ Data returns successfully
- ✅ No TypeErrors or KeyErrors in logs

### Step 2: Test Frontend Dashboard

#### Start Frontend
```bash
cd frontend
npm install  # if needed
npm run dev
```

#### Test Dashboard UI

**1. Dashboard Loads**
- [ ] Opens without errors (http://localhost:5173)
- [ ] No red error screens
- [ ] Check browser console (F12) for errors

**2. Filters Work**
- [ ] Year filter shows years from CLAIMCLOSEDDATE
- [ ] Injury Group filter shows PRIMARY_INJURYGROUP_CODE values
- [ ] County filter shows COUNTYNAME values
- [ ] Venue Rating filter shows VENUERATING values
- [ ] Impact (IOL) filter shows IOL values
- [ ] Applying filters updates dashboard

**3. Graphs Display Data**
- [ ] Year-Severity chart shows data
- [ ] County analysis shows data
- [ ] Injury group chart shows data
- [ ] Adjuster performance table shows data
- [ ] Venue analysis shows data
- [ ] No "undefined" or "null" values in graphs

**4. Data Tables**
- [ ] Claims table shows correct columns:
  - CLAIMID
  - CLAIMCLOSEDDATE
  - CAUSATION_HIGH_RECOMMENDATION
  - DOLLARAMOUNTHIGH
  - PRIMARY_INJURYGROUP_CODE
  - ADJUSTERNAME
  - COUNTYNAME
  - VENUERATING
  - IOL
- [ ] Data displays correctly
- [ ] Sorting works
- [ ] Pagination works

### Step 3: Test Clinical Features

**1. Check Clinical Feature Columns**
Backend API should return clinical features without quotes:
```json
{
  "CLAIMID": 1,
  "Advanced_Pain_Treatment": "No",
  "Causation_Compliance": "Compliant",
  "Clinical_Findings": "Yes",
  ...
}
```

**2. Frontend Should Access**
```typescript
claim.Advanced_Pain_Treatment
claim.Causation_Compliance
// etc.
```

## Common Issues and Fixes

### Issue 1: Backend Returns Empty Data
**Symptom:** API returns `[]` or `{"claims": []}`

**Fix:**
```bash
cd backend
# Reload database
./venv/Scripts/python.exe load_csv_to_database.py
```

### Issue 2: Column Not Found Error
**Symptom:** Error like `KeyError: 'InjuryGroup'` or `column not found`

**Cause:** Old column name still referenced somewhere

**Fix:**
1. Check error stack trace to find file
2. Replace old column names with new ones (see mapping below)

### Issue 3: Frontend Shows "undefined"
**Symptom:** Dashboard shows "undefined" or "NaN" values

**Cause:** Frontend trying to access old column names

**Fix:**
Check components and update references:
- `claim.IMPACT` → `claim.IOL`
- `claim.INJURY_GROUP_CODE` → `claim.PRIMARY_INJURYGROUP_CODE`
- `claim.VENUE_RATING` → `claim.VENUERATING`
- `claim.adjuster` → `claim.ADJUSTERNAME`

### Issue 4: Graphs Don't Display
**Symptom:** Empty graphs or "No data available"

**Cause:** Graph components expecting old column names

**Fix:**
Update graph component prop mappings to use new column names

## Column Name Quick Reference

```
OLD COLUMN NAME              → NEW COLUMN NAME
---------------------          -------------------
claim_id                     → CLAIMID
claim_date                   → CLAIMCLOSEDDATE
IMPACT                       → IOL
INJURY_GROUP_CODE            → PRIMARY_INJURYGROUP_CODE
VENUE_RATING                 → VENUERATING
adjuster                     → ADJUSTERNAME
CAUSATION__HIGH_RECOMMENDATION → CAUSATION_HIGH_RECOMMENDATION
WEIGHTINGINDEX               → RATINGWEIGHT
```

## Deployment Checklist

### Before Deployment
- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] No console errors
- [ ] Filters work correctly
- [ ] Graphs display data
- [ ] Data tables show correct columns
- [ ] Clinical features accessible

### Database
- [ ] Backup existing database: `backend/app/db/claims_analytics.db`
- [ ] Load new data: `./venv/Scripts/python.exe load_csv_to_database.py`
- [ ] Verify record count matches expectations

### CSV Files
- [ ] Backup current CSV files in `backend/data/backup_*/`
- [ ] Verify both dat.csv and weights.csv have 80 columns
- [ ] Verify clinical feature columns have single quotes in CSV
- [ ] Test loading CSV into pandas without errors

### Code Review
- [ ] All old column references updated
- [ ] Type definitions match actual data
- [ ] No hardcoded old column names
- [ ] Comments updated

## Performance Notes

### Current Performance
- **Claims Count:** 1,000 records
- **Load Time:** < 2 seconds
- **Aggregation:** < 3 seconds

### For Larger Datasets (850K+ records)
If you replace test data with actual 850K records:

1. **Use Fast Mode**
```typescript
// Frontend API call
const response = await axios.get(`${API_URL}/aggregated?use_fast=true`);
```

2. **Create Materialized Views**
Run backend optimization scripts to create pre-computed views

3. **Pagination**
Use paginated endpoints for large data tables

4. **Lazy Loading**
Load graphs on-demand instead of all at once

## Verification Script

Run this to verify everything is working:

```bash
# Backend health check
cd backend
./venv/Scripts/python.exe -c "
import pandas as pd
from pathlib import Path
import sqlite3

# Check CSV
df = pd.read_csv('data/dat.csv', nrows=5)
print(f'✓ CSV loaded: {df.shape[1]} columns')
print(f'✓ Sample columns: {list(df.columns[:10])}')

# Check database
conn = sqlite3.connect('app/db/claims_analytics.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM claims')
count = cursor.fetchone()[0]
print(f'✓ Database has {count} claims')

cursor.execute('PRAGMA table_info(claims)')
cols = cursor.fetchall()
print(f'✓ Claims table has {len(cols)} columns')
conn.close()

print('\\n✅ Backend verification passed!')
"
```

## Next Steps After Testing

1. **If all tests pass:**
   - Deploy to production
   - Monitor for errors
   - Check performance metrics

2. **If tests fail:**
   - Review error messages
   - Check SCHEMA_UPDATE_SUMMARY.md for column mappings
   - Update remaining components
   - Re-test

3. **Additional enhancements:**
   - Add more filters for clinical features
   - Create dedicated views for clinical feature analysis
   - Optimize queries for 850K+ records
   - Add data export functionality

## Support

For issues:
1. Check browser console (F12) for frontend errors
2. Check backend terminal for API errors
3. Review SCHEMA_UPDATE_SUMMARY.md for column mappings
4. Verify CSV files have correct structure (80 columns)

---
Last Updated: 2025-01-04
