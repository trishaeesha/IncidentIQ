# IncidentIQ — Research Protocol and Completion Gate

## Research question

Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

## Experimental modes

- HUMAN_ONLY
- GENERIC_AI
- INCIDENTIQ

## Conditions

- CLEAR
- AMBIGUOUS
- CONFLICTING
- INCOMPLETE
- MISLEADING
- NOVEL / HISTORICAL MISMATCH

A condition is valid only when explicit evidence supports it. RCAEval metadata alone cannot define the condition.

## Primary outcomes

1. Diagnosis correctness
2. Time to correct hypothesis
3. Time to correct diagnostic action
4. Unnecessary diagnostic actions
5. Incorrect diagnostic actions
6. Verification time

Secondary outcomes:

- confidence and confidence error
- AI following rate
- AI override rate
- incorrect AI following
- workload

## Current engineering result

The deterministic baseline is integrated with real RCAEval telemetry and evaluator-only scoring. It is safety-oriented but currently abstains frequently and can still localize incorrectly. An isolated off-the-shelf NLI Transformer experiment was also run; it returned neutral for obvious evidence/hypothesis pairs, so it is not justified as the final NLP component.

## Human-study gate

The human experiment is the only remaining stage that cannot be completed by repository automation. It requires real participants and recorded trials. No participant result is to be fabricated.

## Model-upgrade gate

A contextual NLP model should be introduced only after the human/AI experiment and baseline failure analysis identify a semantic evidence-relation failure that the model can plausibly address.

## Deployment gate

Deployment is permitted only after:
- participant-safe payload leakage tests pass
- evaluator separation is verified
- gray-area cases are validated
- baseline and improved-system results are reproducible
- failure cases and limitations are documented
