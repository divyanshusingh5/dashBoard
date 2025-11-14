"""
Quick PostgreSQL Connection Test
Run this to verify PostgreSQL connection works before running migration
"""

import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("PostgreSQL Connection Test")
print("=" * 80)

# Test 1: Check if psycopg is installed
print("\n1. Testing psycopg installation...")
try:
    import psycopg
    print("   ✅ psycopg (v3) is installed")
    DRIVER = "psycopg"
except ImportError:
    print("   ❌ psycopg (v3) not found")
    DRIVER = None

# Test 2: Check if psycopg2 is installed
if DRIVER is None:
    print("\n2. Testing psycopg2 installation...")
    try:
        import psycopg2
        print("   ✅ psycopg2 is installed")
        DRIVER = "psycopg2"
    except ImportError as e:
        print(f"   ❌ psycopg2 not found: {str(e)}")
        print("\n   ⚠️  No PostgreSQL driver installed!")
        print("\n   Install one of:")
        print("   Option 1 (recommended): pip install \"psycopg[binary]\"")
        print("   Option 2: pip install psycopg2-binary")
        sys.exit(1)

# Test 3: Read DATABASE_URL from .env
print("\n3. Reading DATABASE_URL from .env...")
try:
    from dotenv import load_dotenv
    import os

    load_dotenv()
    db_url = os.getenv('DATABASE_URL')

    if db_url:
        print(f"   ✅ DATABASE_URL found")
        # Hide password
        if '@' in db_url:
            parts = db_url.split('@')
            safe_url = parts[0].split(':')[0] + ':***@' + parts[1]
            print(f"   URL: {safe_url}")
        else:
            print(f"   URL: {db_url}")
    else:
        print("   ❌ DATABASE_URL not found in .env")
        print("   Please add: DATABASE_URL=postgresql://postgres:password@localhost:5432/claims_analytics")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ Error reading .env: {str(e)}")
    db_url = "postgresql://postgres:user@localhost:5432/claims_analytics"
    print(f"   Using default: {db_url}")

# Test 4: Parse connection string
print("\n4. Parsing connection string...")
try:
    if '://' in db_url:
        protocol = db_url.split('://')[0]
        rest = db_url.split('://')[1]

        print(f"   Protocol: {protocol}")

        # Check if correct driver specified
        if DRIVER == "psycopg" and "+psycopg" not in protocol:
            print("   ⚠️  WARNING: Using psycopg (v3) but URL doesn't have '+psycopg'")
            print("   Update DATABASE_URL to: postgresql+psycopg://...")
            # Auto-fix
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
            print(f"   Auto-fixed to: postgresql+psycopg://...")

        if '@' in rest:
            auth, location = rest.split('@')
            if ':' in location:
                host, rest = location.split(':', 1)
                if '/' in rest:
                    port, database = rest.split('/', 1)
                    print(f"   Host: {host}")
                    print(f"   Port: {port}")
                    print(f"   Database: {database}")

        print("   ✅ Connection string parsed successfully")
except Exception as e:
    print(f"   ⚠️  Could not parse connection string: {str(e)}")

# Test 5: Connect to PostgreSQL
print("\n5. Testing PostgreSQL connection...")
try:
    if DRIVER == "psycopg":
        # psycopg v3
        import psycopg

        # Fix URL if needed
        if "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://")

        # Remove driver from URL for psycopg.connect
        connect_url = db_url.replace("postgresql+psycopg://", "postgresql://")

        conn = psycopg.connect(connect_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ Connected successfully!")
        print(f"   PostgreSQL: {version[:60]}...")

        # Test if database has claims table
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'claims'
        """)

        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM claims")
            count = cursor.fetchone()[0]
            print(f"   ✅ 'claims' table exists with {count:,} rows")
        else:
            print("   ⚠️  'claims' table does not exist yet")
            print("   Run migrate_csv_to_postgres.py to create it")

        conn.close()

    else:
        # psycopg2
        import psycopg2

        # Remove driver from URL for psycopg2.connect
        connect_url = db_url.replace("postgresql://", "").replace("postgresql+psycopg2://", "")

        # Parse URL for psycopg2
        if '@' in connect_url:
            auth, location = connect_url.split('@')
            user, password = auth.split(':')
            if ':' in location:
                host, rest = location.split(':', 1)
                if '/' in rest:
                    port, database = rest.split('/', 1)

                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        database=database,
                        user=user,
                        password=password
                    )

                    cursor = conn.cursor()
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    print(f"   ✅ Connected successfully!")
                    print(f"   PostgreSQL: {version[:60]}...")

                    # Test if database has claims table
                    cursor.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'claims'
                    """)

                    if cursor.fetchone():
                        cursor.execute("SELECT COUNT(*) FROM claims")
                        count = cursor.fetchone()[0]
                        print(f"   ✅ 'claims' table exists with {count:,} rows")
                    else:
                        print("   ⚠️  'claims' table does not exist yet")
                        print("   Run migrate_csv_to_postgres.py to create it")

                    conn.close()

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nYour PostgreSQL connection is working correctly!")
    print("\nNext steps:")
    if DRIVER == "psycopg":
        print("  1. Make sure DATABASE_URL in .env uses: postgresql+psycopg://...")
    print("  2. Run migration: python migrate_csv_to_postgres.py")
    print("  3. Create views: python create_materialized_views_postgres.py")
    print("  4. Start app: python run.py")

except Exception as e:
    print(f"   ❌ Connection failed: {str(e)}")
    print("\n   Troubleshooting:")
    print("   1. Check PostgreSQL is running:")
    print("      Windows: net start postgresql-x64-14")
    print("   2. Check credentials in .env are correct")
    print("   3. Check database exists:")
    print("      psql -U postgres -c \"CREATE DATABASE claims_analytics;\"")
    print("   4. Check firewall allows localhost:5432")

    if "DLL" in str(e) or "module" in str(e):
        print("\n   ⚠️  DLL Error Detected!")
        print("   Fix:")
        print("   pip uninstall psycopg2-binary -y")
        print("   pip install \"psycopg[binary]\"")
        print("   Then update DATABASE_URL to: postgresql+psycopg://...")

    sys.exit(1)
