"""Deterministic hypothesis generation and decision support for IncidentIQ."""

from __future__ import annotations

from typing import Any

from .contextual_relation import relate


class HypothesisEngine:
    """Interpret structured evidence into competing diagnostic hypotheses."""

    GROUND_TRUTH_FIELDS = {
        "root_cause_service",
        "fault",
        "fault_description",
        "ground_truth",
        "ground_truth_label",
    }

    RULES = [
        {
            "name": "resource saturation",
            "expected": (
                "cpu",
                "memory",
                "resource",
                "utilization",
                "saturation",
            ),
            "service": True,
            "check": (
                "Check CPU and memory utilization for the affected "
                "service during the incident window."
            ),
        },
        {
            "name": "increased request load",
            "expected": (
                "request_rate",
                "throughput",
                "traffic",
                "request rate",
                "requests increased",
            ),
            "service": True,
            "check": (
                "Check request rate and throughput for the affected "
                "service during the incident window."
            ),
        },
        {
            "name": "downstream latency",
            "expected": (
                "downstream",
                "dependency",
                "span latency",
            ),
            "service": True,
            "check": (
                "Inspect downstream dependency latency and trace spans "
                "for the affected service."
            ),
        },
        {
            "name": "error or failure increase",
            "expected": (
                "error",
                "errors",
                "failure",
                "failures",
                "error_rate",
                "status 5",
            ),
            "service": True,
            "check": (
                "Check error and failure rates for the affected service "
                "during the incident window."
            ),
        },
        {
            "name": "database or storage pressure",
            "expected": (
                "database",
                "db",
                "query latency",
                "disk",
                "storage",
                "queue depth",
                "connection pool",
            ),
            "service": True,
            "check": (
                "Inspect database, storage, queue-depth, and connection "
                "pool telemetry for the affected service."
            ),
        },
        {
            "name": "network or communication issue",
            "expected": (
                "network",
                "connection",
                "timeout",
                "packet",
                "communication",
                "unreachable",
            ),
            "service": True,
            "check": (
                "Check network connectivity, timeout signals, and "
                "communication errors between affected components."
            ),
        },
    ]

    CONTRADICTORY_WORDS = (
        "decrease",
        "decreased",
        "decreasing",
        "reduced",
        "reduction",
        "lower",
        "lowered",
        "normal",
        "stable",
        "unchanged",
        "not elevated",
        "remains normal",
        "remained normal",
        "no anomaly",
        "no relevant anomaly",
    )

    def infer(self, evidence_rows: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate deterministic competing hypotheses from observations."""

        self._validate_no_ground_truth_leakage(evidence_rows)

        rows = [dict(row) for row in evidence_rows]

        if not rows:
            return {
                "case_id": None,
                "status": "insufficient_evidence",
                "hypotheses": [],
                "decision": "Insufficient evidence.",
                "notes": ["No structured evidence was provided."],
            }

        case_ids = {
            row.get("case_id")
            for row in rows
            if row.get("case_id") is not None
        }

        case_id = next(iter(sorted(case_ids)), None)

        candidates: list[dict[str, Any]] = []

        for rule in self.RULES:
            supporting: list[dict[str, Any]] = []
            contradicting: list[dict[str, Any]] = []
            missing: list[dict[str, Any]] = []
            neutral: list[dict[str, Any]] = []

            services: list[str] = []

            for row in rows:
                availability = str(
                    row.get("availability", "available")
                ).lower()

                observation = str(
                    row.get("observation", "")
                ).lower()

                direction = str(
                    row.get("direction", "")
                ).lower()

                signal = str(
                    row.get("signal", "")
                ).lower()

                source = str(
                    row.get("source", "")
                ).lower()

                combined_text = " ".join(
                    [
                        observation,
                        direction,
                        signal,
                        source,
                    ]
                )

                expected = any(
                    token.lower() in combined_text
                    for token in rule["expected"]
                )
                if not expected and relate(row, rule["name"]) == "supporting":
                    expected = True

                unavailable = availability in {
                    "missing",
                    "unavailable",
                    "not_available",
                    "absent",
                }

                if unavailable:
                    if expected or self._is_missing_relevant_telemetry(
                        observation,
                        signal,
                        source,
                    ):
                        missing.append(self._ref(row))
                    continue

                is_contradictory = self._is_contradictory(
                    direction,
                    observation,
                )

                if is_contradictory and expected:
                    contradicting.append(self._ref(row))
                    continue

                if expected:
                    strength = str(
                        row.get(
                            "evidence_strength",
                            row.get("strength", "weak"),
                        )
                    ).lower()

                    if strength not in {
                        "contradictory",
                        "negative",
                    }:
                        supporting.append(self._ref(row))

                        service = str(
                            row.get("service", "")
                        ).strip()

                        if service:
                            services.append(service)

                    else:
                        neutral.append(self._ref(row))

                elif self._is_relevant_neutral_evidence(
                    row,
                    rule,
                ):
                    neutral.append(self._ref(row))

            if not supporting and not contradicting and not missing:
                continue

            primary_service = self._choose_service(
                services,
                rows,
            )

            # Evidence from unrelated services must not contradict a
            # service-specific hypothesis. Otherwise a global incident
            # symptom can drown out the signal at the candidate service.
            if primary_service:
                supporting = [
                    item for item in supporting
                    if item.get("service") in {None, primary_service}
                ]
                contradicting = [
                    item for item in contradicting
                    if item.get("service") in {None, primary_service}
                ]
                neutral = [
                    item for item in neutral
                    if item.get("service") in {None, primary_service}
                ]

            uncertainty, uncertainty_reasons = (
                self._calculate_uncertainty(
                    supporting,
                    contradicting,
                    missing,
                    neutral,
                )
            )

            confidence = self._calculate_confidence(
                supporting,
                contradicting,
                missing,
                neutral,
            )

            rationale = self._build_rationale(
                rule["name"],
                supporting,
                contradicting,
                missing,
                neutral,
                uncertainty,
            )

            candidate = {
                "hypothesis": rule["name"],
                "primary_service": primary_service,
                "supporting_evidence": supporting,
                "contradicting_evidence": contradicting,
                "missing_evidence": missing,
                "neutral_evidence": neutral,
                "uncertainty": uncertainty,
                "uncertainty_reasons": uncertainty_reasons,
                "confidence": confidence,
                "discriminating_checks": [
                    {
                        "check": rule["check"],
                        "reason": (
                            "This check can provide evidence that "
                            "distinguishes the hypothesis from alternatives."
                        ),
                    }
                ],
                "next_diagnostic_action": rule["check"],
                "rationale": rationale,
            }

            candidates.append(candidate)

        candidates.sort(
            key=lambda item: (
                -float(item.get("confidence", 0.0)),
                item.get("hypothesis", ""),
            )
        )

        if not candidates:
            return {
                "case_id": case_id,
                "status": "insufficient_evidence",
                "hypotheses": [],
                "decision": "Insufficient evidence.",
                "notes": [
                    "Available observations did not match a supported "
                    "diagnostic hypothesis."
                ],
            }

        if all(
            h["uncertainty"] == "insufficient_evidence"
            for h in candidates
        ):
            status = "insufficient_evidence"
        elif len(candidates) == 1:
            status = "hypotheses_available"
        else:
            top_score = float(candidates[0].get("confidence", 0.0))
            second_score = float(candidates[1].get("confidence", 0.0))
            margin = top_score - second_score
            if candidates[0].get("uncertainty") == "high" or margin < 0.15:
                status = "unable_to_distinguish"
            else:
                status = "hypotheses_available"

        decision = self._build_decision(
            candidates,
            status,
        )

        return {
            "case_id": case_id,
            "status": status,
            "hypotheses": candidates,
            "decision": decision,
            "notes": self._build_notes(
                candidates,
                status,
            ),
        }

    def update(
        self,
        previous_result: dict[str, Any],
        new_evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Update hypotheses using previous evidence plus new observations."""

        self._validate_no_ground_truth_leakage(new_evidence)

        previous_snapshot = previous_result.get(
            "_evidence_snapshot",
            [],
        )

        combined = [
            dict(row)
            for row in previous_snapshot
        ]

        combined.extend(
            dict(row)
            for row in new_evidence
        )

        updated = self.infer(combined)

        updated["_evidence_snapshot"] = combined

        return updated

    @classmethod
    def _validate_no_ground_truth_leakage(
        cls,
        evidence_rows: list[dict[str, Any]],
    ) -> None:
        """Reject evaluator-only ground-truth fields."""

        for index, row in enumerate(evidence_rows):
            forbidden = cls.GROUND_TRUTH_FIELDS.intersection(
                row.keys()
            )

            if forbidden:
                fields = ", ".join(sorted(forbidden))
                raise ValueError(
                    "Ground-truth fields are not allowed in "
                    f"HypothesisEngine input at row {index}: {fields}"
                )

    @classmethod
    def _is_contradictory(
        cls,
        direction: str,
        observation: str,
    ) -> bool:
        """Detect observations that oppose an expected increase."""

        direction = direction.lower().strip()
        observation = observation.lower().strip()

        negative_directions = {
            "decrease",
            "decreased",
            "decreasing",
            "reduced",
            "reduction",
            "lower",
            "lowered",
            "normal",
            "stable",
            "unchanged",
        }

        if direction in negative_directions:
            return True

        return any(
            phrase in observation
            for phrase in cls.CONTRADICTORY_WORDS
        )

    @staticmethod
    def _is_missing_relevant_telemetry(
        observation: str,
        signal: str,
        source: str,
    ) -> bool:
        """Detect explicitly unavailable telemetry that is relevant."""

        text = " ".join(
            [
                observation.lower(),
                signal.lower(),
                source.lower(),
            ]
        )

        telemetry_terms = (
            "trace",
            "traces",
            "metric",
            "metrics",
            "log",
            "logs",
            "telemetry",
            "latency",
            "dependency",
            "request",
            "error",
            "cpu",
            "memory",
        )

        return any(
            term in text
            for term in telemetry_terms
        )

    @staticmethod
    def _is_relevant_neutral_evidence(
        row: dict[str, Any],
        rule: dict[str, Any],
    ) -> bool:
        """Identify relevant observations that do not support or contradict."""

        observation = str(
            row.get("observation", "")
        ).lower()

        signal = str(
            row.get("signal", "")
        ).lower()

        source = str(
            row.get("source", "")
        ).lower()

        text = " ".join(
            [
                observation,
                signal,
                source,
            ]
        )

        relevant = any(
            token.lower() in text
            for token in rule["expected"]
        )

        if relevant:
            return False

        neutral_terms = (
            "disk",
            "queue",
            "network",
            "database",
            "storage",
            "connection",
            "trace",
            "latency",
        )

        return any(
            term in text
            for term in neutral_terms
        )

    @staticmethod
    def _ref(
        row: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a stable evidence reference."""

        return {
            "evidence_id": row.get("evidence_id"),
            "source": row.get("source"),
            "service": row.get("service"),
            "observation": row.get("observation"),
            "direction": row.get("direction"),
            "magnitude": row.get("magnitude"),
            "time_context": row.get("time_context"),
            "evidence_strength": row.get(
                "evidence_strength",
                row.get("strength", "weak"),
            ),
            "availability": row.get(
                "availability",
                "available",
            ),
        }

    @staticmethod
    def _choose_service(
        services: list[str],
        rows: list[dict[str, Any]],
    ) -> str | None:
        """Choose a deterministic primary service."""

        if services:
            counts: dict[str, int] = {}

            for service in services:
                counts[service] = counts.get(service, 0) + 1

            return sorted(
                counts,
                key=lambda service: (
                    -counts[service],
                    service,
                ),
            )[0]

        row_services = sorted(
            {
                str(row.get("service", "")).strip()
                for row in rows
                if str(row.get("service", "")).strip()
            }
        )

        return row_services[0] if row_services else None

    @staticmethod
    def _calculate_uncertainty(
        supporting: list[dict[str, Any]],
        contradicting: list[dict[str, Any]],
        missing: list[dict[str, Any]],
        neutral: list[dict[str, Any]],
    ) -> tuple[str, list[str]]:
        """Assign transparent qualitative uncertainty."""

        reasons: list[str] = []

        if not supporting and not contradicting:
            if missing:
                reasons.append(
                    "Relevant telemetry is unavailable."
                )
                return "insufficient_evidence", reasons

            reasons.append(
                "No directly relevant supporting or contradicting evidence."
            )
            return "insufficient_evidence", reasons

        if contradicting:
            reasons.append(
                "At least one relevant observation contradicts the hypothesis."
            )

        if missing:
            reasons.append(
                "Some relevant telemetry is unavailable."
            )

        if supporting:
            strong_count = sum(
                1
                for item in supporting
                if str(
                    item.get("evidence_strength", "")
                ).lower()
                == "strong"
            )

            if strong_count:
                reasons.append(
                    "Relevant supporting evidence includes strong observations."
                )
            else:
                reasons.append(
                    "Supporting evidence is present but may require confirmation."
                )

        if contradicting and supporting:
            return "high", reasons

        if missing and supporting:
            return "high", reasons

        if supporting:
            return "low", reasons

        return "high", reasons

    @staticmethod
    def _calculate_confidence(
        supporting: list[dict[str, Any]],
        contradicting: list[dict[str, Any]],
        missing: list[dict[str, Any]],
        neutral: list[dict[str, Any]],
    ) -> float:
        """Return a deterministic relative support score, not a probability."""

        if not supporting:
            return 0.0

        strength_values = {
            "strong": 1.0,
            "moderate": 0.7,
            "weak": 0.4,
        }

        support_score = sum(
            strength_values.get(
                str(
                    item.get("evidence_strength", "weak")
                ).lower(),
                0.4,
            )
            for item in supporting
        )

        contradiction_penalty = 0.5 * len(
            contradicting
        )

        missing_penalty = 0.15 * len(
            missing
        )

        score = (
            support_score
            - contradiction_penalty
            - missing_penalty
        )

        return round(
            max(0.0, min(1.0, score)),
            3,
        )

    @staticmethod
    def _build_rationale(
        hypothesis: str,
        supporting: list[dict[str, Any]],
        contradicting: list[dict[str, Any]],
        missing: list[dict[str, Any]],
        neutral: list[dict[str, Any]],
        uncertainty: str,
    ) -> str:
        """Create a transparent explanation for the hypothesis."""

        parts = [
            f"Hypothesis: {hypothesis}.",
        ]

        if supporting:
            parts.append(
                f"{len(supporting)} observation(s) support the hypothesis."
            )

        if contradicting:
            parts.append(
                f"{len(contradicting)} observation(s) contradict the hypothesis."
            )

        if missing:
            parts.append(
                f"{len(missing)} relevant observation(s) are unavailable."
            )

        if neutral:
            parts.append(
                f"{len(neutral)} observation(s) are relevant but neutral."
            )

        parts.append(
            f"Current uncertainty is {uncertainty}."
        )

        parts.append(
            "Temporal association is treated as evidence context, "
            "not as proof of causality."
        )

        return " ".join(parts)

    @staticmethod
    def _build_decision(
        hypotheses: list[dict[str, Any]],
        status: str,
    ) -> str:
        """Create a human-controlled decision-support statement."""

        if status == "insufficient_evidence":
            return "Insufficient evidence."

        if status == "unable_to_distinguish":
            return (
                "Unable to distinguish between competing hypotheses."
            )

        top = hypotheses[0]

        if top["uncertainty"] in {
            "high",
            "insufficient_evidence",
        }:
            return (
                "Current evidence does not justify selecting one "
                "explanation."
            )

        return (
            "Candidate hypothesis with comparatively stronger "
            "current support."
        )

    @staticmethod
    def _build_notes(
        hypotheses: list[dict[str, Any]],
        status: str,
    ) -> list[str]:
        """Create deterministic notes for downstream evaluation."""

        notes: list[str] = []

        if status == "insufficient_evidence":
            notes.append(
                "The engine abstains because available evidence is insufficient."
            )

        elif status == "unable_to_distinguish":
            notes.append(
                "Multiple hypotheses remain plausible under the current evidence."
            )

        else:
            notes.append(
                "A candidate hypothesis has comparatively stronger current support."
            )

        notes.append(
            "Hypothesis results are evidence interpretations, not ground-truth labels."
        )

        notes.append(
            "Human review is required before any operational action."
        )

        return notes


def infer_hypotheses(
    evidence_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Convenience wrapper around HypothesisEngine.infer."""

    return HypothesisEngine().infer(evidence_rows)