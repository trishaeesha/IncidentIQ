"""Run the optional NLI evidence-relation experiment on one real case.

NLI is used only to compare observation/hypothesis semantic relations. It never
receives RCAEval evaluator labels and never makes the final decision.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
from src.data.rcaeval_loader import load_case_paths, read_injection_time
from src.evidence import extract_evidence
from src.models import HypothesisEngine
from src.nlp import NLIEvidenceInterpreter

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--data-root",required=True); p.add_argument("--case",required=True)
 args=p.parse_args()
 paths=load_case_paths(Path(args.data_root),args.case)
 ev=extract_evidence(case_id=args.case,injection_time=read_injection_time(Path(args.data_root),args.case),metrics=paths["metrics"],logs=paths["logs"],traces=paths["traces"])
 rows=[x.to_dict() for x in ev if x.availability=="available"]
 hyp=HypothesisEngine().infer(rows)
 pairs=[]
 for h in hyp.get("hypotheses",[])[:3]:
  for e in h.get("supporting_evidence",[])[:5]:
   pairs.append((e.get("observation",""), f"The incident is explained by {h['hypothesis']} in service {h.get('primary_service') or 'the affected service'}."))
  for e in h.get("contradicting_evidence",[])[:3]:
   pairs.append((e.get("observation",""),h["hypothesis"]))
 nli=NLIEvidenceInterpreter().classify_many(pairs)
 print(json.dumps({"case_id":args.case,"baseline_status":hyp.get("status"),"baseline_hypotheses":[h["hypothesis"] for h in hyp.get("hypotheses",[])],"nli_relations":[r.__dict__ for r in nli]},indent=2))
if __name__=="__main__": main()
