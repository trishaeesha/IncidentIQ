"""Decision-support layer for hypothesis comparison and next diagnostic action."""

from __future__ import annotations

from typing import Any


class DecisionEngine:
    """Turn deterministic hypothesis results into a human-controlled decision aid."""

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
        tied = len(ordered) > 1 and abs(
            float(top.get("confidence", 0.0)) - float(ordered[1].get("confidence", 0.0))
        ) < 0.05

        if status == "unable_to_distinguish" or tied:
            action = self._choose_discriminating_action(ordered)
            return {
                "case_id": inference.get("case_id"),
                "decision": "Unable to distinguish between competing hypotheses.",
                "selected_hypothesis": None,
                "competing_hypotheses": [h.get("hypothesis") for h in ordered],
                "recommended_action": action,
                "human_control_required": True,
                "rationale": "Current evidence does not justify selecting one explanation.",
            }

        return {
            "case_id": inference.get("case_id"),
            "decision": "Candidate hypothesis with comparatively stronger current support.",
            "selected_hypothesis": top.get("hypothesis"),
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
            checks = hypothesis.get("discriminating_checks", [])
            for check in checks:
                if check.get("check"):
                    return check["check"]
        return None
