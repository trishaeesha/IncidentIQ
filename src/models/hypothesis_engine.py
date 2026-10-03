"""Deterministic hypothesis generation and evidence-to-hypothesis evaluation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from .schemas import HypothesisResult


class HypothesisEngine:
    """Generate a small, interpretable set of hypotheses from structured evidence.

    The engine consumes observations only. It never accepts RCAEval answer fields.
    Scores are heuristic support scores, not calibrated probabilities.
    """

    _MAX_HYPOTHESES = 3

    _RULES = (
        {
            "name": "resource saturation",
            "description": "The affected service may be constrained by a resource such as CPU, memory, disk, or network capacity.",
            "terms": ("cpu", "memory", "mem", "disk", "network", "throttle", "utilization", "saturation"),
            "expected": ("high", "increase", "elevated", "throttling", "sustained"),
            "check": "Inspect resource utilization and throttling for the affected service during the incident window.",
            "supported": "Sustained high utilization or throttling is observed.",
            "unsupported": "Resource utilization remains normal while the incident persists.",
        },
        {
            "name": "increased request load",
            "description": "The incident may be associated with an increase in incoming request volume or throughput.",
            "terms": ("request", "throughput", "traffic", "rps", "qps", "rate", "volume"),
            "expected": ("increase", "elevated", "high", "spike"),
            "check": "Compare request rate/throughput before and during the incident for the affected service.",
            "supported": "Request volume is elevated in the incident window.",
            "unsupported": "Request volume is unchanged or lower.",
        },
        {
            "name": "dependency latency or downstream degradation",
            "description": "A dependency or downstream service may be contributing elevated latency or failures.",
            "terms": ("latency", "duration", "downstream", "dependency", "upstream", "span", "rpc", "call"),
            "expected": ("increase", "elevated", "high", "error"),
            "check": "Inspect downstream calls and their latency/error rates for the affected request path.",
            "supported": "A downstream call shows elevated latency or errors in the incident window.",
            "unsupported": "Relevant downstream calls remain normal.",
        },
        {
            "name": "error propagation",
            "description": "Errors observed across logs or traces may indicate propagation through the request path.",
            "terms": ("error", "exception", "failure", "failed", "5xx", "statuscode", "warning"),
            "expected": ("increase", "elevated", "high", "spike"),
            "check": "Trace the first temporally concentrated error across services and compare upstream/downstream error rates.",
            "supported": "Error activity increases in a temporally related service or request path.",
            "unsupported": "Relevant error rates remain normal.",
        },
    )

    _STRONG = {"strong"}
    _MODERATE = {"moderate", "medium"}
    _WEAK = {"weak", "low"}

    def infer(self, evidence: Iterable[dict[str, Any]], case_id: str | None = None) -> dict[str, Any]:
        rows = [self._validate_observation(row) for row in evidence]
        if case_id is None and rows:
            case_id = rows[0].get("case_id")

        if not rows:
            return self._empty_result(case_id, "No investigator-visible evidence was supplied.")

        candidates = []
        for rule in self._RULES:
            result = self._evaluate_rule(rule, rows)
            if result is not None:
                candidates.append(result)

        candidates.sort(
            key=lambda h: (
                self._support_value(h),
                -len(h.contradicting_evidence),
                h.hypothesis,
            ),
            reverse=True,
        )
        candidates = candidates[: self._MAX_HYPOTHESES]

        if not candidates:
            return self._empty_result(
                case_id,
                "Observed telemetry does not match a baseline hypothesis rule; insufficient evidence.",
            )

        self._add_competition_aware_actions(candidates)
        distinguishable = len(candidates) == 1 or self._support_margin(candidates) >= 0.20
        status = "hypotheses_available" if distinguishable else "unable_to_distinguish"

        return {
            "case_id": case_id,
            "status": status,
            "decision": (
                "Candidate explanation has comparatively stronger evidence."
                if distinguishable
                else "Unable to distinguish between competing hypotheses from current evidence."
            ),
            "hypotheses": [h.to_dict() for h in candidates],
            "notes": [
                "Confidence is a deterministic heuristic, not a calibrated probability.",
                "Temporal association is not treated as causal proof.",
            ],
        }

    def update(
        self,
        prior: dict[str, Any],
        new_evidence: Iterable[dict[str, Any]],
    ) -> dict[str, Any]:
        """Recompute the hypothesis set from prior-visible evidence plus new evidence.

        This is intentionally recomputational rather than stateful: it avoids hidden
        memory and makes updates reproducible from the complete investigator-visible record.
        """
        prior_rows = prior.get("_evidence_snapshot", []) if isinstance(prior, dict) else []
        combined = list(prior_rows) + list(new_evidence)
        result = self.infer(combined, case_id=prior.get("case_id") if isinstance(prior, dict) else None)
        result["_evidence_snapshot"] = combined
        return result

    @staticmethod
    def _validate_observation(row: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(row, dict):
            raise TypeError("Each evidence item must be a dictionary.")
        forbidden = {"root_cause_service", "fault", "fault_description", "ground_truth", "labels"}
        if forbidden.intersection(row):
            raise ValueError("Ground-truth fields are not accepted by the inference path.")
        required = {"source", "observation"}
        missing = required.difference(row)
        if missing:
            raise ValueError(f"Evidence item missing required fields: {sorted(missing)}")
        return dict(row)

    def _evaluate_rule(self, rule: dict[str, Any], rows: list[dict[str, Any]]) -> HypothesisResult | None:
        supporting, contradicting, missing, neutral = [], [], [], []
        services = defaultdict(float)

        relevant_available = 0
        for row in rows:
            text = " ".join(
                str(row.get(k, "")).lower()
                for k in ("source", "signal", "observation", "service", "direction")
            )
            matched = any(term in text for term in rule["terms"])
            if not matched:
                neutral.append(self._ref(row))
                continue

            availability = str(row.get("availability", "available")).lower()
            if availability in {"missing", "unavailable", "not_available", "absent"}:
                missing.append(self._ref(row))
                continue

            relevant_available += 1
            direction = str(row.get("direction", "")).lower()
            observation = str(row.get("observation", "")).lower()
            expected = any(token in direction or token in observation for token in rule["expected"])
            strength = str(row.get("evidence_strength", "")).lower()

            if expected and strength not in {"contradictory", "negative"}:
                supporting.append(self._ref(row))
                services[str(row.get("service") or "unknown")] += self._strength_value(strength)
            elif strength in {"strong", "moderate", "medium"} or "normal" in observation or "unchanged" in observation:
                contradicting.append(self._ref(row))
            else:
                neutral.append(self._ref(row))

        if not supporting and not missing and not contradicting:
            return None

        support = sum(self._strength_value(x["strength"]) for x in supporting)
        contradiction = sum(self._strength_value(x["strength"]) for x in contradicting)
        confidence = max(0.0, min(1.0, 0.25 + 0.15 * support - 0.20 * contradiction))
        uncertainty_reasons = []

        if missing:
            uncertainty_reasons.append("Relevant telemetry is unavailable.")
        if contradicting:
            uncertainty_reasons.append("Some observations conflict with the expected pattern.")
        if not supporting:
            uncertainty_reasons.append("No direct supporting observation is available.")
        if supporting and len(supporting) == 1:
            uncertainty_reasons.append("Support relies on a single observation.")

        if not uncertainty_reasons:
            uncertainty = "low"
        elif contradiction or missing:
            uncertainty = "high"
        else:
            uncertainty = "moderate"

        primary_service = max(services, key=services.get) if services else None
        return HypothesisResult(
            hypothesis=rule["name"],
            primary_service=primary_service,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            missing_evidence=missing,
            neutral_evidence=neutral,
            uncertainty=uncertainty,
            uncertainty_reasons=uncertainty_reasons,
            confidence=round(confidence, 3),
            discriminating_checks=[{
                "check": rule["check"],
                "expected_if_supported": rule["supported"],
                "expected_if_unsupported": rule["unsupported"],
            }],
            next_diagnostic_action=rule["check"],
        )

    @staticmethod
    def _ref(row: dict[str, Any]) -> dict[str, Any]:
        return {
            k: row.get(k)
            for k in (
                "source", "service", "observation", "direction",
                "magnitude", "time_context", "evidence_strength",
                "availability",
            )
            if k in row
        }

    @classmethod
    def _strength_value(cls, strength: str) -> float:
        if strength in cls._STRONG:
            return 1.0
        if strength in cls._MODERATE:
            return 0.7
        if strength in cls._WEAK:
            return 0.4
        return 0.5

    @staticmethod
    def _support_value(h: HypothesisResult) -> float:
        return sum(
            1.0 if x.get("strength") == "strong" else 0.7 if x.get("strength") in {"moderate", "medium"} else 0.4
            for x in h.supporting_evidence
        )

    @staticmethod
    def _support_margin(hypotheses: list[HypothesisResult]) -> float:
        if len(hypotheses) < 2:
            return 1.0
        vals = sorted((HypothesisEngine._support_value(h) for h in hypotheses), reverse=True)
        return vals[0] - vals[1]

    @staticmethod
    def _add_competition_aware_actions(hypotheses: list[HypothesisResult]) -> None:
        if len(hypotheses) < 2:
            return
        for h in hypotheses:
            h.discriminating_checks.append({
                "check": f"Compare this explanation against: {', '.join(x.hypothesis for x in hypotheses if x is not h)}.",
                "purpose": "Seek an observation that would separate the competing explanations.",
            })

    @staticmethod
    def _empty_result(case_id: str | None, reason: str) -> dict[str, Any]:
        return {
            "case_id": case_id,
            "status": "insufficient_evidence",
            "decision": "Insufficient evidence.",
            "hypotheses": [],
            "notes": [reason],
        }


def infer_hypotheses(evidence: Iterable[dict[str, Any]], case_id: str | None = None) -> dict[str, Any]:
    """Functional entry point for callers that do not need an engine instance."""
    return HypothesisEngine().infer(evidence, case_id=case_id)
