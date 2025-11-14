# Fix psycopg2 DLL Error on Windows

## ❌ Error You're Seeing:
```
ERROR: DLL load failed while importing _psycopg: The specified module could not be found.
```

## ✅ Solutions (Try in Order)

### Solution 1: Reinstall psycopg2-binary (Most Common Fix)

```bash
# Uninstall current version
pip uninstall psycopg2 psycopg2-binary -y

# Install fresh psycopg2-binary
pip install psycopg2-binary

# If that fails, try specific version
pip install psycopg2-binary==2.9.9
```

---

### Solution 2: Use psycopg (Version 3) Instead

PostgreSQL driver version 3 works better on Windows:

```bash
# Uninstall old versions
pip uninstall psycopg2 psycopg2-binary -y

# Install psycopg3 (newer, better Windows support)
pip install psycopg[binary]
```

**Then update your DATABASE_URL format:**

```env
# Change from:
DATABASE_URL=postgresql://postgres:user@localhost:5432/claims_analytics

# To (add +psycopg):
DATABASE_URL=postgresql+psycopg://postgres:user@localhost:5432/claims_analytics
```

---

### Solution 3: Install Visual C++ Redistributable

psycopg2 requires Microsoft Visual C++ runtime:

1. Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Run installer
3. Restart computer
4. Try again:
```bash
pip uninstall psycopg2-binary -y
pip install psycopg2-binary
```

---

### Solution 4: Use conda (If Using Anaconda)

```bash
conda install -c conda-forge psycopg2
```

---

### Solution 5: Build from Source

```bash
# Install PostgreSQL development files first
# Download from: https://www.postgresql.org/download/windows/

# Then install
pip install psycopg2
```

---

## 🎯 RECOMMENDED FIX (Easiest)

**Use psycopg3 (newest version, best Windows support):**

```bash
# 1. Uninstall old version
pip uninstall psycopg2 psycopg2-binary -y

# 2. Install psycopg3
pip install "psycopg[binary,pool]"

# 3. Update requirements.txt
# Remove: psycopg2-binary>=2.9.0
# Add: psycopg[binary,pool]>=3.1.0

# 4. Update .env - change DATABASE_URL
# From: postgresql://postgres:user@localhost:5432/claims_analytics
# To:   postgresql+psycopg://postgres:user@localhost:5432/claims_analytics

# 5. Test
python migrate_csv_to_postgres.py
```

---

## ✅ Verification

After fixing, test connection:

```bash
python -c "import psycopg; print('✅ psycopg installed correctly!')"
```

Or for psycopg2:
```bash
python -c "import psycopg2; print('✅ psycopg2 installed correctly!')"
```

---

## 🔧 Alternative: Test Without Migration Script

If you just want to verify PostgreSQL connection works:

```bash
# Create test file: test_postgres.py
```

```python
# test_postgres.py
import psycopg

# Update with your credentials
conn = psycopg.connect(
    "postgresql://postgres:YOUR_PASSWORD@localhost:5432/claims_analytics"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
version = cursor.fetchone()[0]
print(f"✅ Connected! PostgreSQL version: {version}")

cursor.execute("SELECT COUNT(*) FROM claims;")
count = cursor.fetchone()[0]
print(f"✅ Claims count: {count:,}")

conn.close()
```

```bash
python test_postgres.py
```

---

## 📝 Update Migration Script for psycopg3

If you switch to psycopg3, the migration script needs a small update:

**File: `migrate_csv_to_postgres.py` - Line 24**

Change:
```python
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
```

To:
```python
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

This also fixes the deprecation warning you saw.

---

## 🎯 FASTEST SOLUTION (1 Minute)

```bash
# 1. Uninstall
pip uninstall psycopg2-binary -y

# 2. Install psycopg3
pip install "psycopg[binary]"

# 3. Update DATABASE_URL in .env
# Add +psycopg to the URL:
# postgresql+psycopg://postgres:user@localhost:5432/claims_analytics

# 4. Done! Run migration
python migrate_csv_to_postgres.py
```

---

## 💡 Why This Happens

**psycopg2-binary on Windows:**
- Requires specific Visual C++ DLLs
- May conflict with other Python packages
- Binary wheels sometimes don't include all dependencies

**psycopg (v3) on Windows:**
- Better Windows compatibility
- Pure Python with optional C extensions
- More reliable on Windows systems

---

## 🆘 Still Not Working?

If none of the above work, you can use **SQLite temporarily** while debugging PostgreSQL connection:

**Keep using SQLite (already works):**
```env
# Comment out PostgreSQL URL in .env
# DATABASE_URL=postgresql://...
```

The app will fall back to SQLite at `backend/app/db/claims_analytics.db`

Then fix PostgreSQL connection separately without blocking your work.

---

## ✅ Expected Success Output

After fixing, you should see:

```
INFO:__main__:Connecting to PostgreSQL database...
INFO:__main__:Database: claims_analytics
INFO:__main__:✓ Connected to PostgreSQL: PostgreSQL 14.x...
INFO:__main__:Creating database schema...
INFO:__main__:✓ Database schema created successfully
...
```

---

**Choose Solution 1 or 2 above, most likely to work!** ✅
