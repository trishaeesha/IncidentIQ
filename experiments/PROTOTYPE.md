# IncidentIQ Prototype

Run `python experiments/prototype_server.py` from the repository root, then open the local prototype server on port 8010.

The console is connected to the existing HypothesisEngine and DecisionEngine. It displays telemetry evidence, competing hypotheses, uncertainty, contradiction and missing-evidence counts, and a next diagnostic action.

The demo input contains small evidence samples from the five validated RCAEval-derived study cases. It is a prototype dataset, not a replacement for the full RCAEval pipeline.

Research-integrity boundary:
- evaluator ground truth is not loaded into the diagnostic path
- confidence is a relative evidence-support score, not a calibrated probability
- human control remains required before operational action
- the prototype does not claim participant-study results
- generic AI and human-only study arms remain separate from this product console

Next integration: replace the demo evidence adapter with the existing real-case loader while preserving telemetry -> evidence extraction -> HypothesisEngine -> DecisionEngine -> human decision.