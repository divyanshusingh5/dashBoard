# Dashboard Schema Update Summary

## Overview
Updated the dashboard application to use the actual data structure with 80 columns matching your production dataset.

## Changes Completed

### 1. CSV Files Transformation
Both `dat.csv` and `weights.csv` now have the same 80-column structure:

**Key Columns (80 total):**
- Core identifiers: `CLAIMID`, `EXPSR_NBR`
- Dates: `CLAIMCLOSEDDATE`, `INCIDENTDATE`
- Financial: `CAUSATION_HIGH_RECOMMENDATION`, `SETTLEMENTAMOUNT`, `DOLLARAMOUNTHIGH`, `GENERALS`
- Version: `VERSIONID`, `DURATIONTOREPORT`
- Person info: `ADJUSTERNAME`, `HASATTORNEY`, `AGE`, `GENDER`, `OCCUPATION_AVAILABLE`, `OCCUPATION`
- Injury info: `ALL_BODYPARTS`, `ALL_INJURIES`, `ALL_INJURYGROUP_CODES`, `ALL_INJURYGROUP_TEXTS`, `PRIMARY_INJURY`, `PRIMARY_BODYPART`, `PRIMARY_INJURYGROUP_CODE`, `INJURY_COUNT`, `BODYPART_COUNT`, `INJURYGROUP_COUNT`, `BODY_REGION`
- Settlement timing: `SETTLEMENT_DAYS`, `SETTLEMENT_MONTHS`, `SETTLEMENT_YEARS`, `SETTLEMENT_SPEED_CATEGORY`
- Location/venue: `IOL`, `COUNTYNAME`, `VENUESTATE`, `VENUERATINGTEXT`, `VENUERATINGPOINT`, `RATINGWEIGHT`, `VENUERATING`, `VULNERABLECLAIMANT`
- **40+ Clinical Features** (with single quotes in CSV): `'Advanced_Pain_Treatment'`, `'Causation_Compliance'`, `'Clinical_Findings'`, `'Cognitive_Symptoms'`, etc.

**Important Note:** In the CSV files, clinical feature columns have single quotes (e.g., `'Advanced_Pain_Treatment'`), but in the database schema they don't have quotes (e.g., `Advanced_Pain_Treatment`).

### 2. Database Schema Updated
File: `backend/app/db/schema.py`

**Updates:**
- Added missing columns: `OCCUPATION_AVAILABLE`, `OCCUPATION`
- Added venue columns: `VENUERATINGTEXT`, `VENUERATINGPOINT`, `RATINGWEIGHT`, `VULNERABLECLAIMANT`
- Added settlement timing: `SETTLEMENT_DAYS`, `SETTLEMENT_MONTHS`, `SETTLEMENT_YEARS`, `SETTLEMENT_SPEED_CATEGORY`
- Added missing clinical features: `Dental_Treatment`, `Dental_Visibility`
- Increased string column sizes from 50 to 200 for clinical features
- All 40+ clinical features now mapped correctly

### 3. Data Loading Script Created
File: `backend/load_csv_to_database.py`

**Features:**
- Automatically maps CSV columns with quotes to DB columns without quotes
- Handles the SQLite variable limit (uses chunksize=10 for 83 columns)
- Calculates derived fields: `variance_pct`, `SEVERITY_SCORE`, `CAUTION_LEVEL`
- Successfully loaded 1000 claims into database

### 4. Transformation Scripts Created
- `backend/transform_dat_to_actual.py` - Transforms old dat.csv to new 80-column structure
- `backend/transform_weights_to_actual.py` - Transforms weights.csv to new 80-column structure with numeric values

## Remaining Tasks

### Backend Updates Needed

#### 1. Update Data Service (CRITICAL)
File: `backend/app/services/data_service.py`

**Changes needed:**
- Remove references to old column names:
  - `InjuryGroup` → `PRIMARY_INJURYGROUP_CODE`
  - `Adjuster` → `ADJUSTERNAME`
  - `State` → `VENUESTATE`
  - `County` → `COUNTYNAME`
  - `SettlementYear` → Extract from `CLAIMCLOSEDDATE`
  - `SettlementAmount` → `DOLLARAMOUNTHIGH` or `SETTLEMENTAMOUNT`
  - `ModelPrediction` → `CAUSATION_HIGH_RECOMMENDATION`
  - `ConsensusValue` → `DOLLARAMOUNTHIGH`

#### 2. Update API Endpoints
Files to update:
- `backend/app/api/endpoints/aggregation.py`
- `backend/app/api/endpoints/aggregation_optimized_venue_shift.py`
- Any other endpoint files that reference old column names

**Key changes:**
- Update all column name references
- Update filter logic to use new column names
- Update aggregation queries

#### 3. Create SQLite-based Data Service
File: `backend/app/services/data_service_sqlite.py` (if it exists)

**Ensure it:**
- Maps CSV columns correctly (with quotes → without quotes)
- Uses correct column names in queries
- Handles clinical feature columns properly

### Frontend Updates Needed

#### 1. Update Type Definitions
File: `frontend/src/types/claims.ts`

