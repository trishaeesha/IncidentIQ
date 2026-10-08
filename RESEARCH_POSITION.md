# IncidentIQ Research Position

## Contribution target

IncidentIQ is evaluated as **human-AI decision support for software incident troubleshooting**, not as an autonomous RCA agent.

The project deliberately does not claim novelty from automated RCA, agentic troubleshooting, cost-aware investigation, or abstention alone. The intended contribution is the **evidence-grounded decision-support workflow** and its evaluation in terms of human diagnostic decision-making.

## Research question

> Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

## Experimental comparison

1. Human only
2. Human + generic AI
3. Human + IncidentIQ

## Incident conditions

1. Clear / straightforward evidence
2. Ambiguous evidence
3. Conflicting telemetry
4. Incomplete / missing evidence
5. Misleading evidence
6. Novel / historical mismatch

The sixth condition is part of the final design but is currently excluded from the validated participant evidence because no independent historical-similarity/reference corpus was established.

## Primary outcomes

- diagnosis correctness
- time to correct hypothesis
- time to correct diagnostic action
- unnecessary actions
- incorrect actions
- verification time
- AI-following and override
- confidence/calibration
- workload

## Integrity rule

RCAEval ground truth is evaluator-only. Participant-facing telemetry and AI outputs must never expose root-cause labels, fault labels, condition labels, or condition rationales.

## Current evidence boundary

Five gray-area conditions passed raw-telemetry validation. The existing 30-participant export is a completed **five-condition historical study** and is not evidence for the excluded sixth condition.

The defensible current contribution is therefore an executable, evidence-grounded, human-controlled troubleshooting workflow with bounded empirical evaluation—not a claim of general autonomous root-cause accuracy.
