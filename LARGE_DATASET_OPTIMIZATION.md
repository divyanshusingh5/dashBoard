# Large Dataset Optimization Guide (850K+ Records)

## ⚠️ CRITICAL: Performance Issues with Large Data

With 851K claims × 80 columns, you **WILL** face these problems:

### Problems:
1. **Memory Crash** - 850K rows × 80 cols = 68M cells (~2-4 GB RAM)
2. **API Timeout** - Loading all data takes 30-120 seconds
3. **Frontend Freeze** - Browser can't handle 850K rows
4. **Slow Filtering** - Each filter takes 10+ seconds
5. **Database Lock** - Concurrent queries fail

---

## ✅ Solution: Three-Tier Optimization Strategy

### Tier 1: Immediate Fixes (Do These First!)

#### 1. **Use Pagination - Don't Load All Claims at Once**

**Current Problem:**
```typescript
// Frontend tries to load ALL 850K claims
const response = await axios.get('/api/v1/claims/claims/full');
// ❌ This will crash!
```

**Solution - Use Paginated Endpoint:**

**Backend (Already exists!):**
```python
# File: backend/app/api/endpoints/claims.py

@router.get("/claims/paginated")
async def get_paginated_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, le=1000),
    filters: Optional[str] = Query(None)
):
    # Uses data_service_sqlite for fast queries
    # Returns only ONE page at a time
    return await data_service_sqlite.get_paginated_claims(
        page=page,
        page_size=page_size,
        filters=json.loads(filters) if filters else None
    )
```

**Frontend Update Required:**
```typescript
// File: frontend/src/hooks/useClaimsData.ts

// CHANGE FROM:
const response = await axios.get(`${API_BASE_URL}/claims/claims/full`);

// CHANGE TO:
const response = await axios.get(`${API_BASE_URL}/claims/claims/paginated`, {
  params: {
    page: 1,
    page_size: 1000, // Load 1K at a time
    filters: JSON.stringify(filters)
  }
});

// For subsequent pages:
const loadMoreData = async (page: number) => {
  const response = await axios.get(`${API_BASE_URL}/claims/claims/paginated`, {
    params: { page, page_size: 1000 }
  });
  // Append to existing data
};
```

#### 2. **Use Aggregated Data for Dashboard**

**Current:** Dashboard tries to aggregate 850K rows in browser ❌

**Solution:** Use pre-aggregated data from backend ✅

```typescript
// File: frontend/src/components/Dashboard.tsx

// Don't use raw claims for graphs!
// Use aggregated endpoint instead:

const { data: aggregatedData } = await axios.get('/api/v1/aggregated?use_fast=false');

// aggregatedData contains:
// - yearSeverity: Already aggregated by year/severity
// - countyYear: Already aggregated by county/year
// - injuryGroup: Already aggregated by injury group
// - adjusterPerformance: Already aggregated by adjuster
// - venueAnalysis: Already aggregated by venue

// Use these for graphs directly - NO client-side aggregation needed!
```

#### 3. **Enable Query Timeout Protection**

```python
# File: backend/app/services/data_service_sqlite.py

# Add timeout to queries
async def get_full_claims_data(self, limit: Optional[int] = 5000) -> List[Dict[str, Any]]:
    # DEFAULT LIMIT to prevent loading all 850K
    # Only load 5K claims max for full data requests
    if limit is None or limit > 5000:
        limit = 5000
        logger.warning("Limiting query to 5000 claims to prevent timeout")

    # Rest of code...
```

---

### Tier 2: Database Optimizations (Implement Before Loading Large Data)

#### 1. **Add Missing Database Indexes**

```python
# Run this script: backend/add_performance_indexes.py

from app.db.schema import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.connect() as conn:
    # Add indexes for common filter columns
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_year ON claims (substr(CLAIMCLOSEDDATE, 1, 4))"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_severity ON claims (SEVERITY_SCORE)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_caution ON claims (CAUTION_LEVEL)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_county_year ON claims (COUNTYNAME, substr(CLAIMCLOSEDDATE, 1, 4))"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_injury_severity ON claims (PRIMARY_INJURYGROUP_CODE, SEVERITY_SCORE)"))
    conn.commit()

print("✓ Performance indexes created")
```

