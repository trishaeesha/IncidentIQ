from experiments.gray_area_candidates import validated_candidates

def test_gray_area_candidates_are_conservatively_validated():
    results = validated_candidates()
    assert len(results) == 3
    assert all(x.validation_status == "VALIDATED" for x in results)
