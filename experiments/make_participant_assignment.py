"""Create one participant assignment from the researcher trial manifest.

Each participant sees each case/condition at most once, with modes balanced by
participant seed. The participant file contains no condition label or source
RCAEval case ID.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

MODES=("human_only","generic_ai","incidentiq")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--researcher-manifest",required=True)
    p.add_argument("--participant-id",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--seed",type=int,default=20261003)
    a=p.parse_args()

    data=json.loads(Path(a.researcher_manifest).read_text(encoding="utf-8"))
    valid=[t for t in data["trials"] if t.get("validation_status")=="VALIDATED"]
    rng=random.Random(a.seed)
    groups={}
    for t in valid:
        groups.setdefault((t["public_case_id"],t["condition"]),[]).append(t)

    keys=sorted(groups)
    rng.shuffle(keys)
    public=[]
    for index,key in enumerate(keys,1):
        candidates=groups[key]
        mode=MODES[index % len(MODES)]
        chosen=next((x for x in candidates if x["mode"]==mode),candidates[0])
        public.append({
            "trial_id":f"TRIAL-{index:03d}",
            "public_case_id":chosen["public_case_id"],
            "mode":chosen["mode"],
            "evidence":chosen.get("evidence",[]),
            "instructions":"Review the telemetry. State your diagnosis, confidence, and diagnostic action.",
        })

    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
        "schema_version":1,
        "participant_safe":True,
        "participant_id":a.participant_id,
        "trial_count":len(public),
        "trials":public,
    },indent=2),encoding="utf-8")
    print(json.dumps({"participant":a.participant_id,"trials":len(public),"output":str(out)},indent=2))

if __name__=="__main__":
    main()