**Add/Update types:**
```typescript
export interface ClaimData {
  CLAIMID: number;
  EXPSR_NBR: string;
  CLAIMCLOSEDDATE: string;
  CAUSATION_HIGH_RECOMMENDATION: number;
  INCIDENTDATE: string;
  SETTLEMENTAMOUNT: number;
  DOLLARAMOUNTHIGH: number;
  GENERALS: number;
  VERSIONID: number;
  DURATIONTOREPORT: number;
  ADJUSTERNAME: string;
  HASATTORNEY: string | number;
  AGE: number;
  GENDER: string | number;
  OCCUPATION_AVAILABLE: number;
  OCCUPATION?: string;
  ALL_BODYPARTS: string;
  ALL_INJURIES: string;
  ALL_INJURYGROUP_CODES: string;
  ALL_INJURYGROUP_TEXTS: string;
  PRIMARY_INJURY: string;
  PRIMARY_BODYPART: string;
  PRIMARY_INJURYGROUP_CODE: string;
  INJURY_COUNT: number;
  BODYPART_COUNT: number;
  INJURYGROUP_COUNT: number;
  BODY_REGION: string;
  SETTLEMENT_DAYS: number;
  SETTLEMENT_MONTHS: number;
  SETTLEMENT_YEARS: number;
  SETTLEMENT_SPEED_CATEGORY: string;
  IOL: number;
  COUNTYNAME: string;
  VENUESTATE: string;
  VENUERATINGTEXT: string;
  VENUERATINGPOINT: number;
  RATINGWEIGHT: number;
  VENUERATING: string;
  VULNERABLECLAIMANT?: string;
  // 40+ clinical features
  Advanced_Pain_Treatment?: string;
  Causation_Compliance?: string;
  Clinical_Findings?: string;
  // ... add all 40 features

  // Calculated fields
  SEVERITY_SCORE?: number;
  CAUTION_LEVEL?: string;
  variance_pct?: number;
}

export interface FilterState {
  year: string;
  injuryGroupCode: string;  // was: injuryGroup
  county: string;
  venueRating: string;
  impact: string;  // IOL
  severityScore: string;
  cautionLevel: string;
  version?: string;
}
```

#### 2. Update useClaimsData Hook
File: `frontend/src/hooks/useClaimsData.ts`

**Current mapping is mostly correct, but verify:**
- Year extraction from `CLAIMCLOSEDDATE`
- Injury group from `PRIMARY_INJURYGROUP_CODE`
- Venue rating from `VENUERATING`
- Impact from `IOL`

#### 3. Update FilterSidebar Component
File: `frontend/src/components/dashboard/FilterSidebar.tsx`

**Changes:**
- Verify filter keys match new FilterState
- Add any new filters for clinical features if needed
- Update labels if necessary

#### 4. Update Dashboard Components
Files to check:
- All graph/chart components that reference claim data
- Any components using old column names
- Settlement speed category usage

## Quick Reference: Column Name Mapping

### Old → New Column Names
```
InjuryGroup          → PRIMARY_INJURYGROUP_CODE
Adjuster             → ADJUSTERNAME
State                → VENUESTATE
County               → COUNTYNAME
SettlementYear       → Extract from CLAIMCLOSEDDATE
SettlementAmount     → DOLLARAMOUNTHIGH or SETTLEMENTAMOUNT
ModelPrediction      → CAUSATION_HIGH_RECOMMENDATION
ConsensusValue       → DOLLARAMOUNTHIGH
IMPACT               → IOL
WEIGHTINGINDEX       → RATINGWEIGHT
```

### Clinical Features (40+ columns)
In CSV: `'Feature_Name'` (with single quotes)
In DB: `Feature_Name` (without quotes)
In Frontend: Access as `claim.Feature_Name`

## Testing Checklist

### Backend Tests
- [ ] Start backend server: `cd backend && ./venv/Scripts/python.exe -m uvicorn app.main:app --reload`
- [ ] Test `/api/v1/claims/claims/full` endpoint
- [ ] Test `/api/v1/aggregated` endpoint
- [ ] Verify filter options endpoint
- [ ] Check that all columns are returned correctly

### Frontend Tests
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Dashboard loads without errors
- [ ] Filters work correctly
- [ ] Graphs display data
- [ ] Claims table shows correct columns
- [ ] No console errors related to missing columns

## Database Files
- Location: `backend/app/db/claims_analytics.db`
- Backup: `backend/data/backup_YYYYMMDD_HHMMSS/`

## Scripts for Future Use

### Reload Database from CSV
```bash
cd backend
./venv/Scripts/python.exe load_csv_to_database.py
```

### Transform New CSV Files
```bash
cd backend
./venv/Scripts/python.exe transform_dat_to_actual.py
./venv/Scripts/python.exe transform_weights_to_actual.py
```

## Notes
1. The weights.csv now has the same 80-column structure as dat.csv
2. For weights, the clinical feature columns contain numeric weight values instead of text
3. The database properly handles NaN/null values for optional fields
4. All date fields are stored as strings in format "YYYY-MM-DD HH:MM:SS.000"

## Next Steps
1. Update backend data service column references
2. Update all API endpoints
3. Update frontend types
4. Test thoroughly
5. Deploy changes

---
Generated: 2025-01-04
