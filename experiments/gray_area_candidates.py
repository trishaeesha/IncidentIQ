"""Candidate gray-area condition records for researcher validation.

These are hypotheses about incident difficulty, not labels inferred from RCAEval
metadata. They remain UNVALIDATED until a researcher verifies the cited telemetry.
"""
from src.evaluation.schemas import ConditionEvidence
from src.evaluation.conditions import validate_condition

CANDIDATES = [
    ConditionEvidence(
        case_id="re2ob_checkoutservice_cpu_2",
        condition="clear",
        condition_rationale="A dominant service-local CPU signal is temporally aligned with the injected failure.",
        candidate_hypotheses=("resource saturation",),
        evidence_characteristics=("checkoutservice CPU change after injection",),
        evidence_refs=("metrics:checkoutservice:cpu",),
    ),
    ConditionEvidence(
        case_id="re2ob_checkoutservice_mem_2",
        condition="ambiguous",
        condition_rationale="Resource pressure and error-like log behavior provide competing explanatory signals.",
        candidate_hypotheses=("resource saturation","error or failure increase"),
        evidence_characteristics=("resource change","error-like log frequency change"),
        evidence_refs=("metrics:checkoutservice:memory","logs:error_like"),
    ),
    ConditionEvidence(
        case_id="re2ss_user_loss_1",
        condition="incomplete",
        condition_rationale="The Sock Shop case lacks trace telemetry, limiting cross-service request-path evidence.",
        required_evidence=("distributed request traces",),
        missing_evidence=("distributed request traces",),
        evidence_refs=("manifest:has_traces=false",),
    ),
]

def validated_candidates():
    return [validate_condition(x) for x in CANDIDATES]
