import inspect

import pandas as pd

from src.evidence import extract_evidence, extract_metric_evidence, group_evidence_by_service


INJECTION = 100.0


def test_time_column_is_never_treated_as_evidence(tmp_path):
    p = tmp_path / "metrics.parquet"
    pd.DataFrame({"timestamp": [90.0, 110.0], "cpu": [1.0, 3.0]}).to_parquet(p)
    records = extract_metric_evidence(p, INJECTION)
    assert len(records) == 1
    assert records[0]["metric"] == "cpu"


def test_baseline_quality_uses_same_mean_baseline_as_relative_change(tmp_path):
    p = tmp_path / "metrics.parquet"
    # Mean = 10, median = 1. The quality calculation must use the mean,
    # because relative_change also uses the mean.
    pd.DataFrame({
        "timestamp": [90.0, 91.0, 92.0, 110.0],
        "cpu": [1.0, 1.0, 1.0, 20.0],
    }).to_parquet(p)
    records = extract_metric_evidence(p, INJECTION)
    assert records[0]["baseline_quality"] == "stable"


def test_near_zero_baseline_has_no_absurd_relative_percentage(tmp_path):
    p = tmp_path / "metrics.parquet"
    pd.DataFrame({"timestamp": [90.0, 110.0], "cpu": [0.0, 10_000.0]}).to_parquet(p)
    records = extract_metric_evidence(p, INJECTION)
    assert records[0]["relative_change"] is None


def test_missing_logs_and_traces_do_not_crash():
    records = extract_evidence(case_id="case", injection_time=INJECTION)
    assert {r.evidence_source for r in records} == {"metrics", "logs", "traces"}
    assert all(r.relation is None for r in records)
    assert all(r.availability == "unavailable" for r in records)


def test_empty_telemetry_is_unavailable_not_contradictory(tmp_path):
    p = tmp_path / "logs.parquet"
    pd.DataFrame().to_parquet(p)
    records = extract_evidence(case_id="case", injection_time=INJECTION, logs=p)
    assert records[0].availability == "unavailable"
    assert records[0].relation is None


def test_log_extraction_counts_services_and_error_warning_signals(tmp_path):
    p = tmp_path / "logs.parquet"
    pd.DataFrame({
        "timestamp": [90.0, 91.0, 110.0, 111.0, 112.0],
        "container_name": ["checkoutservice"] * 5,
        "message": ["ok", "ok", "error connecting", "warning retry", "exception raised"],
    }).to_parquet(p)

    records = extract_evidence(case_id="case", injection_time=INJECTION, logs=p)
    signals = {r.raw_measurements["signal"] for r in records}
    assert "log_rate" in signals
    assert "error_like" in signals
    assert "warning_like" in signals
    assert all(r.relation is None for r in records)
    assert all(r.availability == "available" for r in records)


def test_trace_extraction_latency_operation_and_status(tmp_path):
    p = tmp_path / "traces.parquet"
    pd.DataFrame({
        "time": [90.0, 91.0, 110.0, 111.0],
        "serviceName": ["checkoutservice"] * 4,
        "operationName": ["checkout"] * 4,
        "duration": [100.0, 120.0, 250.0, 300.0],
        "statusCode": [0, 0, 0, 1],
    }).to_parquet(p)

    records = extract_evidence(case_id="case", injection_time=INJECTION, traces=p)
    signals = {r.raw_measurements["signal"] for r in records}
    assert "latency_median" in signals
    assert "service_latency_median" in signals
    assert "operation_span_count" in signals
    assert "error_status" in signals
    assert all(r.relation is None for r in records)


def test_unified_schema_is_consistent(tmp_path):
    p = tmp_path / "metrics.parquet"
    pd.DataFrame({
        "timestamp": [90.0, 91.0, 110.0, 111.0],
        "checkoutservice_cpu": [10.0, 10.0, 20.0, 22.0],
    }).to_parquet(p)

    records = extract_evidence(case_id="case", injection_time=INJECTION, metrics=p)
    item = records[0].to_dict()

    required = {
        "case_id", "source", "service", "observation", "direction",
        "magnitude", "time_context", "evidence_strength", "relation",
        "availability",
    }
    assert required.issubset(item)
    assert item["relation"] is None
    assert item["source"] == "metrics"
    assert item["service"] == "checkoutservice"
    assert item["time_context"]["phase"] == "post_injection"


def test_service_grouping_works():
    from src.evidence.schema import EvidenceRecord

    records = [
        EvidenceRecord("c", "metrics", "m", "increase", 1, {}, "checkoutservice", "strong", None, "", {}),
        EvidenceRecord("c", "traces", "t", "increase", 1, {}, "checkoutservice", "strong", None, "", {}),
    ]
    grouped = group_evidence_by_service(records)
    assert list(grouped) == ["checkoutservice"]
    assert len(grouped["checkoutservice"]) == 2


def test_multiple_cases_are_independent(tmp_path):
    p1 = tmp_path / "m1.parquet"
    p2 = tmp_path / "m2.parquet"
    for p, after in ((p1, 2.0), (p2, 5.0)):
        pd.DataFrame({"timestamp": [90.0, 110.0], "cpu": [1.0, after]}).to_parquet(p)

    r1 = extract_metric_evidence(p1, INJECTION)
    r2 = extract_metric_evidence(p2, INJECTION)
    assert r1[0]["after"] != r2[0]["after"]


def test_temporal_context_is_preserved(tmp_path):
    p = tmp_path / "metrics.parquet"
    pd.DataFrame({"timestamp": [90.0, 91.0, 110.0, 111.0], "cpu": [1.0, 1.0, 2.0, 2.0]}).to_parquet(p)
    record = extract_evidence(case_id="case", injection_time=INJECTION, metrics=p)[0]
    assert record.time_context["phase"] == "post_injection"
    assert record.time_context["injection_time"] == INJECTION


def test_leakage_guard_source_does_not_accept_or_reference_fault_fields():
    from src.evidence import extractor

    params = inspect.signature(extractor.extract_evidence).parameters
    for field in ("root_cause_service", "fault", "fault_description"):
        assert field not in params

    source = inspect.getsource(extractor.extract_evidence)
    for field in ("root_cause_service", "fault", "fault_description"):
        assert field not in source
