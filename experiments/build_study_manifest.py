"""Build researcher and participant manifests from validated real outputs.

Participant generation is fail-closed: a telemetry validation report is required,
and only cases explicitly marked VALIDATED by the researcher-side validator can
enter the participant pool. Structural evidence alone is never enough.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

CONDITIONS=("clear","ambiguous","conflicting","incomplete","misleading","novel")
MODES=("human_only","generic_ai","incidentiq")

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

def _ref_matches(ref, row):
    parts=str(ref).split(":")
    source=str(row.get("source",""))
    service=str(row.get("service") or "")
    signal=str(row.get("signal") or "")
    if len(parts)==2:
        return source==parts[0] and signal.lower()==parts[1].lower()
    if len(parts)==3:
        rs,rv,rg=parts
        if source!=rs or service.lower()!=rv.lower():
            return False
        if source=="metrics":
            return signal.lower() in {rg.lower(), f"{rv.lower()}_{rg.lower()}"}
        return signal.lower()==rg.lower()
    return False

def transform(rows,condition,resolved_refs=()):
    rows=[sanitize(r) for r in rows]
    if condition=="clear":
        return rows,"VALIDATED",["full available evidence"]
    if condition=="ambiguous":
        selected=[r for r in rows if any(_ref_matches(ref,r) for ref in resolved_refs)]
        if len(selected)<2:
            return rows,"UNVALIDATED",["validated ambiguous refs did not resolve to at least two observations"]
        return selected,"VALIDATED",["validated competing evidence references retained"]
    if condition=="conflicting":
        selected=[r for r in rows if any(_ref_matches(ref,r) for ref in resolved_refs)]
        if len(selected)<2:
            return rows,"UNVALIDATED",["validated conflicting refs did not resolve"]
        return selected,"VALIDATED",["validated opposing cross-source evidence retained"]
    if condition=="incomplete":
        return rows,"VALIDATED",["preserve all available evidence; missing modality is genuine"]
    if condition=="misleading":
        distractors=[r for r in rows if any(_ref_matches(ref,r) for ref in resolved_refs)]
        remainder=[r for r in rows if r not in distractors]
        if not distractors:
            return rows,"UNVALIDATED",["validated distractor ref did not resolve"]
        return distractors+remainder,"VALIDATED",["validated distractor is presented first; remaining available evidence is preserved"]
    if condition=="novel":
        return rows,"UNVALIDATED",["requires verified historical-reference removal"]
    raise ValueError(condition)

def load_validation(path):
    payload=json.loads(Path(path).read_text(encoding="utf-8"))
    validated=set()
    refs={}
    for row in payload.get("candidates", []):
        key=(row["case_id"],row["condition"])
        if row.get("status")=="VALIDATED" and row.get("telemetry_verified") is True:
            validated.add(key)
            refs[key]=tuple(row.get("resolved_evidence_refs",[]))
    return validated,refs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outputs",required=True)
    p.add_argument("--telemetry-validation",required=True,
                   help="Researcher-only report produced by validate_gray_area_telemetry.py")
    p.add_argument("--researcher-out",required=True)
    p.add_argument("--researcher-pool-out",required=True)
    p.add_argument("--participant-pool-out",required=True)
    a=p.parse_args()

    validated_conditions,validated_refs=load_validation(a.telemetry_validation)
    records=[]
    for path in sorted(Path(a.outputs).glob("*.json")):
        data=json.loads(path.read_text(encoding="utf-8"))
        if data.get("case_id") and data.get("evidence_digest"): records.append(data)

    researcher=[]; pool=[]; researcher_pool=[]; pool_index=0
    for case_index,data in enumerate(records,1):
        public_case=f"CASE-{case_index:02d}"
        raw_case=data["case_id"]
        for condition in CONDITIONS:
            evidence,status,notes=transform(data["evidence_digest"],condition,validated_refs.get((raw_case,condition),()))
            raw_status=status
            if (raw_case, condition) not in validated_conditions:
                status="UNVALIDATED"
                notes=["case-condition is not present in researcher telemetry validation report as VALIDATED"]
            for mode in MODES:
                researcher.append({"trial_id":f"{public_case}-{condition}-{mode}",
                    "public_case_id":public_case,"source_case_id":raw_case,
                    "condition":condition,"validation_status":status,
                    "validation_notes":notes})
                if status=="VALIDATED":
                    pool_index+=1
                    pool.append({"trial_id":f"TRIAL-POOL-{pool_index:04d}",
                        "public_case_id":public_case,
                        "mode":mode,"evidence":evidence,
                        "instructions":"Review the telemetry. State your diagnosis, confidence, and diagnostic action."})

    for case_index,data in enumerate(records,1):
        public_case=f"CASE-{case_index:02d}"
        raw_case=data["case_id"]
        for condition in CONDITIONS:
            if (raw_case,condition) not in validated_conditions:
                continue
            evidence,_,_=transform(data["evidence_digest"],condition,validated_refs.get((raw_case,condition),()))
            for mode in MODES:
                researcher_pool.append({
                    "trial_id":f"RESEARCH-{len(researcher_pool)+1:04d}",
                    "public_case_id":public_case,
                    "source_case_id":raw_case,
                    "condition_key":condition,
                    "mode":mode,
                    "evidence":evidence,
                    "instructions":"Review the telemetry. State your diagnosis, confidence, and diagnostic action.",
                })

    Path(a.researcher_out).write_text(
        json.dumps({"trial_count":len(researcher),"trials":researcher},indent=2),
        encoding="utf-8"
    )
    Path(a.researcher_pool_out).write_text(
        json.dumps({"schema_version":1,"participant_safe":False,
                    "researcher_pool":True,"trial_count":len(researcher_pool),
                    "trials":researcher_pool},indent=2),
        encoding="utf-8"
    )
    Path(a.participant_pool_out).write_text(
        json.dumps({"schema_version":1,"participant_safe":True,
                    "participant_pool":True,"trial_count":len(pool),
                    "trials":pool},indent=2),
        encoding="utf-8"
    )
    print(json.dumps({"cases":len(records),"validated_conditions":len(validated_conditions),
                      "researcher_trials":len(researcher),
                      "validated_pool_trials":len(pool)},indent=2))

if __name__=="__main__": main()
