"""Evaluation and decision-quality metrics."""
from .conditions import validate_condition, validate_selected_conditions
from .experiment import (
    TrialAssignment,
    assert_participant_safe,
    build_assignment,
    build_validated_assignment,
    deterministic_trial_id,
    participant_record_schema_fields,
    serialize_reproducibility,
)
from .metrics import (
    confidence_error,
    diagnosis_correct,
    evaluate_trial,
    summarize,
    time_to_correct_action,
    time_to_correct_hypothesis,
)
from .schemas import (
    ConditionEvidence,
    DecisionEvent,
    DiagnosticAction,
    EvaluationResult,
    GrayAreaCondition,
    GroundTruthRecord,
    Mode,
    ParticipantTrialRecord,
)

__all__ = [
    "ConditionEvidence", "DecisionEvent", "DiagnosticAction", "EvaluationResult",
    "GrayAreaCondition", "GroundTruthRecord", "Mode", "ParticipantTrialRecord",
    "TrialAssignment", "assert_participant_safe", "build_assignment",
    "build_validated_assignment", "deterministic_trial_id",
    "participant_record_schema_fields", "serialize_reproducibility",
    "validate_condition", "validate_selected_conditions", "confidence_error",
    "diagnosis_correct", "evaluate_trial", "summarize",
    "time_to_correct_action", "time_to_correct_hypothesis",
]
