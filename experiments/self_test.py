"""Dependency-free regression tests. Run: python experiments/self_test.py"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.evaluation import ConditionEvidence,DiagnosticAction,DecisionEvent,GroundTruthRecord,GrayAreaCondition,Mode,ParticipantTrialRecord,assert_participant_safe,build_assignment,evaluate_trial,validate_condition

def test_three_modes():
    assert [m.value for m in Mode]==["human_only","generic_ai","incidentiq"]

def test_six_conditions():
    assert [c.value for c in GrayAreaCondition]==["clear","ambiguous","conflicting","incomplete","misleading","novel"]

def test_condition_validation():
    c=ConditionEvidence("c1","ambiguous","Two plausible causes.",("a","b"),evidence_refs=())
    assert validate_condition(c).validation_status=="UNVALIDATED"
    c=ConditionEvidence("c1","ambiguous","Two plausible causes.",("a","b"),("metrics",),evidence_refs=("e1",))
    assert validate_condition(c).validation_status=="VALIDATED"

def test_trial_and_separation():
    a=build_assignment("p1","case1","svc",Mode.INCIDENTIQ,"clear",7)
    assert a.mode=="incidentiq"
    assert a.trial_id==build_assignment("p1","case1","svc",Mode.INCIDENTIQ,"clear",7).trial_id
    assert_participant_safe({"case_id":"case1","mode":"human_only"})
    try: assert_participant_safe({"fault":"cpu"})
    except ValueError: pass
    else: raise AssertionError("ground-truth leakage was not detected")

def test_diagnosis_and_actions():
    trial=ParticipantTrialRecord("t1","p1","c1","svc",Mode.HUMAN_ONLY,"now",final_diagnosis="CheckoutService",confidence=80,diagnostic_actions=[DiagnosticAction("a1","inspect"),DiagnosticAction("a2","restart")],decision_events=[DecisionEvent(3.0,"hypothesis",hypothesis="CheckoutService"),DecisionEvent(8.0,"action",action_id="a1")])
    truth=GroundTruthRecord("t1","c1",("checkoutservice",),("a1",),("a2",),())
    r=evaluate_trial(trial,truth)
    assert r.diagnosis_correct is True and r.time_to_correct_hypothesis_s==3.0 and r.time_to_correct_action_s==8.0 and r.unnecessary_action_count==1

def test_ai_reliance():
    trial=ParticipantTrialRecord("t2","p1","c1","svc",Mode.GENERIC_AI,"now",ai_recommendations=["good","bad"],actions_followed=["good","bad"])
    truth=GroundTruthRecord("t2","c1",("x",),("good",),(),("bad",))
    r=evaluate_trial(trial,truth)
    assert r.ai_following_rate==1.0 and r.incorrect_ai_following_count==1 and r.correct_ai_following_count==1

def run():
    tests=[test_three_modes,test_six_conditions,test_condition_validation,test_trial_and_separation,test_diagnosis_and_actions,test_ai_reliance]
    for t in tests: t()
    print(f"{len(tests)} tests passed")

if __name__=="__main__": run()
