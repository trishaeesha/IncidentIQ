from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "ml" / "results"

structured_file = RESULTS_DIR / "rcaeval_features.csv"
nlp_file = RESULTS_DIR / "nlp_features.csv"
output_file = RESULTS_DIR / "combined_features.csv"

structured = pd.read_csv(structured_file)
nlp = pd.read_csv(nlp_file)

combined = structured.merge(
    nlp,
    on=["case_id", "condition", "target_service"],
    how="inner"
)

combined.to_csv(output_file, index=False)

print("Combined feature table created successfully.")
print(f"Output: {output_file}")
print(f"Rows: {len(combined)}")
print(f"Columns: {len(combined.columns)}")
print()
print(combined[[
    "case_id",
    "condition",
    "target_service",
    "evidence_count",
    "log_count_x",
    "trace_available",
    "total_nlp_indicators"
]].to_string(index=False))
