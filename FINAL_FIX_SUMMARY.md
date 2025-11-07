# Frontend Timeout Error - COMPLETE DIAGNOSIS & FIX

## ROOT CAUSE IDENTIFIED ✅

```
ERROR: Database query failed: (sqlite3.OperationalError) no such column: claims.id
```

**Location:** `backend/app/services/data_service_sqlite.py` line 47

**Problem:** The SQLAlchemy ORM is trying to query `claims.id` but the database column is named `CLAIMID`.

## Why This Causes the Timeout Error

1. Frontend tries to load Recalibration tab
2. Calls `/api/v1/claims/claims/full` endpoint
3. Endpoint calls `data_service.get_full_claims_data()`
4. Function tries to query: `session.query(Claim).all()`
5. **SQLAlchemy generates SQL with `claims.id`** ❌
6. SQL query fails: "no such column: claims.id"
7. Falls back to CSV loading (CSV doesn't exist)
8. Returns empty array: `[]`
9. Frontend receives empty data but expects 630K claims
10. Frontend shows timeout error

## The Fix

### Option 1: Fix the Schema Primary Key (RECOMMENDED)

**File:** `backend/app/db/schema.py`

**Current schema:**
```python
class Claim(Base):
    __tablename__ = 'claims'

    CLAIMID = Column(Integer, primary_key=True)  # ← This is the issue
```

**Problem:** SQLAlchemy expects the primary key to be named `id` by default. When it's named `CLAIMID`, it causes issues with some queries.

**Solution:** Add an `id` column and make `CLAIMID` a unique indexed column instead:

```python
class Claim(Base):
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True, autoincrement=True)
    CLAIMID = Column(Integer, unique=True, nullable=False, index=True)
    # ... rest of columns ...
```

**Then recreate the database:**
```bash
cd backend
# Backup current database
cp app/db/claims_analytics.db app/db/claims_analytics.db.backup

# Drop and recreate with new schema
rm app/db/claims_analytics.db

# Run migration with updated schema
./venv/Scripts/python.exe migrate_smart.py
```

### Option 2: Don't Use Recalibration Tab (QUICK FIX)

If you don't need the Recalibration tab right now, simply disable it to avoid the error.

**File:** `frontend/src/pages/IndexAggregated.tsx`

**Changes:**

1. Remove the import:
```typescript
// Remove this line:
import RecalibrationTab from "@/components/tabs/RecalibrationTab";
```

2. Remove the lazy loading code (lines 32-51):
```typescript
// Remove these lines:
const [rawClaims, setRawClaims] = useState<any[]>([]);
const [rawLoading, setRawLoading] = useState(false);
const [rawError, setRawError] = useState<string | null>(null);

useEffect(() => {
  if (activeTab === "recalibration" && rawClaims.length === 0 && !rawLoading) {
    // ... remove entire useEffect block ...
  }
}, [activeTab]);
```

3. Remove the tab trigger (find and remove):
```typescript
<TabsTrigger value="recalibration">Recalibration</TabsTrigger>
```

4. Remove the tab content (find and remove):
```typescript
<TabsContent value="recalibration">
  <ErrorBoundary FallbackComponent={TabErrorFallback} resetKeys={[activeTab]}>
    <RecalibrationTab data={rawClaims} isLoading={rawLoading} error={rawError} />
  </ErrorBoundary>
</TabsContent>
```

**Then the UI will work immediately!** The other tabs (Overview, Analysis, Business, Recommendations) all use the aggregated API which is working perfectly.

## Recommended Action Plan

**Immediate (5 minutes):**
1. Use Option 2 (disable Recalibration tab)
2. Test the UI - it should load instantly
3. Use the working tabs (Overview, Analysis, etc.)

**Later (when you need Recalibration):**
1. Implement Option 1 (fix schema)
2. Re-migrate data
3. Re-enable Recalibration tab

## What's Currently Working

- ✅ Backend server (port 8000)
- ✅ Database (630K claims)
- ✅ `/aggregation/aggregated` endpoint
- ✅ All aggregated tabs (Overview, Analysis, Business, Recommendations)
- ✅ Materialized views
- ✅ Venue shift analysis
- ✅ Table-based recommendations

## What's Broken

- ❌ `/claims/claims/full` endpoint (returns empty)
- ❌ Recalibration tab (tries to load all claims)
- ❌ Any feature that needs individual claim records

## Testing After Fix

### Test Option 2 (Disable Recalibration):
1. Make the changes to IndexAggregated.tsx
2. Save the file
3. Frontend should hot-reload
4. Refresh browser
5. UI should load immediately with Overview tab showing data

### Test Option 1 (Fix Schema):
```bash
# After recreating database and migrating data
curl "http://localhost:8000/api/v1/claims/claims/full?limit=10"
# Should return 10 claims, not empty array
```

## Summary

**Problem:** SQLAlchemy querying `claims.id` but column is `claims.CLAIMID`
**Impact:** Recalibration tab fails to load, shows timeout error
**Quick Fix:** Disable Recalibration tab (Option 2)
**Proper Fix:** Add `id` column to schema and re-migrate (Option 1)
**Recommendation:** Use Option 2 now, implement Option 1 later

The aggregated data tabs are all working perfectly - you just need to avoid the broken Recalibration tab for now!
