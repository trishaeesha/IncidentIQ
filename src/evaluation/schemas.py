"""Schemas for controlled human-AI incident evaluation.

Participant-facing records deliberately exclude ground-truth labels and condition
rationales. Evaluator records hold scoring-only information separately.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class Mode(str, Enum):
    HUMAN_ONLY = "human_only"
    GENERIC_AI = "generic_ai"
    INCIDENTIQ = "incidentiq"


class GrayAreaCondition(str, Enum):
    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    CONFLICTING = "conflicting"
    INCOMPLETE = "incomplete"
    MISLEADING = "misleading"
    NOVEL = "novel"


ALLOWED_MODES = tuple(m.value for m in Mode)
ALLOWED_CONDITIONS = tuple(c.value for c in GrayAreaCondition)


@dataclass(frozen=True)
class DiagnosticAction:
    action_id: str
    action_type: str
    target: Optional[str] = None
    rationale: Optional[str] = None
    timestamp_s: Optional[float] = None


@dataclass(frozen=True)
class DecisionEvent:
    timestamp_s: float
    event_type: str
    observation: Optional[str] = None
    hypothesis: Optional[str] = None
    reason_evidence: tuple[str, ...] = ()
    action_id: Optional[str] = None
    result: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class ParticipantTrialRecord:
    trial_id: str
    participant_id: str
    case_id: str
    system: str
    mode: Mode
    start_time: str
    end_time: Optional[str] = None
    final_diagnosis: Optional[str] = None
    confidence: Optional[float] = None
    diagnostic_actions: list[DiagnosticAction] = field(default_factory=list)
    decision_events: list[DecisionEvent] = field(default_factory=list)
    ai_recommendations: list[str] = field(default_factory=list)
    actions_followed: list[str] = field(default_factory=list)
    actions_overridden: list[str] = field(default_factory=list)
    workload_score: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        return data


@dataclass(frozen=True)
class GroundTruthRecord:
    trial_id: str
    case_id: str
    correct_diagnoses: tuple[str, ...]
    correct_action_ids: tuple[str, ...] = ()
    unnecessary_action_ids: tuple[str, ...] = ()
    incorrect_action_ids: tuple[str, ...] = ()
    condition: Optional[str] = None


@dataclass(frozen=True)
class ConditionEvidence:
    case_id: str
    condition: str
    condition_rationale: str
    candidate_hypotheses: tuple[str, ...] = ()
    evidence_characteristics: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    conflicting_sources: tuple[str, ...] = ()
    misleading_signals: tuple[str, ...] = ()
    historical_match_quality: Optional[str] = None
    evidence_refs: tuple[str, ...] = ()
    validation_status: str = "UNVALIDATED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationResult:
    trial_id: str
    diagnosis_correct: Optional[bool]
    time_to_correct_hypothesis_s: Optional[float]
    time_to_correct_action_s: Optional[float]
    unnecessary_action_count: int
    incorrect_action_count: int
    verification_time_s: Optional[float]
    confidence: Optional[float]
    confidence_error: Optional[float]
    ai_following_rate: Optional[float]
    ai_override_rate: Optional[float]
    incorrect_ai_following_count: int
    correct_ai_override_count: int
    correct_ai_following_count: int
    workload_score: Optional[float]
    condition: Optional[str] = None
