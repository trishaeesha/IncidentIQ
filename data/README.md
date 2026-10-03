# Data

## Primary source: RCAEval

IncidentIQ uses RCAEval as the initial source of controlled software failure cases.

RCAEval contains labeled failure cases across microservice systems with telemetry such as metrics, logs, and traces depending on the subset.

### Important rule

Do not commit RCAEval telemetry or other raw datasets to this GitHub repository.

The repository should contain dataset acquisition instructions, dataset manifests / selected case IDs, preprocessing code, derived lightweight metadata, and experiment configurations.

It should not contain large raw telemetry files.

## Initial benchmark construction

We will first inspect the RCAEval case index and select approximately 60–100 cases for a controlled benchmark.

Selection must be explicit and reproducible. We will balance system/application, fault type, telemetry modality, incident difficulty, evidence ambiguity, and competing hypotheses.

The six gray-area conditions are experimental labels to be constructed and validated, not labels assumed to exist in RCAEval:

1. clear evidence
2. ambiguous evidence
3. conflicting evidence
4. incomplete evidence
5. misleading evidence
6. novel / historical-mismatch evidence

## Human decision trajectories

RCAEval provides incident ground truth, but it does not by itself provide complete engineer troubleshooting trajectories.

Therefore, the human-AI study will collect or construct trajectories containing:

Incident → Observation → Hypothesis → Evidence/Reason → Diagnostic Test → Result → Updated Hypothesis → Final Diagnosis.

This distinction is critical: dataset RCA labels are not human decision-process labels.

## Reproducibility

Record the exact RCAEval version/commit, selected case IDs, preprocessing version, and benchmark construction rules in configs/ and experiments/.
