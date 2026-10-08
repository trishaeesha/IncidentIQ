# IncidentIQ Data Dictionary

## Purpose

This document defines the fields used by the IncidentIQ participant study and
the downstream analysis pipeline.

The participant dataset is intentionally not stored in the public repository.

## Participant Trial Fields

| Field | Type | Description |
|---|---|---|
| participantId | string | Anonymous participant identifier such as P01 |
| trialIndex | integer | Trial number for the participant |
| caseId | string | Public incident case identifier such as CASE-01 |
| condition | categorical | Experimental evidence condition |
| diagnosis | string | Diagnosis selected by the participant |
| confidence | numeric | Participant confidence in the selected diagnosis |
| workload | numeric | Participant-reported workload |
| aiFollowed | boolean | Whether the participant followed the AI recommendation |
| aiOverridden | boolean | Whether the participant overrode the AI recommendation |
| elapsedSeconds | numeric | Time taken to complete the trial |
| savedAt | datetime | Time at which the trial was recorded |

## Derived Analysis Fields

| Field | Type | Description |
|---|---|---|
| correct_diagnosis | boolean | Whether the submitted diagnosis matches the expected diagnosis |
| diagnosis_correct | boolean | Standardized correctness target used by participant analysis |
| accuracy | numeric | Proportion of correct diagnostic decisions |
| accuracy_percent | numeric | Accuracy expressed as a percentage |

## Experimental Conditions

| Condition | Meaning |
|---|---|
| clear | Evidence strongly supports the correct diagnosis |
| ambiguous | Evidence supports more than one plausible interpretation |
| conflicting | Evidence contains competing signals |
| incomplete | Important evidence or telemetry is missing |
| misleading | Evidence contains a strong distracting signal |

## Study Modes

| Mode | Meaning |
|---|---|
| human_only | Participant makes the diagnosis without AI assistance |
| generic_ai | Participant receives generic AI assistance |
| incidentiq | Participant receives IncidentIQ evidence-grounded assistance |

## Incident Cases

| Case | Condition | Scenario |
|---|---|---|
| CASE-01 | clear | Checkoutservice CPU/resource saturation |
| CASE-02 | ambiguous | Checkoutservice memory pressure with error-like logs |
| CASE-03 | conflicting | Checkoutservice packet-loss incident |
| CASE-04 | misleading | Distracting emailservice latency; actual checkoutservice network loss |
| CASE-05 | incomplete | User-service packet loss with missing telemetry |

## ML Variables

The participant ML pipeline uses:

- `condition`
- `caseId`

as categorical predictors.

The target is:

- `diagnosis_correct`

`participantId` is used only for grouped cross-validation and is not used
as a predictive feature.

Variables such as confidence, workload, elapsed time, AI following, and AI
override behavior are analyzed separately because they occur during or after
the participant decision and can be endogenous to the decision process.

## Privacy

No participant names, email addresses, tokens, authentication keys, Google
Sheet identifiers, or other personal/sensitive study information should be
committed to the public repository.
