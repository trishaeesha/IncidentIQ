"""Build participant-safe gray-area trial specifications.

The generator never changes evaluator truth. It creates a presentation plan for
controlled evidence conditions; researchers must validate each transformed case
before participant use.
"""
from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass(frozen=True)
class TrialSpec:
    case_id: str
    condition: str
    mode: str
    transformations: tuple[str,...]
    participant_notes: str

CASES=("re2ob_checkoutservice_cpu_2","re2ob_checkoutservice_mem_2")
MODES=("human_only","generic_ai","incidentiq")
CONDITIONS=("clear","ambiguous","conflicting","incomplete","misleading","novel")

TRANSFORMS={
 "clear":("full_multimodal_telemetry",),
 "ambiguous":("retain_only_evidence_compatible_with_two_hypotheses",),
 "conflicting":("retain_competing_signals_from_distinct_modalities",),
 "incomplete":("hide_one_available_telemetry_modality",),
 "misleading":("add_high_salience_non_root_distractor_signal",),
 "novel":("remove_high_similarity_historical_match",),
}

def build(case_ids=CASES):
 trials=[]
 for case in case_ids:
  for condition in CONDITIONS:
   for mode in MODES:
    trials.append(TrialSpec(
      case_id=case,condition=condition,mode=mode,
      transformations=TRANSFORMS[condition],
      participant_notes="Condition label and evaluator rationale must never be shown to participants."
    ))
 return trials

if __name__=="__main__":
 out=Path("outputs/gray_area_trial_specs.json")
 out.parent.mkdir(parents=True,exist_ok=True)
 trials=build()
 out.write_text(json.dumps([asdict(x) for x in trials],indent=2))
 print(f"generated {len(trials)} participant-safe trial specifications")
