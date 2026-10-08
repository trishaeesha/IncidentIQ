# Run IncidentIQ in VS Code

1. Open the repository folder in VS Code.
2. Install the recommended extensions.
3. Run the "IncidentIQ: Setup" task.
4. Run the "IncidentIQ: Run" task or press F5.
5. Open http://127.0.0.1:8080/

Run the "IncidentIQ: Test" task to execute the regression suite.

Current truth:
- Evidence extraction/reasoning is implemented.
- Hypothesis and decision support are implemented.
- Human-control boundary is implemented.
- Prototype API/UI is implemented.
- Live Evidence is simulated incremental evidence only.
- Production telemetry is not connected.
- NLP/NLI is optional research work and must be runtime-verified before being claimed as verified.
- RCAEval is benchmark/evaluation work; raw telemetry is not committed.

Do not commit participant identifiers, raw private study exports, secrets, or evaluator-only ground truth.
