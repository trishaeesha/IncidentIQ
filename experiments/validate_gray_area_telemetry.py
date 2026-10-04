"""Validate gray-area candidates against real RCAEval telemetry.

This is a researcher/evaluator-only utility. It may read evaluator metadata and raw
telemetry, but it never writes evaluator truth into participant-facing artifacts.

Validation is deliberately conservative:
- CLEAR/AMBIGUOUS/INCOMPLETE require observable telemetry evidence.
- Declared evidence references must resolve to extracted observations.
- CONFLICTING requires opposing directions from at least two sources.
- MISLEADING and NOVEL remain unvalidated unless explicit researcher evidence is
  supplied; the script never invents distractors or historical similarity claims.
- RCAEval metadata can confirm case identity and modality availability, but it can
  never substitute for raw telemetry validation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.rcaeval_loader import case_paths, read_injection_time
from src.evidence import extract_evidence


def available_rows(evidence: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for item in evidence:
        if getattr(item, "availability", None) != "available":
            continue
        raw = getattr(item, "raw_measurements", {}) or {}
        rows.append({
            "source": getattr(item, "evidence_source", ""),
            "service": getattr(item, "affected_service_component", ""),
            "signal": raw.get("signal"),
            "observation": getattr(item, "observation", ""),
            "direction": getattr(item, "direction_change", ""),
            "strength": getattr(item, "evidence_strength", ""),
            "time_context": getattr(item, "time_context", None),
        })
    return rows


def families(rows: list[dict[str, Any]]) -> set[str]:
    tokens = {
        "resource": ("cpu", "memory", "mem", "load", "utilization"),
        "error": ("error", "exception", "failure", "5xx", "status"),
        "network": ("network", "packet", "loss", "timeout", "connection"),
        "latency": ("latency", "delay", "duration", "slow"),
        "storage": ("disk", "storage", "io", "database", "queue"),
    }
    out = set()
    for row in rows:
        text = " ".join(str(row.get(k, "")) for k in ("source", "signal", "observation")).lower()
        for family, words in tokens.items():
            if any(w in text for w in words):
                out.add(family)
    return out


def _ref_matches(ref: str, row: dict[str, Any]) -> bool:
    """Resolve a candidate evidence ref against one extracted observation.

    Supported refs are intentionally narrow and mirror the current evidence
    extractor rather than inventing a second evidence vocabulary:
      metrics:<service>:<signal>
      logs:<signal>
      logs:<service>:<signal>
    """
    parts = str(ref).split(":")
    source = str(row.get("source", ""))
    service = str(row.get("service") or "")
    signal = str(row.get("signal") or "")

    if len(parts) == 2:
        ref_source, ref_signal = parts
        return source == ref_source and signal.lower() == ref_signal.lower()

    if len(parts) == 3:
        ref_source, ref_service, ref_signal = parts
        if source != ref_source or service.lower() != ref_service.lower():
            return False
        # Metric signals are emitted as full names such as checkoutservice_cpu.
        if source == "metrics":
            return signal.lower() in {
                ref_signal.lower(),
                f"{ref_service.lower()}_{ref_signal.lower()}",
            }
        return signal.lower() == ref_signal.lower()

    return False


def resolve_refs(refs: set[str], rows: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    matched = {ref for ref in refs if any(_ref_matches(ref, row) for row in rows)}
    return matched, refs - matched


def validate(
    candidate: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    metadata_row: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    condition = candidate["condition"]
    refs = set(candidate.get("evidence_refs", []))
    reasons = []

    if not rows:
        return "REJECTED", ["no available telemetry rows after extraction"]

    matched_refs, missing_refs = resolve_refs(refs, rows)

    # Manifest-only references are availability claims and are checked separately.
    telemetry_refs = {ref for ref in refs if not ref.startswith("manifest:")}
    if telemetry_refs and missing_refs & telemetry_refs:
        return "REJECTED", [
            f"declared evidence refs not resolved by extracted telemetry: {sorted(missing_refs & telemetry_refs)}"
        ]

    if condition == "clear":
        if len(candidate.get("candidate_hypotheses", [])) != 1:
            return "REJECTED", ["clear condition must name exactly one candidate hypothesis"]
        if len(rows) < 1:
            return "REJECTED", ["no observable evidence"]
        return "VALIDATED", [
            "declared evidence refs resolved to extracted telemetry",
            "one dominant hypothesis is proposed for researcher review",
        ]

    if condition == "ambiguous":
        if len(families(rows)) < 2:
            return "REJECTED", ["fewer than two observable evidence families"]
        if len(candidate.get("candidate_hypotheses", [])) < 2:
            return "REJECTED", ["fewer than two plausible hypotheses declared"]
        return "VALIDATED", [
            "declared evidence refs resolved to extracted telemetry",
            "at least two observable evidence families and two hypotheses",
        ]

    if condition == "conflicting":
        sources = {str(r.get("source")) for r in rows if r.get("source")}
        directions = {str(r.get("direction", "")).lower() for r in rows}
        positive = directions & {"increase", "increased", "elevated", "high"}
        negative = directions & {"decrease", "decreased", "normal", "stable", "unchanged", "low"}
        if len(sources) < 2:
            return "REJECTED", ["fewer than two telemetry sources"]
        if not positive or not negative:
            return "REJECTED", ["no opposing observed directions"]
        return "VALIDATED", ["opposing directions observed across at least two sources"]

    if condition == "incomplete":
        # Incomplete must represent a real missing modality, not an arbitrary
        # deletion of an available evidence source. The candidate currently
        # targets RE2-SS, where RCAEval metadata explicitly records no traces.
        if not metadata_row:
            return "REJECTED", ["RCAEval metadata row required to establish missing modality"]
        if metadata_row.get("has_traces") is not False:
            return "REJECTED", ["candidate requires has_traces=false in RCAEval metadata"]
        sources = {str(r.get("source")) for r in rows if r.get("source")}
        if "metrics" not in sources or "logs" not in sources:
            return "REJECTED", ["expected both metrics and logs to be observable while traces are absent"]
        return "VALIDATED", [
            "metrics and logs are observable in raw telemetry",
            "RCAEval metadata confirms traces are unavailable",
            "incomplete condition will preserve available evidence rather than hide an arbitrary source",
        ]

    if condition == "misleading":
        return "UNVALIDATED", ["requires an independently documented distractor unrelated to the evaluator root cause"]

    if condition == "novel":
        return "UNVALIDATED", ["requires a separately validated historical similarity/reference corpus"]

    return "REJECTED", [f"unknown condition: {condition}"]


def _load_metadata(path: str | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return {item["row"]["case"]: item["row"] for item in payload.get("rows", [])}


def _metadata_observation(row: dict[str, Any], case_id: str) -> dict[str, Any]:
    if not row:
        return {"case_id": case_id, "metadata_status": "MISSING"}
    return {
        "case_id": case_id,
        "metadata_status": "FOUND",
        "dataset": row.get("dataset"),
        "root_cause_service": row.get("root_cause_service"),
        "fault": row.get("fault"),
        "inject_time": row.get("inject_time"),
        "has_logs": row.get("has_logs"),
        "n_logs": row.get("n_logs"),
        "has_traces": row.get("has_traces"),
        "n_traces": row.get("n_traces"),
        "n_metrics": row.get("n_metrics"),
        "n_timesteps": row.get("n_timesteps"),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", required=True)
    p.add_argument("--metadata", default=None)
    p.add_argument("--candidates", default="experiments/gray_area_candidates.py")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    import importlib.util
    spec = importlib.util.spec_from_file_location("gray_candidates", args.candidates)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    metadata = _load_metadata(args.metadata)
    report = []

    for candidate in module.CANDIDATES:
        case_id = candidate.case_id
        metadata_row = metadata.get(case_id)
        paths = case_paths(args.data_root, case_id)
        base = {
            "case_id": case_id,
            "condition": candidate.condition,
            "metadata": _metadata_observation(metadata_row, case_id),
        }

        if not paths["root"].exists():
            report.append({
                **base,
                "status": "PENDING_RAW_TELEMETRY",
                "telemetry_verified": False,
                "reason": [f"case directory not found: {paths['root']}"],
            })
            continue

        try:
            injection_time = read_injection_time(args.data_root, case_id)
            evidence = extract_evidence(
                case_id=case_id,
                injection_time=injection_time,
                metrics=paths["metrics"],
                logs=paths["logs"],
                traces=paths["traces"],
            )
            rows = available_rows(evidence)
            status, reasons = validate(candidate.to_dict(), rows, metadata_row=metadata_row)
            report.append({
                **base,
                "status": status,
                "telemetry_verified": status == "VALIDATED",
                "available_source_count": len({r["source"] for r in rows if r["source"]}),
                "evidence_row_count": len(rows),
                "evidence_refs": list(candidate.evidence_refs),
                "resolved_evidence_refs": sorted(resolve_refs(set(candidate.evidence_refs), rows)[0]),
                "reasons": reasons,
            })
        except Exception as exc:
            report.append({
                **base,
                "status": "ERROR",
                "telemetry_verified": False,
                "reason": [f"{type(exc).__name__}: {exc}"],
            })

    payload = {
        "schema_version": 2,
        "telemetry_verification_required": True,
        "participant_safe": False,
        "metadata_is_not_telemetry_validation": True,
        "candidates": report,
        "rule": "Only VALIDATED candidates may enter the researcher pool; PENDING_RAW_TELEMETRY, UNVALIDATED, REJECTED, and ERROR candidates are excluded.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    counts = {}
    for row in report:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(json.dumps({"candidates": len(report), "status_counts": counts, "output": str(out)}, indent=2))


if __name__ == "__main__":
    main()
