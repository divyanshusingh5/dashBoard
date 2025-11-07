"""
Generate Aggregated CSV Files for Frontend
Creates small summary CSV files from dat.csv for fast dashboard loading
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
base_dir = Path(__file__).parent.resolve().parent
dat_csv = base_dir / "frontend" / "public" / "dat.csv"
output_dir = base_dir / "frontend" / "public"

# Verify paths exist
if not dat_csv.exists():
    print(f"ERROR: dat.csv not found at {dat_csv}")
    exit(1)

print("Loading dat.csv...")
df = pd.read_csv(dat_csv)

# Extract year from claim_date
df['year'] = pd.to_datetime(df['claim_date'], errors='coerce').dt.year
df['year'] = df['year'].fillna(2024).astype(int)

print(f"Loaded {len(df)} claims")

# 1. Year-Severity Summary
print("\n[1/6] Generating year_severity_summary.csv...")
year_severity = df.groupby(['year', 'CAUTION_LEVEL']).agg({
    'claim_id': 'count',
    'DOLLARAMOUNTHIGH': ['sum', 'mean'],
    'predicted_pain_suffering': ['sum', 'mean'],
    'SETTLEMENT_DAYS': 'mean',
    'variance_pct': 'mean'
}).reset_index()

year_severity.columns = ['year', 'severity_category', 'claim_count',
                         'total_actual_settlement', 'avg_actual_settlement',
                         'total_predicted_settlement', 'avg_predicted_settlement',
                         'avg_settlement_days', 'avg_variance_pct']

# Add over/under prediction counts
def count_over_under(group):
    return pd.Series({
        'overprediction_count': (group['variance_pct'] > 0).sum(),
        'underprediction_count': (group['variance_pct'] < 0).sum(),
        'high_variance_count': (group['variance_pct'].abs() >= 15).sum()
    })

over_under = df.groupby(['year', 'CAUTION_LEVEL']).apply(count_over_under).reset_index()
year_severity = year_severity.merge(over_under, left_on=['year', 'severity_category'],
                                     right_on=['year', 'CAUTION_LEVEL'], how='left')
year_severity = year_severity.drop('CAUTION_LEVEL', axis=1, errors='ignore')

year_severity.to_csv(output_dir / 'year_severity_summary.csv', index=False)
print(f"   Created: {len(year_severity)} rows")

# 2. County-Year Summary
print("[2/6] Generating county_year_summary.csv...")
county_year = df.groupby(['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING']).agg({
    'claim_id': 'count',
    'DOLLARAMOUNTHIGH': ['sum', 'mean'],
    'variance_pct': 'mean'
}).reset_index()

county_year.columns = ['county', 'state', 'year', 'venue_rating', 'claim_count',
                       'total_settlement', 'avg_settlement', 'avg_variance_pct']

# Add high variance stats
high_var = df[df['variance_pct'].abs() >= 15].groupby(['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING']).size().reset_index(name='high_variance_count')
county_year = county_year.merge(high_var, left_on=['county', 'state', 'year', 'venue_rating'],
                                 right_on=['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING'], how='left')
county_year = county_year.drop(['COUNTYNAME', 'VENUESTATE', 'VENUE_RATING'], axis=1, errors='ignore')
county_year['high_variance_count'] = county_year['high_variance_count'].fillna(0).astype(int)
county_year['high_variance_pct'] = (county_year['high_variance_count'] / county_year['claim_count'] * 100).round(2)

# Add over/under prediction
over = df[df['variance_pct'] > 0].groupby(['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING']).size().reset_index(name='overprediction_count')
under = df[df['variance_pct'] < 0].groupby(['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING']).size().reset_index(name='underprediction_count')
county_year = county_year.merge(over, left_on=['county', 'state', 'year', 'venue_rating'],
                                 right_on=['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING'], how='left')
county_year = county_year.drop(['COUNTYNAME', 'VENUESTATE', 'VENUE_RATING'], axis=1, errors='ignore')
county_year = county_year.merge(under, left_on=['county', 'state', 'year', 'venue_rating'],
                                 right_on=['COUNTYNAME', 'VENUESTATE', 'year', 'VENUE_RATING'], how='left')
county_year = county_year.drop(['COUNTYNAME', 'VENUESTATE', 'VENUE_RATING'], axis=1, errors='ignore')
county_year['overprediction_count'] = county_year['overprediction_count'].fillna(0).astype(int)
county_year['underprediction_count'] = county_year['underprediction_count'].fillna(0).astype(int)

county_year.to_csv(output_dir / 'county_year_summary.csv', index=False)
print(f"   Created: {len(county_year)} rows")

# 3. Injury Group Summary
print("[3/6] Generating injury_group_summary.csv...")
injury_group = df.groupby(['INJURY_GROUP_CODE', 'CAUTION_LEVEL']).agg({
    'claim_id': 'count',
    'DOLLARAMOUNTHIGH': ['mean', 'sum'],
    'predicted_pain_suffering': 'mean',
    'variance_pct': 'mean',
    'SETTLEMENT_DAYS': 'mean'
}).reset_index()

injury_group.columns = ['injury_group', 'severity_category', 'claim_count',
                        'avg_settlement', 'total_settlement', 'avg_predicted',
                        'avg_variance_pct', 'avg_settlement_days']

injury_group['body_region'] = 'General'  # Can be enhanced with mapping
injury_group.to_csv(output_dir / 'injury_group_summary.csv', index=False)
print(f"   Created: {len(injury_group)} rows")

# 4. Adjuster Performance Summary
print("[4/6] Generating adjuster_performance_summary.csv...")
adjuster_perf = df.groupby('adjuster').agg({
    'claim_id': 'count',
    'DOLLARAMOUNTHIGH': 'mean',
    'predicted_pain_suffering': 'mean',
    'variance_pct': 'mean',
    'SETTLEMENT_DAYS': 'mean'
}).reset_index()

adjuster_perf.columns = ['adjuster_name', 'claim_count', 'avg_actual_settlement',
                         'avg_predicted_settlement', 'avg_variance_pct', 'avg_settlement_days']

# Calculate high variance count
high_variance = df[df['variance_pct'].abs() >= 15].groupby('adjuster').size().reset_index(name='high_variance_count')
adjuster_perf = adjuster_perf.merge(high_variance, left_on='adjuster_name', right_on='adjuster', how='left')
adjuster_perf = adjuster_perf.drop('adjuster', axis=1, errors='ignore')
adjuster_perf['high_variance_count'] = adjuster_perf['high_variance_count'].fillna(0).astype(int)
adjuster_perf['high_variance_pct'] = (adjuster_perf['high_variance_count'] / adjuster_perf['claim_count'] * 100).round(2)

# Calculate over/under prediction
over = df[df['variance_pct'] > 0].groupby('adjuster').size().reset_index(name='overprediction_count')
under = df[df['variance_pct'] < 0].groupby('adjuster').size().reset_index(name='underprediction_count')
adjuster_perf = adjuster_perf.merge(over, left_on='adjuster_name', right_on='adjuster', how='left')
adjuster_perf = adjuster_perf.drop('adjuster', axis=1, errors='ignore')
adjuster_perf = adjuster_perf.merge(under, left_on='adjuster_name', right_on='adjuster', how='left')
adjuster_perf = adjuster_perf.drop('adjuster', axis=1, errors='ignore')
adjuster_perf['overprediction_count'] = adjuster_perf['overprediction_count'].fillna(0).astype(int)
adjuster_perf['underprediction_count'] = adjuster_perf['underprediction_count'].fillna(0).astype(int)

adjuster_perf.to_csv(output_dir / 'adjuster_performance_summary.csv', index=False)
print(f"   Created: {len(adjuster_perf)} rows")

# 5. Venue Analysis Summary
print("[5/6] Generating venue_analysis_summary.csv...")
venue_analysis = df.groupby(['VENUE_RATING', 'VENUESTATE', 'COUNTYNAME']).agg({
    'claim_id': 'count',
    'DOLLARAMOUNTHIGH': 'mean',
    'predicted_pain_suffering': 'mean',
    'variance_pct': 'mean',
    'RATINGWEIGHT': 'mean'
}).reset_index()

venue_analysis.columns = ['venue_rating', 'state', 'county', 'claim_count',
                          'avg_settlement', 'avg_predicted', 'avg_variance_pct',
                          'avg_venue_rating_point']

# Add high variance percentage
high_var_venue = df[df['variance_pct'].abs() >= 15].groupby(['VENUE_RATING', 'VENUESTATE', 'COUNTYNAME']).size().reset_index(name='high_variance_count')
venue_analysis = venue_analysis.merge(high_var_venue,
                                      left_on=['venue_rating', 'state', 'county'],
                                      right_on=['VENUE_RATING', 'VENUESTATE', 'COUNTYNAME'], how='left')
venue_analysis = venue_analysis.drop(['VENUE_RATING', 'VENUESTATE', 'COUNTYNAME'], axis=1, errors='ignore')
venue_analysis['high_variance_count'] = venue_analysis['high_variance_count'].fillna(0).astype(int)
venue_analysis['high_variance_pct'] = (venue_analysis['high_variance_count'] / venue_analysis['claim_count'] * 100).round(2)

venue_analysis.to_csv(output_dir / 'venue_analysis_summary.csv', index=False)
print(f"   Created: {len(venue_analysis)} rows")

# 6. Variance Drivers Analysis
print("[6/6] Generating variance_drivers_analysis.csv...")

# Get numeric columns for correlation
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlations = []

for col in numeric_cols:
    if col != 'variance_pct' and df[col].notna().sum() > 0:
        try:
            corr = df[col].corr(df['variance_pct'])
            if not pd.isna(corr) and abs(corr) > 0.05:  # Only correlations > 5%
                correlations.append({
                    'factor_name': col,
                    'factor_value': 'Varies',
                    'claim_count': len(df),
                    'avg_variance_pct': df['variance_pct'].mean(),
                    'contribution_score': abs(corr) * 100,
                    'correlation_strength': 'Strong' if abs(corr) > 0.5 else 'Moderate' if abs(corr) > 0.3 else 'Weak'
                })
        except:
            pass

variance_drivers = pd.DataFrame(correlations).sort_values('contribution_score', ascending=False).head(30)
variance_drivers.to_csv(output_dir / 'variance_drivers_analysis.csv', index=False)
print(f"   Created: {len(variance_drivers)} rows")

print("\n" + "="*70)
print("SUCCESS! All aggregated CSV files generated!")
print("="*70)
print(f"\nGenerated files in: {output_dir}")
print("  - year_severity_summary.csv")
print("  - county_year_summary.csv")
print("  - injury_group_summary.csv")
print("  - adjuster_performance_summary.csv")
print("  - venue_analysis_summary.csv")
print("  - variance_drivers_analysis.csv")
print("\nRefresh your browser to see the dashboard!")
