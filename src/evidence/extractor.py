"""Deterministic evidence extraction from RCAEval telemetry.

The metric extractor preserves the existing project-owner schema. Log and trace
extractors add modality-specific observations and a common EvidenceRecord view.
No RCAEval ground-truth fields are read by this module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .schema import EvidenceRecord


def _load_parquet(path: str | Path | None) -> pd.DataFrame | None:
    if path is None or not Path(path).exists():
        return None
    return pd.read_parquet(path)


def _find_time_column(df: pd.DataFrame) -> str | None:
    candidates = ("timestamp", "time", "time_stamp", "datetime", "starttime", "start_time")
    lowered = {str(c).lower(): c for c in df.columns}
    for name in candidates:
        if name in lowered:
            return lowered[name]
    for column in df.columns:
        name = str(column).lower()
        if "timestamp" in name or name.endswith("_time"):
            return column
    return None


def _numeric_columns(df: pd.DataFrame, exclude: set[str] | None = None) -> list[str]:
    excluded = exclude or set()
    return [
        column for column in df.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(df[column])
    ]


def _infer_service(metric_name: str) -> str | None:
    name = str(metric_name)
    suffixes = (
        "_cpu", "_mem", "_diskio", "_socket", "_workload", "_error",
        "_latency-50", "_latency-90",
    )
    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return None


def _baseline_quality(values: pd.Series) -> str:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return "unavailable"
    median = float(clean.median())
    if abs(median) < 1e-9:
        return "near_zero"
    std = float(clean.std())
    if pd.isna(std):
        return "stable"
    cv = abs(std / median)
    if cv < 0.25:
        return "stable"
    if cv < 0.75:
        return "variable"
    return "highly_variable"


def _relative_change(before: float, after: float) -> float | None:
    if abs(before) < 1e-9:
        return None
    return (after - before) / abs(before)


def _strength(relative: float | None, baseline_quality: str) -> str:
    if baseline_quality == "near_zero":
        return "moderate"
    if relative is None:
        return "weak"
    magnitude = abs(relative)
    if magnitude < 0.20:
        return "weak"
    if magnitude < 0.50:
        return "moderate"
    return "strong"


def _direction(delta: float) -> str:
    if delta > 0:
        return "increase"
    if delta < 0:
        return "decrease"
    return "no_change"


# ---------------------------------------------------------------------------
# Existing metric engine: schema and behavior intentionally preserved.
# ---------------------------------------------------------------------------

def extract_metric_evidence(
    metrics_path: str | Path,
    injection_time: float | int,
) -> list[dict[str, Any]]:
    path = Path(metrics_path)
    df = _load_parquet(path)
    if df is None or df.empty:
        return []

    time_column = _find_time_column(df)
    if time_column is None:
        return []

    timestamps = pd.to_numeric(df[time_column], errors="coerce")
    valid_timestamps = timestamps.dropna()
    if valid_timestamps.empty:
        return []

    before = df[timestamps < float(injection_time)]
    after = df[timestamps >= float(injection_time)]
    if before.empty or after.empty:
        return []

    numeric_columns = _numeric_columns(df, exclude={time_column})
    evidence: list[dict[str, Any]] = []

    for metric in numeric_columns:
        before_values = pd.to_numeric(before[metric], errors="coerce").dropna()
        after_values = pd.to_numeric(after[metric], errors="coerce").dropna()
        if before_values.empty or after_values.empty:
            continue

        before_value = float(before_values.mean())
        after_value = float(after_values.mean())
        absolute_change = after_value - before_value
        baseline_quality = _baseline_quality(before_values)
        relative_change = _relative_change(before_value, after_value)
        evidence.append({
            "source": "metrics",
            "metric": str(metric),
            "service": _infer_service(str(metric)),
            "before": before_value,
            "after": after_value,
            "absolute_change": absolute_change,
            "relative_change": relative_change,
            "direction": _direction(absolute_change),
            "strength": _strength(relative_change, baseline_quality),
            "baseline_quality": baseline_quality,
            "before_samples": int(len(before_values)),
            "after_samples": int(len(after_values)),
            "time_context": {
                "injection_time": float(injection_time),
                "before_start": float(valid_timestamps.min()),
                "after_end": float(valid_timestamps.max()),
            },
        })

    evidence.sort(
        key=lambda item: (
            abs(item["relative_change"])
            if item["relative_change"] is not None
            else abs(item["absolute_change"])
        ),
        reverse=True,
    )
    return evidence


# ---------------------------------------------------------------------------
# Log evidence
# ---------------------------------------------------------------------------

def _time_context(ts: pd.Series, injection_time: float | int, before: pd.Series, after: pd.Series) -> dict[str, Any]:
    clean = pd.to_numeric(ts, errors="coerce").dropna()
    context: dict[str, Any] = {"injection_time": injection_time}
    if not clean.empty:
        context.update({
            "before_start": float(clean[before.index].min()) if not before.empty else None,
            "before_end": float(clean[before.index].max()) if not before.empty else None,
            "after_start": float(clean[after.index].min()) if not after.empty else None,
            "after_end": float(clean[after.index].max()) if not after.empty else None,
        })
    return context


def _log_time_column(df: pd.DataFrame) -> str | None:
    return _find_time_column(df)


def _text_column(df: pd.DataFrame) -> str | None:
    lowered = {str(c).lower(): c for c in df.columns}
    for name in ("message", "msg", "log", "body", "content"):
        if name in lowered:
            return lowered[name]
    return None


def _service_column(df: pd.DataFrame) -> str | None:
    lowered = {str(c).lower(): c for c in df.columns}
    for name in ("container_name", "service", "service_name", "container", "pod", "application"):
        if name in lowered:
            return lowered[name]
    return None


def _rate(count: int, start: float | None, end: float | None) -> float | None:
    if start is None or end is None or end <= start:
        return None
    return count / (end - start)


def _log_signal(message: str) -> str:
    text = str(message).lower()
    # Preliminary lexical signal only; not a ground-truth failure classifier.
    if any(token in text for token in ("error", "exception", "failed", "failure")):
        return "error_like"
    if any(token in text for token in ("warn", "warning")):
        return "warning_like"
    return "other"


def extract_log_evidence(
    logs_path: str | Path,
    injection_time: float | int,
) -> list[dict[str, Any]]:
    df = _load_parquet(logs_path)
    if df is None or df.empty:
        return []

    time_col = _log_time_column(df)
    message_col = _text_column(df)
    if time_col is None:
        return []

    ts = pd.to_numeric(df[time_col], errors="coerce")
    valid = ts.notna()
    before = df[valid & (ts < float(injection_time))]
    after = df[valid & (ts >= float(injection_time))]
    if before.empty and after.empty:
        return []

    service_col = _service_column(df)
    records: list[dict[str, Any]] = []

    before_start = float(ts.loc[before.index].min()) if not before.empty else None
    before_end = float(ts.loc[before.index].max()) if not before.empty else None
    after_start = float(ts.loc[after.index].min()) if not after.empty else None
    after_end = float(ts.loc[after.index].max()) if not after.empty else None

    groups: list[tuple[str, pd.DataFrame, pd.DataFrame]] = []
    if service_col:
        names = sorted(set(before[service_col].fillna("<unknown>").astype(str)) |
                       set(after[service_col].fillna("<unknown>").astype(str)))
        for service in names:
            groups.append((
                service,
                before[before[service_col].fillna("<unknown>").astype(str) == service],
                after[after[service_col].fillna("<unknown>").astype(str) == service],
            ))
    else:
        groups.append(("<unknown>", before, after))

    for service, b, a in groups:
        b_count, a_count = len(b), len(a)
        b_rate, a_rate = _rate(b_count, before_start, before_end), _rate(a_count, after_start, after_end)
        delta = (a_rate - b_rate) if b_rate is not None and a_rate is not None else float(a_count - b_count)
        rel = _relative_change(b_rate, a_rate) if b_rate is not None and a_rate is not None else None
        records.append({
            "source": "logs",
            "service": None if service == "<unknown>" else service,
            "observation": "log message count/rate changed" if b_count and a_count else "log messages observed in one side of the injection boundary",
            "signal": "log_rate",
            "before": b_rate if b_rate is not None else b_count,
            "after": a_rate if a_rate is not None else a_count,
            "absolute_change": delta,
            "relative_change": rel,
            "direction": _direction(delta),
            "strength": _strength(rel, "stable" if b_count else "unavailable"),
            "baseline_quality": "stable" if b_count else "unavailable",
            "before_samples": b_count,
            "after_samples": a_count,
            "time_context": {
                "injection_time": float(injection_time),
                "before_start": before_start,
                "before_end": before_end,
                "after_start": after_start,
                "after_end": after_end,
                "temporal_relation": "temporally associated with injection",
            },
            "explanation": "Counts/rates are deterministic observations; they do not establish failure or causality.",
        })

    if message_col:
        for label in ("error_like", "warning_like"):
            classified = df[valid & df[message_col].fillna("").map(_log_signal).eq(label)]
            b = classified[ts.loc[classified.index] < float(injection_time)]
            a = classified[ts.loc[classified.index] >= float(injection_time)]
            b_count, a_count = len(b), len(a)
            if not b_count and not a_count:
                continue
            b_rate = _rate(b_count, before_start, before_end)
            a_rate = _rate(a_count, after_start, after_end)
            delta = (a_rate - b_rate) if b_rate is not None and a_rate is not None else float(a_count - b_count)
            rel = _relative_change(b_rate, a_rate) if b_rate is not None and a_rate is not None else None
            records.append({
                "source": "logs",
                "service": None,
                "observation": f"{label.replace('_', '-')} message frequency changed",
                "signal": label,
                "before": b_rate if b_rate is not None else b_count,
                "after": a_rate if a_rate is not None else a_count,
                "absolute_change": delta,
                "relative_change": rel,
                "direction": _direction(delta),
                "strength": _strength(rel, "stable" if b_count else "unavailable"),
                "baseline_quality": "stable" if b_count else "unavailable",
                "before_samples": b_count,
                "after_samples": a_count,
                "time_context": {
                    "injection_time": float(injection_time),
                    "before_start": before_start,
                    "before_end": before_end,
                    "after_start": after_start,
                    "after_end": after_end,
                    "temporal_relation": "temporally associated with injection",
                },
                "explanation": "Keyword-based preliminary classification; message text is not ground truth for failure.",
            })
    return records


# ---------------------------------------------------------------------------
# Trace evidence
# ---------------------------------------------------------------------------

def _trace_column(df: pd.DataFrame, names: tuple[str, ...]) -> str | None:
    lowered = {str(c).lower(): c for c in df.columns}
    for name in names:
        if name in lowered:
            return lowered[name]
    return None


def extract_trace_evidence(
    traces_path: str | Path,
    injection_time: float | int,
) -> list[dict[str, Any]]:
    df = _load_parquet(traces_path)
    if df is None or df.empty:
        return []

    time_col = _trace_column(df, ("time", "timestamp", "starttime", "start_time"))
    duration_col = _trace_column(df, ("duration", "duration_ms"))
    service_col = _trace_column(df, ("servicename", "service_name", "service"))
    operation_col = _trace_column(df, ("operationname", "operation_name", "methodname", "method_name"))
    status_col = _trace_column(df, ("statuscode", "status_code", "status"))

    if time_col is None:
        return []

    ts = pd.to_numeric(df[time_col], errors="coerce")
    valid = ts.notna()
    before = df[valid & (ts < float(injection_time))]
    after = df[valid & (ts >= float(injection_time))]
    if before.empty and after.empty:
        return []

    b_start = float(ts.loc[before.index].min()) if not before.empty else None
    b_end = float(ts.loc[before.index].max()) if not before.empty else None
    a_start = float(ts.loc[after.index].min()) if not after.empty else None
    a_end = float(ts.loc[after.index].max()) if not after.empty else None

    records: list[dict[str, Any]] = []

    def add_record(service: str | None, operation: str | None, signal: str,
                   before_value: float | int, after_value: float | int,
                   explanation: str) -> None:
        delta = float(after_value) - float(before_value)
        rel = _relative_change(float(before_value), float(after_value))
        records.append({
            "source": "traces",
            "service": service,
            "operation": operation,
            "observation": signal.replace("_", " ") + " changed",
            "signal": signal,
            "before": before_value,
            "after": after_value,
            "absolute_change": delta,
            "relative_change": rel,
            "direction": _direction(delta),
            "strength": _strength(rel, "stable" if before_value else "near_zero"),
            "baseline_quality": "stable" if before_value else "near_zero",
            "before_samples": len(before),
            "after_samples": len(after),
            "time_context": {
                "injection_time": float(injection_time),
                "before_start": b_start, "before_end": b_end,
                "after_start": a_start, "after_end": a_end,
                "temporal_relation": "temporally associated with injection",
            },
            "explanation": explanation,
        })

    add_record(None, None, "span_count", len(before), len(after),
               "Span counts are deterministic observations and do not establish causality.")

    if duration_col:
        bvals = pd.to_numeric(before[duration_col], errors="coerce").dropna()
        avals = pd.to_numeric(after[duration_col], errors="coerce").dropna()
        if not bvals.empty and not avals.empty:
            add_record(None, None, "latency_median", float(bvals.median()), float(avals.median()),
                       "Median span duration changed in the pre/post windows.")

    if service_col:
        services = sorted(set(before[service_col].fillna("<unknown>").astype(str)) |
                          set(after[service_col].fillna("<unknown>").astype(str)))
        for service in services:
            b = before[before[service_col].fillna("<unknown>").astype(str) == service]
            a = after[after[service_col].fillna("<unknown>").astype(str) == service]
            add_record(None if service == "<unknown>" else service, None, "service_span_count", len(b), len(a),
                       "Service-level span counts are observational; simultaneous changes do not imply a causal relationship.")

            if duration_col:
                bv = pd.to_numeric(b[duration_col], errors="coerce").dropna()
                av = pd.to_numeric(a[duration_col], errors="coerce").dropna()
                if not bv.empty and not av.empty:
                    add_record(None if service == "<unknown>" else service, None, "service_latency_median",
                               float(bv.median()), float(av.median()),
                               "Service latency changed in the pre/post windows.")

    if status_col:
        status = pd.to_numeric(df[status_col], errors="coerce")
        # Conservative: non-zero numeric status is an error-like status signal,
        # but this is not interpreted as root cause.
        for label, mask in (("error_status", status > 0),):
            bcount = int((mask & (ts < float(injection_time))).sum())
            acount = int((mask & (ts >= float(injection_time))).sum())
            if bcount or acount:
                add_record(None, None, label, bcount, acount,
                           "Numeric non-zero status codes are treated as an error-like trace signal only; schema-specific semantics may vary.")

    return records


# ---------------------------------------------------------------------------
# Unified representation and service grouping
# ---------------------------------------------------------------------------

def _record(case_id: str, item: dict[str, Any]) -> EvidenceRecord:
    return EvidenceRecord(
        case_id=str(case_id),
        evidence_source=str(item["source"]),
        observation=str(item.get("observation", "")),
        direction_change=item.get("direction"),
        magnitude=item.get("absolute_change"),
        time_context=item.get("time_context", {}),
        affected_service_component=item.get("service"),
        evidence_strength=str(item.get("strength", "weak")),
        classification=None,
        explanation=str(item.get("explanation", "")),
        raw_measurements={
            "before": item.get("before"),
            "after": item.get("after"),
            "absolute_change": item.get("absolute_change"),
            "relative_change": item.get("relative_change"),
            "signal": item.get("signal") or item.get("metric") or item.get("operation"),
        },
    )


def extract_evidence(
    *,
    case_id: str,
    injection_time: float | int,
    metrics: str | Path | None = None,
    logs: str | Path | None = None,
    traces: str | Path | None = None,
) -> list[EvidenceRecord]:
    """Return common evidence records for available local telemetry.

    Missing modalities are represented explicitly as classification='missing'.
    No root-cause/fault metadata is accepted by this API.
    """
    output: list[EvidenceRecord] = []
    for source, path, extractor in (
        ("metrics", metrics, extract_metric_evidence),
        ("logs", logs, extract_log_evidence),
        ("traces", traces, extract_trace_evidence),
    ):
        if path is None or not Path(path).exists():
            output.append(EvidenceRecord(
                case_id=str(case_id),
                evidence_source=source,
                observation=f"No usable {source} telemetry was provided.",
                direction_change=None,
                magnitude=None,
                time_context={"injection_time": injection_time, "status": "missing"},
                affected_service_component=None,
                evidence_strength="weak",
                classification="missing",
                explanation=f"{source} telemetry is unavailable; absence is not treated as contradiction.",
                raw_measurements={},
            ))
            continue
        for item in extractor(path, injection_time):
            output.append(_record(case_id, item))
    return output


def group_evidence_by_service(records: list[EvidenceRecord]) -> dict[str, list[EvidenceRecord]]:
    """Group evidence deterministically by inferred/observed service."""
    grouped: dict[str, list[EvidenceRecord]] = {}
    for record in records:
        service = record.affected_service_component or "<unknown>"
        grouped.setdefault(service, []).append(record)
    return grouped


def extract_case_evidence(case_root: str | Path, injection_time: float | int) -> dict[str, Any]:
    """Backward-compatible case-level wrapper."""
    root = Path(case_root)
    metric_path = root / "metrics.parquet"
    logs_path = root / "logs.parquet"
    traces_path = root / "traces.parquet"
    metric_evidence = extract_metric_evidence(metric_path, injection_time)
    unified = extract_evidence(
        case_id=root.name,
        injection_time=injection_time,
        metrics=metric_path if metric_path.exists() else None,
        logs=logs_path if logs_path.exists() else None,
        traces=traces_path if traces_path.exists() else None,
    )
    return {
        "metrics_available": metric_path.exists(),
        "logs_available": logs_path.exists(),
        "traces_available": traces_path.exists(),
        "metric_evidence": metric_evidence,
        "evidence": [record.to_dict() for record in unified],
        "service_groups": {
            key: [record.to_dict() for record in value]
            for key, value in group_evidence_by_service(unified).items()
        },
    }
