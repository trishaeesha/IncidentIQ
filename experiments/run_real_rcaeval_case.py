"""Run one real RCAEval case through the IncidentIQ baseline pipeline.

Research-integrity rule: this runner never loads RCAEval evaluator labels such as
fault or root_cause_service into the evidence/hypothesis/decision pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow direct execution as `python experiments/run_real_rcaeval_case.py`
# from a clean checkout without requiring package installation.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from typing import Any

from src.data.rcaeval_loader import load_case_paths, read_injection_time
from src.evidence import extract_evidence, group_evidence_by_service
from src.models import DecisionEngine, HypothesisEngine


FORBIDDEN = {
    "root_cause_service",
    "fault",
    "fault_description",
    "ground_truth",
    "answer_key",
    "condition_rationale",
    "condition_label",
}


def assert_no_ground_truth(value: Any, location: str = "root") -> None:
    """Reject evaluator-only fields anywhere in pipeline inputs/outputs."""
    if isinstance(value, dict):
        leaked = FORBIDDEN.intersection(value)
        if leaked:
            raise AssertionError(
                f"Ground-truth leakage at {location}: {sorted(leaked)}"
            )
        for key, item in value.items():
            assert_no_ground_truth(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_no_ground_truth(item, f"{location}[{index}]")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--case", default="re2ob_checkoutservice_cpu_2")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    paths = load_case_paths(data_root, args.case)
    injection_time = read_injection_time(data_root, args.case)

    evidence = extract_evidence(
        case_id=args.case,
        injection_time=injection_time,
        metrics=paths["metrics"],
        logs=paths["logs"],
        traces=paths["traces"],
    )
    evidence_dicts = [item.to_dict() for item in evidence]
    assert_no_ground_truth(evidence_dicts, "evidence")

    hypothesis = HypothesisEngine().infer(evidence_dicts)
    assert_no_ground_truth(hypothesis, "hypothesis")

    decision = DecisionEngine().decide(hypothesis)
    assert_no_ground_truth(decision, "decision")

    grouped = group_evidence_by_service(evidence)
    available_sources = sorted(
        {item.evidence_source for item in evidence if item.availability == "available"}
    )

    output = {
        "case_id": args.case,
        "injection_time": injection_time,
        "available_sources": available_sources,
        "evidence_count": len(evidence),
        "services_observed": sorted(grouped),
        "hypothesis_status": hypothesis.get("status"),
        "hypotheses": [
            {
                "hypothesis": item.get("hypothesis"),
                "confidence": item.get("confidence"),
                "uncertainty": item.get("uncertainty"),
                "supporting_count": len(item.get("supporting_evidence", [])),
                "contradicting_count": len(item.get("contradicting_evidence", [])),
                "missing_count": len(item.get("missing_evidence", [])),
                "next_diagnostic_action": item.get("next_diagnostic_action"),
            }
            for item in hypothesis.get("hypotheses", [])
        ],
        "decision": decision,
        "research_integrity": {
            "ground_truth_fields_in_pipeline": False,
            "human_control_required": decision.get("human_control_required", True),
        },
    }

    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
