from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "RCAEval_DATA"
RESULTS_DIR = ROOT / "ml" / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CASES = {
    "re2ob_checkoutservice_cpu_2": {
        "condition": "resource_cpu",
        "target_service": "checkoutservice",
    },
    "re2ob_checkoutservice_mem_2": {
        "condition": "resource_memory",
        "target_service": "checkoutservice",
    },
    "re2ss_user_loss_1": {
        "condition": "network_packet_loss",
        "target_service": "user",
    },
}

PATTERNS = {
    "uncertainty": r"\b(?:uncertain|unclear|possible|possibly|may|could|might)\b",
    "conflict": r"\b(?:contradict|conflict|conflicting|inconsistent|however|but)\b",
    "error": r"\b(?:error|failure|failed|timeout|exception)\b",
    "network": r"\b(?:network|connection|packet|tcp|http)\b",
    "cpu": r"\b(?:cpu|processor|compute)\b",
    "memory": r"\b(?:memory|oom|out of memory|heap)\b",
    "latency": r"\b(?:latency|slow|delay|response time)\b",
}

def count_pattern(text_series, pattern):
    return int(
        text_series.str.contains(
            pattern,
            case=False,
            regex=True,
            na=False,
        ).sum()
    )

rows = []

for case_id, metadata in CASES.items():
    print(f"Processing {case_id}...")

    logs_file = DATA_DIR / case_id / "logs.parquet"

    if not logs_file.exists():
        print(f"WARNING: logs file not found: {logs_file}")
        continue

    logs = pd.read_parquet(logs_file)

    messages = logs["message"].fillna("").astype(str)

    row = {
        "case_id": case_id,
        "condition": metadata["condition"],
        "target_service": metadata["target_service"],
        "log_count": len(messages),
        "unique_log_messages": messages.nunique(),
        "average_log_length": messages.str.len().mean(),
    }

    for category, pattern in PATTERNS.items():
        count = count_pattern(messages, pattern)

        row[f"{category}_count"] = count
        row[f"{category}_per_1000_logs"] = (
            count / len(messages) * 1000
            if len(messages) > 0
            else 0
        )

    row["total_nlp_indicators"] = sum(
        row[f"{category}_count"]
        for category in PATTERNS
    )

    rows.append(row)

output = pd.DataFrame(rows)

output_file = RESULTS_DIR / "nlp_features.csv"
output.to_csv(output_file, index=False)

print()
print("NLP feature table created successfully.")
print(f"Output: {output_file}")
print(f"Rows: {len(output)}")
print(f"Columns: {len(output.columns)}")
print()
print(output.to_string(index=False))
