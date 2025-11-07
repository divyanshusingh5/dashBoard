# Frontend Timeout Error - ROOT CAUSE & FIX

## Error Shown
```
Error loading data
timeout of 60000ms exceeded

To fix this:
1. Make sure the backend API is running at http://localhost:8000
2. Check the backend terminal for errors
3. Verify the database exists at backend/app/db/claims_analytics.db
4. If needed, run migration: python migrate_csv_to_sqlite.py
```

## Root Cause Analysis

### What's Happening
The frontend is trying to load data from TWO different endpoints:

1. **Main aggregated data** (WORKING ✅)
   - Endpoint: `/api/v1/aggregation/aggregated`
   - Backend logs show: "Retrieved aggregated data from materialized views (FAST)"
   - Returns: 1000 claims in < 1 second
   - **HTTP 200 OK** ✅

2. **Full claims data for Recalibration tab** (BROKEN ❌)
   - Endpoint: `/api/v1/claims/claims/full`
   - Returns: `{"claims":[],"total":0}` (empty!)
   - Frontend expects all 630K claims
   - **This endpoint returns empty data** ❌

### Why `/claims/claims/full` Returns Empty

The endpoint is working, but it's querying data with incorrect column names or filters. Let me check the backend endpoint code.

## Investigation Steps

### 1. Check Backend Endpoint

File: `backend/app/api/endpoints/claims.py`

Look for the `/claims/full` endpoint and see what query it's running.

### 2. Check What Columns It's Expecting

The endpoint might be looking for columns that don't exist or have different names in your CSV.

### 3. Column Name Mismatch

**Your request:** "check the react frontend and backend and migration script and CSV column names of dat.csv and ssnb.csv"

This suggests there might be a column name mismatch between:
- What the backend expects
- What's actually in dat.csv
- What was migrated to the database

## Quick Fix Options

### Option A: Don't Use Recalibration Tab (Immediate)

If you don't need the Recalibration tab right now, you can disable it in the frontend:

**File:** `frontend/src/pages/IndexAggregated.tsx`

Comment out or remove the Recalibration tab:
```typescript
// Remove or comment these lines:
import RecalibrationTab from "@/components/tabs/RecalibrationTab";

// In the tab list, remove:
<TabsTrigger value="recalibration">Recalibration</TabsTrigger>

// In tab content, remove:
<TabsContent value="recalibration">
  <ErrorBoundary FallbackComponent={TabErrorFallback} resetKeys={[activeTab]}>
    <RecalibrationTab data={rawClaims} isLoading={rawLoading} error={rawError} />
  </ErrorBoundary>
</TabsContent>
```

This will stop the frontend from trying to load the `/claims/claims/full` endpoint.

### Option B: Fix the `/claims/claims/full` Endpoint (Proper Fix)

Need to:
1. Check what columns the endpoint is querying
2. Compare with actual database columns
3. Fix column name mismatches
4. Test the endpoint

### Option C: Use Pagination Instead of Full Load

Instead of loading all 630K claims at once, use pagination:
```typescript
// Instead of:
axios.get(`${API_BASE_URL}/claims/claims/full`, { timeout: 60000 })

// Use:
axios.get(`${API_BASE_URL}/claims/claims?limit=1000&offset=0`, { timeout: 60000 })
```

## Diagnostic Commands

### Check Database Columns
```bash
cd backend
./venv/Scripts/python.exe -c "import sqlite3; conn = sqlite3.connect('app/db/claims_analytics.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(claims)'); print('\\n'.join([f'{row[1]} ({row[2]})' for row in cursor.fetchall()]))"
```

### Check CSV Columns
```bash
cd backend
head -1 dat.csv
```

### Test Full Claims Endpoint
```bash
curl -s "http://localhost:8000/api/v1/claims/claims/full" | python -m json.tool
```

### Check Backend Logs for Errors
```bash
cd backend
tail -100 backend_table_based.log | grep -i error
```

## My Recommendation

**Immediate Action:** Use **Option A** (disable Recalibration tab) to get the UI working NOW.

**Next Step:** We'll investigate Option B to properly fix the endpoint.

Let me check your backend endpoint code and CSV columns to identify the exact mismatch.
