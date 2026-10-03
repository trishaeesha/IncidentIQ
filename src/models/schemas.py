"""Schemas for deterministic IncidentIQ hypothesis and decision support."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceRef:
    source: str
    service: str | None
    observation: str
    strength: str
    time_context: dict[str, Any] | None = None
    availability: str = "available"
    evidence_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HypothesisResult:
    hypothesis: str
    primary_service: str | None
    supporting_evidence: list[dict[str, Any]] = field(default_factory=list)
    contradicting_evidence: list[dict[str, Any]] = field(default_factory=list)
    missing_evidence: list[dict[str, Any]] = field(default_factory=list)
    neutral_evidence: list[dict[str, Any]] = field(default_factory=list)
    uncertainty: str = "high"
    uncertainty_reasons: list[str] = field(default_factory=list)
    confidence: float = 0.0
    discriminating_checks: list[dict[str, Any]] = field(default_factory=list)
    next_diagnostic_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
