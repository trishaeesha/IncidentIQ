"""Audit gray-area candidates without pretending structural checks are telemetry validation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from src.evaluation.conditions import validate_condition

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="experiments/gray_area_candidates.py")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    # Importing the candidate module is intentional: it is researcher-side only.
    import importlib.util
    spec=importlib.util.spec_from_file_location("gray_candidates",a.input)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    report=[]
    for candidate in module.CANDIDATES:
        structural=validate_condition(candidate)
        report.append({
            "case_id":candidate.case_id,
            "condition":candidate.condition,
            "schema_gate_status":structural.validation_status,
            "evidence_refs":list(candidate.evidence_refs),
            "telemetry_verified":False,
            "status":"PENDING_TELEMETRY_VERIFICATION",
            "reason":"Schema/rationale gates passed or failed, but evidence_refs have not been checked against raw RCAEval telemetry in this environment."
        })
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps({"telemetry_verification_required":True,"candidates":report},indent=2),encoding="utf-8")
    print(json.dumps({"candidates":len(report),"telemetry_verified":0,"output":a.out},indent=2))

if __name__=="__main__": main()
