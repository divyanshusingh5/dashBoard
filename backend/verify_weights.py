import pandas as pd

weights = pd.read_csv('data/weights.csv')
dat = pd.read_csv('data/dat.csv')

missing = [f for f in weights['factor_name'].values if f not in dat.columns]

print(f'Weights without matching dat.csv columns: {len(missing)}')
print('\nMissing columns:')
for m in missing:
    print(f'  - {m}')
