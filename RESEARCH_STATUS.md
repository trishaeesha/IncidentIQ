# IncidentIQ Research Status

Updated: 2026-10-03

## Research question
Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

## Verified engineering status
1. Real RCAEval RE2 telemetry can flow through Evidence -> Hypothesis -> Decision.
2. Eleven selected RE2 cases execute successfully in GitHub Actions.
3. RCAEval trace timestamps are normalized using numeric epoch-like start timestamps.
4. Evidence from unrelated services is not allowed to contradict a service-local hypothesis.
5. Neutral evidence is not treated as contradiction or confidence penalty.
6. Ground-truth leakage checks remain active.
7. Friend 3's evaluation framework is integrated.
8. Friend 3's 23 regression tests pass.
9. The contextual NLI experiment uses a pretrained DeBERTa-v3-xsmall NLI cross-encoder and passes CI smoke testing.
10. A minimal standard-library API and Docker deployment scaffold exist.

## Baseline findings
The deterministic baseline is intentionally weak and transparent. Across the 11-case exploratory run, it handled some obvious resource cases but also produced unsupported fault-family hypotheses such as storage pressure on incidents whose fault families were memory, socket, or network loss. Several cases correctly abstained. These are failure-analysis observations, not final benchmark accuracy.

The baseline therefore provides a justified comparison point for contextual evidence-relation modeling.

## Human experiment status
NOT EXECUTED.

No human participant results are fabricated. The repository contains the trial schema, randomization/carryover controls, participant leakage guards, evaluator-only truth schema, six-condition validation framework, and metrics.

The remaining empirical step requiring humans is the controlled comparison:
- human_only
- generic_ai
- incidentiq

across validated:
- clear
- ambiguous
- conflicting
- incomplete
- misleading
- novel

## Research integrity
RCAEval ground-truth labels are evaluator-only. They must never enter participant payloads, generic-AI inputs, IncidentIQ inference, or condition assignment.

## Next empirical work
1. Researcher validation of gray-area case candidates.
2. Participant pilot.
3. Full human-AI study.
4. Analyze condition-specific benefit/harm and reliance.
5. Compare deterministic baseline vs contextual NLI ablation.
6. Only then consider learned ML prediction of when assistance helps/hurts; no training dataset exists yet, so ML benefit prediction must not be fabricated.

## Deployment
`app.py` exposes:
- GET /health
- POST /analyze

The API returns hypotheses and a human-controlled decision recommendation. It performs no autonomous remediation.