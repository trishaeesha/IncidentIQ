"""Build evaluator-only trial truth from the validated researcher pool and RCAEval metadata."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def load_metadata(path: Path):
    if path.suffix.lower() == ".json":
        data=json.loads(path.read_text(encoding="utf-8-sig"))
        rows=data.get("rows", data if isinstance(data,list) else [])
        return {x["row"]["case"]:x["row"] for x in rows}
    import pandas as pd
    df=pd.read_parquet(path)
    return {str(r["case"]):dict(r) for _,r in df.iterrows()}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cohort",required=True)
    p.add_argument("--researcher-pool",required=True)
    p.add_argument("--rcaeval-metadata",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    cohort=json.loads(Path(a.cohort).read_text(encoding="utf-8"))
    pool=json.loads(Path(a.researcher_pool).read_text(encoding="utf-8"))
    metadata=load_metadata(Path(a.rcaeval_metadata))

    case_map={}
    for t in pool.get("trials",[]):
        case_map[t["public_case_id"]]={
            "source_case_id":t["source_case_id"],
            "condition":t["condition_key"],
        }

    out=[]
    for participant in cohort.get("participants",[]):
        for t in participant.get("trials",[]):
            m=case_map[t["public_case_id"]]
            row=metadata[m["source_case_id"]]
            root=row.get("root_cause_service")
            if not root:
                raise ValueError(f"missing RCAEval root_cause_service for {m['source_case_id']}")
            out.append({
                "trial_id":t["trial_id"],
                "participant_id":participant["participant_id"],
                "mode":t["mode"],
                "condition":m["condition"],
                "source_case_id":m["source_case_id"],
                "correct_diagnoses":[str(root)],
                "action_ground_truth_available":False,
                "unnecessary_action_ids":[],
                "incorrect_action_ids":[],
            })

    Path(a.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps({"evaluator_trials":len(out),"action_ground_truth_available":False},indent=2))

if __name__=="__main__":
    main()
