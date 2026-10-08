from pathlib import Path


PARTICIPANT_PAGE = Path(__file__).parents[1] / "study-site" / "web" / "index.html"


def test_participant_page_does_not_ship_evaluator_labels_or_condition_metadata():
    text = PARTICIPANT_PAGE.read_text(encoding="utf-8").lower()
    forbidden = (
        "root_cause_service",
        "fault_description",
        "ground_truth",
        "answer_key",
        "condition_rationale",
        "historical mismatch",
        "novel",
        "condition:t.condition",
    )
    leaked = [item for item in forbidden if item in text]
    assert not leaked, f"participant page contains evaluator/internal fields: {leaked}"


def test_participant_page_gets_trials_from_backend():
    text = PARTICIPANT_PAGE.read_text(encoding="utf-8").lower()
    assert 'call("reserve"' in text
    assert 'call("resume"' in text
    assert 'call("test"' in text
    assert 'var cases=[' not in text
