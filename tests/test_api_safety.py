from app import assert_safe


def test_api_rejects_evaluator_ground_truth_fields():
    try:
        assert_safe({"evidence": [{"observation": "CPU increased", "ground_truth": "hidden"}]})
    except ValueError as exc:
        assert "ground-truth fields" in str(exc)
    else:
        raise AssertionError("ground-truth payload was accepted")


def test_api_accepts_normal_evidence_payload():
    assert_safe({"case_id": "demo", "evidence": [{"observation": "CPU increased"}]})