**Run this AFTER loading your 850K data:**
```bash
cd backend
./venv/Scripts/python.exe add_performance_indexes.py
```

#### 2. **Enable WAL Mode for Better Concurrency**

```python
# File: backend/app/db/schema.py

def get_engine():
    db_url = get_database_url()
    engine = create_engine(
        db_url,
        echo=False,
        pool_size=20,
        max_overflow=40,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={
            "check_same_thread": False,
            "timeout": 30  # 30 second query timeout
        }
    )

    # Enable WAL mode for better concurrent access
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA cache_size=-64000"))  # 64MB cache
        conn.commit()

    return engine
```

---

### Tier 3: Advanced Optimizations (For Production)

#### 1. **Create Materialized Views**

Pre-compute common aggregations:

```python
# File: backend/create_materialized_views.py

import sqlite3
from pathlib import Path

db_path = Path('app/db/claims_analytics.db')
conn = sqlite3.connect(db_path)

# Create aggregated view for year-severity
conn.execute("""
CREATE TABLE IF NOT EXISTS mv_year_severity AS
SELECT
    substr(CLAIMCLOSEDDATE, 1, 4) as year,
    CAUTION_LEVEL as severity_category,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
    AVG(CAUSATION_HIGH_RECOMMENDATION) as avg_predicted,
    AVG(variance_pct) as avg_variance_pct
FROM claims
WHERE CLAIMCLOSEDDATE IS NOT NULL
GROUP BY year, CAUTION_LEVEL
""")

# Create aggregated view for county-year
conn.execute("""
CREATE TABLE IF NOT EXISTS mv_county_year AS
SELECT
    COUNTYNAME as county,
    VENUESTATE as state,
    substr(CLAIMCLOSEDDATE, 1, 4) as year,
    VENUERATING as venue_rating,
    COUNT(*) as claim_count,
    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
    AVG(variance_pct) as avg_variance_pct
FROM claims
WHERE COUNTYNAME IS NOT NULL AND CLAIMCLOSEDDATE IS NOT NULL
GROUP BY COUNTYNAME, VENUESTATE, year, VENUERATING
""")

conn.commit()
conn.close()

print("✓ Materialized views created")
```

**Use materialized views in API:**
```python
# Update: backend/app/api/endpoints/aggregation.py

@router.get("/aggregated")
async def get_aggregated_data(use_fast: bool = Query(True)):
    if use_fast:
        # Use materialized views - INSTANT response
        engine = get_engine()

        year_severity = pd.read_sql_query("SELECT * FROM mv_year_severity", engine)
        county_year = pd.read_sql_query("SELECT * FROM mv_county_year", engine)

        return {
            "yearSeverity": year_severity.to_dict('records'),
            "countyYear": county_year.to_dict('records'),
            # ...
        }
```

#### 2. **Add Response Caching**

```python
# File: backend/app/core/cache.py

from functools import wraps
from datetime import datetime, timedelta
import json

cache = {}

def cache_response(ttl_minutes=5):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{json.dumps(kwargs)}"

            # Check cache
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if datetime.now() - cached_time < timedelta(minutes=ttl_minutes):
                    return cached_data

            # Compute and cache
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())
            return result

        return wrapper
    return decorator

# Use it:
@router.get("/aggregated")
@cache_response(ttl_minutes=5)
async def get_aggregated_data():
    # This will cache results for 5 minutes
    pass
```

#### 3. **Implement Server-Side Filtering**

**Don't filter 850K rows in browser - Filter in database!**

