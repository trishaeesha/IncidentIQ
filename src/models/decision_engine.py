"""Decision-support layer for hypothesis comparison and next diagnostic action."""

from __future__ import annotations

from typing import Any


class DecisionEngine:
    """Turn deterministic hypothesis results into a human-controlled decision aid."""

    MIN_SELECTION_CONFIDENCE = 0.55

    def decide(self, inference: dict[str, Any]) -> dict[str, Any]:
        hypotheses = inference.get("hypotheses", [])
        status = inference.get("status", "insufficient_evidence")

        if not hypotheses:
            return {
                "case_id": inference.get("case_id"),
                "decision": "Insufficient evidence.",
                "selected_hypothesis": None,
                "recommended_action": None,
                "human_control_required": True,
                "selected_primary_service": None,
                "rationale": inference.get("notes", ["No candidate hypotheses were generated."]),
            }

        ordered = sorted(
            hypotheses,
            key=lambda h: (
                float(h.get("confidence", 0.0)),
                len(h.get("supporting_evidence", [])),
                -len(h.get("contradicting_evidence", [])),
                str(h.get("hypothesis", "")),
            ),
            reverse=True,
        )

        top = ordered[0]
        top_confidence = float(top.get("confidence", 0.0))
        tied = len(ordered) > 1 and abs(
            top_confidence - float(ordered[1].get("confidence", 0.0))
        ) < 0.05

        if (
            status == "unable_to_distinguish"
            or tied
            or top_confidence < self.MIN_SELECTION_CONFIDENCE
            or str(top.get("uncertainty", "")).lower() == "high"
        ):
            action = self._choose_discriminating_action(ordered)
            return {
                "case_id": inference.get("case_id"),
                "decision": "Unable to justify selecting one explanation from current evidence.",
                "selected_hypothesis": None,
                "selected_primary_service": None,
                "competing_hypotheses": [h.get("hypothesis") for h in ordered],
                "recommended_action": action,
                "human_control_required": True,
                "rationale": (
                    "The current evidence does not meet the baseline selection threshold; "
                    "the system recommends further verification rather than presenting a "
                    "weak hypothesis as the diagnosis."
                ),
            }

        return {
            "case_id": inference.get("case_id"),
            "decision": "Candidate hypothesis with comparatively stronger current support.",
            "selected_hypothesis": top.get("hypothesis"),
            "selected_primary_service": top.get("primary_service"),
            "competing_hypotheses": [h.get("hypothesis") for h in ordered[1:]],
            "recommended_action": top.get("next_diagnostic_action"),
            "human_control_required": True,
            "rationale": (
                "Selection is based on deterministic evidence support and contradiction counts; "
                "it is not a causal or calibrated probability judgment."
            ),
        }

    @staticmethod
    def _choose_discriminating_action(hypotheses: list[dict[str, Any]]) -> str | None:
        for hypothesis in hypotheses:
            for check in hypothesis.get("discriminating_checks", []):
                if check.get("check"):
                    return check["check"]
        return None
