import sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[1]\nif str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))\n\nfrom src.models.contextual_relation import relate

def test_contextual_relation_uses_signal_context():
    assert relate({"service":"checkoutservice","signal":"cpu","observation":"changed after injection"},"resource saturation")=="supporting"
    assert relate({"service":"checkoutservice","signal":"diskio","observation":"changed after injection"},"database or storage pressure")=="supporting"
    assert relate({"service":"checkoutservice","signal":"error_like_frequency","observation":"changed"},"error or failure increase")=="supporting"
