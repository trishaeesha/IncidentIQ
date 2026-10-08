# IncidentIQ Research Status

Updated: 2026-10-08

## Research question

When does AI assistance help versus harm human software-incident troubleshooting decisions?

## Verified engineering status

1. Real RCAEval telemetry can flow through the Evidence -> Hypothesis -> Decision pipeline.
2. Ground-truth leakage checks remain active.
3. Evidence-relation logic preserves service and signal context.
4. Neutral evidence is not treated as contradiction or confidence penalty.
5. The NLI evidence interpreter is implemented using a pretrained NLI model.
6. NLI dependencies are installed and operational.
7. NLI unit tests pass.
8. The `/health` endpoint reports NLI availability.
9. The `/nli` endpoint executes evidence-hypothesis relation inference.
10. A real RCAEval checkoutservice CPU case was executed through the NLI experiment.
11. The integrated project test suite passes.
12. The application provides human-controlled decision recommendations and performs no autonomous remediation.

## NLI status

NLI implementation: VERIFIED.

Actual verification:
- NLI unit tests: 2 passed.
- Label mapping: contradiction / entailment / neutral verified.
- Direct inference: EXECUTED.
- `/health`: VERIFIED.
- `/nli`: VERIFIED.
- Real RCAEval CPU case: EXECUTED.

The current experiment does NOT verify that NLI improves diagnostic accuracy or decision quality. NLI should therefore be reported as an operational evidence-relation component, not as a demonstrated improvement.

## ML participant analysis

Participant analysis is based on the cleaned dataset containing:

- 27 participants
- 135 trials
- 5 trials per participant
- participant-grouped evaluation
- 5-fold GroupKFold cross-validation

Models evaluated:
- Logistic Regression
- Random Forest

Pre-decision features:
- condition
- trialIndex

Post-decision features:
- confidence
- workload
- elapsedSeconds
- aiFollowed
- aiOverridden

Observed mean cross-validation ROC-AUC:

| Model | Feature set | ROC-AUC |
|---|---|---:|
| Logistic Regression | Pre-decision | 0.478720 |
| Random Forest | Pre-decision | 0.535771 |
| Logistic Regression | Post-decision | 0.538457 |
| Random Forest | Post-decision | 0.557754 |

These ML results are exploratory. They are not causal evidence and do not establish a deployable predictive RCA model.

## Participant findings

Observed condition-level accuracy:

| Condition | Accuracy |
|---|---:|
| Clear | 62.96% |
| Ambiguous | 55.56% |
| Conflicting | 55.56% |
| Incomplete | 55.56% |
| Misleading | 44.44% |

Observed accuracy when participants followed AI:
- AI followed: 60.00%
- AI not followed: 46.00%

Observed accuracy when participants overrode AI:
- AI overridden: 43.75%
- AI not overridden: 58.25%

These are observational relationships only. They must not be interpreted as causal effects of AI assistance.

## RCAEval status

Available local telemetry was executed for:

1. `re2ob_checkoutservice_cpu_2`
2. `re2ob_checkoutservice_mem_2`
3. `re2ss_user_loss_1`

Status: EXECUTED — 3 cases.

Six additional required cases remain BLOCKED because their required telemetry directories are not available in the local RCAEval dataset.

The blocked cases are:

1. `re1ob_currencyservice_disk_3`
2. `re2ob_currencyservice_disk_3`
3. `re2ob_emailservice_disk_2`
4. `re2ob_emailservice_mem_2`
5. `re2ob_emailservice_socket_3`
6. `re2ob_recommendationservice_mem_3`

Therefore, full execution of the complete required RCAEval case set is NOT VERIFIED.

## Research integrity

RCAEval ground-truth labels are evaluator-only.

Ground-truth labels must never enter:
- participant payloads
- generic-AI inputs
- IncidentIQ inference
- condition assignment
- predictive features

No fabricated empirical results should be reported.

## Testing

The final integrated repository test suite was executed with:

`python -m pytest -q tests`

Actual result:

`15 passed in 1.16s`

## Deployment

`app.py` exposes:

- GET `/health`
- POST `/analyze`
- POST `/nli`

The API returns evidence-grounded hypotheses and human-controlled decision recommendations.

It performs no autonomous remediation.

## Remaining limitations

1. Six RCAEval cases remain blocked because required telemetry is unavailable locally.
2. NLI operational functionality is verified, but semantic improvement is not verified.
3. Participant relationships are observational and should not be interpreted causally.
4. The Google Apps Script / Google Sheet study backend remains unconfigured unless deployment is required.
5. The final repository should be reviewed and merged by an authorized collaborator.

