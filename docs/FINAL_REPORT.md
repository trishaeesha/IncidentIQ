# IncidentIQ Final Research & Submission Report

Updated: 2026-10-08

## Executive summary
IncidentIQ is an evidence-grounded, human-controlled decision-support system for software incident troubleshooting. It structures telemetry-derived observations, preserves competing hypotheses, distinguishes supporting, contradicting, neutral, and unavailable evidence, recommends discriminating diagnostic checks, and requires a human final decision. It performs no autonomous remediation.

The integrated repository passes CI and the research-validation harness. Five gray-area telemetry conditions were validated from actual RCAEval telemetry. A final five-case RCAEval execution was completed on GitHub Actions.

Verified five-case result: 5 cases, 2 exact root-service matches, 2 incorrect selections, 1 abstention, 40% exact-match accuracy overall, and 50% exact-match accuracy among non-abstained cases. This is a small case-specific benchmark result, not a general accuracy claim.

## Human participant study
The audited historical export contains 30 raw participant files, 140 raw trials, 27 complete participants, 3 incomplete participants, and 135 valid analysis trials. Established project results are 54.8% accuracy, 27.3 s mean decision time, 11 s median, 3.52/5 confidence, 3.50/5 workload, 63.0% AI-followed, 23.7% AI-overridden, and 44.4% misleading-condition accuracy.

This is a five-condition historical study, not evidence for the frozen six-condition design.

## Research boundaries
NLI is an experimental evidence-relation layer, not a root-cause decision mechanism. Exploratory ML is not a deployable RCA system. Confidence on the 1–5 scale is not treated as probability calibration. AI-following differences are not interpreted causally.

The sixth novel/historical-mismatch condition remains excluded because no independent historical-similarity/reference corpus was validated.

Production real-time telemetry and broader benchmark performance are not verified.

## Security and integrity
The public participant page was corrected to remove stale evaluator/condition leakage, and a regression test guards against reintroduction. Raw participant exports, private telemetry, and evaluator-only labels are not committed.

## Final interpretation
The defensible contribution is an executable evidence-grounded human-AI troubleshooting workflow that preserves competing explanations, exposes supporting and contradicting evidence, recommends discriminating checks, and keeps the final diagnostic decision under human control. The current evaluation also exposes failure and abstention cases that define the next research direction.

## Reproducibility
Final RCAEval summary: `docs/rcaeval_final_five_summary.json`
Current status: `FINAL_STATUS.md`
Research boundary: `RESEARCH_STATUS.md`
