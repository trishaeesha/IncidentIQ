"""Deterministic evidence extraction from RCAEval telemetry.

Evidence Engine v2.

Design principles:
- Uses telemetry only.
- Does not use RCAEval fault/root-cause fields.
- Does not treat the time column as a metric.
- Handles near-zero baselines without absurd relative percentages.
- Preserves raw measurements.
- Produces service-level context where service can be inferred safely
  from metric names.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _load_parquet(path: Path | None) -> pd.DataFrame | None:
    """Load a parquet file if it exists."""
    if path is None or not path.exists():
        return None

    return pd.read_parquet(path)


def _find_time_column(df: pd.DataFrame) -> str | None:
    """Find the telemetry time column."""
    candidates = [
        "timestamp",
        "time",
        "time_stamp",
        "datetime",
    ]

    lowered = {
        str(column).lower(): column
        for column in df.columns
    }

    for name in candidates:
        if name in lowered:
            return lowered[name]

    for column in df.columns:
        name = str(column).lower()

        if "timestamp" in name or name.endswith("_time"):
            return column

    return None


def _numeric_columns(
    df: pd.DataFrame,
    exclude: set[str] | None = None,
) -> list[str]:
    """Return numeric columns excluding known non-metric fields."""
    excluded = exclude or set()

    return [
        column
        for column in df.columns
        if column not in excluded
        and pd.api.types.is_numeric_dtype(df[column])
    ]


def _infer_service(metric_name: str) -> str | None:
    """Infer service name from RCAEval metric naming convention.

    Examples:
        checkoutservice_cpu -> checkoutservice
        frontend_latency-90 -> frontend
        frontend-external_workload -> frontend-external
    """
    name = str(metric_name)

    suffixes = [
        "_cpu",
        "_mem",
        "_diskio",
        "_socket",
        "_workload",
        "_error",
        "_latency-50",
        "_latency-90",
    ]

    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)]

    return None


def _baseline_quality(
    values: pd.Series,
) -> str:
    """Describe whether the pre-injection baseline is numerically stable."""
    clean = pd.to_numeric(values, errors="coerce").dropna()

    if clean.empty:
        return "unavailable"

    median = float(clean.median())

    if abs(median) < 1e-9:
        return "near_zero"

    std = float(clean.std())

    if pd.isna(std):
        return "stable"

    coefficient = abs(std / median)

    if coefficient < 0.25:
        return "stable"

    if coefficient < 0.75:
        return "variable"

    return "highly_variable"


def _strength_from_change(
    absolute_change: float,
    relative_change: float | None,
    baseline_quality: str,
) -> str:
    """Assign provisional evidence strength.

    These thresholds are engineering heuristics for the prototype.
    They are NOT validated scientific thresholds.
    """
    if baseline_quality == "near_zero":
        if abs(absolute_change) < 1e-9:
            return "weak"

        return "moderate"

    if relative_change is None:
        return "weak"

    magnitude = abs(relative_change)

    if magnitude < 0.20:
        return "weak"

    if magnitude < 0.50:
        return "moderate"

    return "strong"


def _direction(
    absolute_change: float,
) -> str:
    """Convert numerical change to a qualitative direction."""
    if absolute_change > 0:
        return "increase"

    if absolute_change < 0:
        return "decrease"

    return "no_change"


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

    timestamps = pd.to_numeric(
        df[time_column],
        errors="coerce",
    )

    valid_timestamps = timestamps.dropna()

    if valid_timestamps.empty:
        return []

    before = df[
        timestamps < float(injection_time)
    ]

    after = df[
        timestamps >= float(injection_time)
    ]

    if before.empty or after.empty:
        return []

    # CRITICAL:
    # Never allow the time column to become evidence.
    numeric_columns = _numeric_columns(
        df,
        exclude={time_column},
    )

    evidence: list[dict[str, Any]] = []

    for metric in numeric_columns:

        before_values = pd.to_numeric(
            before[metric],
            errors="coerce",
        ).dropna()

        after_values = pd.to_numeric(
            after[metric],
            errors="coerce",
        ).dropna()

        if before_values.empty or after_values.empty:
            continue

        before_value = float(before_values.mean())
        after_value = float(after_values.mean())

        absolute_change = (
            after_value - before_value
        )

        baseline_quality = _baseline_quality(
            before_values
        )

        # Avoid meaningless relative percentages
        # when the baseline is zero or almost zero.
        if abs(before_value) < 1e-9:
            relative_change = None
        else:
            relative_change = (
                absolute_change / abs(before_value)
            )

        direction = _direction(
            absolute_change
        )

        strength = _strength_from_change(
            absolute_change=absolute_change,
            relative_change=relative_change,
            baseline_quality=baseline_quality,
        )

        service = _infer_service(
            str(metric)
        )

        evidence.append(
            {
                "source": "metrics",
                "metric": str(metric),
                "service": service,
                "before": before_value,
                "after": after_value,
                "absolute_change": absolute_change,
                "relative_change": relative_change,
                "direction": direction,
                "strength": strength,
                "baseline_quality": baseline_quality,
                "before_samples": int(
                    len(before_values)
                ),
                "after_samples": int(
                    len(after_values)
                ),
                "time_context": {
                    "injection_time": float(
                        injection_time
                    ),
                    "before_start": float(
                        valid_timestamps.min()
                    ),
                    "after_end": float(
                        valid_timestamps.max()
                    ),
                },
            }
        )

    # Sort by absolute change.
    # If relative change is unavailable, absolute change
    # remains the safest ranking signal for near-zero baselines.
    evidence.sort(
        key=lambda item: (
            abs(item["relative_change"])
            if item["relative_change"] is not None
            else abs(item["absolute_change"])
        ),
        reverse=True,
    )

    return evidence


def extract_case_evidence(
    case_root: str | Path,
    injection_time: float | int,
) -> dict[str, Any]:
    """Extract the current deterministic evidence representation."""

    root = Path(case_root)

    metrics_path = (
        root / "metrics.parquet"
    )

    logs_path = (
        root / "logs.parquet"
    )

    traces_path = (
        root / "traces.parquet"
    )

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
