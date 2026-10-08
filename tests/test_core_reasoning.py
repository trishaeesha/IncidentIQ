from src.models import DecisionEngine, HypothesisEngine


def evidence(observation, *, service="checkoutservice", direction="increase", signal="observation", strength="strong", evidence_id="e1"):
    return {
        "evidence_id": evidence_id,
        "source": "metrics",
        "service": service,
        "observation": observation,
        "signal": signal,
        "direction": direction,
        "strength": strength,
        "evidence_strength": strength,
        "availability": "available",
    }


def test_hypothesis_engine_preserves_competing_hypotheses():
    rows = [
        evidence("CPU utilization increased", signal="cpu", evidence_id="cpu"),
        evidence("Error rate increased", signal="error_rate", evidence_id="err"),
        evidence("Request latency increased", signal="latency", evidence_id="lat"),
    ]
    result = HypothesisEngine().infer(rows)
    names = {h["hypothesis"] for h in result["hypotheses"]}
    assert "resource saturation" in names
    assert "error or failure increase" in names
    assert result["decision"]


def test_hypothesis_engine_rejects_ground_truth_fields():
    rows = [evidence("CPU increased")]
    rows[0]["ground_truth"] = "checkoutservice"
    try:
        HypothesisEngine().infer(rows)
    except ValueError as exc:
        assert "Ground-truth fields" in str(exc)
    else:
        raise AssertionError("ground-truth leakage was not rejected")


def test_decision_engine_requires_human_control():
    inference = HypothesisEngine().infer([
        evidence("CPU utilization increased", signal="cpu"),
        evidence("Error rate increased", signal="error_rate", evidence_id="err"),
    ])
    decision = DecisionEngine().decide(inference)
    assert decision["human_control_required"] is True
    assert "recommended_action" in decision


def test_incremental_update_keeps_previous_evidence():
    engine = HypothesisEngine()
    first = engine.infer([evidence("CPU utilization increased", signal="cpu")])
    updated = engine.update(
        first,
        [evidence("Error rate increased", signal="error_rate", evidence_id="err")],
    )
    ids = {row["evidence_id"] for h in updated["hypotheses"] for row in h["supporting_evidence"]}
    assert "cpu" in ids or "err" in ids
