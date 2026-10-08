# IncidentIQ Research Status

Updated: 2026-10-08

## Current repository state

The repository contains the integrated IncidentIQ core, experimental NLP/NLI component, ML/research analysis code, RCAEval evaluation scaffolding, browser prototype, and VS Code/GitHub automation.

This file separates implemented, runtime-verified, and not-yet-verified work. No benchmark or human-study result is promoted to verified merely because its code exists.

## Core IncidentIQ

Implemented:
- deterministic evidence extraction and provenance-aware evidence records
- competing hypothesis generation
- supporting / contradicting / missing / neutral evidence
- uncertainty representation
- recommended discriminating diagnostic checks
- human-controlled decision support
- API and browser prototype
- simulated incremental Live Evidence interaction

Runtime verified:
- integrated API launched successfully from the GitHub working copy
- /health returned status=ok with nlp_available=true
- /analyze executed the evidence -> hypothesis -> decision path
- browser prototype displayed the decision-support output
- human-control boundary remained explicit
- simulated live evidence remains simulated; production telemetry is not connected
- no autonomous remediation is performed

## NLP / NLI

Implemented:
- optional sentence-transformers NLI component
- supporting / contradiction / neutral relation output
- lazy model loading
- isolated NLI experiment runner
- NLI unit tests
- GitHub workflow for the optional NLI experiment
- UI display of the experimental relation and score

Runtime verified on the user's existing local environment:
- /health reported nlp_available=true
- actual NLI inference completed successfully
- "checkoutservice CPU utilization remained normal" vs CPU saturation returned contradiction (score approximately 0.8241)
- unrelated request activity vs CPU saturation returned neutral (score approximately 0.7611)
- "checkoutservice CPU utilization increased significantly" vs resource saturation returned neutral (score approximately 0.4216), so this example is recorded as observed rather than relabeled as entailment

NLI relations are an experimental evidence-relation layer, not a root-cause decision mechanism.

## ML / research analysis

Integrated:
- feature engineering
- participant analysis
- grouped participant-level ML evaluation
- condition analysis
- relationship analysis
- visualization utilities
- research documentation

Previously verified exploratory findings remain research findings only:
- pre-decision grouped CV was near chance
- post-decision features modestly increased exploratory AUC
- these models are not deployable real-time RCA systems

The repository must not invent new metrics when source data or an execution result is unavailable.

## RCAEval

Integrated:
- local case loader
- evidence extraction path
- contextual NLI experiment
- regression tests
- benchmark workflows

Raw RCAEval telemetry is intentionally not committed. Any real-case benchmark execution must download or provide the permitted telemetry at runtime.

The five-case conflicted RCAEval evaluation is NOT VERIFIED unless the required telemetry is actually available and the validation script completes.

## Human participant study

A direct audit of the uploaded raw participant export (30 JSON files, 140 raw trials) reproduced the dataset structure independently: 27 participants have 5 trials each, while 3 participants are incomplete; the raw condition counts are 30 clear, 28 ambiguous, 27 conflicting, 27 misleading, and 28 incomplete. There is one duplicate participant+trial key in the raw export. Restricting to the 27 complete participants yields exactly 135 analysis trials. The directly recomputed descriptive values are mean decision time 27.3407 s (27.3 s), median 11 s, mean confidence 3.5185 (3.52/5), mean workload 3.5037 (3.50/5), AI followed 85/135 (63.0%), and AI overridden 32/135 (23.7%). The raw participant export is not committed to GitHub. The previously reported 54.8% accuracy remains the project's verified result, but this raw export alone does not contain an authoritative evaluator answer key, so accuracy is not independently re-derived from these JSON files.

Verified analysis dataset from the project handoff:
- 27 complete participants
- 135 valid trials
- 5 trials per participant
- 27 trials per condition

Verified descriptive results:
- accuracy 54.8%
- mean decision time 27.3 s
- median decision time 11 s
- mean confidence 3.52 / 5
- mean workload 3.50 / 5
- AI followed 63.0%
- AI overridden 23.7%
- misleading-condition accuracy 44.4%

These results describe the IncidentIQ-assisted study arm. They do not establish improvement over a human-only control.

Statistical placeholders from the handoff remain placeholders where exact execution output was not preserved. No missing p-values are invented.

## Research integrity

Never commit:
- participant identifiers or private participant exports
- secrets
- evaluator-only RCAEval ground truth
- private telemetry

Never claim:
- causal effects from correlations
- automatic improvement from AI following
- calibrated probability from the 1–5 confidence scale
- production real-time telemetry
- deployable real-time RCA from exploratory ML
- autonomous remediation

## Current remaining work

The research-validation workflow successfully validated five gray-area telemetry cells: clear, ambiguous, conflicting, incomplete, and misleading. Participant-safe planned assignments passed leakage/cohort checks, the prototype smoke test passed, and the research-report regression test passed. These are harness/telemetry-validation results, not human participant outcomes.

The sixth novel/historical-mismatch condition is explicitly excluded from the participant study because no independent historical-similarity/reference corpus was validated. Adding it would manufacture novelty rather than test it.

The uploaded 30-participant export is a real, audited five-case study dataset: 27 participants are complete and 3 are incomplete. It is therefore valid evidence for that historical five-condition study, but it does not satisfy the frozen six-condition final design and must be reported with that limitation.

The remaining scientific work is intentionally limited to:
- run and preserve the final five-case RCAEval evaluation results once the permitted telemetry is available in the execution environment
- keep production telemetry marked unverified unless a real source is connected and tested
- preserve the five-condition participant results as a bounded historical study result rather than relabeling them as six-condition evidence

The automated AI research reviewer is non-blocking. Its latest successful workflow run used the fallback \"Execution not verified.\" The authoritative code gate is the regular CI workflow.

## Final verification path

Completed for the current integrated runtime:
1. regression CI passes on the integrated branch
2. API starts successfully
3. /health verified
4. /analyze verified
5. browser prototype verified
6. NLI model availability verified
7. actual NLI inference verified

Still pending:
- final five-case conflicted RCAEval scoring evaluation
- production telemetry connection
- any broader benchmark claim beyond the verified executions above
- a final six-condition human study; the existing 30-participant dataset is five-condition historical evidence

No new model, dataset, Docker image, VM, or other large download is required for the completed verification above.
