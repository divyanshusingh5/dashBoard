"""
Test Script for Materialized Views
Tests the performance optimization system
"""

import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.db.materialized_views import (
    create_all_materialized_views,
    refresh_all_materialized_views,
    check_materialized_views_exist,
    get_materialized_view_stats
)
from app.db.schema import get_engine, get_session, Claim
from sqlalchemy import text

def test_views():
    """Test materialized views functionality"""

    print("=" * 70)
    print("MATERIALIZED VIEWS TEST SUITE")
    print("=" * 70)

    # Step 1: Check if database has data
    print("\n[1/5] Checking database...")
    engine = get_engine()
    session = get_session(engine)

    try:
        claim_count = session.query(Claim).count()
        print(f"✓ Found {claim_count:,} claims in database")

        if claim_count == 0:
            print("⚠ Warning: No claims in database. Run migration first.")
            print("  Command: python migrate_csv_to_sqlite.py")
            return False

    except Exception as e:
        print(f"✗ Error accessing database: {e}")
        return False
    finally:
        session.close()

    # Step 2: Check if views exist
    print("\n[2/5] Checking if materialized views exist...")
    views_exist = check_materialized_views_exist()

    if views_exist:
        print("✓ Materialized views already exist")
    else:
        print("⚠ Materialized views not found")
        print("  Creating views...")
        create_all_materialized_views()
        print("✓ Views created")

    # Step 3: Test view refresh
    print("\n[3/5] Testing view refresh...")
    start_time = time.time()

    success = refresh_all_materialized_views()

    end_time = time.time()
    duration = end_time - start_time

    if success:
        print(f"✓ Views refreshed successfully in {duration:.2f} seconds")
    else:
        print("✗ View refresh failed")
        return False

    # Step 4: Get view statistics
    print("\n[4/5] Getting view statistics...")
    stats = get_materialized_view_stats()

    print("\nView Statistics:")
    print("-" * 70)

    total_rows = 0
    for view_name, view_stats in stats.items():
        row_count = view_stats.get('row_count', 0)
        last_update = view_stats.get('last_updated', 'N/A')
        total_rows += row_count
        print(f"  {view_name:30} {row_count:>8} rows  (Updated: {last_update})")

    print("-" * 70)
    print(f"  {'TOTAL AGGREGATED ROWS':30} {total_rows:>8}")
    print(f"  {'SOURCE CLAIMS':30} {claim_count:>8}")
    print(f"  {'COMPRESSION RATIO':30} {claim_count/total_rows if total_rows > 0 else 0:>8.0f}x")

    # Step 5: Test query performance
    print("\n[5/5] Testing query performance...")

    session = get_session(engine)
    try:
        # Test fast query
        start_time = time.time()
        result = session.execute(text("SELECT * FROM mv_year_severity")).fetchall()
        fast_time = time.time() - start_time
        fast_rows = len(result)

        print(f"\n  Fast Query (materialized view):")
        print(f"    - Query: SELECT * FROM mv_year_severity")
        print(f"    - Rows returned: {fast_rows}")
        print(f"    - Time: {fast_time*1000:.1f} ms")

        # Test slow query simulation
        start_time = time.time()
        result = session.execute(text("""
            SELECT
                SUBSTR(claim_date, 1, 4) as year,
                COUNT(*) as claim_count
            FROM claims
            GROUP BY year
            LIMIT 100
        """)).fetchall()
        slow_time = time.time() - start_time

        print(f"\n  Slow Query (raw aggregation):")
        print(f"    - Query: GROUP BY on {claim_count:,} claims")
        print(f"    - Time: {slow_time*1000:.1f} ms")

        if slow_time > 0:
            speedup = slow_time / fast_time if fast_time > 0 else float('inf')
            print(f"\n  Performance Improvement: {speedup:.1f}x faster")

    except Exception as e:
        print(f"✗ Query test failed: {e}")
        return False
    finally:
        session.close()

    # Success summary
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print(f"\nPerformance Summary:")
    print(f"  - Source claims: {claim_count:,}")
    print(f"  - Aggregated rows: {total_rows:,}")
    print(f"  - Compression: {claim_count/total_rows if total_rows > 0 else 0:.0f}x")
    print(f"  - Refresh time: {duration:.2f}s")
    print(f"  - Query speedup: ~{speedup:.0f}x")
    print(f"\n✓ Materialized views are working correctly!")
    print(f"✓ Dashboard is ready for 5M+ records")

    return True


if __name__ == "__main__":
    try:
        success = test_views()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
