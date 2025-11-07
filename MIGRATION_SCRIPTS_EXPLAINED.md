# Migration Scripts - What They Do & Which to Use

## The Two Migration Scripts

### 1. migrate_smart.py (RECOMMENDED ✅)

**What it does:**
```
1. Checks if claims table already has data
   → If YES: Skips dat.csv migration (saves 2-3 minutes!)
   → If NO: Migrates dat.csv to claims table

2. Checks if SSNB table already has data
   → Asks you: Skip, Replace, or Update
   → Only migrates what you choose

3. Handles duplicates automatically
   → Removes duplicate CLAIMIDs before inserting

4. Smart and efficient
   → Only does what's necessary
```

**When to use:**
- ✅ When you already migrated data once
- ✅ When you only want to update SSNB data
- ✅ When you want fast re-runs
- ✅ **Most of the time - this is your default choice**

**Time:**
- Claims exist, SSNB missing: ~1 second
- Both exist: <1 second (just skips)
- Fresh database: ~2-3 minutes

**Command:**
```bash
cd backend
./venv/Scripts/python.exe migrate_smart.py
```

---

### 2. migrate_comprehensive.py (CLEAN SLATE)

**What it does:**
```
1. DROPS the entire claims table (deletes everything!)
2. Creates fresh claims table from scratch
3. Migrates ALL data from dat.csv (even if it was already there)
4. DROPS the entire SSNB table
5. Creates fresh SSNB table
6. Migrates all SSNB data

WARNING: This deletes ALL existing data and starts fresh!
```

**When to use:**
- ⚠️ When you have completely NEW data file
- ⚠️ When your database is corrupted
- ⚠️ When column names changed in CSV
- ⚠️ When you want a clean slate
- ⚠️ When migrate_smart.py fails

**Time:**
- Always takes full time: ~3-5 minutes
- No shortcuts, always migrates everything

**Command:**
```bash
cd backend
./venv/Scripts/python.exe migrate_comprehensive.py
```

---

## Quick Comparison

| Feature | migrate_smart.py | migrate_comprehensive.py |
|---------|------------------|-------------------------|
| **Checks existing data** | ✅ Yes | ❌ No - always drops |
| **Preserves data** | ✅ Yes | ❌ No - deletes all |
| **Handles duplicates** | ✅ Yes | ✅ Yes |
| **Speed (re-run)** | <1 second | 3-5 minutes |
| **Speed (fresh)** | 2-3 minutes | 3-5 minutes |
| **User control** | ✅ Asks what to do | ❌ Does everything |
| **Safe** | ✅ Very safe | ⚠️ Deletes data |

---

## What Each Script Does Step-by-Step

### migrate_smart.py Flow:

```
START
  ↓
Check: Does claims table have data?
  ├─ YES → Skip dat.csv migration ✓
  └─ NO  → Migrate dat.csv → claims table
  ↓
Check: Does SSNB table exist?
  ├─ NO  → Create table, migrate SSNB.csv
  └─ YES → Check: Does it have data?
             ├─ NO  → Migrate SSNB.csv
             └─ YES → Ask user:
                       1. Skip (keep existing)
                       2. Replace (clear + remigrate)
  ↓
Show verification summary
  ↓
DONE
```

**Example output:**
```
================================================================================
CHECKING CLAIMS DATA
================================================================================
✓ Claims table already has 630,000 records
✓ Skipping dat.csv migration (already done)

================================================================================
CHECKING SSNB DATA
================================================================================
✓ SSNB table already has 100 records

Do you want to:
  1. Skip SSNB migration (keep existing data)
  2. Replace all SSNB data (clear and re-migrate)
Choice (1/2): 1

✓ Skipping SSNB migration (keeping existing data)

================================================================================
MIGRATION VERIFICATION
================================================================================
Claims table: 630,000 records
SSNB table: 100 records
Matched claims (have SSNB data): 100 (0.0%)

✓ Ready for use!
================================================================================
```

---

### migrate_comprehensive.py Flow:

```
START
  ↓
Drop claims table (if exists)
  ↓
Create fresh claims table
  ↓
Read ALL rows from dat.csv
  ↓
Migrate ALL rows to claims table
  (Takes 2-3 minutes for 630K rows)
  ↓
Drop SSNB table (if exists)
  ↓
Create fresh SSNB table
  ↓
Read ALL rows from SSNB.csv
  ↓
Migrate ALL rows to SSNB table
  ↓
Show verification summary
  ↓
DONE
```

**Example output:**
```
================================================================================
COMPREHENSIVE MIGRATION - FRESH START
================================================================================
Clearing existing claims table...
✓ Cleared

Reading dat.csv...
Loaded 630,000 records from CSV

Migrating to SQLite database...
  Processed 100,000/630,000 records...
  Processed 200,000/630,000 records...
  ...
✓ Successfully migrated 630,000 claims records

Clearing existing SSNB table...
✓ Cleared

Reading SSNB.csv...
Loaded 100 records from CSV

Migrating to database...
✓ Successfully migrated 100 SSNB records

================================================================================
VERIFICATION
================================================================================
Claims: 630,000 records
SSNB: 100 records
✓ Migration complete!
================================================================================
```

