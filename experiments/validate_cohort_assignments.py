"""Validate participant cohort balance and leakage constraints."""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

MODES={"human_only","generic_ai","incidentiq"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    errors=[]
    participants=data.get("participants",[])
    if not data.get("participant_safe"):
        errors.append("cohort manifest is not marked participant_safe")
    if len(participants)<3:
        errors.append("fewer than 3 participants")

    cell_modes=defaultdict(list)
    participant_cells=defaultdict(set)
    for participant in participants:
        pid=participant.get("participant_id")
        for trial in participant.get("trials",[]):
            if "condition" in trial or "condition_key" in trial or "condition_rationale" in trial:
                errors.append(f"{pid}: condition metadata leaked")
            cell=(trial.get("public_case_id"), trial.get("trial_cell_id", trial.get("public_case_id")))
            # The cohort generator has one row per cell but does not expose condition.
            # Balance is therefore checked by position: each participant has the same
            # trial count and each position receives a rotating mode.
            if trial.get("mode") not in MODES:
                errors.append(f"{pid}: invalid mode {trial.get('mode')}")
            if trial.get("trial_id") in participant_cells[pid]:
                errors.append(f"{pid}: duplicate trial id")
            participant_cells[pid].add(trial.get("trial_id"))
        if participant.get("trial_count") != len(participant.get("trials",[])):
            errors.append(f"{pid}: trial_count mismatch")

    counts=defaultdict(lambda: defaultdict(int))
    for participant in participants:
        for i,trial in enumerate(participant.get("trials",[])):
            counts[i][trial.get("mode")]+=1

    for i,mode_counts in counts.items():
        missing=MODES-set(mode_counts)
        if missing:
            errors.append(f"trial position {i+1}: missing modes {sorted(missing)}")

    report={"participant_count":len(participants),"errors":errors,
            "valid":not errors,
            "mode_counts_by_position":{str(k):dict(v) for k,v in counts.items()}}
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"valid":not errors,"errors":len(errors),"participants":len(participants)},indent=2))
    if errors: raise SystemExit(1)

if __name__=="__main__": main()
