from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "ml" / "results"

input_file = RESULTS_DIR / "combined_features.csv"
output_file = RESULTS_DIR / "dataset_summary.csv"

df = pd.read_csv(input_file)

summary = pd.DataFrame({
    "metric": [
        "rows",
        "columns",
        "numeric_features",
        "categorical_features",
        "missing_values",
        "unique_cases",
        "conditions"
    ],
    "value": [
        len(df),
        len(df.columns),
        len(df.select_dtypes(include="number").columns),
        len(df.select_dtypes(exclude="number").columns),
        int(df.isna().sum().sum()),
        df["case_id"].nunique(),
        ", ".join(df["condition"].unique())
    ]
})

summary.to_csv(output_file, index=False)

print("Dataset summary created successfully.")
print()
print(summary.to_string(index=False))
