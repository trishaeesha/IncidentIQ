"""Evaluator-only scoring for IncidentIQ RCAEval runs.

Ground-truth labels are loaded only in this evaluator process and are never
passed into the participant-facing evidence/hypothesis/decision pipeline.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True)
    p.add_argument("--result",required=True)
    args=p.parse_args()
    cases=pd.read_parquet(args.cases)
    result=json.loads(Path(args.result).read_text())
    case_id=result["case_id"]
    row=cases.loc[cases["case"]==case_id]
    if row.empty:
        raise ValueError(f"Case not found: {case_id}")
    truth=str(row.iloc[0]["root_cause_service"])
    selected=result["decision"].get("selected_hypothesis")
    hs=result.get("hypotheses",[])
    selected_obj=next((h for h in hs if h["hypothesis"]==selected),None)
    predicted_service=selected_obj.get("primary_service") if selected_obj else None
    print(json.dumps({
        "case_id":case_id,
        "ground_truth_root_service":truth,
        "predicted_root_service":predicted_service,
        "root_service_correct": predicted_service==truth if predicted_service else False,
        "abstained": selected is None,
        "selected_hypothesis":selected,
        "selected_confidence": selected_obj.get("confidence") if selected_obj else None
    },indent=2))
if __name__=="__main__": main()
