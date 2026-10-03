"""Evaluation and decision-quality metrics."""
from .case_set import ValidatedCase, reject_unvalidated, select_validated_cases, summarize_case_set
from .case_validation import CaseValidationReport, validate_case_candidate, validate_case_mapping
from .conditions import validate_condition, validate_selected_conditions
from .experiment import (
    TrialAssignment, assert_participant_safe, balanced_mode_order, build_assignment,
    build_validated_assignment, deterministic_trial_id, participant_record_schema_fields,
    randomized_case_order, serialize_reproducibility, validate_no_carryover,
)
from .integration import build_generic_ai_record, build_incidentiq_trial_payload, incidentiq_recommendations
from .metrics import confidence_error, diagnosis_correct, evaluate_trial, summarize, time_to_correct_action, time_to_correct_hypothesis
from .schemas import (
    ConditionEvidence, DecisionEvent, DiagnosticAction, EvaluationResult,
    GrayAreaCondition, GroundTruthRecord, Mode, ParticipantTrialRecord,
)

__all__ = [
    "ConditionEvidence", "DecisionEvent", "DiagnosticAction", "EvaluationResult",
    "GrayAreaCondition", "GroundTruthRecord", "Mode", "ParticipantTrialRecord",
    "TrialAssignment", "ValidatedCase", "CaseValidationReport",
    "assert_participant_safe", "balanced_mode_order", "build_assignment",
    "build_validated_assignment", "deterministic_trial_id", "randomized_case_order",
    "participant_record_schema_fields", "serialize_reproducibility", "validate_no_carryover",
    "validate_condition", "validate_selected_conditions", "validate_case_candidate",
    "validate_case_mapping", "select_validated_cases", "reject_unvalidated",
    "summarize_case_set", "confidence_error", "diagnosis_correct", "evaluate_trial",
    "summarize", "time_to_correct_action", "time_to_correct_hypothesis",
    "build_generic_ai_record", "build_incidentiq_trial_payload", "incidentiq_recommendations",
]
