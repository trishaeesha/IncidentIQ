import pandas as pd

from src.evidence import extract_evidence, extract_metric_evidence, group_evidence_by_service

INJECTION = 100.0


def test_time_column_is_never_treated_as_evidence(tmp_path):
    p = tmp_path / "metrics.parquet"
    pd.DataFrame({"timestamp":[90.0,110.0],"cpu":[1.0,3.0]}).to_parquet(p)
    records = extract_metric_evidence(p, INJECTION)
    assert len(records) == 1
    assert records[0]["metric"] == "cpu"


def test_near_zero_baseline_has_no_absurd_relative_percentage(tmp_path):
    p = tmp_path / "metrics.parquet"
    pd.DataFrame({"timestamp":[90.0,110.0],"cpu":[0.0,10_000.0]}).to_parquet(p)
    records = extract_metric_evidence(p, INJECTION)
    assert records[0]["relative_change"] is None


def test_missing_logs_and_traces_do_not_crash():
    records = extract_evidence(case_id="case", injection_time=INJECTION)
    assert {r.evidence_source for r in records} == {"metrics","logs","traces"}
    assert all(r.classification == "missing" for r in records)


def test_empty_telemetry_returns_missing(tmp_path):
    p = tmp_path / "logs.parquet"
    pd.DataFrame().to_parquet(p)
    records = extract_evidence(case_id="case", injection_time=INJECTION, logs=p)
    assert records[0].classification == "missing"


def test_log_extraction_counts_services_and_error_warning_signals(tmp_path):
    p = tmp_path / "logs.parquet"
    pd.DataFrame({
        "timestamp":[90.0,91.0,110.0,111.0,112.0],
        "container_name":["checkoutservice"]*5,
        "message":["ok","ok","error connecting","warning retry","exception raised"],
    }).to_parquet(p)
    records = extract_evidence(case_id="case", injection_time=INJECTION, logs=p)
    signals = {r.raw_measurements["signal"] for r in records}
    assert "log_rate" in signals
    assert "error_like" in signals
    assert "warning_like" in signals


def test_trace_extraction_latency_and_service(tmp_path):
    p = tmp_path / "traces.parquet"
    pd.DataFrame({
        "time":[90.0,91.0,110.0,111.0],
        "serviceName":["checkoutservice"]*4,
        "operationName":["checkout"]*4,
        "duration":[100.0,120.0,250.0,300.0],
        "statusCode":[0,0,0,1],
    }).to_parquet(p)
    records = extract_evidence(case_id="case", injection_time=INJECTION, traces=p)
    signals = {r.raw_measurements["signal"] for r in records}
    assert "latency_median" in signals
    assert "service_latency_median" in signals
    assert "error_status" in signals


def test_service_grouping_works():
    from src.evidence.schema import EvidenceRecord
    records = [
        EvidenceRecord("c","metrics","m","increase",1,{}, "checkoutservice","strong",None,"",{}),
        EvidenceRecord("c","traces","t","increase",1,{}, "checkoutservice","strong",None,"",{}),
    ]
    grouped = group_evidence_by_service(records)
    assert list(grouped) == ["checkoutservice"]
    assert len(grouped["checkoutservice"]) == 2


def test_multiple_cases_are_independent(tmp_path):
    p1 = tmp_path / "m1.parquet"
    p2 = tmp_path / "m2.parquet"
    for p, after in ((p1,2.0),(p2,5.0)):
        pd.DataFrame({"timestamp":[90.0,110.0],"cpu":[1.0,after]}).to_parquet(p)
    r1 = extract_metric_evidence(p1, INJECTION)
    r2 = extract_metric_evidence(p2, INJECTION)
    assert r1[0]["after"] != r2[0]["after"]


def test_leakage_guard_source_does_not_accept_fault_fields():
    import inspect
    from src.evidence.extractor import extract_evidence
    params = inspect.signature(extract_evidence).parameters
    assert "root_cause_service" not in params
    assert "fault" not in params
    assert "fault_description" not in params
