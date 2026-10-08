"""Assemble the final IncidentIQ research report without inventing human results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def scored_count(analysis: dict[str, Any]) -> int:
    """Read the score_human_study output without assuming one field name."""
    for key in ("scored_records", "n_scored"):
        value = analysis.get(key)
        if isinstance(value, int):
            return value
    return 0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--telemetry", required=True)
    p.add_argument("--analysis", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    telemetry = load(args.telemetry)
    analysis = load(args.analysis)

    validated = [
        x
        for x in telemetry.get("candidates", [])
        if x.get("status") == "VALIDATED" and x.get("telemetry_verified") is True
    ]
    n_scored = scored_count(analysis)

    report = {
        "title": "IncidentIQ: Evidence-Grounded AI Decision Support for Software Incident Troubleshooting",
        "research_question": "When does evidence-grounded AI assistance help or harm human software-incident diagnostic decisions?",
        "engineering_validation": {
            "validated_gray_area_conditions": len(validated),
            "validated_conditions": [x.get("condition") for x in validated],
            "human_results_available": n_scored > 0,
        },
        "human_study_analysis": analysis,
        "conclusion_status": (
            "PENDING_HUMAN_DATA" if n_scored == 0 else "READY_FOR_EVIDENCE_REVIEW"
        ),
        "integrity_rule": (
            "Do not claim superiority, significance, generalization, or harm until "
            "actual participant records have been scored and the preregistered "
            "analysis supports the claim."
        ),
    }

    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["conclusion_status"],
                "validated_conditions": len(validated),
                "n_scored": n_scored,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
