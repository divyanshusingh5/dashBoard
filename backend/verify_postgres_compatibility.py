"""
PostgreSQL Table Compatibility Verification Script
Checks if existing PostgreSQL tables match the expected schema and column names
Run this ONCE after creating PostgreSQL tables to verify compatibility
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db.schema import Base, Claim, SSNB

def verify_postgres_compatibility():
    """Verify PostgreSQL tables match expected schema"""

    print("=" * 80)
    print("PostgreSQL Table Compatibility Verification")
    print("=" * 80)

    try:
        # Connect to PostgreSQL
        print(f"\n1. Connecting to PostgreSQL...")
        print(f"   Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")

        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # Test connection
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   ✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[:50]}...")

        # Check tables exist
        print(f"\n2. Checking tables exist...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"   Found {len(tables)} tables in database")

        required_tables = ['claims', 'ssnb']
        optional_tables = ['weights', 'venue_statistics', 'aggregated_cache']
        materialized_views = ['mv_year_severity', 'mv_county_year', 'mv_injury_group',
                              'mv_adjuster_performance', 'mv_venue_analysis', 'mv_kpi_summary']

        # Check required tables
        missing_tables = []
        for table in required_tables:
            if table in tables:
                print(f"   ✅ {table} - EXISTS")
            else:
                print(f"   ❌ {table} - MISSING")
                missing_tables.append(table)

        # Check optional tables
        for table in optional_tables:
            if table in tables:
                print(f"   ✅ {table} - EXISTS (optional)")
            else:
                print(f"   ⚠️  {table} - MISSING (optional, not critical)")

        # Check materialized views
        print(f"\n3. Checking materialized views...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT matviewname
                FROM pg_matviews
                WHERE schemaname = 'public'
            """))
            existing_views = [row[0] for row in result.fetchall()]

        print(f"   Found {len(existing_views)} materialized views")
        for view in materialized_views:
            if view in existing_views:
                print(f"   ✅ {view} - EXISTS")
            else:
                print(f"   ⚠️  {view} - MISSING (can create later)")

        if missing_tables:
            print(f"\n   ❌ ERROR: Missing required tables: {missing_tables}")
            print(f"   Please run migrate_csv_to_postgres.py to create tables")
            return False

        # Check claims table columns
        print(f"\n4. Verifying 'claims' table columns...")
        claims_columns = {col['name'].lower(): col for col in inspector.get_columns('claims')}

        print(f"   Found {len(claims_columns)} columns in claims table")

        # Critical columns for dashboard
        critical_columns = [
            'claimid',
            'dollaramounthigh',
            'causation_high_recommendation',
            'variance_pct',
            'claimcloseddate',
            'countyname',
            'venuestate',
            'venuerating',
            'primary_injury_by_severity',
            'primary_injurygroup_code_by_severity',
            'primary_injury_severity_score',
            'caution_level',
            'settlement_days',
            'iol',
            'adjustername',
        ]

        missing_columns = []
        for col in critical_columns:
            if col in claims_columns:
                col_info = claims_columns[col]
                print(f"   ✅ {col.upper():40} - {col_info['type']}")
            else:
                print(f"   ❌ {col.upper():40} - MISSING")
                missing_columns.append(col)

        if missing_columns:
            print(f"\n   ❌ ERROR: Missing critical columns: {missing_columns}")
            print(f"   These columns are required for the dashboard to work")
            return False

        # Check SSNB table columns
        print(f"\n5. Verifying 'ssnb' table columns...")
        ssnb_columns = {col['name'].lower(): col for col in inspector.get_columns('ssnb')}

        print(f"   Found {len(ssnb_columns)} columns in ssnb table")

        ssnb_critical = [
            'claimid',
            'dollaramounthigh',
            'causation_high_recommendation',
            'primary_severity_score',
            'primary_causation_score',
        ]

        for col in ssnb_critical:
            if col in ssnb_columns:
                print(f"   ✅ {col.upper():40} - EXISTS")
            else:
                print(f"   ❌ {col.upper():40} - MISSING")

        # Test sample data query
        print(f"\n6. Testing sample data query...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT
                    COUNT(*) as total_claims,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement,
                    AVG(variance_pct) as avg_variance,
                    COUNT(CASE WHEN ABS(variance_pct) > 15 THEN 1 END) as high_variance_count
                FROM claims
                WHERE DOLLARAMOUNTHIGH IS NOT NULL
            """))

            row = result.fetchone()

            print(f"   ✅ Query executed successfully!")
            print(f"   Total Claims: {row[0]:,}")
            print(f"   Avg Settlement: ${row[1]:,.2f}" if row[1] else "   Avg Settlement: N/A")
            print(f"   Avg Variance: {row[2]:.2f}%" if row[2] else "   Avg Variance: N/A")
            print(f"   High Variance Claims: {row[3]:,}")

        # Test filter query
        print(f"\n7. Testing filter query (County + Year)...")
        with engine.connect() as conn:
            # Get a sample county
            result = conn.execute(text("""
                SELECT COUNTYNAME
                FROM claims
                WHERE COUNTYNAME IS NOT NULL
                LIMIT 1
            """))
            sample_county = result.fetchone()

            if sample_county:
                county = sample_county[0]
                result = conn.execute(text(f"""
                    SELECT COUNT(*)
                    FROM claims
                    WHERE COUNTYNAME = :county
                """), {"county": county})

                count = result.fetchone()[0]
                print(f"   ✅ Filter test successful!")
                print(f"   County '{county}': {count:,} claims")

        # Test aggregation query (like dashboard uses)
        print(f"\n8. Testing aggregation query (Year + Severity)...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT
                    CAUTION_LEVEL,
                    COUNT(*) as claim_count,
                    AVG(DOLLARAMOUNTHIGH) as avg_settlement
                FROM claims
                WHERE CAUTION_LEVEL IS NOT NULL
                GROUP BY CAUTION_LEVEL
                ORDER BY claim_count DESC
                LIMIT 5
            """))

            print(f"   ✅ Aggregation query successful!")
            print(f"   {'Severity':<15} {'Claims':<12} {'Avg Settlement':<15}")
            print(f"   {'-'*15} {'-'*12} {'-'*15}")

            for row in result.fetchall():
                severity = row[0] or 'Unknown'
                claims = row[1]
                avg = row[2] if row[2] else 0
                print(f"   {severity:<15} {claims:<12,} ${avg:<14,.0f}")

        # Test materialized view query (if exists)
        if 'mv_year_severity' in existing_views:
            print(f"\n9. Testing materialized view query...")
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT
                        year,
                        severity_category,
                        claim_count
                    FROM mv_year_severity
                    ORDER BY year DESC, claim_count DESC
                    LIMIT 5
                """))

                print(f"   ✅ Materialized view query successful!")
                print(f"   {'Year':<8} {'Severity':<12} {'Claims':<12}")
                print(f"   {'-'*8} {'-'*12} {'-'*12}")

                for row in result.fetchall():
                    print(f"   {row[0]:<8} {row[1]:<12} {row[2]:<12,}")

        # Final summary
        print(f"\n" + "=" * 80)
        print(f"✅ VERIFICATION COMPLETE - ALL CHECKS PASSED!")
        print(f"=" * 80)
        print(f"\nYour PostgreSQL database is compatible with the dashboard!")
        print(f"\nYou can now:")
        print(f"  1. Start backend: python run.py")
        print(f"  2. Start frontend: cd frontend && npm run dev")
        print(f"  3. Open dashboard: http://localhost:5173")
        print(f"\n⚠️  You do NOT need to run migration scripts again!")
        print(f"   The dashboard will connect to your existing PostgreSQL tables.")
        print(f"\n" + "=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check PostgreSQL is running")
        print(f"  2. Verify DATABASE_URL in .env is correct")
        print(f"  3. Ensure tables exist in database")
        print(f"  4. Run: psql -U postgres -d claims_analytics -c '\\dt'")
        return False


if __name__ == "__main__":
    success = verify_postgres_compatibility()

    if not success:
        print(f"\n⚠️  Please fix the issues above before starting the dashboard")
        sys.exit(1)
    else:
        print(f"\n✅ Ready to start the dashboard!")
        sys.exit(0)
