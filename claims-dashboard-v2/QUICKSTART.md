# Quick Start Guide

Get the Claims Dashboard v2.0 running in under 5 minutes!

## 🚀 Prerequisites

- Python 3.10 or higher
- (Optional) Snowflake account for cloud database

## ⚡ Quick Setup

### Option 1: SQLite (Recommended for Development)

```bash
# 1. Navigate to backend
cd claims-dashboard-v2/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment (use SQLite)
copy .env.sqlite .env  # Windows
# cp .env.sqlite .env  # Linux/Mac

# 6. Create database directory
mkdir -p app/db

# 7. Initialize database with tables
sqlite3 app/db/claims_analytics.db < app/db/queries/ddl/sqlite/create_tables.sql

# 8. Create indexes
sqlite3 app/db/claims_analytics.db < app/db/queries/ddl/sqlite/create_indexes.sql

# 9. Verify database creation
sqlite3 app/db/claims_analytics.db ".tables"
# Should show: aggregated_cache  claims  ssnb  venue_statistics  weights

# 10. Test configuration (Python REPL)
python
>>> from app.core import settings
>>> print(settings.DATABASE_TYPE)  # Should print: sqlite
>>> print(settings.database_url)   # Should print: sqlite:///./app/db/claims_analytics.db
>>> exit()
```

### Option 2: Snowflake (For Production)

```bash
# 1-4. Same as SQLite option (navigate, venv, activate, install)

# 5. Set up environment (use Snowflake)
copy .env.snowflake .env  # Windows
# cp .env.snowflake .env  # Linux/Mac

# 6. Edit .env with your Snowflake credentials
notepad .env  # Windows
# nano .env   # Linux/Mac

# Update these values:
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=CLAIMS_DB
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ANALYST

# 7. Create tables in Snowflake
# Use SnowSQL or Snowflake Web UI:
snowsql -a your_account -u your_username

USE ROLE ANALYST;
USE WAREHOUSE COMPUTE_WH;
CREATE DATABASE IF NOT EXISTS CLAIMS_DB;
USE DATABASE CLAIMS_DB;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;
USE SCHEMA ANALYTICS;

# Run the DDL script
!source app/db/queries/ddl/snowflake/create_tables.sql

# Verify
SHOW TABLES;

# 8. Test configuration
python
>>> from app.core import settings
>>> print(settings.DATABASE_TYPE)  # Should print: snowflake
>>> from app.core import check_database_connection
>>> import asyncio
>>> asyncio.run(check_database_connection())  # Should print: True
```

## 🧪 Testing the Setup

### Test Database Connection

Create a test script `test_connection.py`:

```python
# test_connection.py
import asyncio
from app.core import settings, check_database_connection, get_session

async def test():
    print(f"Database Type: {settings.DATABASE_TYPE}")
    print(f"Database URL: {settings.database_url}")

    print("\nTesting connection...")
    connected = await check_database_connection()

    if connected:
        print("✅ Database connection successful!")

        # Test query
        session = get_session()
        try:
            result = session.execute("SELECT COUNT(*) FROM claims")
            count = result.fetchone()[0]
            print(f"✅ Found {count} claims in database")
        except Exception as e:
            print(f"⚠️  No data yet: {e}")
        finally:
            session.close()
    else:
        print("❌ Database connection failed!")

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```bash
python test_connection.py
```

Expected output:
```
Database Type: sqlite
Database URL: sqlite:///./app/db/claims_analytics.db
Testing connection...
✅ Database connection successful!
⚠️  No data yet: no such table: claims
```

### Test Query Loader

Create `test_query_loader.py`:

```python
# test_query_loader.py
from app.utils.query_loader import query_loader

# Test loading DDL
print("Loading DDL...")
create_tables = query_loader.load_ddl("create_tables.sql")
print(f"✅ Loaded {len(create_tables)} characters of DDL")
print(f"First 100 chars: {create_tables[:100]}...")

# Test loading indexes
print("\nLoading indexes...")
create_indexes = query_loader.load_ddl("create_indexes.sql")
print(f"✅ Loaded {len(create_indexes)} characters of index DDL")

# Show database type
print(f"\n Database type: {query_loader.db_type}")
```

Run it:
```bash
python test_query_loader.py
```

## 📊 Next Steps

### 1. Import Data (Once Models are Created)

```bash
# Copy your CSV data
cp /path/to/dat.csv data/dat.csv
cp /path/to/SSNB.csv data/SSNB.csv
cp /path/to/weights.csv data/weights.csv

# Run migration script (will be created in next phase)
python scripts/migrate_csv_to_db.py
```

### 2. Start API Server (Once Endpoints are Created)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

### 3. Start Frontend (Once Created)

```bash
cd ../frontend
npm install
npm run dev
```

Visit: http://localhost:5173

## 🔄 Switching Databases

You can easily switch between SQLite and Snowflake:

```bash
# Switch to SQLite
copy .env.sqlite .env

# Switch to Snowflake
copy .env.snowflake .env

# Restart your application for changes to take effect
```

## 🐛 Troubleshooting

### SQLite Database Not Found

```bash
# Create the directory
mkdir -p app/db

# Recreate the database
sqlite3 app/db/claims_analytics.db < app/db/queries/ddl/sqlite/create_tables.sql
```

### Import Error: Module 'app' Not Found

```bash
# Make sure you're in the backend directory
cd backend

# Make sure PYTHONPATH includes current directory
export PYTHONPATH=.  # Linux/Mac
set PYTHONPATH=.     # Windows
```

### Snowflake Connection Failed

1. Check your credentials in `.env`
2. Verify your Snowflake account is active
3. Ensure your IP is whitelisted in Snowflake
4. Check warehouse is running

### "No Module Named 'pydantic_settings'"

```bash
# Update pydantic-settings
pip install --upgrade pydantic-settings
```

## 📚 Additional Resources

- [README.md](README.md) - Full project documentation
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current implementation status
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## ✅ Verification Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list | grep fastapi`)
- [ ] Environment file configured (`.env` exists)
- [ ] Database created (SQLite file exists OR Snowflake tables exist)
- [ ] Tables created (`.tables` shows 5 tables)
- [ ] Test connection successful
- [ ] Query loader working

Once all items are checked, you're ready to continue development!

---

**Current Status**: Foundation Complete
**Next Phase**: Models and Repositories
**Estimated Time**: 2-3 hours

Happy coding! 🎉
