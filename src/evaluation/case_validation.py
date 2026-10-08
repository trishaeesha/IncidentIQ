"""Researcher-facing validation of evidence-defined gray-area case candidates.

This module never invents a gray-area label. A researcher supplies a candidate
condition plus evidence references and characteristics; the validator only
checks whether the supplied record contains the minimum evidence needed to
justify that candidate. RCAEval metadata alone is never sufficient.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .conditions import validate_condition
from .schemas import ConditionEvidence


@dataclass(frozen=True)
class CaseValidationReport:
    case_id: str
    validation_status: str
    condition: str
    condition_rationale: str
    candidate_hypotheses: tuple[str, ...]
    evidence_characteristics: tuple[str, ...]
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    conflicting_sources: tuple[str, ...]
    misleading_signals: tuple[str, ...]
    historical_match_quality: str | None
    evidence_refs: tuple[str, ...]
    validation_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "condition": self.condition,
            "condition_rationale": self.condition_rationale,
            "candidate_hypotheses": list(self.candidate_hypotheses),
            "evidence_characteristics": list(self.evidence_characteristics),
            "required_evidence": list(self.required_evidence),
            "missing_evidence": list(self.missing_evidence),
            "conflicting_sources": list(self.conflicting_sources),
            "misleading_signals": list(self.misleading_signals),
            "historical_match_quality": self.historical_match_quality,
            "evidence_refs": list(self.evidence_refs),
            "validation_status": self.validation_status,
            "validation_notes": list(self.validation_notes),
        }


def _nonempty(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(v.strip() for v in values if v and v.strip())


def validate_case_candidate(candidate: ConditionEvidence) -> CaseValidationReport:
    """Apply conservative, condition-specific evidence gates.

    The function validates a researcher-supplied candidate. It does not inspect
    RCAEval ground-truth fields and does not assign a condition automatically.
    """
    evidence = _nonempty(candidate.evidence_characteristics)
    refs = _nonempty(candidate.evidence_refs)
    hypotheses = _nonempty(candidate.candidate_hypotheses)
    required = _nonempty(candidate.required_evidence)
    missing = _nonempty(candidate.missing_evidence)
    conflicts = _nonempty(candidate.conflicting_sources)
    misleading = _nonempty(candidate.misleading_signals)
    rationale = candidate.condition_rationale.strip()
    quality = (candidate.historical_match_quality or "").strip().lower()

    notes: list[str] = []

    if not rationale:
        notes.append("Condition rationale is empty.")
    if not refs:
        notes.append("No evidence references were supplied.")
    if not evidence:
        notes.append("No observable evidence characteristics were supplied.")

    condition = candidate.condition.strip().lower()

    if condition == "clear":
        if len(hypotheses) != 1:
            notes.append("Clear requires exactly one evidence-supported candidate hypothesis.")
        if not evidence:
            notes.append("Clear requires observable evidence supporting the candidate.")
    elif condition == "ambiguous":
        if len(hypotheses) < 2:
            notes.append("Ambiguous requires at least two plausible candidate hypotheses.")
        if len(set(hypotheses)) < 2:
            notes.append("Ambiguous hypotheses must be distinct.")
        if not evidence:
            notes.append("Ambiguous requires observable evidence for the competing hypotheses.")
    elif condition == "conflicting":
        if not conflicts:
            notes.append("Conflicting requires explicitly identified conflicting sources.")
        if len(conflicts) < 2:
            notes.append("Conflicting requires at least two source references that disagree.")
        if not evidence:
            notes.append("Conflicting requires observable evidence describing the disagreement.")
    elif condition == "incomplete":
        if not required:
            notes.append("Incomplete requires explicitly stated evidence needed for diagnosis.")
        if not missing:
            notes.append("Incomplete requires explicitly identified unavailable evidence.")
        if not set(missing).intersection(required):
            notes.append("Missing evidence must overlap the evidence required for the decision.")
    elif condition == "misleading":
        if not misleading:
            notes.append("Misleading requires an explicitly identified misleading signal.")
        if not hypotheses:
            notes.append("Misleading requires at least one candidate explanation supported by the full evidence.")
        if not rationale:
            notes.append("Misleading requires a rationale distinguishing the signal from the stronger discriminator.")
    elif condition == "novel":
        if quality not in {"none", "low", "poor"}:
            notes.append("Novel requires an explicitly documented low/poor historical match.")
        if not evidence:
            notes.append("Novel requires observable evidence for the current incident.")
    else:
        notes.append("Condition is outside the fixed six-condition design.")

    base = ConditionEvidence(
        case_id=candidate.case_id,
        condition=condition,
        condition_rationale=rationale,
        candidate_hypotheses=hypotheses,
        evidence_characteristics=evidence,
        required_evidence=required,
        missing_evidence=missing,
        conflicting_sources=conflicts,
        misleading_signals=misleading,
        historical_match_quality=quality or None,
        evidence_refs=refs,
    )
    baseline = validate_condition(base)
    if baseline.validation_status != "VALIDATED":
        notes.append("The existing conservative condition gate did not validate this candidate.")

    status = "VALIDATED" if not notes else "UNVALIDATED"
    if status == "VALIDATED":
        notes.append("Validation is evidence-based and researcher-supplied; no RCAEval metadata was used as a condition label.")

    return CaseValidationReport(
        case_id=base.case_id,
        condition=base.condition,
        condition_rationale=base.condition_rationale,
        candidate_hypotheses=base.candidate_hypotheses,
        evidence_characteristics=base.evidence_characteristics,
        required_evidence=base.required_evidence,
        missing_evidence=base.missing_evidence,
        conflicting_sources=base.conflicting_sources,
        misleading_signals=base.misleading_signals,
        historical_match_quality=base.historical_match_quality,
        evidence_refs=base.evidence_refs,
        validation_status=status,
        validation_notes=tuple(notes),
    )


def validate_case_mapping(candidate: Mapping[str, Any]) -> CaseValidationReport:
    """Validate a JSON-like researcher record without changing its label."""
    evidence = ConditionEvidence(
        case_id=str(candidate.get("case_id", "")),
        condition=str(candidate.get("condition", "")),
        condition_rationale=str(candidate.get("condition_rationale", "")),
        candidate_hypotheses=tuple(candidate.get("candidate_hypotheses", ()) or ()),
        evidence_characteristics=tuple(candidate.get("evidence_characteristics", ()) or ()),
        required_evidence=tuple(candidate.get("required_evidence", ()) or ()),
        missing_evidence=tuple(candidate.get("missing_evidence", ()) or ()),
        conflicting_sources=tuple(candidate.get("conflicting_sources", ()) or ()),
        misleading_signals=tuple(candidate.get("misleading_signals", ()) or ()),
        historical_match_quality=candidate.get("historical_match_quality"),
        evidence_refs=tuple(candidate.get("evidence_refs", ()) or ()),
    )
    return validate_case_candidate(evidence)
