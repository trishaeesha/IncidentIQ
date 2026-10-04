"""Profile extracted raw telemetry for gray-area condition discovery.

Researcher-only: this reports observable evidence patterns but does not label a
case as conflicting unless the explicit validation rule is later satisfied.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.rcaeval_loader import case_paths, read_injection_time
from src.evidence import extract_evidence
from experiments.validate_gray_area_telemetry import available_rows, families

CASES = (
    "re2ob_checkoutservice_cpu_2",
    "re2ob_checkoutservice_mem_2",
    "re2ss_user_loss_1",
)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data-root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    report=[]
    for case_id in CASES:
        paths=case_paths(a.data_root,case_id)
        injection=read_injection_time(a.data_root,case_id)
        evidence=extract_evidence(case_id=case_id,injection_time=injection,
                                  metrics=paths["metrics"],logs=paths["logs"],traces=paths["traces"])
        rows=available_rows(evidence)
        direction_counts={}
        for row in rows:
            key=(row["source"],row["direction"])
            direction_counts["|".join(map(str,key))]=direction_counts.get("|".join(map(str,key)),0)+1
        report.append({
            "case_id":case_id,
            "sources":sorted({r["source"] for r in rows if r["source"]}),
            "families":sorted(families(rows)),
            "direction_counts":direction_counts,
            "service_counts":{},
            "evidence_rows":len(rows),
            "observations":[{k:r.get(k) for k in ("source","service","signal","observation","direction","strength","time_context")} for r in rows],
            "raw_traces_present":paths["traces"].exists(),
        })
        for r in rows:
            s=r["service"] or "<unknown>"
            report[-1]["service_counts"][s]=report[-1]["service_counts"].get(s,0)+1
    Path(a.out).write_text(json.dumps({"cases":report},indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
