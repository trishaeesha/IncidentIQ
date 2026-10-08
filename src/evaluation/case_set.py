"""Controlled selection of researcher-validated RCAEval cases.

This module selects only already-validated candidates. It never fabricates
gray-area cases and never treats repeated injections as independent conceptual
incidents unless the researcher explicitly supplies a distinct conceptual group.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ValidatedCase:
    case_id: str
    condition: str
    system: str
    fault_type: str
    modality: tuple[str, ...]
    repeat_group: str
    validation_status: str
    service_key: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "condition": self.condition,
            "system": self.system,
            "fault_type": self.fault_type,
            "modality": list(self.modality),
            "repeat_group": self.repeat_group,
            "validation_status": self.validation_status,
            "service_key": self.service_key,
        }


def select_validated_cases(
    candidates: Iterable[ValidatedCase],
    *,
    target_min: int = 60,
    target_max: int = 90,
) -> list[ValidatedCase]:
    """Select at most one case per repeat group by default.

    Candidates must already be marked VALIDATED. The function does not balance
    conditions by inventing or relabeling cases. Within a condition it uses
    deterministic lexical ordering, so a later researcher can replace the
    policy with a preregistered sampling rule without hidden randomness.
    """
    if target_min < 0 or target_max < target_min:
        raise ValueError("Invalid target range.")

    usable = [
        c for c in candidates
        if c.validation_status == "VALIDATED"
        and c.case_id
        and c.condition
        and c.repeat_group
    ]
    usable.sort(key=lambda c: (c.condition, c.system, c.fault_type, c.repeat_group, c.case_id))

    selected: list[ValidatedCase] = []
    seen_groups: set[str] = set()
    for case in usable:
        if case.repeat_group in seen_groups:
            continue
        selected.append(case)
        seen_groups.add(case.repeat_group)
        if len(selected) >= target_max:
            break

    # target_min is a reporting target, not a quota. Returning fewer cases is
    # intentional when the validated evidence pool is smaller.
    return selected


def summarize_case_set(cases: Iterable[ValidatedCase]) -> dict[str, object]:
    selected = list(cases)
    conditions: dict[str, int] = {}
    systems: dict[str, int] = {}
    faults: dict[str, int] = {}
    modalities: dict[str, int] = {}

    for case in selected:
        conditions[case.condition] = conditions.get(case.condition, 0) + 1
        systems[case.system] = systems.get(case.system, 0) + 1
        faults[case.fault_type] = faults.get(case.fault_type, 0) + 1
        for modality in case.modality:
            modalities[modality] = modalities.get(modality, 0) + 1

    return {
        "validated_cases": len(selected),
        "condition_distribution": dict(sorted(conditions.items())),
        "systems": dict(sorted(systems.items())),
        "fault_types": dict(sorted(faults.items())),
        "modality_availability": dict(sorted(modalities.items())),
        "repeated_case_policy": "one case per researcher-defined repeat_group by default",
    }


def reject_unvalidated(cases: Iterable[ValidatedCase]) -> None:
    invalid = [c.case_id for c in cases if c.validation_status != "VALIDATED"]
    if invalid:
        raise ValueError(
            "Case set contains unvalidated cases: " + ", ".join(sorted(invalid))
        )
