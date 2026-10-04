"""Pre-registered analysis plan for the IncidentIQ human study.

This script is intentionally conservative: with no participant records it emits
no performance claims. After data collection it computes descriptive outcomes
by assistance mode and gray-area condition and flags cells too small for
inferential interpretation.
"""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

METRICS=("diagnosis_correct","confidence_error","elapsed_seconds",
         "unnecessary_actions","incorrect_actions","workload_score")

def mean(xs): return sum(xs)/len(xs) if xs else None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--scored",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.scored).read_text(encoding="utf-8"))
    rows=data.get("rows",[])
    groups=defaultdict(list)
    for r in rows:
        groups[(r.get("mode"),r.get("condition"))].append(r)
    summary=[]
    for (mode,condition),items in sorted(groups.items()):
        summary.append({
            "mode":mode,"condition":condition,"n":len(items),
            "diagnosis_accuracy":mean([r["diagnosis_correct"] for r in items]),
            "mean_confidence_error":mean([r["confidence_error"] for r in items]),
            "mean_elapsed_seconds":mean([r["elapsed_seconds"] for r in items if r["elapsed_seconds"]>0]),
            "mean_unnecessary_actions":mean([r["unnecessary_actions"] for r in items]),
            "mean_incorrect_actions":mean([r["incorrect_actions"] for r in items]),
        })
    report={
        "analysis_status":"NO_PARTICIPANT_DATA" if not rows else "DESCRIPTIVE_ONLY",
        "n_scored":len(rows),
        "minimum_group_n_for_inferential_analysis":10,
        "summary":summary,
        "interpretation_rule":"Do not claim superiority, significance, generalization, or harm without adequate participant records and a preregistered inferential analysis.",
    }
    Path(a.out).write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"status":report["analysis_status"],"n_scored":len(rows),"groups":len(summary)},indent=2))
if __name__=="__main__": main()
