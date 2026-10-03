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

## Status

Research design / benchmark construction phase.
