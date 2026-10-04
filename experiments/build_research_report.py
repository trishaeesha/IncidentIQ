"""Assemble the final IncidentIQ research report without inventing human results."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--telemetry",required=True)
    p.add_argument("--analysis",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    telemetry=load(a.telemetry)
    analysis=load(a.analysis)
    validated=[x for x in telemetry.get("candidates",[]) if x.get("status")=="VALIDATED" and x.get("telemetry_verified") is True]
    report={
      "title":"IncidentIQ: Evidence-Grounded AI Decision Support for Software Incident Troubleshooting",
      "research_question":"When does evidence-grounded AI assistance help or harm human software-incident diagnostic decisions?",
      "engineering_validation":{"validated_gray_area_conditions":len(validated),"validated_conditions":[x.get("condition") for x in validated],"human_results_available":analysis.get("n_scored",0)>0},
      "human_study_analysis":analysis,
      "conclusion_status":"PENDING_HUMAN_DATA" if analysis.get("n_scored",0)==0 else "READY_FOR_EVIDENCE_REVIEW",
      "integrity_rule":"Do not claim superiority, significance, generalization, or harm until actual participant records have been scored and the preregistered analysis supports the claim.",
    }
    Path(a.out).write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"status":report["conclusion_status"],"validated_conditions":len(validated),"n_scored":analysis.get("n_scored",0)},indent=2))

if __name__=="__main__": main()