from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "ml" / "results"

input_file = RESULTS_DIR / "rcaeval_analysis_features.csv"
output_file = RESULTS_DIR / "feature_importance.csv"

df = pd.read_csv(input_file)

features = [
    "evidence_count",
    "log_count_x",
    "trace_available",
    "total_nlp_indicators",
    "network_count",
    "cpu_count",
    "memory_count",
    "latency_count",
]

rows = []

for feature in features:
    if feature in df.columns:
        rows.append({
            "feature": feature,
            "mean": df[feature].mean(),
            "minimum": df[feature].min(),
            "maximum": df[feature].max(),
            "interpretation": "Descriptive RCAEval feature; not predictive importance"
        })

result = pd.DataFrame(rows)
result.to_csv(output_file, index=False)

print("Feature analysis created.")
print(f"Output: {output_file}")
print()
print(result.to_string(index=False))
