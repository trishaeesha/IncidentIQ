import copy

import pytest

from src.models import DecisionEngine, HypothesisEngine


def evidence(**overrides):
    row = {
        "case_id": "case-1",
        "source": "metrics",
        "service": "checkoutservice",
        "observation": "CPU utilization increased substantially after the incident began.",
        "direction": "increase",
        "magnitude": 17.86,
        "time_context": "post_injection",
        "evidence_strength": "strong",
        "availability": "available",
    }
    row.update(overrides)
    return row


def test_single_clear_hypothesis():
    result = HypothesisEngine().infer([evidence()])
    assert result["status"] == "hypotheses_available"
    assert result["hypotheses"][0]["hypothesis"] == "resource saturation"
    assert result["hypotheses"][0]["supporting_evidence"]


def test_competing_hypotheses():
    result = HypothesisEngine().infer([
        evidence(),
        evidence(
            source="metrics",
            observation="Request throughput increased sharply.",
            signal="request_rate",
            service="checkoutservice",
        ),
    ])
    names = {h["hypothesis"] for h in result["hypotheses"]}
    assert {"resource saturation", "increased request load"} <= names
    assert result["status"] == "unable_to_distinguish"


def test_supporting_evidence():
    result = HypothesisEngine().infer([evidence(evidence_strength="strong")])
    assert result["hypotheses"][0]["supporting_evidence"][0]["evidence_strength"] == "strong"


def test_contradicting_evidence():
    result = HypothesisEngine().infer([
        evidence(),
        evidence(
            observation="CPU utilization remained normal during the incident.",
            direction="stable",
            evidence_strength="strong",
        ),
    ])
    h = next(h for h in result["hypotheses"] if h["hypothesis"] == "resource saturation")
    assert h["contradicting_evidence"]


def test_missing_telemetry():
    result = HypothesisEngine().infer([
        evidence(availability="unavailable", observation="Trace telemetry unavailable."),
        evidence(source="traces", signal="latency", observation="No trace telemetry available."),
    ])
    assert result["status"] == "insufficient_evidence" or result["hypotheses"]
    if result["hypotheses"]:
        assert result["hypotheses"][0]["missing_evidence"]


def test_insufficient_evidence():
    result = HypothesisEngine().infer([{
        "case_id": "case-2",
        "source": "metrics",
        "service": "checkoutservice",
        "observation": "No relevant anomaly observed.",
        "direction": "stable",
        "evidence_strength": "weak",
        "availability": "available",
    }])
    assert result["status"] == "insufficient_evidence"
    assert result["decision"] == "Insufficient evidence."


def test_hypothesis_update_after_new_evidence():
    engine = HypothesisEngine()
    initial = engine.infer([evidence()])
    updated = engine.update(
        {**initial, "_evidence_snapshot": [evidence()]},
        [evidence(
            observation="CPU utilization remained normal while latency stayed high.",
            direction="stable",
            evidence_strength="strong",
        )],
    )
    h = next(h for h in updated["hypotheses"] if h["hypothesis"] == "resource saturation")
    assert len(h["contradicting_evidence"]) == 1
    assert h["uncertainty"] == "high"


def test_ground_truth_leakage_protection():
    with pytest.raises(ValueError):
        HypothesisEngine().infer([evidence(fault="cpu_fault")])
    with pytest.raises(ValueError):
        HypothesisEngine().infer([evidence(root_cause_service="checkoutservice")])
    with pytest.raises(ValueError):
        HypothesisEngine().infer([evidence(fault_description="CPU fault")])


def test_deterministic_output():
    rows = [evidence(), evidence(
        source="traces",
        signal="latency",
        observation="Downstream span latency increased.",
        direction="increase",
        evidence_strength="moderate",
    )]
    assert HypothesisEngine().infer(rows) == HypothesisEngine().infer(copy.deepcopy(rows))


def test_multiple_services():
    result = HypothesisEngine().infer([
        evidence(service="checkoutservice"),
        evidence(
            service="currencyservice",
            source="traces",
            signal="latency",
            observation="currencyservice downstream latency increased.",
            direction="increase",
            evidence_strength="strong",
        ),
    ])
    services = {h["primary_service"] for h in result["hypotheses"]}
    assert "checkoutservice" in services or "currencyservice" in services


def test_temporal_context_without_causal_claims():
    result = HypothesisEngine().infer([evidence()])
    text = str(result).lower()
    assert "caused by" not in text
    assert "proves" not in text
    assert "after" in text or "post_injection" in text


def test_decision_engine_abstains_on_competition():
    inference = HypothesisEngine().infer([
        evidence(),
        evidence(
            observation="Request throughput increased sharply.",
            signal="request_rate",
            service="checkoutservice",
        ),
    ])
    decision = DecisionEngine().decide(inference)
    assert decision["selected_hypothesis"] is None
    assert decision["human_control_required"] is True


def test_decision_engine_recommends_check():
    inference = HypothesisEngine().infer([evidence()])
    decision = DecisionEngine().decide(inference)
    assert decision["recommended_action"]


def test_accepts_real_evidence_engine_time_context_shape():
    result = HypothesisEngine().infer([evidence(
        time_context={"phase": "post_injection", "injection_time": 100.0},
    )])
    ref = result["hypotheses"][0]["supporting_evidence"][0]
    assert isinstance(ref["time_context"], dict)
    assert ref["time_context"]["phase"] == "post_injection"


def test_decision_abstains_when_confidence_is_too_low():
    inference = {
        "case_id": "case-low-confidence",
        "status": "hypotheses_available",
        "hypotheses": [{
            "hypothesis": "resource saturation",
            "confidence": 0.40,
            "uncertainty": "moderate",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "discriminating_checks": [{"check": "Inspect resource utilization."}],
            "next_diagnostic_action": "Inspect resource utilization.",
        }],
    }
    decision = DecisionEngine().decide(inference)
    assert decision["selected_hypothesis"] is None
    assert decision["human_control_required"] is True


def test_decision_abstains_on_high_uncertainty():
    inference = {
        "case_id": "case-high-uncertainty",
        "status": "hypotheses_available",
        "hypotheses": [{
            "hypothesis": "resource saturation",
            "confidence": 0.80,
            "uncertainty": "high",
            "supporting_evidence": [{"strength": "strong"}],
            "contradicting_evidence": [{"strength": "strong"}],
            "discriminating_checks": [{"check": "Inspect resource utilization."}],
            "next_diagnostic_action": "Inspect resource utilization.",
        }],
    }
    decision = DecisionEngine().decide(inference)
    assert decision["selected_hypothesis"] is None
