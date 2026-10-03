"""Build participant-safe trial specifications from real IncidentIQ outputs.

This file never reads evaluator truth. It deliberately blocks gray-area
conditions that cannot be demonstrated from observable telemetry.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

FORBIDDEN = {
    "root_cause_service", "fault", "fault_description", "ground_truth",
    "answer_key", "condition_rationale", "condition_label", "condition_status",
    "condition", "condition_evidence",
}
CONDITIONS = ("clear", "ambiguous", "conflicting", "incomplete", "misleading", "novel")
MODES = ("human_only", "generic_ai", "incidentiq")


def assert_safe(value, where="root"):
    if isinstance(value, dict):
        bad = FORBIDDEN.intersection(str(k).lower() for k in value)
        if bad:
            raise ValueError(f"forbidden field(s) at {where}: {sorted(bad)}")
        for k, v in value.items():
            assert_safe(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            assert_safe(v, f"{where}[{i}]")


def sanitize(row):
    allowed = (
        "source", "service", "observation", "direction", "magnitude",
        "time_context", "evidence_strength", "availability", "signal",
        "before", "after", "absolute_change", "relative_change",
        "sample_count", "operation",
    )
    return {k: row[k] for k in allowed if k in row}


def family(row):
    text = " ".join(str(row.get(k, "")) for k in ("signal", "observation", "source")).lower()
    groups = {
        "resource": ("cpu", "memory", "mem", "load", "utilization"),
        "error": ("error", "exception", "failure", "status 5"),
        "network": ("network", "packet", "loss", "timeout", "connection"),
        "latency": ("latency", "delay", "slow", "duration"),
        "storage": ("disk", "storage", "io", "database", "queue"),
    }
    for name, tokens in groups.items():
        if any(token in text for token in tokens):
            return name
    return "other"


def transform(rows, condition):
    rows = [sanitize(r) for r in rows]
    if condition == "clear":
        return rows, "VALIDATED", ["full available participant-safe evidence"]

    if condition == "ambiguous":
        families = {family(r) for r in rows if family(r) != "other"}
        if len(families) < 2:
            return rows, "UNVALIDATED", ["fewer than two observable evidence families"]
        return rows, "VALIDATED", ["multiple observable evidence families retained"]

    if condition == "conflicting":
        directions = {str(r.get("direction", "")).lower() for r in rows}
        positive = bool(directions & {"increase", "increased", "elevated"})
        negative = bool(directions & {"decrease", "decreased", "normal", "stable", "unchanged"})
        sources = {str(r.get("source", "")) for r in rows}
        if len(sources) < 2 or not (positive and negative):
            return rows, "UNVALIDATED", ["opposing cross-source signals were not demonstrated"]
        return rows, "VALIDATED", ["competing directional signals retained"]

    if condition == "incomplete":
        sources = sorted({str(r.get("source", "")) for r in rows})
        if len(sources) < 2:
            return rows, "UNVALIDATED", ["fewer than two telemetry sources"]
        hidden = sources[-1]
        return [r for r in rows if str(r.get("source", "")) != hidden], "VALIDATED", [f"one source hidden: {hidden}"]

    if condition == "misleading":
        return rows, "UNVALIDATED", ["requires a researcher-verified unrelated distractor signal"]

    if condition == "novel":
        return rows, "UNVALIDATED", ["requires a verified historical-reference removal"]

    raise ValueError(condition)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source = Path(args.outputs)
    records = []
    for path in sorted(source.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert_safe(data, path.name)
        if not data.get("case_id") or not data.get("evidence_digest"):
            continue
        records.append(data)

    trials = []
    for index, data in enumerate(records, 1):
        public_case = f"CASE-{index:02d}"
        for condition in CONDITIONS:
            evidence, status, notes = transform(data["evidence_digest"], condition)
            for mode in MODES:
                trials.append({
                    "trial_id": f"{public_case}-{condition}-{mode}",
                    "public_case_id": public_case,
                    "condition": condition,
                    "validation_status": status,
                    "validation_notes": notes,
                    "mode": mode,
                    "evidence": evidence,
                    "instructions": "Review the telemetry and state your diagnosis, confidence, and diagnostic action."
                })

    manifest = {
        "schema_version": 1,
        "participant_safe": True,
        "researcher_must_validate_before_use": True,
        "trial_count": len(trials),
        "trials": trials,
    }
    assert_safe(manifest)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"cases": len(records), "trials": len(trials), "output": str(out)}, indent=2))


if __name__ == "__main__":
    main()
