"""Evidence-traceable gray-area condition validation.

No condition is inferred from RCAEval metadata alone. A condition is marked
VALIDATED only when the supplied observable evidence supports its definition.
Otherwise it remains UNVALIDATED.
"""
from __future__ import annotations

from dataclasses import replace
from .schemas import ConditionEvidence, GrayAreaCondition


def validate_condition(candidate: ConditionEvidence) -> ConditionEvidence:
    """Validate a proposed condition using explicit observable evidence.

    This is a conservative gate, not a classifier. It never assigns a condition
    to a case; it only validates a researcher-supplied candidate rationale.
    """
    try:
        condition = GrayAreaCondition(candidate.condition)
    except ValueError:
        return replace(candidate, validation_status="UNVALIDATED")

    rationale = candidate.condition_rationale.strip()
    refs = tuple(r for r in candidate.evidence_refs if r.strip())

    if not rationale or not refs:
        return replace(candidate, validation_status="UNVALIDATED")

    evidence = set(candidate.evidence_characteristics)
    missing = set(candidate.missing_evidence)
    conflicts = set(candidate.conflicting_sources)
    misleading = set(candidate.misleading_signals)
    hypotheses = set(candidate.candidate_hypotheses)

    valid = False
    if condition is GrayAreaCondition.CLEAR:
        valid = len(hypotheses) == 1 and bool(evidence)
    elif condition is GrayAreaCondition.AMBIGUOUS:
        valid = len(hypotheses) >= 2 and bool(evidence)
    elif condition is GrayAreaCondition.CONFLICTING:
        valid = bool(conflicts) and bool(evidence)
    elif condition is GrayAreaCondition.INCOMPLETE:
        valid = bool(missing) and bool(candidate.required_evidence)
    elif condition is GrayAreaCondition.MISLEADING:
        valid = bool(misleading) and bool(hypotheses)
    elif condition is GrayAreaCondition.NOVEL:
        quality = (candidate.historical_match_quality or "").lower()
        valid = quality in {"none", "low", "poor"} and bool(evidence)

    return replace(candidate, validation_status="VALIDATED" if valid else "UNVALIDATED")


def validate_selected_conditions(
    candidates: list[ConditionEvidence],
) -> list[ConditionEvidence]:
    """Validate all supplied candidates without inventing missing conditions."""
    return [validate_condition(c) for c in candidates]
