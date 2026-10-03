"""Adapters from IncidentIQ pipeline outputs to evaluator-safe records.

The evaluator consumes outputs from the existing Evidence, Hypothesis, and
Decision layers without modifying those layers. Ground truth remains outside
this adapter and is never passed into the system under test.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .experiment import assert_participant_safe


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def incidentiq_recommendations(
    hypothesis_output: Mapping[str, Any],
    decision_output: Mapping[str, Any],
) -> list[str]:
    """Extract only recommendations visible to a participant."""
    recommendations: list[str] = []

    selected = decision_output.get("selected_hypothesis")
    if selected:
        recommendations.append(str(selected))

    action = decision_output.get("recommended_action")
    if action:
        recommendations.append(str(action))

    if not selected and not action:
        for hypothesis in hypothesis_output.get("hypotheses", []):
            next_action = hypothesis.get("next_diagnostic_action")
            if next_action:
                recommendations.append(str(next_action))

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(recommendations))


def build_incidentiq_trial_payload(
    *,
    trial_id: str,
    participant_id: str,
    case_id: str,
    system: str,
    mode: str,
    start_time: str,
    hypothesis_output: Mapping[str, Any],
    decision_output: Mapping[str, Any],
) -> dict[str, Any]:
    """Create an evaluator input payload from real IncidentIQ outputs.

    This intentionally excludes condition labels, condition rationale, and all
    RCAEval ground-truth fields. The evaluator may retain the original
    hypothesis output separately for audit, but it is not participant truth.
    """
    recommendations = incidentiq_recommendations(hypothesis_output, decision_output)
    payload = {
        "trial_id": trial_id,
        "participant_id": participant_id,
        "case_id": case_id,
        "system": system,
        "mode": mode,
        "start_time": start_time,
        "ai_recommendations": recommendations,
    }
    assert_participant_safe(payload)
    return payload


def build_generic_ai_record(
    *,
    trial_id: str,
    model: str,
    model_version: str | None,
    prompt: str,
    input_evidence: list[dict[str, Any]],
    output: str,
    recommendations: list[str],
    temperature: float | None,
    settings: Mapping[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Record a reproducible generic-AI interaction.

    The caller is responsible for supplying exactly the evidence available to
    the participant. No IncidentIQ structured interpretation is accepted here.
    """
    record = {
        "trial_id": trial_id,
        "model": model,
        "model_version": model_version,
        "prompt": prompt,
        "input_evidence": input_evidence,
        "output": output,
        "recommendations": recommendations,
        "temperature": temperature,
        "settings": dict(settings or {}),
        "timestamp": timestamp or utc_timestamp(),
    }
    assert_participant_safe(record)
    return record
