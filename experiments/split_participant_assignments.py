"""Split the validated planned cohort into participant-safe launch files."""
from __future__ import annotations
import argparse,json
from pathlib import Path

FORBIDDEN={"condition","condition_key","condition_rationale","source_case_id","root_cause_service","fault","fault_description","ground_truth"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--out-dir",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    for participant in data.get("participants",[]):
        for trial in participant.get("trials",[]):
            leaked=FORBIDDEN.intersection(trial)
            if leaked: raise ValueError(f"leakage for {participant['participant_id']}: {sorted(leaked)}")
        payload={"schema_version":1,"participant_safe":True,
                 "participant_id":participant["participant_id"],
                 "trial_count":len(participant["trials"]),
                 "trials":participant["trials"]}
        (out/f"{participant['participant_id']}.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"participants":len(data.get("participants",[])),"out_dir":str(out)},indent=2))
if __name__=="__main__": main()
