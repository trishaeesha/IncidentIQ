"""Counterbalance experimental modes across a participant cohort.

For each case-condition cell, participants are assigned human_only,
generic_ai, and incidentiq as evenly as possible. This is the correct level
for comparing the three modes; a single participant need not see every mode.
"""
from __future__ import annotations
import argparse,json,random
from pathlib import Path
MODES=("human_only","generic_ai","incidentiq")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pool",required=True)
    p.add_argument("--participants",type=int,required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--seed",type=int,default=20261003)
    a=p.parse_args()
    if a.participants<3: raise SystemExit("Need at least 3 participants for one full mode rotation per cell.")
    data=json.loads(Path(a.pool).read_text(encoding="utf-8"))
    cells={}
    for trial in data["trials"]:
        cells.setdefault((trial["public_case_id"],trial["condition_key"]),[]).append(trial)
    rng=random.Random(a.seed)
    assignments=[]
    for pid_index in range(a.participants):
        participant_id=f"P{pid_index+1:02d}"
        keys=list(cells); rng.shuffle(keys)
        rows=[]
        for cell_index,key in enumerate(keys):
            candidates=cells[key]
            mode=MODES[(cell_index+pid_index)%3]
            chosen=next(x for x in candidates if x["mode"]==mode)
            rows.append({
                "trial_id":f"{participant_id}-T{cell_index+1:03d}",
                "participant_id":participant_id,
                "public_case_id":chosen["public_case_id"],
                "mode":chosen["mode"],
                "evidence":chosen["evidence"],
                "instructions":chosen["instructions"],
            })
        assignments.append({"participant_id":participant_id,"trial_count":len(rows),"trials":rows})
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema_version":1,"participant_safe":True,
        "participants":assignments},indent=2),encoding="utf-8")
    print(json.dumps({"participants":a.participants if hasattr(a,"participants") else None,
                      "participant_count":len(assignments),
                      "cells":len(cells),"output":str(out)},indent=2))

if __name__=="__main__": main()
