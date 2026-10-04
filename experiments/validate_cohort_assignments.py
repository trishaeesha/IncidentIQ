"""Validate participant cohort balance and leakage constraints."""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

MODES={"human_only","generic_ai","incidentiq"}

def fingerprint(evidence):
    return json.dumps(evidence, sort_keys=True, separators=(",", ":"))

def assistance_fingerprint(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--pool",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    pool=json.loads(Path(a.pool).read_text(encoding="utf-8"))
    errors=[]
    participants=data.get("participants",[])
    pool_index=defaultdict(list)
    for trial in pool.get("trials",[]):
        pool_index[(trial.get("mode"),fingerprint(trial.get("evidence",[])))].append(
            (trial.get("public_case_id"),trial.get("condition_key"))
        )

    if not data.get("participant_safe"):
        errors.append("cohort manifest is not marked participant_safe")
    if len(participants)<3:
        errors.append("fewer than 3 participants")

    seen_by_participant=defaultdict(set)
    observed=defaultdict(lambda: defaultdict(set))
    for participant in participants:
        pid=participant.get("participant_id")
        trials=participant.get("trials",[])
        if participant.get("trial_count") != len(trials):
            errors.append(f"{pid}: trial_count mismatch")
        for trial in trials:
            if any(k in trial for k in ("condition","condition_key","condition_rationale")):
                errors.append(f"{pid}: condition metadata leaked")
            mode=trial.get("mode")
            if mode not in MODES:
                errors.append(f"{pid}: invalid mode {mode}")
            tid=trial.get("trial_id")
            if tid in seen_by_participant[pid]:
                errors.append(f"{pid}: duplicate trial id {tid}")
            seen_by_participant[pid].add(tid)

            matches=pool_index.get((mode,fingerprint(trial.get("evidence",[]))),[])
            if len(matches)!=1:
                errors.append(f"{pid}/{tid}: evidence does not map uniquely to researcher pool")
                continue
            cell=matches[0]
            observed[cell][mode].add(pid)
            expected_assistance = next(
                x.get("assistance") for x in pool.get("trials",[])
                if x.get("mode")==mode and x.get("public_case_id")==cell[0] and fingerprint(x.get("evidence",[]))==fingerprint(trial.get("evidence",[]))
            )
            if assistance_fingerprint(trial.get("assistance")) != assistance_fingerprint(expected_assistance):
                errors.append(f"{pid}/{tid}: assistance does not match researcher pool")

    for cell,by_mode in observed.items():
        if set(by_mode)!=MODES:
            errors.append(f"{cell}: not all three modes represented")
            continue
        sizes={mode:len(pids) for mode,pids in by_mode.items()}
        if max(sizes.values())-min(sizes.values())>1:
            errors.append(f"{cell}: mode imbalance {sizes}")
        overlap=set.intersection(*(set(pids) for pids in by_mode.values()))
        if overlap:
            errors.append(f"{cell}: participant(s) assigned multiple modes: {sorted(overlap)}")

    report={"participant_count":len(participants),"errors":errors,
            "valid":not errors,
            "cells_checked":len(observed),
            "mode_counts_by_cell":{
                f"{cell[0]}::{cell[1]}":{mode:len(pids) for mode,pids in by_mode.items()}
                for cell,by_mode in observed.items()
            }}
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"valid":not errors,"errors":len(errors),"participants":len(participants),"cells":len(observed),"error_details":errors},indent=2))
    if errors: raise SystemExit(1)

if __name__=="__main__": main()
