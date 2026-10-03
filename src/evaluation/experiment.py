"""Experiment control, leakage guards, and reproducibility records."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Mapping

from .conditions import validate_condition
from .schemas import (
    ALLOWED_CONDITIONS,
    ALLOWED_MODES,
    ConditionEvidence,
    Mode,
    ParticipantTrialRecord,
)


FORBIDDEN_KEYS = {
    "root_cause_service",
    "fault",
    "fault_description",
    "ground_truth",
    "answer_key",
    "condition_rationale",
    "condition_label",
    "condition_status",
}
FORBIDDEN_VALUES = {
    "clear", "ambiguous", "conflicting", "incomplete", "misleading",
    "novel", "historical mismatch", "unvalidated",
}


@dataclass(frozen=True)
class TrialAssignment:
    trial_id: str
    participant_id: str
    case_id: str
    system: str
    mode: str
    condition: str
    seed: int

    def __post_init__(self) -> None:
        if self.mode not in ALLOWED_MODES:
            raise ValueError(f"Unsupported mode: {self.mode}")
        if self.condition not in ALLOWED_CONDITIONS:
            raise ValueError(f"Unsupported condition: {self.condition}")


def deterministic_trial_id(
    participant_id: str, case_id: str, mode: str, seed: int
) -> str:
    raw = f"{participant_id}|{case_id}|{mode}|{seed}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_assignment(
    participant_id: str,
    case_id: str,
    system: str,
    mode: Mode,
    condition: str,
    seed: int,
) -> TrialAssignment:
    if not isinstance(mode, Mode):
        raise ValueError(f"Unsupported mode: {mode!r}")
    return TrialAssignment(
        trial_id=deterministic_trial_id(participant_id, case_id, mode.value, seed),
        participant_id=participant_id,
        case_id=case_id,
        system=system,
        mode=mode.value,
        condition=condition,
        seed=seed,
    )


def build_validated_assignment(
    participant_id: str,
    case_id: str,
    system: str,
    mode: Mode,
    condition_evidence: ConditionEvidence,
    seed: int,
) -> TrialAssignment:
    """Create an assignment only from an evidence-validated condition record."""
    validated = validate_condition(condition_evidence)
    if validated.validation_status != "VALIDATED":
        raise ValueError(
            f"Condition {condition_evidence.condition!r} is not validated from evidence"
        )
    return build_assignment(
        participant_id=participant_id,
        case_id=case_id,
        system=system,
        mode=mode,
        condition=validated.condition,
        seed=seed,
    )


def validate_participant_payload(payload: Mapping[str, Any]) -> list[str]:
    """Detect direct and obvious nested leakage in participant-facing data."""
    violations: list[str] = []

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                key_l = str(key).lower()
                if key_l in FORBIDDEN_KEYS:
                    violations.append(f"forbidden key: {path}{key}")
                walk(item, f"{path}{key}.")
        elif isinstance(value, (list, tuple)):
            for i, item in enumerate(value):
                walk(item, f"{path}[{i}].")
        elif isinstance(value, str):
            value_l = value.strip().lower()
            for token in FORBIDDEN_VALUES:
                if value_l == token:
                    violations.append(f"forbidden condition token at {path}: {value}")

    walk(payload)
    return violations


def assert_participant_safe(payload: Mapping[str, Any]) -> None:
    violations = validate_participant_payload(payload)
    if violations:
        raise ValueError("Participant payload leakage: " + "; ".join(violations))


def participant_record_schema_fields() -> tuple[str, ...]:
    return (
        "trial_id", "participant_id", "case_id", "system", "mode",
        "start_time", "end_time", "final_diagnosis", "confidence",
        "diagnostic_actions", "decision_events", "ai_recommendations",
        "actions_followed", "actions_overridden", "workload_score",
    )


def serialize_reproducibility(
    assignment: TrialAssignment,
    participant_record: ParticipantTrialRecord,
) -> str:
    payload = {
        "assignment": asdict(assignment),
        "participant_record": participant_record.to_dict(),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
