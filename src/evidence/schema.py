"""Evidence record types used by the IncidentIQ evidence engine."""

from dataclasses import dataclass, asdict
from typing import Any, Literal

EvidenceClassification = Literal["supporting", "contradictory", "missing"] | None

@dataclass(frozen=True)
class EvidenceRecord:
    case_id: str
    evidence_source: str
    observation: str
    direction_change: str | None
    magnitude: float | None
    time_context: dict[str, Any]
    affected_service_component: str | None
    evidence_strength: str
    classification: EvidenceClassification
    explanation: str
    raw_measurements: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
