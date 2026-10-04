"""Create one opaque participant assignment from the researcher trial pool.

Each participant receives at most one mode for each case/condition cell.
"""
from __future__ import annotations
import argparse,json,random
from pathlib import Path

MODES=("human_only","generic_ai","incidentiq")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pool",required=True)
    p.add_argument("--participant-id",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--seed",type=int,default=20261003)
    a=p.parse_args()

    data=json.loads(Path(a.pool).read_text(encoding="utf-8"))
    if not data.get("participant_pool"):
        raise ValueError("Input is not a researcher participant pool.")
    pool=data["trials"]
    groups={}
    for trial in pool:
        groups.setdefault((trial["public_case_id"],trial["condition_key"]),[]).append(trial)

    keys=list(groups)
    random.Random(a.seed).shuffle(keys)
    assigned=[]
    for index,key in enumerate(keys,1):
        candidates=groups[key]
        desired=MODES[index % len(MODES)]
        chosen=next((x for x in candidates if x["mode"]==desired),candidates[0])
        assigned.append({
            "trial_id":f"TRIAL-{index:03d}",
            "public_case_id":chosen["public_case_id"],
            "mode":chosen["mode"],
            "evidence":chosen["evidence"],
            "assistance":chosen.get("assistance"),
            "instructions":chosen["instructions"],
        })

    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema_version":1,"participant_safe":True,
        "participant_id":a.participant_id,"trial_count":len(assigned),
        "trials":assigned},indent=2),encoding="utf-8")
    print(json.dumps({"participant":a.participant_id,"trials":len(assigned),"output":str(out)},indent=2))

if __name__=="__main__": main()
