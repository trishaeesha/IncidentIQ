"""Deterministic decision-level evaluation metrics."""
from __future__ import annotations

from typing import Iterable, Optional
from .schemas import (
    DiagnosticAction,
    EvaluationResult,
    GroundTruthRecord,
    ParticipantTrialRecord,
)


def _norm(value: str) -> str:
    return " ".join(value.strip().lower().split())


def diagnosis_correct(
    final_diagnosis: Optional[str], truth: GroundTruthRecord
) -> Optional[bool]:
    if final_diagnosis is None:
        return None
    answer = _norm(final_diagnosis)
    return any(answer == _norm(x) for x in truth.correct_diagnoses)


def _first_timestamp_for_hypothesis(
    trial: ParticipantTrialRecord, truth: GroundTruthRecord
) -> Optional[float]:
    correct = {_norm(x) for x in truth.correct_diagnoses}
    for event in sorted(trial.decision_events, key=lambda e: e.timestamp_s):
        if event.hypothesis and _norm(event.hypothesis) in correct:
            return event.timestamp_s
    return None


def _first_timestamp_for_action(
    trial: ParticipantTrialRecord, truth: GroundTruthRecord
) -> Optional[float]:
    correct = set(truth.correct_action_ids)
    for event in sorted(trial.decision_events, key=lambda e: e.timestamp_s):
        if event.action_id in correct:
            return event.timestamp_s
    return None


def time_to_correct_hypothesis(
    trial: ParticipantTrialRecord, truth: GroundTruthRecord
) -> Optional[float]:
    timestamp = _first_timestamp_for_hypothesis(trial, truth)
    if timestamp is None:
        return None
    return max(0.0, timestamp)


def time_to_correct_action(
    trial: ParticipantTrialRecord, truth: GroundTruthRecord
) -> Optional[float]:
    timestamp = _first_timestamp_for_action(trial, truth)
    if timestamp is None:
        return None
    return max(0.0, timestamp)


def action_counts(
    trial: ParticipantTrialRecord, truth: GroundTruthRecord
) -> tuple[int, int]:
    ids = [a.action_id for a in trial.diagnostic_actions]
    unnecessary = sum(x in set(truth.unnecessary_action_ids) for x in ids)
    incorrect = sum(x in set(truth.incorrect_action_ids) for x in ids)
    return unnecessary, incorrect


def verification_time(trial: ParticipantTrialRecord) -> Optional[float]:
    """Return elapsed time spent on explicitly recorded verification events."""
    times = [
        e.timestamp_s
        for e in trial.decision_events
        if e.event_type.lower() == "verification"
    ]
    if not times:
        return None
    return max(times) - min(times) if len(times) > 1 else 0.0


def _ai_metrics(
    trial: ParticipantTrialRecord,
    truth: GroundTruthRecord,
) -> tuple[Optional[float], Optional[float], int, int, int]:
    recommendations = trial.ai_recommendations
    if trial.mode is ParticipantTrialRecord.__dataclass_fields__["mode"].type:  # pragma: no cover
        pass
    if not recommendations:
        return None, None, 0, 0, 0

    rec_ids = list(recommendations)
    followed = set(trial.actions_followed)
    overridden = set(trial.actions_overridden)
    correct = set(truth.correct_action_ids)
    incorrect = set(truth.incorrect_action_ids)

    followed_count = sum(x in followed for x in rec_ids)
    overridden_count = sum(x in overridden for x in rec_ids)
    incorrect_following = sum(x in followed and x in incorrect for x in rec_ids)
    correct_override = sum(x in overridden and x in incorrect for x in rec_ids)
    correct_following = sum(x in followed and x in correct for x in rec_ids)
    total = len(rec_ids)

    return (
        followed_count / total,
        overridden_count / total,
        incorrect_following,
        correct_override,
        correct_following,
    )


def evaluate_trial(
    trial: ParticipantTrialRecord, truth: GroundTruthRecord
) -> EvaluationResult:
    unnecessary, incorrect = action_counts(trial, truth)
    follow, override, bad_follow, good_override, good_follow = _ai_metrics(trial, truth)
    return EvaluationResult(
        trial_id=trial.trial_id,
        diagnosis_correct=diagnosis_correct(trial.final_diagnosis, truth),
        time_to_correct_hypothesis_s=time_to_correct_hypothesis(trial, truth),
        time_to_correct_action_s=time_to_correct_action(trial, truth),
        unnecessary_action_count=unnecessary,
        incorrect_action_count=incorrect,
        verification_time_s=verification_time(trial),
        confidence=trial.confidence,
        ai_following_rate=follow,
        ai_override_rate=override,
        incorrect_ai_following_count=bad_follow,
        correct_ai_override_count=good_override,
        correct_ai_following_count=good_follow,
    )


def confidence_error(confidence: Optional[float], correct: Optional[bool]) -> Optional[float]:
    if confidence is None or correct is None:
        return None
    return abs(confidence / 100.0 - float(correct))


def summarize(values: Iterable[Optional[float]]) -> dict[str, Optional[float]]:
    xs = [x for x in values if x is not None]
    if not xs:
        return {"n": 0, "mean": None, "median": None}
    xs.sort()
    n = len(xs)
    mean = sum(xs) / n
    median = xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    return {"n": n, "mean": mean, "median": median}
