"""
Create weights summary for recalibration UI
Extracts factor-level weight statistics from per-claim weights.csv
"""
import pandas as pd
import numpy as np

def create_weights_summary():
    """Create factor-level summary from per-claim weights"""
    print("Loading weights.csv...")
    df = pd.read_csv('data/weights.csv', low_memory=False)

    # Clinical feature columns (with single quotes)
    clinical_features = [col for col in df.columns if col.startswith("'") and col.endswith("'")]

    print(f"Found {len(clinical_features)} clinical features")

    # Create summary for each feature
    summary_rows = []

    for feature in clinical_features:
        # Get weight values (excluding NaN)
        weights = df[feature].dropna()

        if len(weights) == 0:
            continue

        # Calculate statistics
        summary_rows.append({
            'factor_name': feature.strip("'"),  # Remove quotes
            'base_weight': round(weights.mean(), 4),
            'min_weight': round(weights.min(), 4),
            'max_weight': round(weights.max(), 4),
            'std_weight': round(weights.std(), 4),
            'median_weight': round(weights.median(), 4),
            'category': categorize_feature(feature.strip("'")),
            'description': generate_description(feature.strip("'")),
            'usage_count': int(len(weights)),
            'usage_pct': round(len(weights) / len(df) * 100, 2)
        })

    # Create summary dataframe
    summary_df = pd.DataFrame(summary_rows)

    # Save summary
    output_path = 'data/weights_summary.csv'
    summary_df.to_csv(output_path, index=False)
    print(f"\nCreated weights summary: {output_path}")
    print(f"Total factors: {len(summary_df)}")
    print("\nSample:")
    print(summary_df.head(10))

    return summary_df

def categorize_feature(feature_name):
    """Categorize feature by name"""
    if 'Causation' in feature_name or 'Compliance' in feature_name:
        return 'Causation'
    elif 'Treatment' in feature_name or 'Therapy' in feature_name:
        return 'Treatment'
    elif 'Injury' in feature_name or 'Trauma' in feature_name:
        return 'Injury'
    elif 'Pain' in feature_name or 'Symptom' in feature_name:
        return 'Clinical'
    elif 'Disability' in feature_name or 'Recovery' in feature_name:
        return 'Disability'
    else:
        return 'Other'

def generate_description(feature_name):
    """Generate human-readable description"""
    # Convert snake_case to readable text
    words = feature_name.replace('_', ' ')
    return f"Weight contribution for {words.lower()}"

if __name__ == '__main__':
    create_weights_summary()
