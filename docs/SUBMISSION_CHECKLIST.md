# IncidentIQ Submission Checklist

Updated: 2026-10-08

## Completed and verified

- [x] Core evidence -> hypothesis -> decision-support pipeline integrated.
- [x] Human-control boundary preserved; no autonomous remediation.
- [x] API and browser prototype runtime verified.
- [x] NLI runtime verified experimentally with bounded claims.
- [x] Five gray-area telemetry conditions validated from actual RCAEval telemetry.
- [x] Participant-facing evaluator/condition leakage fixed and regression-tested.
- [x] Historical participant export audited: 30 raw files, 27 complete participants, 135 valid trials.
- [x] Final five-case RCAEval execution completed.
- [x] Final five-case result documented: 2/5 exact root-service matches, 1 abstention, 2/4 among non-abstained.
- [x] Ground-truth labels remain evaluator-only and raw telemetry is not committed.
- [x] Research status, final status, and final report documents aligned to the evidence boundary.
- [x] CI/research validation gates completed for the integrated runtime.

## Required claims discipline

The submission may claim:

- evidence-grounded human-AI decision support;
- competing hypotheses with supporting, contradicting, neutral, and missing evidence;
- discriminating diagnostic recommendations;
- experimental NLI evidence relations;
- five validated gray-area telemetry conditions;
- an audited historical five-condition participant study;
- a small five-case RCAEval result.

The submission must not claim:

- general RCA accuracy from five cases;
- that IncidentIQ causally improves human accuracy;
- that AI following causes better performance;
- reliable root-cause determination by NLI;
- validated production real-time telemetry;
- a validated sixth novel/historical-mismatch condition;
- a six-condition 30-participant human study;
- autonomous remediation.

## Intentionally future work

These are not blockers for the current evidence-bounded submission:

1. Independent historical-similarity/reference corpus for the sixth condition.
2. Final six-condition human study.
3. Larger RCAEval benchmark evaluation.
4. Production telemetry integration and independent validation.
5. Stronger causal human-AI comparison with appropriate controls.

No fabricated data, benchmark scores, participant outcomes, or production evidence should be added to close these items.

## Final reviewer checks

Before submission, confirm:

- [ ] Demo uses the integrated branch/runtime.
- [ ] Presentation uses the exact five-case RCAEval result and historical five-condition participant limitation.
- [ ] No slide or abstract says "six-condition human study."
- [ ] No slide or abstract reports 40% as general RCA accuracy.
- [ ] No slide claims production deployment.
- [ ] No slide claims causal improvement from AI assistance.
