from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "RCAEval_DATA"


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


def load_case(case_name):
    case_dir = DATA_ROOT / case_name

    metrics = pd.read_parquet(case_dir / "metrics.parquet")
    logs = pd.read_parquet(case_dir / "logs.parquet")

    traces_path = case_dir / "traces.parquet"

    if traces_path.exists():
        traces = pd.read_parquet(traces_path)
    else:
        traces = None

    return metrics, logs, traces


def count_log_features(logs):
    messages = (
        logs["message"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    text = " ".join(messages.tolist())

    return {
        "log_count": len(messages),

        "uncertainty_count": sum(
            text.count(word)
            for word in [
                "uncertain",
                "unclear",
                "possible",
                "may ",
                "could ",
            ]
        ),

        "conflict_count": sum(
            text.count(word)
            for word in [
                "contradict",
                "conflicting",
                "inconsistent",
                "however",
                "but ",
            ]
        ),

        "error_count": sum(
            text.count(word)
            for word in [
                "error",
                "failure",
                "failed",
                "timeout",
                "exception",
            ]
        ),

        "network_indicator_count": sum(
            text.count(word)
            for word in [
                "network",
                "connection",
                "packet",
                "tcp",
                "http",
            ]
        ),

        "cpu_indicator_count": sum(
            text.count(word)
            for word in [
                "cpu",
                "processor",
                "compute",
            ]
        ),

        "memory_indicator_count": sum(
            text.count(word)
            for word in [
                "memory",
                "oom",
                "out of memory",
                "heap",
            ]
        ),
    }


def summarize_metrics(metrics):
    numeric = metrics.select_dtypes(include=np.number)

    result = {
        "metric_row_count": len(metrics),
        "metric_column_count": len(numeric.columns),
    }

    for column in numeric.columns:

        values = pd.to_numeric(
            numeric[column],
            errors="coerce"
        ).dropna()

        if len(values) == 0:
            continue

        safe_name = (
            column
            .replace("-", "_")
            .replace(".", "_")
            .replace(" ", "_")
        )

        result[f"{safe_name}_mean"] = values.mean()
        result[f"{safe_name}_max"] = values.max()
        result[f"{safe_name}_std"] = values.std()

    return result


def summarize_traces(traces):

    if traces is None:
        return {
            "trace_available": 0,
            "trace_count": 0,
            "trace_error_count": 0,
            "trace_duration_mean": 0,
            "trace_duration_max": 0,
        }

    result = {
        "trace_available": 1,
        "trace_count": len(traces),
    }

    if "statusCode" in traces.columns:

        status = pd.to_numeric(
            traces["statusCode"],
            errors="coerce"
        )

        result["trace_error_count"] = int(
            (status >= 400).sum()
        )

    else:
        result["trace_error_count"] = 0

    if "duration" in traces.columns:

        duration = pd.to_numeric(
            traces["duration"],
            errors="coerce"
        ).dropna()

        if len(duration) > 0:
            result["trace_duration_mean"] = duration.mean()
            result["trace_duration_max"] = duration.max()
        else:
            result["trace_duration_mean"] = 0
            result["trace_duration_max"] = 0

    else:
        result["trace_duration_mean"] = 0
        result["trace_duration_max"] = 0

    return result


def build_feature_table():

    rows = []

    for case_name, metadata in CASES.items():

        print(f"Processing {case_name}...")

        metrics, logs, traces = load_case(case_name)

        row = {
            "case_id": case_name,
            "condition": metadata["condition"],
            "target_service": metadata["target_service"],

            "metrics_available": 1,
            "logs_available": 1,
            "traces_available": int(traces is not None),

            "evidence_count": (
                1
                + 1
                + int(traces is not None)
            ),
        }

        row.update(count_log_features(logs))
        row.update(summarize_metrics(metrics))
        row.update(summarize_traces(traces))

        rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":

    output_dir = ROOT / "ml" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = build_feature_table()

    output_file = output_dir / "rcaeval_features.csv"

    df.to_csv(output_file, index=False)

    print()
    print("Feature table created successfully.")
    print(f"Output: {output_file}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print()
    print(df[[
        "case_id",
        "condition",
        "target_service",
        "evidence_count",
        "log_count",
        "trace_available",
    ]].to_string(index=False))