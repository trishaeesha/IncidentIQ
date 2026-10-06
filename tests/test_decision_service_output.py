import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.decision_engine import DecisionEngine


def test_decision_exposes_selected_primary_service():
    inference = {
        "case_id": "c1",
        "status": "hypotheses_available",
        "hypotheses": [{
            "hypothesis": "resource saturation",
            "primary_service": "checkoutservice",
            "confidence": 0.9,
            "uncertainty": "low",
            "supporting_evidence": [{"service": "checkoutservice"}],
            "contradicting_evidence": [],
            "next_diagnostic_action": "inspect CPU",
        }],
    }
    result = DecisionEngine().decide(inference)
    assert result["selected_primary_service"] == "checkoutservice"
