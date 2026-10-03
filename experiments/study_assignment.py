"""Research-study plan generated from the validated evaluation framework.

This module creates participant-safe trial assignments. It never exposes
ground-truth labels or gray-area rationales.
"""
from __future__ import annotations
from dataclasses import asdict
from src.evaluation.experiment import (
    build_validated_assignment,
    randomized_case_order,
    balanced_mode_order,
)
from src.evaluation.schemas import Mode, ConditionEvidence


def build_study_assignments(
    participant_id: str,
    cases: list[tuple[str, ConditionEvidence]],
    seed: int = 20261003,
):
    ordered = randomized_case_order([case_id for case_id, _ in cases], seed)
    lookup = {case_id: evidence for case_id, evidence in cases}
    modes = balanced_mode_order(len(ordered), seed)
    assignments = []
    for idx, case_id in enumerate(ordered):
        evidence = lookup[case_id]
        assignments.append(
            build_validated_assignment(
                participant_id=participant_id,
                case_id=case_id,
                system="IncidentIQ",
                mode=modes[idx],
                condition_evidence=evidence,
                seed=seed + idx,
            )
        )
    return [asdict(x) for x in assignments]
