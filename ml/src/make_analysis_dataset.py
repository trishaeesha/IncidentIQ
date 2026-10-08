from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "ml" / "results"

input_file = RESULTS_DIR / "combined_features.csv"
output_file = RESULTS_DIR / "rcaeval_analysis_features.csv"

df = pd.read_csv(input_file)

keep = [
    "case_id",
    "condition",
    "target_service",
    "evidence_count",
    "log_count_x",
    "trace_available",
    "total_nlp_indicators",
    "uncertainty_count",
    "conflict_count",
    "error_count",
    "network_count",
    "cpu_count",
    "memory_count",
    "latency_count",
]

available = [column for column in keep if column in df.columns]

analysis_df = df[available].copy()

analysis_df.to_csv(output_file, index=False)

print("Compact RCAEval analysis dataset created.")
print(f"Output: {output_file}")
print(f"Rows: {len(analysis_df)}")
print(f"Columns: {len(analysis_df.columns)}")
print()
print(analysis_df.to_string(index=False))
