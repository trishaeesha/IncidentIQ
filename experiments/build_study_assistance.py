"""Build participant-visible assistance for the three study modes.

The generic_ai arm is a deliberately simple, deterministic generic assistant:
it surfaces the strongest single evidence observation and does not expose
cross-source conflict, uncertainty, or a diagnostic action.

The incidentiq arm uses the project's HypothesisEngine + DecisionEngine and
exposes ranked hypotheses, uncertainty, supporting/contradicting evidence
counts, and the next diagnostic action.

This is a study manipulation, not a claim that either arm is an LLM.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.models import HypothesisEngine, DecisionEngine

def generic_assistance(evidence):
    available=[x for x in evidence if x.get("availability","available")=="available"]
    if not available:
        return {"label":"Generic AI","summary":"No usable telemetry observation was available."}
    ranked=sorted(available,key=lambda x: {"strong":2,"moderate":1,"weak":0}.get(str(x.get("evidence_strength")),0),reverse=True)
    top=ranked[0]
    return {"label":"Generic AI","summary":f"Most salient observation: {top.get('service') or 'unknown service'} — {top.get('observation') or top.get('signal') or 'telemetry change'}."}

def incidentiq_assistance(evidence):
    h=HypothesisEngine().infer(evidence)
    d=DecisionEngine().decide(h)
    return {
        "label":"IncidentIQ",
        "hypotheses":[
            {"hypothesis":x.get("hypothesis"),"primary_service":x.get("primary_service"),
             "confidence":x.get("confidence"),"uncertainty":x.get("uncertainty"),
             "supporting_count":len(x.get("supporting_evidence",[])),
             "contradicting_count":len(x.get("contradicting_evidence",[])),
             "missing_count":len(x.get("missing_evidence",[])),
             "next_diagnostic_action":x.get("next_diagnostic_action")}
            for x in h.get("hypotheses",[])
        ],
        "decision":d,
    }

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    for trial in data.get("trials",[]):
        mode=trial.get("mode")
        if mode=="human_only":
            trial.pop("assistance",None)
        elif mode=="generic_ai":
            trial["assistance"]=generic_assistance(trial.get("evidence",[]))
        elif mode=="incidentiq":
            trial["assistance"]=incidentiq_assistance(trial.get("evidence",[]))
        else:
            raise ValueError(f"unknown mode: {mode}")
    Path(a.output).write_text(json.dumps(data,indent=2),encoding="utf-8")
    print(json.dumps({"trials":len(data.get("trials",[])),"output":a.output},indent=2))
if __name__=="__main__":
    main()
