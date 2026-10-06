import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.evidence.extractor import extract_trace_evidence


def test_rcaeval_trace_uses_epoch_start_time(tmp_path):
    path = tmp_path / "traces.parquet"
    df = pd.DataFrame(
        {
            "time": ["00:17", "00:18", "00:19", "00:20"],
            "startTime": [1699999999000000, 1700000000000000, 1700000001000000, 1700000002000000],
            "duration": [10, 10, 20, 30],
            "serviceName": ["svc"] * 4,
            "operationName": ["op"] * 4,
            "statusCode": [0, 0, 1, 1],
        }
    )
    df.to_parquet(path, index=False)

    records = extract_trace_evidence(path, 1700000000)
    assert records
    assert any(r["signal"] == "span_count" for r in records)
    assert any(r["signal"] == "error_status" for r in records)


from src.models.hypothesis_engine import HypothesisEngine


def test_neutral_evidence_does_not_overpower_strong_signal():
    engine = HypothesisEngine()
    evidence = [
        {
            "source": "metrics", "service": "checkoutservice",
            "observation": "checkoutservice_cpu increased after injection",
            "direction": "increase", "evidence_strength": "strong",
            "availability": "available",
        }
    ] + [
        {
            "source": "traces", "service": "other",
            "observation": f"trace observation {i}",
            "direction": "increase", "evidence_strength": "weak",
            "availability": "available",
        }
        for i in range(20)
    ]
    result = engine.infer(evidence)
    resource = next(h for h in result["hypotheses"] if h["hypothesis"] == "resource saturation")
    assert resource["confidence"] >= 0.8
