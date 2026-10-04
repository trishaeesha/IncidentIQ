# IncidentIQ experimental freeze

## Frozen research question
When does evidence-grounded IncidentIQ decision support help or harm human
software-incident diagnosis under heterogeneous, incomplete, conflicting, and
misleading telemetry?

## Frozen arms
1. human_only — telemetry only.
2. generic_ai — deterministic single-salient-observation assistant. It does not
   expose cross-source conflict, uncertainty, or a diagnostic next action.
3. incidentiq — IncidentIQ hypothesis + decision path, including uncertainty,
   supporting/contradicting evidence counts, and next diagnostic action.

These are operational study arms. No claim is made that the generic_ai arm is
an external commercial LLM.

## Frozen validated conditions
- clear: RE2-OB checkoutservice CPU case.
- ambiguous: RE2-OB checkoutservice memory case.
- conflicting: RE2-OB checkoutservice loss case with same-service cross-source
  opposing evidence.
- incomplete: RE2-SS user loss case with genuine absence of traces.
- misleading: independent RE2-OB checkoutservice loss case with a strong
  non-root emailservice latency distractor.

## Explicit exclusion
The novel condition is excluded from the participant study. No historical
similarity/reference corpus has been independently validated, so adding it
would manufacture novelty rather than test it.

## Primary outcomes
- diagnosis correctness
- confidence calibration error
- elapsed diagnostic time
- unnecessary/incorrect diagnostic actions
- workload
- AI-follow versus AI-override behavior

## Integrity rules
- Participant manifests contain no condition key, root-cause label, fault label,
  or evaluator answer.
- Researcher validation may use evaluator metadata, but participant scoring
  uses a separate evaluator-only file.
- No participant results are generated synthetically.
- No effect-size or significance claim is made before actual participant data.
- Small cells are reported descriptively rather than over-interpreted.

## Ablation
After the human study, compare:
A. current IncidentIQ full decision path
B. smallest semantic component required by the observed failure analysis
C. baseline path without that component

The ablation is only run after real participant/evaluation data establish that
the component addresses an observed failure. It must not be used to retrofit
a novelty claim.

## Stopping rule
If a condition fails raw telemetry validation, it is removed rather than
repaired by deleting or fabricating evidence. If the participant pool fails
leakage/balance validation, no human study begins.
