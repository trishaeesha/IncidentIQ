"""Deterministic evidence extraction from RCAEval telemetry.

This module compares telemetry before and after the known injection boundary.
It does NOT use RCAEval ground-truth fault/root-cause fields.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _load_parquet(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    return pd.read_parquet(path)


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]


def _find_time_column(df: pd.DataFrame) -> str | None:
    candidates = [
        "timestamp",
        "time",
        "time_stamp",
        "datetime",
    ]

    lowered = {str(c).lower(): c for c in df.columns}

    for name in candidates:
        if name in lowered:
            return lowered[name]

    for column in df.columns:
        name = str(column).lower()
        if "time" in name or "timestamp" in name:
            return column

    return None


def _numeric_summary(
    df: pd.DataFrame,
    numeric_columns: list[str],
) -> dict[str, float]:
    summary: dict[str, float] = {}

    for column in numeric_columns:
        values = pd.to_numeric(df[column], errors="coerce").dropna()

        if values.empty:
            continue

        summary[str(column)] = float(values.mean())

    return summary


def extract_metric_evidence(
    metrics_path: str | Path,
    injection_time: float | int,
) -> list[dict[str, Any]]:
    """Extract deterministic pre/post metric observations."""

    path = Path(metrics_path)
    df = _load_parquet(path)

    if df is None or df.empty:
        return []

    time_column = _find_time_column(df)

    if time_column is None:
        return []

    timestamps = pd.to_numeric(df[time_column], errors="coerce")

    before = df[timestamps < float(injection_time)]
    after = df[timestamps >= float(injection_time)]

    if before.empty or after.empty:
        return []

    numeric_columns = _numeric_columns(df)

    before_summary = _numeric_summary(before, numeric_columns)
    after_summary = _numeric_summary(after, numeric_columns)

    evidence: list[dict[str, Any]] = []

    for metric, before_value in before_summary.items():
        after_value = after_summary.get(metric)

        if after_value is None:
            continue

        absolute_change = after_value - before_value

        denominator = max(abs(before_value), 1e-9)
        relative_change = absolute_change / denominator

        if abs(relative_change) < 0.20:
            strength = "weak"
        elif abs(relative_change) < 0.50:
            strength = "moderate"
        else:
            strength = "strong"

        direction = (
            "increase"
            if absolute_change > 0
            else "decrease"
            if absolute_change < 0
            else "no_change"
        )

        evidence.append(
            {
                "source": "metrics",
                "metric": metric,
                "before": before_value,
                "after": after_value,
                "absolute_change": absolute_change,
                "relative_change": relative_change,
                "direction": direction,
                "strength": strength,
            }
        )

    evidence.sort(
        key=lambda item: abs(item["relative_change"]),
        reverse=True,
    )

    return evidence


def extract_case_evidence(
    case_root: str | Path,
    injection_time: float | int,
) -> dict[str, Any]:
    """Extract the first deterministic evidence representation for a case."""

    root = Path(case_root)

    metrics_path = root / "metrics.parquet"
    logs_path = root / "logs.parquet"
    traces_path = root / "traces.parquet"

    metric_evidence = extract_metric_evidence(
        metrics_path,
        injection_time,
    )

    return {
        "metrics_available": metrics_path.exists(),
        "logs_available": logs_path.exists(),
        "traces_available": traces_path.exists(),
        "metric_evidence": metric_evidence,
    }
