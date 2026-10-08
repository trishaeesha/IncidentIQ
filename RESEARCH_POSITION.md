# IncidentIQ research position

## Current contribution target

IncidentIQ is evaluated as human-AI decision support for software incident troubleshooting, not as another autonomous RCA agent.

Recent work already covers automated RCA, agentic troubleshooting, and recovery-action evaluation. For example, Microsoft research reports RCACopilot for automated RCA, StepFly for agentic troubleshooting-guide execution, and R2Act for diagnosis-to-recovery evaluation. Therefore IncidentIQ does not claim novelty from RCA, agentic tool use, cost-aware investigation, or abstention alone. citeturn0search11turn0search7turn0search1

## Research question

Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

## Experimental comparison

1. Human only
2. Human + generic AI
3. Human + IncidentIQ

## Incident conditions

- clear
- ambiguous
- conflicting
- incomplete
- misleading
- novel/historical mismatch (design condition, currently excluded from participant study)

Conditions are not inferred from RCAEval metadata alone. Each condition requires evidence-traceable researcher validation.

## Primary outcomes

- diagnosis correctness
- time to correct hypothesis
- time to correct diagnostic action
- unnecessary actions
- incorrect actions
- verification time
- confidence/calibration
- AI following and override
- workload

## Integrity rule

RCAEval ground truth is evaluator-only. Participant-facing telemetry and AI outputs must never expose root-cause labels, fault labels, condition labels, or condition rationales.

## Current evidence boundary

Five gray-area conditions have passed raw-telemetry validation. The novel/historical-mismatch condition is not validated because no independent historical-similarity/reference corpus exists. The existing 30-participant export is a completed five-condition study and is not evidence for the excluded sixth condition.