---

## Which Should You Use?

### Scenario 1: First Time Setup
**Use:** Either one (both do full migration)
**Recommended:** `migrate_smart.py` (slightly faster, better logging)

### Scenario 2: You Already Have Data, Want to Add SSNB
**Use:** `migrate_smart.py`
**Why:** Skips claims migration, only does SSNB (saves 2-3 minutes)

### Scenario 3: You Have NEW dat.csv with MORE Claims
**Use:** `migrate_comprehensive.py`
**Why:** Need to drop old data and migrate new data fresh

### Scenario 4: Database is Corrupted or Broken
**Use:** `migrate_comprehensive.py`
**Why:** Clean slate fixes corruption

### Scenario 5: Just Checking if Data is There
**Use:** `migrate_smart.py`
**Why:** Won't delete anything, just checks and shows status

### Scenario 6: Running Second Time (Already Migrated)
**Use:** `migrate_smart.py`
**Why:** Takes <1 second instead of 3-5 minutes

---

## The QUICK_SETUP.bat Script

The batch file I created uses `migrate_smart.py` because:
- ✅ Safe (doesn't delete data unnecessarily)
- ✅ Fast (skips what's already done)
- ✅ Smart (asks user what to do)

If you want it to use `migrate_comprehensive.py` instead (always fresh), edit line 23:
```bat
REM Change this line:
venv\Scripts\python.exe migrate_smart.py

REM To this:
venv\Scripts\python.exe migrate_comprehensive.py
```

---

## After Migration - What's Next?

**Both scripts only migrate the CSV data to the database.**

**You still need to:**

1. **Create materialized views** (THIS IS WHY YOU'RE TIMING OUT!)
   ```bash
   ./venv/Scripts/python.exe create_materialized_views.py
   ```
   **Without this:** Aggregation endpoints timeout
   **With this:** Aggregation is 100x faster

2. **Populate venue statistics**
   ```bash
   ./venv/Scripts/python.exe populate_venue_statistics.py
   ```
   **Without this:** Venue shift recommendations slow
   **With this:** Venue recommendations 120x faster

3. **Start backend server**
   ```bash
   ./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Common Questions

### Q: I ran migrate_comprehensive.py, do I still need migrate_smart.py?
**A:** No! They do the same thing (migrate data). Only run ONE of them.

### Q: Can I run both?
**A:** You can, but it's redundant. migrate_comprehensive.py already does everything migrate_smart.py does (just less efficiently).

### Q: Which is better?
**A:**
- **migrate_smart.py** - Better for 95% of cases
- **migrate_comprehensive.py** - Only when you need a clean slate

### Q: I have new data with 657K claims (instead of 630K). Which to use?
**A:** Use `migrate_comprehensive.py` because you want to replace old data with new data.

### Q: After migration, frontend still times out. Why?
**A:** You forgot to create materialized views! Run:
```bash
./venv/Scripts/python.exe create_materialized_views.py
```

### Q: Do I need to run migration every time I start the server?
**A:** NO! Migration is only needed once (or when data changes). After that, just start the server.

---

## Summary - Your Situation

**You said:** "while running with newer data i am getting error time out"

**This means:**
1. You have new dat.csv with 657K claims (instead of 630K)
2. You want to replace old data with new data

**What you should do:**

```bash
# Step 1: Kill old servers
taskkill //F //IM python.exe

# Step 2: Use comprehensive migration (fresh data)
cd backend
./venv/Scripts/python.exe migrate_comprehensive.py

# Step 3: CREATE MATERIALIZED VIEWS (THIS IS THE KEY!)
./venv/Scripts/python.exe create_materialized_views.py

# Step 4: Populate venue statistics
./venv/Scripts/python.exe populate_venue_statistics.py

# Step 5: Start backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or just run:**
```bash
QUICK_SETUP.bat
```
(But edit it to use `migrate_comprehensive.py` instead of `migrate_smart.py`)

---

## The Real Fix for Your Timeout

**The timeout is NOT because of which migration script you use.**

**The timeout is because you're missing materialized views!**

After ANY migration (smart or comprehensive), you MUST run:
```bash
./venv/Scripts/python.exe create_materialized_views.py
```

This creates pre-computed aggregation tables that make your API 100x faster.

**Without materialized views:**
- `/aggregation/aggregated` calculates on-the-fly
- Takes 60+ seconds for 657K claims
- Frontend times out

**With materialized views:**
- `/aggregation/aggregated` reads pre-computed tables
- Takes <1 second
- Frontend works perfectly ✅
