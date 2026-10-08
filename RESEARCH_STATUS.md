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
- permitted real RCAEval telemetry and the five-case conflicted evaluation
- production telemetry connection
- any broader benchmark claim beyond the verified executions above

No new model, dataset, Docker image, VM, or other large download is required for the completed verification above.
