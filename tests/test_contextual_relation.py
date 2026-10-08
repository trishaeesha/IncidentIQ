import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.contextual_relation import relate


def test_contextual_relation_uses_signal_context():
    assert (
        relate(
            {"service": "checkoutservice", "signal": "cpu", "observation": "changed after injection"},
            "resource saturation",
        )
        == "supporting"
    )
    assert (
        relate(
            {"service": "checkoutservice", "signal": "diskio", "observation": "changed after injection"},
            "database or storage pressure",
        )
        == "supporting"
    )
    assert (
        relate(
            {"service": "checkoutservice", "signal": "error_like_frequency", "observation": "changed"},
            "error or failure increase",
        )
        == "supporting"
    )
