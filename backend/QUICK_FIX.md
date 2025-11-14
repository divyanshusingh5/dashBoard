# QUICK FIX - psycopg2 DLL Error

## 🎯 Your Error:
```
DLL load failed while importing _psycopg: The specified module could not be found.
```

## ✅ FASTEST FIX (Choose One)

### Option A: Try Reinstalling psycopg2-binary First (30 seconds)

```bash
pip uninstall psycopg2 psycopg2-binary -y
pip install psycopg2-binary==2.9.9
python test_postgres_connection.py
```

If this works, you're done! ✅

If not, try Option B ⬇️

---

### Option B: Switch to psycopg v3 (Recommended for Windows) (2 minutes)

```bash
# 1. Uninstall old driver
pip uninstall psycopg2 psycopg2-binary -y

# 2. Install psycopg v3
pip install "psycopg[binary,pool]"

# 3. Update .env file - Add +psycopg to DATABASE_URL
```

**Before (.env):**
```env
DATABASE_URL=postgresql://postgres:user@localhost:5432/claims_analytics
```

**After (.env):**
```env
DATABASE_URL=postgresql+psycopg://postgres:user@localhost:5432/claims_analytics
```

```bash
# 4. Test connection
python test_postgres_connection.py

# 5. If test passes, run migration
python migrate_csv_to_postgres.py
```

---

## 🧪 Test Your Fix

After applying fix, run:

```bash
python test_postgres_connection.py
```

**Expected output:**
```
================================================================================
PostgreSQL Connection Test
================================================================================

1. Testing psycopg installation...
   ✅ psycopg (v3) is installed

3. Reading DATABASE_URL from .env...
   ✅ DATABASE_URL found
   URL: postgresql+psycopg:***@localhost:5432/claims_analytics

5. Testing PostgreSQL connection...
   ✅ Connected successfully!
   PostgreSQL: PostgreSQL 14.x...
   ⚠️  'claims' table does not exist yet

================================================================================
✅ ALL TESTS PASSED!
================================================================================

Next steps:
  1. Make sure DATABASE_URL in .env uses: postgresql+psycopg://...
  2. Run migration: python migrate_csv_to_postgres.py
  3. Create views: python create_materialized_views_postgres.py
  4. Start app: python run.py
```

---

## 📝 What Changed:

### If You Used Option A (psycopg2-binary):
- No changes to .env needed
- Just reinstalled the driver

### If You Used Option B (psycopg v3):
- **.env:** Changed `postgresql://` to `postgresql+psycopg://`
- **requirements.txt:** Will use `psycopg[binary]` instead of `psycopg2-binary`
- **Better Windows compatibility!**

---

## ⚠️ Still Not Working?

### Error: "PostgreSQL is not running"
```bash
# Windows
net start postgresql-x64-14

# Check if running
tasklist | findstr postgres
```

### Error: "Database does not exist"
```bash
psql -U postgres -c "CREATE DATABASE claims_analytics;"
```

### Error: "Authentication failed"
- Check password in `.env` is correct
- Try connecting with psql:
```bash
psql -U postgres -d claims_analytics
```
If this works, password is correct.

---

## 🚀 After Fix Works:

```bash
# 1. Run migration (5-10 minutes)
python migrate_csv_to_postgres.py

# 2. Create views (1-2 minutes)
python create_materialized_views_postgres.py

# 3. Start backend
python run.py

# 4. Start frontend (new terminal)
cd frontend
npm run dev

# 5. Open dashboard
http://localhost:5173
```

---

## 💡 Why This Happened

**psycopg2-binary on Windows:**
- Requires Visual C++ runtime DLLs
- Some Windows systems missing required DLLs
- Binary wheels may not include dependencies

**psycopg v3 (recommended fix):**
- Better Windows compatibility
- Modern Python support
- More reliable on Windows

---

## ✅ Checklist

- [ ] Uninstalled old psycopg2
- [ ] Installed new driver (psycopg or psycopg2-binary)
- [ ] Updated .env if using psycopg v3
- [ ] Ran test_postgres_connection.py
- [ ] Test passed ✅
- [ ] Ready to run migration!

---

**Choose Option A or B above and you'll be running in 2 minutes!** 🚀
