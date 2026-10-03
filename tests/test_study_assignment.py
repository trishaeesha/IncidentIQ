from experiments.study_assignment import build_study_assignments
from experiments.gray_area_candidates import CANDIDATES

def test_study_assignment_is_reproducible_and_balanced():
    a = build_study_assignments("pilot-001", [(x.case_id, x) for x in CANDIDATES], seed=42)
    b = build_study_assignments("pilot-001", [(x.case_id, x) for x in CANDIDATES], seed=42)
    assert a == b
    assert len({x["trial_id"] for x in a}) == len(a)
    assert {x["mode"] for x in a}.issubset({"human_only","generic_ai","incidentiq"})
