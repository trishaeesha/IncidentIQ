"""Validate gray-area candidates against real RCAEval telemetry.

This is a researcher/evaluator-only utility. It may read evaluator metadata and raw
telemetry, but it never writes evaluator truth into participant-facing artifacts.

Validation is deliberately conservative:
- CLEAR/AMBIGUOUS/INCOMPLETE require observable telemetry evidence.
- CONFLICTING requires opposing directions from at least two sources.
- MISLEADING and NOVEL remain unvalidated unless explicit researcher evidence is
  supplied; the script never invents distractors or historical similarity claims.
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
        rows.append({
            "source": getattr(item, "evidence_source", ""),
            "service": getattr(item, "affected_service_component", ""),
            "signal": getattr(item, "raw_measurements", {}).get("signal"),
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


def validate(candidate: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[str, list[str]]:
    condition = candidate["condition"]
    refs = set(candidate.get("evidence_refs", []))
    reasons = []

    if not rows:
        return "REJECTED", ["no available telemetry rows after extraction"]

    if condition == "clear":
        if len(candidate.get("candidate_hypotheses", [])) != 1:
            return "REJECTED", ["clear condition must name exactly one candidate hypothesis"]
        if len(rows) < 1:
            return "REJECTED", ["no observable evidence"]
        return "VALIDATED", ["real telemetry was extracted; one dominant hypothesis is proposed for researcher review"]

    if condition == "ambiguous":
        if len(families(rows)) < 2:
            return "REJECTED", ["fewer than two observable evidence families"]
        if len(candidate.get("candidate_hypotheses", [])) < 2:
            return "REJECTED", ["fewer than two plausible hypotheses declared"]
        return "VALIDATED", ["at least two observable evidence families and two hypotheses"]

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
        sources = sorted({str(r.get("source")) for r in rows if r.get("source")})
        if len(sources) < 2:
            return "REJECTED", ["cannot hide one modality while retaining another"]
        return "VALIDATED", [f"at least two sources available; candidate can hide one source ({sources[-1]})"]

    if condition == "misleading":
        return "UNVALIDATED", ["requires an independently documented distractor unrelated to the evaluator root cause"]

    if condition == "novel":
        return "UNVALIDATED", ["requires a separately validated historical similarity/reference corpus"]

    return "REJECTED", [f"unknown condition: {condition}"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", required=True)
    p.add_argument("--candidates", default="experiments/gray_area_candidates.py")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    import importlib.util
    spec = importlib.util.spec_from_file_location("gray_candidates", args.candidates)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    report = []
    for candidate in module.CANDIDATES:
        paths = case_paths(args.data_root, candidate.case_id)
        if not paths["root"].exists():
            report.append({
                "case_id": candidate.case_id,
                "condition": candidate.condition,
                "status": "REJECTED",
                "telemetry_verified": False,
                "reason": [f"case directory not found: {paths['root']}"],
            })
            continue
        try:
            injection_time = read_injection_time(args.data_root, candidate.case_id)
            evidence = extract_evidence(
                case_id=candidate.case_id,
                injection_time=injection_time,
                metrics=paths["metrics"],
                logs=paths["logs"],
                traces=paths["traces"],
            )
            rows = available_rows(evidence)
            status, reasons = validate(candidate.to_dict(), rows)
            report.append({
                "case_id": candidate.case_id,
                "condition": candidate.condition,
                "status": status,
                "telemetry_verified": status == "VALIDATED",
                "available_source_count": len({r["source"] for r in rows if r["source"]}),
                "evidence_row_count": len(rows),
                "evidence_refs": list(candidate.evidence_refs),
                "reasons": reasons,
            })
        except Exception as exc:
            report.append({
                "case_id": candidate.case_id,
                "condition": candidate.condition,
                "status": "ERROR",
                "telemetry_verified": False,
                "reason": [f"{type(exc).__name__}: {exc}"],
            })

    payload = {
        "schema_version": 1,
        "telemetry_verification_required": True,
        "participant_safe": False,
        "candidates": report,
        "rule": "Only VALIDATED candidates may enter the researcher pool; UNVALIDATED/REJECTED candidates are excluded.",
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