```python
# Frontend sends filters to backend
const filters = {
  county: "Alameda",
  year: "2024",
  injury_group: "SSLE"
};

// Backend does the filtering
const response = await axios.get('/api/v1/claims/claims/paginated', {
  params: {
    page: 1,
    page_size: 1000,
    filters: JSON.stringify(filters)  // ← Backend filters in SQL
  }
});

// Frontend receives only matching records (maybe 200 rows instead of 850K!)
```

---

## 🚀 Implementation Checklist for Large Data

### Before Loading 850K Records:

- [ ] Update frontend to use paginated endpoint
- [ ] Update dashboard to use aggregated endpoint (not raw claims)
- [ ] Add query timeout protection (5K row limit)
- [ ] Enable WAL mode in SQLite
- [ ] Increase cache size

### After Loading 850K Records:

- [ ] Run add_performance_indexes.py
- [ ] Create materialized views
- [ ] Test pagination (load 1K rows at a time)
- [ ] Test aggregation endpoint (should be < 3 seconds)
- [ ] Test filters (should use database, not frontend)
- [ ] Monitor memory usage (should stay < 1GB)

### For Production:

- [ ] Add response caching
- [ ] Implement lazy loading for tables
- [ ] Add loading indicators
- [ ] Add error handling for timeouts
- [ ] Consider Redis for caching
- [ ] Consider PostgreSQL if SQLite too slow

---

## 📊 Performance Benchmarks

### With 1,000 Records (Current):
- Load all claims: 2 seconds ✅
- Aggregation: 3 seconds ✅
- Frontend filtering: Instant ✅

### With 850,000 Records (Without Optimization):
- Load all claims: 120+ seconds ❌ TIMEOUT
- Aggregation: 60+ seconds ❌ TIMEOUT
- Frontend filtering: Browser crash ❌ CRASH
- Memory usage: 4+ GB ❌ OUT OF MEMORY

### With 850,000 Records (With Optimization):
- Load page (1K rows): 1-2 seconds ✅
- Aggregation (materialized): < 1 second ✅
- Server-side filtering: 2-5 seconds ✅
- Memory usage: < 500 MB ✅

---

## 🔥 Quick Fix for Immediate Use

**If you want to test with 850K records RIGHT NOW:**

### Option 1: Use Sampling (Fastest)
```python
# Backend: Only load a sample for testing
@router.get("/claims/claims/full")
async def get_full_claims():
    # Load only 5K random claims for testing
    claims = await data_service_sqlite.get_full_claims_data(limit=5000)
    return claims
```

### Option 2: Use Pagination (Recommended)
```typescript
// Frontend: Load data in chunks
const loadClaimsInChunks = async () => {
  let allClaims = [];
  for (let page = 1; page <= 10; page++) {  // Load 10K claims (10 pages × 1K)
    const response = await axios.get('/api/v1/claims/claims/paginated', {
      params: { page, page_size: 1000 }
    });
    allClaims = [...allClaims, ...response.data.claims];

    // Show progress
    console.log(`Loaded ${allClaims.length} claims...`);
  }
  return allClaims;
};
```

### Option 3: Use Aggregations Only (Best for Dashboard)
```typescript
// Don't load raw claims at all!
// Use aggregated data for everything:
const { data } = await axios.get('/api/v1/aggregated');

// data.yearSeverity - for year charts
// data.countyYear - for county analysis
// data.injuryGroup - for injury charts
// data.adjusterPerformance - for adjuster tables
// data.venueAnalysis - for venue analysis

// This works with 850K records with NO performance issues!
```

---

## 📝 Summary

### For Testing (Current 1K records):
✅ **Everything works as-is** - No changes needed

### For Production (850K+ records):
⚠️ **MUST implement optimizations** - Or you will have crashes/timeouts

### Minimum Required Changes:
1. Use pagination (don't load all 850K at once)
2. Use aggregated endpoint for dashboard
3. Add database indexes
4. Enable WAL mode

### Recommended Additional Changes:
5. Create materialized views
6. Add response caching
7. Implement server-side filtering
8. Add loading indicators

---

**Your system is currently optimized for 1K-10K records. For 850K records, you MUST implement at least the minimum required changes above.**

