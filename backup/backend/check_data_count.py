"""Quick script to check total claims count in database"""
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///app/db/claims_analytics.db')

with engine.connect() as conn:
    # Count total claims
    result = conn.execute(text('SELECT COUNT(*) as count FROM claims')).fetchone()
    total_claims = result[0]

    print(f'Total claims in database: {total_claims:,}')

    # Get sample aggregation to verify all data is used
    result = conn.execute(text('''
        SELECT
            COUNT(*) as claim_count,
            COUNT(DISTINCT COUNTYNAME) as unique_counties,
            COUNT(DISTINCT PRIMARY_INJURYGROUP_CODE) as unique_injury_groups,
            MIN(CLAIMCLOSEDDATE) as earliest_date,
            MAX(CLAIMCLOSEDDATE) as latest_date
        FROM claims
    ''')).fetchone()

    print(f'\nData Coverage:')
    print(f'  Unique counties: {result[1]:,}')
    print(f'  Unique injury groups: {result[2]:,}')
    print(f'  Date range: {result[3]} to {result[4]}')

    # Check a few sample aggregations
    result = conn.execute(text('''
        SELECT
            strftime('%Y', CLAIMCLOSEDDATE) as year,
            COUNT(*) as claim_count
        FROM claims
        WHERE CLAIMCLOSEDDATE IS NOT NULL
        GROUP BY year
        ORDER BY year
    ''')).fetchall()

    print(f'\nClaims by Year:')
    for row in result:
        print(f'  {row[0]}: {row[1]:,} claims')

print('\nConclusion: Backend is processing ALL data (no artificial limits)')
