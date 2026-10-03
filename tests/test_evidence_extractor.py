import pandas as pd

from src.evidence import extract_evidence

INJECTION = "2026-01-01T00:10:00Z"


def test_metric_change_preserves_raw_values_and_does_not_label_support():
    df = pd.DataFrame({
        "timestamp": ["2026-01-01T00:09:00Z", "2026-01-01T00:11:00Z"],
        "service": ["checkout", "checkout"],
        "metric": ["cpu", "cpu"],
        "value": [0.43, 18.29],
    })
    records = extract_evidence(case_id="case-1", injection_time=INJECTION, metrics=df)
    record = next(r for r in records if r.evidence_source == "metrics")
    assert record.raw_measurements["before_median"] == 0.43
    assert record.raw_measurements["after_median"] == 18.29
    assert record.direction_change == "strongly increased"
    assert record.classification is None
    assert record.affected_service_component == "checkout"


def test_log_frequency_change_is_observation_not_root_cause_evidence():
    df = pd.DataFrame({
        "timestamp": ["2026-01-01T00:09:00Z", "2026-01-01T00:11:00Z", "2026-01-01T00:11:30Z"],
        "service": ["checkout", "checkout", "checkout"],
        "message": ["ok", "error", "error"],
    })
    records = extract_evidence(case_id="case-2", injection_time=INJECTION, logs=df)
    record = next(r for r in records if r.evidence_source == "logs")
    assert record.raw_measurements["before_count"] == 1
    assert record.raw_measurements["after_count"] == 2
    assert record.direction_change == "increased"
    assert record.classification is None


def test_missing_modalities_are_explicit():
    records = extract_evidence(case_id="case-3", injection_time=INJECTION)
    assert {r.evidence_source for r in records} == {"metrics", "logs", "traces"}
    assert all(r.classification == "missing" for r in records)


def test_trace_latency_change():
    df = pd.DataFrame({
        "timestamp": ["2026-01-01T00:09:00Z", "2026-01-01T00:11:00Z"],
        "service": ["checkout", "checkout"],
        "duration_ms": [100, 250],
    })
    records = extract_evidence(case_id="case-4", injection_time=INJECTION, traces=df)
    record = next(r for r in records if r.evidence_source == "traces")
    assert record.raw_measurements["before_median"] == 100
    assert record.raw_measurements["after_median"] == 250
    assert record.direction_change == "increased"
    assert record.classification is None
