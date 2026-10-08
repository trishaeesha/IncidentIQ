# IncidentIQ

**Human-AI Decision Support for Evidence-Grounded Software Incident Troubleshooting**

IncidentIQ studies when evidence-grounded AI assistance improves or degrades human engineers' diagnostic decision-making during software incident investigation.

## Research question

> Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

## Core idea

IncidentIQ does not aim to autonomously resolve incidents. It structures incident evidence into observations, supporting evidence, contradictory evidence, missing information, candidate hypotheses, uncertainty, and suggested diagnostic next steps.

The research compares:

1. Human-only
2. Human + generic AI
3. Human + IncidentIQ

across controlled incident conditions such as clear, ambiguous, conflicting, incomplete, misleading, and novel evidence.

## Evaluation

Primary outcomes include final diagnosis accuracy, time to correct hypothesis, time to correct diagnostic action, unnecessary diagnostic actions, incorrect diagnostic actions, verification effort, AI reliance/override behavior, and confidence/calibration.

The central evaluation is not simply whether the AI gives the correct answer. It is whether the AI changes the engineer's decision process in a measurable and useful way.

## Data

The initial benchmark source is RCAEval (phamquiluan/RCAEval), which provides labeled software failure cases and multi-source telemetry for controlled incident scenarios.

Raw datasets are not committed to this repository. See data/README.md.

## Repository structure

    IncidentIQ/
    ├── data/
    │   └── README.md
    ├── configs/
    ├── notebooks/
    ├── src/
    │   ├── data/
    │   ├── evidence/
    │   ├── models/
    │   └── evaluation/
    ├── experiments/
    ├── tests/
    ├── requirements.txt
    └── README.md

## Research discipline

This repository deliberately avoids claiming novelty for generic log anomaly detection, autonomous RCA, cost-aware tool selection, stopping policies, or abstention alone. Those areas already have substantial prior work.

The contribution must be demonstrated experimentally through human-AI diagnostic decision quality under different incident conditions.

## Final integrated status

**Submission-ready with explicit research limitations.**

The core runtime, research-validation harness, NLI experiment, participant-data audit, five-condition gray-area telemetry validation, and final five-case RCAEval evaluation are integrated and documented. The integrated branch is the source of truth for the current submission.

The verified five-case RCAEval result is **2/5 exact root-service matches (40%) overall**, with **1 abstention** and **2/4 (50%) exact matches among non-abstained cases**. This is a small, case-specific benchmark result and must not be presented as general RCA accuracy.

The existing human-participant export is a **historical five-condition study**: 30 raw participant files, 27 complete participants, 3 incomplete participants, and 135 valid analysis trials. It must not be presented as the final six-condition study.

## Development flow

1. Load verified RCAEval cases locally.
2. Extract structured incident evidence from metrics, logs, and traces.
3. Represent supporting, contradictory, and missing evidence.
4. Generate and compare candidate hypotheses.
5. Provide diagnostic guidance and uncertainty.
6. Expose the pipeline through the prototype UI/API.
7. Test on multiple cases.
8. Construct and validate the fixed gray-area conditions using real telemetry.
9. Run human-only, generic-AI, and IncidentIQ evaluations only after participant-safe validation.

## Integrated execution status

The current integration branch contains the core IncidentIQ runtime plus the research-side ML/NLP/RCAEval tooling. The repository is intended to be cloned once and then executed from VS Code.

### What is runnable

- Core API: app.py
- Browser prototype: static/index.html
- Core regression suite: pytest
- Optional NLI unit tests: tests/test_nli_evidence.py
- Optional NLI experiment: experiments/run_nli_case.py
- VS Code setup/run/test tasks
- GitHub Actions CI and research workflows

### Current evidence boundary

- Five gray-area telemetry cells are validated by GitHub Actions: clear, ambiguous, conflicting, incomplete, and misleading.
- The novel/historical-mismatch sixth condition is explicitly excluded because no independent historical-similarity corpus was validated.
- The 30-participant historical study is audited and analyzed within its five-condition boundary.
- The final five-case RCAEval root-service scoring evaluation is verified: 2/5 exact matches (40% overall), 1 abstention, and 2/4 exact matches among non-abstained cases.
- Production telemetry integration is not verified.
- Broader RCAEval benchmark performance is not established.
- No causal claim that AI assistance improves human accuracy is established.

The system does not perform autonomous remediation. Diagnostic recommendations remain human-controlled.

See RUN_IN_VSCODE.md, FINAL_STATUS.md, RESEARCH_STATUS.md, and docs/FINAL_REPORT.md for the detailed execution and evidence boundary.
