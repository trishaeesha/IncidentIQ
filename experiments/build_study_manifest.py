"""Build a researcher manifest and a separate participant-safe manifest.

The participant manifest contains opaque case IDs and no condition labels.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

CONDITIONS = ("clear", "ambiguous", "conflicting", "incomplete", "misleading", "novel")
MODES = ("human_only", "generic_ai", "incidentiq")
FORBIDDEN = {"root_cause_service","fault","fault_description","ground_truth","answer_key",
             "condition","condition_rationale","condition_label","condition_status"}

def assert_safe(value):
    if isinstance(value, dict):
        bad = FORBIDDEN.intersection(str(k).lower() for k in value)
        if bad:
            raise ValueError(f"participant leakage: {sorted(bad)}")
        for v in value.values():
            assert_safe(v)
    elif isinstance(value, list):
        for v in value:
            assert_safe(v)

def sanitize(row):
    allowed=("source","service","observation","direction","magnitude","time_context",
             "evidence_strength","availability","signal","before","after",
             "absolute_change","relative_change","sample_count","operation")
    return {k:row[k] for k in allowed if k in row}

def family(row):
    text=" ".join(str(row.get(k,"")) for k in ("signal","observation","source")).lower()
    groups={"resource":("cpu","memory","mem","load","utilization"),
            "error":("error","exception","failure","status 5"),
            "network":("network","packet","loss","timeout","connection"),
            "latency":("latency","delay","slow","duration"),
            "storage":("disk","storage","io","database","queue")}
    for name,tokens in groups.items():
        if any(t in text for t in tokens): return name
    return "other"

def transform(rows, condition):
    rows=[sanitize(r) for r in rows]
    if condition=="clear":
        return rows,"VALIDATED",["full available evidence"]
    if condition=="ambiguous":
        families={family(r) for r in rows if family(r)!="other"}
        if len(families)<2: return rows,"UNVALIDATED",["fewer than two evidence families"]
        return rows,"VALIDATED",["multiple evidence families retained"]
    if condition=="conflicting":
        directions={str(r.get("direction","")).lower() for r in rows}
        pos=bool(directions & {"increase","increased","elevated"})
        neg=bool(directions & {"decrease","decreased","normal","stable","unchanged"})
        sources={str(r.get("source","")) for r in rows}
        if len(sources)<2 or not(pos and neg):
            return rows,"UNVALIDATED",["opposing cross-source signals not demonstrated"]
        return rows,"VALIDATED",["competing directional signals retained"]
    if condition=="incomplete":
        sources=sorted({str(r.get("source","")) for r in rows})
        if len(sources)<2: return rows,"UNVALIDATED",["fewer than two sources"]
        hidden=sources[-1]
        return [r for r in rows if str(r.get("source",""))!=hidden],"VALIDATED",[f"hidden source: {hidden}"]
    if condition=="misleading":
        return rows,"UNVALIDATED",["researcher must add and verify unrelated distractor"]
    if condition=="novel":
        return rows,"UNVALIDATED",["researcher must verify historical-reference removal"]
    raise ValueError(condition)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outputs",required=True)
    p.add_argument("--researcher-out",required=True)
    p.add_argument("--participant-out",required=True)
    a=p.parse_args()
    source=Path(a.outputs)
    cases=[]
    for path in sorted(source.glob("*.json")):
        data=json.loads(path.read_text(encoding="utf-8"))
        if not data.get("case_id") or not data.get("evidence_digest"): continue
        cases.append(data)

    researcher=[]
    participant=[]
    for index,data in enumerate(cases,1):
        public_case=f"CASE-{index:02d}"
        for condition in CONDITIONS:
            evidence,status,notes=transform(data["evidence_digest"],condition)
            for mode in MODES:
                trial_id=f"{public_case}-{condition}-{mode}"
                researcher.append({"trial_id":trial_id,"public_case_id":public_case,
                    "source_case_id":data["case_id"],"condition":condition,
                    "validation_status":status,"validation_notes":notes})
                if status=="VALIDATED":
                    participant.append({"trial_id":trial_id,"public_case_id":public_case,
                        "mode":mode,"evidence":evidence,
                        "instructions":"Review the telemetry. State your diagnosis, confidence, and diagnostic action."})

    r=Path(a.researcher_out); r.parent.mkdir(parents=True,exist_ok=True)
    r.write_text(json.dumps({"trial_count":len(researcher),"trials":researcher},indent=2),encoding="utf-8")
    q=Path(a.participant_out); q.parent.mkdir(parents=True,exist_ok=True)
    public={"schema_version":1,"participant_safe":True,"trial_count":len(participant),"trials":participant}
    assert_safe(public)
    q.write_text(json.dumps(public,indent=2),encoding="utf-8")
    print(json.dumps({"cases":len(cases),"researcher_trials":len(researcher),
                      "validated_participant_trials":len(participant)},indent=2))

if __name__=="__main__":
    main()
