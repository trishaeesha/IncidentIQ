# Research Analysis Workflow

## Research Question

When does AI assistance help versus harm human software-incident troubleshooting decisions?

## Analysis Flow

Telemetry and evidence
→ diagnosis
→ uncertainty / gray area
→ AI assistance
→ human decision

## Participant Analysis

The participant study is analyzed at the trial level and grouped by participant where cross-validation is required.

Primary outcome:
- diagnosis_correct

Secondary outcomes:
- elapsedSeconds
- confidence
- workload
- aiFollowed
- aiOverridden

## Conditions

- clear
- ambiguous
- conflicting
- incomplete
- misleading

## Evaluation Principles

Participant identity is never used as a predictive feature.

GroupKFold is used so trials from the same participant are not split across training and validation folds.

The analysis is exploratory and does not establish causality.

## RCAEval

RCAEval is used to validate telemetry and evidence-processing behavior.

RCAEval cases are not treated as a sufficient dataset for predictive machine learning.

## NLP

NLP/NLI is evaluated using actual evidence-hypothesis pairs.

Supporting, contradicting, and neutral outputs must be recorded exactly as produced by the implementation.

## Reporting

Every component must be classified as:

- IMPLEMENTED
- EXECUTED
- VERIFIED
- NOT VERIFIED
- BLOCKED
- FAILED

Unknown results must not be presented as successful results.
