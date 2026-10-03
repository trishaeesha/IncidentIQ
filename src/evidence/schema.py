"""Common observation-only evidence representation for IncidentIQ."""

from dataclasses import asdict, dataclass
from typing import Any, Literal

EvidenceRelation = Literal["supporting", "contradictory", "missing"] | None


@dataclass(frozen=True)
class EvidenceRecord:
    """A deterministic telemetry observation.

    classification is retained as a backwards-compatible field name, but it
    is always None during raw evidence extraction. Hypothesis-specific
    interpretation belongs to a later layer.
    """

    case_id: str
    evidence_source: str
    observation: str
    direction_change: str | None
    magnitude: float | None
    time_context: dict[str, Any]
    affected_service_component: str | None
    evidence_strength: str
    classification: EvidenceRelation
    explanation: str
    raw_measurements: dict[str, Any]
    availability: str = "available"

    @property
    def source(self) -> str:
        return self.evidence_source

    @property
    def service(self) -> str | None:
        return self.affected_service_component

    @property
    def relation(self) -> None:
        return None

    def to_dict(self) -> dict[str, Any]:
        """Return the unified observation schema."""
        raw = dict(self.raw_measurements)
        return {
            "case_id": self.case_id,
            "source": self.evidence_source,
            "service": self.affected_service_component,
            "observation": self.observation,
            "direction": self.direction_change,
            "magnitude": self.magnitude,
            "time_context": self.time_context,
            "evidence_strength": self.evidence_strength,
            "relation": None,
            "availability": self.availability,
            **{
                key: raw[key]
                for key in (
                    "signal",
                    "baseline_quality",
                    "before",
                    "after",
                    "absolute_change",
                    "relative_change",
                    "sample_count",
                    "operation",
                )
                if key in raw
            },
        }
