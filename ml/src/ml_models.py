from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "ml" / "results"

input_file = RESULTS_DIR / "rcaeval_analysis_features.csv"
output_file = RESULTS_DIR / "model_metrics.csv"

df = pd.read_csv(input_file)

print("RCAEval analysis dataset loaded.")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print()

print("IMPORTANT:")
print("Only 3 RCAEval cases are available.")
print("This is NOT enough for valid predictive ML.")
print("The following output is descriptive baseline analysis only.")
print()

rows = []

for _, row in df.iterrows():
    rows.append({
        "case_id": row["case_id"],
        "condition": row["condition"],
        "evidence_count": row["evidence_count"],
        "log_count": row["log_count_x"],
        "trace_available": row["trace_available"],
        "total_nlp_indicators": row["total_nlp_indicators"],
        "network_count": row["network_count"],
        "cpu_count": row["cpu_count"],
        "memory_count": row["memory_count"],
        "latency_count": row["latency_count"],
    })

metrics = pd.DataFrame(rows)

metrics["nlp_indicator_density_per_1000_logs"] = (
    metrics["total_nlp_indicators"] /
    metrics["log_count"] * 1000
)

metrics.to_csv(output_file, index=False)

print("Baseline analysis table created.")
print(f"Output: {output_file}")
print()
print(metrics.to_string(index=False))
