"""Aggregate evaluator-only human study records.

No evaluator truth is ever written to the participant manifest.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

def normalize(value):
    return " ".join(str(value or "").lower().replace("_"," ").split())

def correct(answer, truths):
    text=normalize(answer)
    return int(any(normalize(t) and normalize(t) in text for t in truths))

def mean(values):
    return sum(values)/len(values) if values else None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--participants",required=True)
    p.add_argument("--evaluator",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()

    records=[json.loads(x.read_text(encoding="utf-8"))
             for x in sorted(Path(a.participants).glob("*.json"))]
    evaluator=json.loads(Path(a.evaluator).read_text(encoding="utf-8"))
    truth={str(x["trial_id"]):x for x in evaluator}

    rows=[]
    for r in records:
        e=truth.get(str(r.get("trial_id")))
        if not e: continue
        mode=e.get("mode") or r.get("mode")
        ok=correct(r.get("final_diagnosis"),e.get("correct_diagnoses",[]))
        confidence=float(r.get("confidence",0) or 0)/100.0
        actions=r.get("diagnostic_actions",[]) or []
        unnecessary=sum(x.get("action_id") in e.get("unnecessary_action_ids",[]) for x in actions)
        incorrect=sum(x.get("action_id") in e.get("incorrect_action_ids",[]) for x in actions)
        rows.append({
            "trial_id":r.get("trial_id"),
            "participant_id":r.get("participant_id"),
            "mode":mode,
            "condition":e.get("condition"),
            "diagnosis_correct":ok,
            "confidence":confidence,
            "confidence_error":abs(confidence-ok),
            "elapsed_seconds":float(r.get("elapsed_seconds",0) or 0),
            "unnecessary_actions":unnecessary,
            "incorrect_actions":incorrect,
            "ai_followed":int(bool(r.get("actions_followed"))),
            "workload_score":float(r.get("workload_score",0) or 0),
            "ai_overridden":int(bool(r.get("actions_overridden"))),
        })

    groups=defaultdict(list)
    for row in rows:
        groups[(row["mode"],row["condition"])].append(row)

    summary=[]
    for (mode,condition),items in sorted(groups.items()):
        summary.append({
            "mode":mode,
            "condition":condition,
            "n":len(items),
            "diagnosis_accuracy":mean([x["diagnosis_correct"] for x in items]),
            "mean_elapsed_seconds":mean([x["elapsed_seconds"] for x in items if x["elapsed_seconds"]>0]),
            "mean_confidence":mean([x["confidence"] for x in items]),
            "mean_confidence_error":mean([x["confidence_error"] for x in items]),
            "mean_unnecessary_actions":mean([x["unnecessary_actions"] for x in items]),
            "mean_incorrect_actions":mean([x["incorrect_actions"] for x in items]),
            "workload_score":mean([x.get("workload_score",0) for x in items]),
            "ai_follow_rate":mean([x["ai_followed"] for x in items]),
            "ai_override_rate":mean([x["ai_overridden"] for x in items]),
        })

    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"n_scored":len(rows),"summary":summary,"rows":rows},indent=2),encoding="utf-8")
    print(json.dumps({"participant_records":len(records),"scored":len(rows),"groups":len(summary)},indent=2))

if __name__=="__main__":
    main()
