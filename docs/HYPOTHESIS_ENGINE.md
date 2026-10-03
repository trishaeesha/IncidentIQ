# Hypothesis + Decision Engine

## Purpose

The Friend 2 engine converts Friend 1 observation-only evidence into deterministic, human-controlled diagnostic decision support.

Flow:

`structured evidence -> candidate hypotheses -> evidence interpretation -> uncertainty -> discriminating check -> next diagnostic action`

The engine does not perform autonomous remediation or claim causal root cause.

## Input contract

`HypothesisEngine.infer(evidence_rows)` accepts a list of dictionaries using the Friend 1 evidence shape:

- `case_id`
- `source`
- `service`
- `observation`
- `direction`
- `magnitude` (optional)
- `time_context`
- `evidence_strength` (or Friend 1's `strength`)
- `availability` (defaults to `available`)
- `signal` when available

Friend 1's `relation` / `classification` remains observation-level and is not treated as a hypothesis judgment.

RCAEval ground-truth fields such as `root_cause_service`, `fault`, and `fault_description` are rejected by the engine.

## Output contract

The returned dictionary contains:

- `case_id`
- `status`: `hypotheses_available`, `unable_to_distinguish`, or `insufficient_evidence`
- `hypotheses`: deterministically ordered candidate hypothesis records
- `decision`
- `notes`

Each hypothesis record contains:

- `hypothesis`
- `primary_service`
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `neutral_evidence`
- `uncertainty`
- `uncertainty_reasons`
- `confidence`
- `discriminating_checks`
- `next_diagnostic_action`
- `rationale`

The numeric `confidence` field is a deterministic relative-support score, not a calibrated probability.

## Evidence interpretation

The engine applies transparent rules for common hypothesis families:

- resource saturation
- increased request load
- downstream latency
- error or failure increase
- database or storage pressure
- network or communication issue

Evidence is classified relative to each hypothesis. An unavailable observation is recorded as missing/unavailable, never as contradiction.

Contradiction detection explicitly handles negative directions such as decrease, normal, stable, and unchanged when the hypothesis expects an increase.

Observations that are relevant but do not match the hypothesis expectation can remain neutral.

## Multiple hypotheses and abstention

More than one candidate can remain active. When multiple hypotheses are present, the result can be `unable_to_distinguish` rather than forcing one explanation.

Insufficient evidence is first-class: when observations do not provide enough relevant support or contradiction, the engine returns `insufficient_evidence`.

## Updating

`HypothesisEngine.update(previous_result, new_evidence)` combines the prior evidence snapshot with new observations and re-runs the same deterministic inference rules. This supports:

`old evidence + new evidence -> updated hypotheses`

The update method does not introduce hidden memory or an autonomous agent loop.

## Friend 3 interface

Friend 3 should consume only the returned participant-facing fields above. In particular, Friend 3 can use:

1. `status` for abstention/competition state.
2. `hypotheses` for candidate explanations and their evidence breakdown.
3. `confidence` as a deterministic relative score, not probability.
4. `uncertainty` and `uncertainty_reasons`.
5. `discriminating_checks` and `next_diagnostic_action`.
6. `decision`, `rationale`, and `notes`.

Friend 3 must keep RCAEval ground truth separate from participant-facing inference and use it only for evaluation.

## Human control

The decision layer recommends a diagnostic check/action but requires human review. It does not execute production commands, change infrastructure, roll back services, or perform autonomous remediation.

## Verification

The Friend 2 unit suite is `tests/test_hypothesis_decision_engine.py`.

The verified Friend 2 test run completed with 18 passing tests. Full RCAEval execution was not performed because the dataset is not available in this environment.
