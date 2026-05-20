import pandas as pd
import os

folder = "excel"

for fname in sorted(os.listdir(folder)):
    if not fname.endswith('.csv'):
        continue
    path = os.path.join(folder, fname)
    df = pd.read_csv(path)
    print(f"\n{'='*60}")
    print(f"ФАЙЛ: {fname}")
    print(f"Строк: {len(df):,}  |  Колонок: {len(df.columns)}")
    print(f"Колонки: {list(df.columns)}")
    print("Пример данных (2 строки):")
    print(df.head(2).to_string())
