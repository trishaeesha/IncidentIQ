"""Dependency-free regression suite for the Friend 3 framework.

Run from repository root:
    python experiments/self_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation import (
    ConditionEvidence,
    DecisionEvent,
    DiagnosticAction,
    GroundTruthRecord,
    GrayAreaCondition,
    Mode,
    ParticipantTrialRecord,
    assert_participant_safe,
    build_assignment,
    confidence_error,
    evaluate_trial,
    participant_record_schema_fields,
    serialize_reproducibility,
    summarize,
    validate_condition,
)


def base_trial(**kwargs):
    defaults = dict(
        trial_id="t1",
        participant_id="p1",
        case_id="c1",
        system="svc",
        mode=Mode.HUMAN_ONLY,
        start_time="2026-01-01T00:00:00Z",
    )
    defaults.update(kwargs)
    return ParticipantTrialRecord(**defaults)


def test_01_three_modes():
    assert [m.value for m in Mode] == ["human_only", "generic_ai", "incidentiq"]


def test_02_six_conditions():
    assert [c.value for c in GrayAreaCondition] == [
        "clear", "ambiguous", "conflicting", "incomplete", "misleading", "novel"
    ]


def test_03_condition_validation_requires_evidence_refs():
    c = ConditionEvidence("c1", "ambiguous", "Two plausible causes.", ("a", "b"))
    assert validate_condition(c).validation_status == "UNVALIDATED"


def test_04_condition_validation_positive():
    c = ConditionEvidence(
        "c1", "ambiguous", "Two plausible causes.", ("a", "b"),
        ("metrics",), evidence_refs=("e1",)
    )
    assert validate_condition(c).validation_status == "VALIDATED"


def test_05_all_condition_gates_are_conservative():
    cases = [
        ConditionEvidence("c", "clear", "one", ("a",), ("metric",), evidence_refs=("e",)),
        ConditionEvidence("c", "conflicting", "sources disagree", ("a",), ("metric",),
                          conflicting_sources=("s1", "s2"), evidence_refs=("e",)),
        ConditionEvidence("c", "incomplete", "missing telemetry", ("a",), required_evidence=("logs",),
                          missing_evidence=("logs",), evidence_refs=("e",)),
        ConditionEvidence("c", "misleading", "red herring", ("a",), misleading_signals=("s",),
                          evidence_refs=("e",)),
        ConditionEvidence("c", "novel", "poor historical match", ("a",), ("metric",),
                          historical_match_quality="poor", evidence_refs=("e",)),
    ]
    assert all(validate_condition(c).validation_status == "VALIDATED" for c in cases)


def test_06_assignment_allows_only_fixed_modes_conditions():
    for mode in Mode:
        for condition in GrayAreaCondition:
            a = build_assignment("p", "c", "svc", mode, condition.value, 1)
            assert a.mode == mode.value and a.condition == condition.value


def test_07_deterministic_trial_id():
    a = build_assignment("p", "c", "svc", Mode.INCIDENTIQ, "clear", 7)
    b = build_assignment("p", "c", "svc", Mode.INCIDENTIQ, "clear", 7)
    assert a.trial_id == b.trial_id


def test_08_participant_evaluator_separation():
    fields = set(participant_record_schema_fields())
    assert "ground_truth" not in fields and "condition_rationale" not in fields
    assert "final_diagnosis" in fields


def test_09_leakage_guard():
    assert_participant_safe({"case_id": "c1", "mode": "human_only"})
    for payload in (
        {"fault": "cpu"},
        {"root_cause_service": "checkout"},
        {"ground_truth": {"diagnosis": "x"}},
        {"condition_rationale": "hidden"},
        {"label": "ambiguous"},
    ):
        try:
            assert_participant_safe(payload)
        except ValueError:
            pass
        else:
            raise AssertionError(f"leakage was not detected: {payload}")


def test_10_diagnosis_accuracy():
    trial = base_trial(final_diagnosis="CheckoutService")
    truth = GroundTruthRecord("t1", "c1", ("checkoutservice",))
    assert evaluate_trial(trial, truth).diagnosis_correct is True


def test_11_correct_and_incorrect_actions():
    trial = base_trial(
        diagnostic_actions=[
            DiagnosticAction("good", "inspect"),
            DiagnosticAction("bad", "restart"),
            DiagnosticAction("waste", "query"),
        ]
    )
    truth = GroundTruthRecord(
        "t1", "c1", ("x",), ("good",), ("waste",), ("bad",)
    )
    result = evaluate_trial(trial, truth)
    assert result.incorrect_action_count == 1
    assert result.unnecessary_action_count == 1


def test_12_time_to_correct_hypothesis_and_action():
    trial = base_trial(
        decision_events=[
            DecisionEvent(2.0, "hypothesis", hypothesis="wrong"),
            DecisionEvent(5.0, "hypothesis", hypothesis="CheckoutService"),
            DecisionEvent(8.0, "action", action_id="good"),
        ]
    )
    truth = GroundTruthRecord("t1", "c1", ("checkoutservice",), ("good",))
    result = evaluate_trial(trial, truth)
    assert result.time_to_correct_hypothesis_s == 5.0
    assert result.time_to_correct_action_s == 8.0


def test_13_verification_time():
    trial = base_trial(
        decision_events=[
            DecisionEvent(10.0, "verification"),
            DecisionEvent(16.0, "verification"),
        ]
    )
    assert evaluate_trial(trial, GroundTruthRecord("t1", "c1", ("x",))).verification_time_s == 6.0


def test_14_confidence_and_calibration():
    trial = base_trial(final_diagnosis="x", confidence=80)
    result = evaluate_trial(trial, GroundTruthRecord("t1", "c1", ("x",)))
    assert result.confidence == 80
    assert result.confidence_error == 0.2
    assert confidence_error(20, False) == 0.2


def test_15_ai_following_and_override():
    trial = base_trial(
        mode=Mode.INCIDENTIQ,
        ai_recommendations=["good", "bad"],
        actions_followed=["good"],
        actions_overridden=["bad"],
    )
    truth = GroundTruthRecord("t1", "c1", ("x",), ("good",), (), ("bad",))
    result = evaluate_trial(trial, truth)
    assert result.ai_following_rate == 0.5
    assert result.ai_override_rate == 0.5
    assert result.correct_ai_following_count == 1
    assert result.correct_ai_override_count == 1
    assert result.incorrect_ai_following_count == 0


def test_16_missing_telemetry_and_deterministic_evaluation():
    trial = base_trial()
    truth = GroundTruthRecord("t1", "c1", ("x",))
    r1 = evaluate_trial(trial, truth)
    r2 = evaluate_trial(trial, truth)
    assert r1 == r2
    assert r1.time_to_correct_hypothesis_s is None
    assert r1.time_to_correct_action_s is None
    assert r1.verification_time_s is None


def test_17_workload_and_summary():
    trial = base_trial(workload_score=4.0)
    result = evaluate_trial(trial, GroundTruthRecord("t1", "c1", ("x",)))
    assert result.workload_score == 4.0
    assert summarize([1.0, 2.0, 3.0]) == {"n": 3, "mean": 2.0, "median": 2.0}


def test_18_reproducibility_serialization():
    assignment = build_assignment("p1", "c1", "svc", Mode.INCIDENTIQ, "ambiguous", 42)
    trial = base_trial(trial_id=assignment.trial_id, mode=Mode.INCIDENTIQ)
    serialized = serialize_reproducibility(assignment, trial)
    assert assignment.trial_id in serialized
    assert '"seed":42' in serialized


def run():
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    run()
