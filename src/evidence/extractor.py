"""Deterministic evidence extraction from RCAEval telemetry.

This module extracts observations only. It does not interpret observations
against hypotheses and does not consume RCAEval ground-truth fault fields.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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


# Existing metric engine. Calculation behavior is intentionally unchanged.
def extract_metric_evidence(
    metrics_path: str | Path,
    injection_time: float | int,
) -> list[dict[str, Any]]:
    df = _load_parquet(metrics_path)
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
            "observation": f"{metric} changed after injection",
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
                "phase": "post_injection",
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


# Log evidence
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
    # Lexical heuristic only; not a ground-truth failure classifier.
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

    time_col = _find_time_column(df)
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
    before_start = float(ts.loc[before.index].min()) if not before.empty else None
    before_end = float(ts.loc[before.index].max()) if not before.empty else None
    after_start = float(ts.loc[after.index].min()) if not after.empty else None
    after_end = float(ts.loc[after.index].max()) if not after.empty else None

    if service_col:
        names = sorted(
            set(before[service_col].fillna("<unknown>").astype(str))
            | set(after[service_col].fillna("<unknown>").astype(str))
        )
    else:
        names = ["<unknown>"]

    records: list[dict[str, Any]] = []

    for service in names:
        if service_col:
            b = before[before[service_col].fillna("<unknown>").astype(str) == service]
            a = after[after[service_col].fillna("<unknown>").astype(str) == service]
        else:
            b, a = before, after

        b_count, a_count = len(b), len(a)
        b_rate = _rate(b_count, before_start, before_end)
        a_rate = _rate(a_count, after_start, after_end)
        delta = (
            a_rate - b_rate
            if b_rate is not None and a_rate is not None
            else float(a_count - b_count)
        )
        relative = _relative_change(b_rate, a_rate) if b_rate is not None and a_rate is not None else None

        records.append({
            "source": "logs",
            "service": None if service == "<unknown>" else service,
            "observation": "log rate changed after injection",
            "signal": "log_rate",
            "before": b_rate if b_rate is not None else b_count,
            "after": a_rate if a_rate is not None else a_count,
            "absolute_change": delta,
            "relative_change": relative,
            "direction": _direction(delta),
            "strength": _strength(relative, "stable" if b_count else "unavailable"),
            "baseline_quality": "stable" if b_count else "unavailable",
            "before_samples": b_count,
            "after_samples": a_count,
            "time_context": {
                "phase": "post_injection",
                "injection_time": float(injection_time),
                "before_start": before_start,
                "before_end": before_end,
                "after_start": after_start,
                "after_end": after_end,
            },
            "explanation": "Log counts/rates are observations; they do not establish failure or causality.",
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
            delta = (
                a_rate - b_rate
                if b_rate is not None and a_rate is not None
                else float(a_count - b_count)
            )
            relative = _relative_change(b_rate, a_rate) if b_rate is not None and a_rate is not None else None

            records.append({
                "source": "logs",
                "service": None,
                "observation": f"{label.replace('_', '-')} message frequency changed after injection",
                "signal": label,
                "before": b_rate if b_rate is not None else b_count,
                "after": a_rate if a_rate is not None else a_count,
                "absolute_change": delta,
                "relative_change": relative,
                "direction": _direction(delta),
                "strength": _strength(relative, "stable" if b_count else "unavailable"),
                "baseline_quality": "stable" if b_count else "unavailable",
                "before_samples": b_count,
                "after_samples": a_count,
                "time_context": {
                    "phase": "post_injection",
                    "injection_time": float(injection_time),
                    "before_start": before_start,
                    "before_end": before_end,
                    "after_start": after_start,
                    "after_end": after_end,
                },
                "explanation": "Keyword-based preliminary signal only; an error-like message is not ground-truth failure.",
            })

    return records


# Trace evidence
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
    operation_col = _trace_column(
        df, ("operationname", "operation_name", "methodname", "method_name")
    )
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

    def add_record(
        service: str | None,
        operation: str | None,
        signal: str,
        before_value: float | int,
        after_value: float | int,
        observation: str,
        explanation: str,
    ) -> None:
        delta = float(after_value) - float(before_value)
        relative = _relative_change(float(before_value), float(after_value))
        records.append({
            "source": "traces",
            "service": service,
            "operation": operation,
            "observation": observation,
            "signal": signal,
            "before": before_value,
            "after": after_value,
            "absolute_change": delta,
            "relative_change": relative,
            "direction": _direction(delta),
            "strength": _strength(relative, "stable" if before_value else "near_zero"),
            "baseline_quality": "stable" if before_value else "near_zero",
            "before_samples": len(before),
            "after_samples": len(after),
            "time_context": {
                "phase": "post_injection",
                "injection_time": float(injection_time),
                "before_start": b_start,
                "before_end": b_end,
                "after_start": a_start,
                "after_end": a_end,
            },
            "explanation": explanation,
        })

    add_record(
        None, None, "span_count", len(before), len(after),
        "Span/request volume changed after injection",
        "Span counts are deterministic observations and do not establish causality.",
    )

    if duration_col:
        bvals = pd.to_numeric(before[duration_col], errors="coerce").dropna()
        avals = pd.to_numeric(after[duration_col], errors="coerce").dropna()
        if not bvals.empty and not avals.empty:
            add_record(
                None, None, "latency_median",
                float(bvals.median()), float(avals.median()),
                "Request latency changed after injection",
                "Median span duration changed between the pre- and post-injection windows.",
            )

    if service_col:
        services = sorted(
            set(before[service_col].fillna("<unknown>").astype(str))
            | set(after[service_col].fillna("<unknown>").astype(str))
        )
        for service in services:
            b = before[before[service_col].fillna("<unknown>").astype(str) == service]
            a = after[after[service_col].fillna("<unknown>").astype(str) == service]
            clean_service = None if service == "<unknown>" else service

            add_record(
                clean_service, None, "service_span_count", len(b), len(a),
                "Service span volume changed after injection",
                "Service-level span counts are observational; simultaneous changes do not imply causality.",
            )

            if duration_col:
                bv = pd.to_numeric(b[duration_col], errors="coerce").dropna()
                av = pd.to_numeric(a[duration_col], errors="coerce").dropna()
                if not bv.empty and not av.empty:
                    add_record(
                        clean_service, None, "service_latency_median",
                        float(bv.median()), float(av.median()),
                        "Service request latency changed after injection",
                        "Service latency changed in the pre- and post-injection windows.",
                    )

            if operation_col:
                operations = sorted(
                    set(b[operation_col].fillna("<unknown>").astype(str))
                    | set(a[operation_col].fillna("<unknown>").astype(str))
                )
                for operation in operations:
                    bo = b[b[operation_col].fillna("<unknown>").astype(str) == operation]
                    ao = a[a[operation_col].fillna("<unknown>").astype(str) == operation]
                    add_record(
                        clean_service,
                        None if operation == "<unknown>" else operation,
                        "operation_span_count",
                        len(bo), len(ao),
                        "Operation span volume changed after injection",
                        "Operation-level span counts are observational and do not establish causality.",
                    )

    if status_col:
        status = pd.to_numeric(df[status_col], errors="coerce")
        bcount = int((status > 0).loc[before.index].sum())
        acount = int((status > 0).loc[after.index].sum())
        if bcount or acount:
            add_record(
                None, None, "error_status", bcount, acount,
                "Error-like trace status frequency changed after injection",
                "Non-zero numeric status codes are treated as an error-like signal only; schema-specific semantics may vary.",
            )

    return records


# Unified representation
def _record(case_id: str, item: dict[str, Any]) -> EvidenceRecord:
    raw = {
        "before": item.get("before"),
        "after": item.get("after"),
        "absolute_change": item.get("absolute_change"),
        "relative_change": item.get("relative_change"),
        "signal": item.get("signal") or item.get("metric"),
        "baseline_quality": item.get("baseline_quality"),
        "sample_count": {
            "before": item.get("before_samples"),
            "after": item.get("after_samples"),
        },
    }
    if item.get("operation") is not None:
        raw["operation"] = item["operation"]

    return EvidenceRecord(
        case_id=str(case_id),
        evidence_source=str(item["source"]),
        observation=str(item.get("observation", "telemetry observation")),
        direction_change=item.get("direction"),
        magnitude=item.get("absolute_change"),
        time_context=item.get("time_context", {}),
        affected_service_component=item.get("service"),
        evidence_strength=str(item.get("strength", "weak")),
        classification=None,
        explanation=str(item.get("explanation", "")),
        raw_measurements=raw,
        availability="available",
    )


def _unavailable_record(case_id: str, source: str, injection_time: float | int) -> EvidenceRecord:
    return EvidenceRecord(
        case_id=str(case_id),
        evidence_source=source,
        observation=f"No usable {source} telemetry is available.",
        direction_change=None,
        magnitude=None,
        time_context={"injection_time": injection_time},
        affected_service_component=None,
        evidence_strength="weak",
        classification=None,
        explanation=f"{source} telemetry is unavailable; this is an availability observation, not a hypothesis contradiction.",
        raw_measurements={},
        availability="unavailable",
    )


def extract_evidence(
    *,
    case_id: str,
    injection_time: float | int,
    metrics: str | Path | None = None,
    logs: str | Path | None = None,
    traces: str | Path | None = None,
) -> list[EvidenceRecord]:
    """Extract unified observations from available telemetry.

    This API deliberately accepts no RCAEval root-cause or fault metadata.
    """
    output: list[EvidenceRecord] = []

    for source, path, extractor in (
        ("metrics", metrics, extract_metric_evidence),
        ("logs", logs, extract_log_evidence),
        ("traces", traces, extract_trace_evidence),
    ):
        if path is None or not Path(path).exists():
            output.append(_unavailable_record(case_id, source, injection_time))
            continue

        frame = _load_parquet(path)
        if frame is None or frame.empty:
            output.append(_unavailable_record(case_id, source, injection_time))
            continue

        items = extractor(path, injection_time)
        if not items:
            # Source exists but contains no usable observation for this boundary.
            # This is different from hypothesis-level contradiction.
            continue

        output.extend(_record(case_id, item) for item in items)

    return output


def group_evidence_by_service(records: list[EvidenceRecord]) -> dict[str, list[EvidenceRecord]]:
    """Group observations by observed/inferred service only."""
    grouped: dict[str, list[EvidenceRecord]] = {}
    for record in records:
        service = record.affected_service_component or "<unknown>"
        grouped.setdefault(service, []).append(record)
    return grouped


def extract_case_evidence(case_root: str | Path, injection_time: float | int) -> dict[str, Any]:
    """Case-level wrapper for local telemetry files."""
    root = Path(case_root)
    metric_path = root / "metrics.parquet"
    logs_path = root / "logs.parquet"
    traces_path = root / "traces.parquet"

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
        "metric_evidence": extract_metric_evidence(metric_path, injection_time),
        "evidence": [record.to_dict() for record in unified],
        "service_groups": {
            key: [record.to_dict() for record in value]
            for key, value in group_evidence_by_service(unified).items()
        },
    }
