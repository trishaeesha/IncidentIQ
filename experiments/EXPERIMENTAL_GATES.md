# Experimental gates

## Gate A — telemetry validation
A gray-area condition is not considered experimentally validated merely because
its schema fields are populated. The transformed evidence must be checked against
the actual RCAEval telemetry and the evaluator-only root cause.

## Gate B — cohort counterbalancing
The three modes (human-only, generic-AI, IncidentIQ) must be distributed across
participants at each case-condition cell. A single participant seeing only one
mode per cell is acceptable; a single mode across the entire cohort is not.

## Gate C — participant data
No human-study effect size, accuracy improvement, time reduction, or workload
claim is valid until actual participant records exist.

## Gate D — model upgrade
Do not introduce a Transformer solely to satisfy an NLP/DL requirement. Upgrade
only after failure analysis identifies a semantic failure that the proposed
model can plausibly address and the baseline-versus-upgrade comparison is
pre-registered.

## Gate E — ablation
Any improvement must survive component removal tests. At minimum compare the
baseline reasoning path against the smallest proposed semantic component and
the full improved path.
