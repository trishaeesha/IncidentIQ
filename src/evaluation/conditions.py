"""Evidence-traceable gray-area condition validation.

No condition is inferred from RCAEval metadata alone. A condition is marked
VALIDATED only when the supplied observable evidence supports its definition.
Otherwise it remains UNVALIDATED.
"""
from __future__ import annotations
from dataclasses import replace
from .schemas import ConditionEvidence, GrayAreaCondition


def validate_condition(candidate: ConditionEvidence) -> ConditionEvidence:
    """Validate a researcher-supplied condition against explicit evidence gates."""
    try:
        condition = GrayAreaCondition(candidate.condition)
    except ValueError:
        return replace(candidate, validation_status="UNVALIDATED")

    rationale = candidate.condition_rationale.strip()
    refs = tuple(r.strip() for r in candidate.evidence_refs if r and r.strip())
    evidence = {x.strip() for x in candidate.evidence_characteristics if x and x.strip()}
    missing = {x.strip() for x in candidate.missing_evidence if x and x.strip()}
    required = {x.strip() for x in candidate.required_evidence if x and x.strip()}
    conflicts = {x.strip() for x in candidate.conflicting_sources if x and x.strip()}
    misleading = {x.strip() for x in candidate.misleading_signals if x and x.strip()}
    hypotheses = {x.strip() for x in candidate.candidate_hypotheses if x and x.strip()}

    if not rationale or not refs:
        return replace(candidate, validation_status="UNVALIDATED")

    valid = False
    if condition is GrayAreaCondition.CLEAR:
        valid = len(hypotheses) == 1 and bool(evidence)
    elif condition is GrayAreaCondition.AMBIGUOUS:
        valid = len(hypotheses) >= 2 and bool(evidence)
    elif condition is GrayAreaCondition.CONFLICTING:
        valid = len(conflicts) >= 2 and bool(evidence)
    elif condition is GrayAreaCondition.INCOMPLETE:
        valid = bool(required) and bool(missing) and bool(required & missing)
    elif condition is GrayAreaCondition.MISLEADING:
        valid = bool(misleading) and bool(hypotheses) and bool(evidence)
    elif condition is GrayAreaCondition.NOVEL:
        quality = (candidate.historical_match_quality or "").strip().lower()
        valid = quality in {"none", "low", "poor"} and bool(evidence)

    return replace(candidate, validation_status="VALIDATED" if valid else "UNVALIDATED")


def validate_selected_conditions(candidates: list[ConditionEvidence]) -> list[ConditionEvidence]:
    """Validate all supplied candidates without inventing missing conditions."""
    return [validate_condition(c) for c in candidates]
