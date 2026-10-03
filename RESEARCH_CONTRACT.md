# IncidentIQ Research Contract

## Research question
Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

## Experimental modes
A. Human only
B. Human + generic AI assistance
C. Human + IncidentIQ evidence-grounded assistance

## Six incident conditions
1. Clear / straightforward evidence
2. Ambiguous evidence with multiple plausible causes
3. Conflicting telemetry
4. Incomplete / missing evidence
5. Misleading evidence
6. Novel fault / historical mismatch

These are experimental labels and must be constructed and validated from telemetry/evidence. Do not infer them solely from RCAEval metadata.

## Hypotheses
H1: Evidence-grounded AI assistance should provide the greatest decision-efficiency benefit for ambiguous, conflicting, or incomplete incidents, while providing limited or negative benefit for straightforward or misleading incidents.

H2: Explicit supporting, contradictory, and missing-evidence presentation should reduce inappropriate reliance on AI recommendations compared with answer-oriented generic AI assistance.

These are hypotheses, not results.

## Dataset
Primary controlled incident source: RCAEval RE2.
Known facts: 270 RE2 cases across Online Boutique, Sock Shop, and Train Ticket; fault families include CPU, memory, disk, delay, loss, and socket. Depending on system, RE2 contains metrics and logs, and some systems also contain traces.

RCAEval provides incident ground truth, not complete human troubleshooting trajectories. Human decision trajectories must be collected experimentally.

Ground-truth fields are evaluator-only. Never expose root_cause_service, fault, fault_description, ground_truth, or labels to participants, generic AI, participant-facing manifests, or inference code.

## Architecture
Incident -> Evidence -> Evidence structuring -> Candidate hypotheses -> Decision support -> Human diagnostic decision -> Targeted test/action -> Result -> Updated decision.

Evidence extraction OBSERVES; it does not assign causal meaning. Hypothesis/Decision components INTERPRET evidence relative to candidate explanations and preserve uncertainty.

## Technology rule
Every model must earn its place. Do not add BERT + LSTM + Random Forest or similar stacks merely for appearance. The transparent deterministic baseline is valid until experiments justify a learned NLP/Transformer component. ML may later predict when AI assistance helps or hurts, but only after a decision-impact dataset exists. Deep learning is not required merely to satisfy a project label.

## Evaluation
Primary metrics: final diagnosis accuracy, time to correct hypothesis, time to correct diagnostic action, unnecessary actions, incorrect actions, verification time.
Human-AI metrics: AI-following rate, AI override rate, confidence, calibration, workload.
Always report performance by each gray-area condition and include failure analysis. Never invent results.

## Scope guardrails
Do not add by default: autonomous remediation, multi-agent swarms, generic chatbots, Slack/Teams bots, giant dashboards, vector DB/RAG solely for novelty, generic LSTM/GRU/autoencoder anomaly detectors, cost-aware tool-selection algorithms, standalone abstention algorithms, or autonomous RCA agents.

## Integrity rules
Never leak ground-truth labels, tune on the test set, fabricate measurements, claim causality from temporal association alone, or treat repeated injections as unrelated incidents. If execution cannot be verified, say: "Execution not verified." Do not silently change the research question, modes, six conditions, dataset, or core architecture.

## Automated reviewer role
The GitHub AI reviewer is a research/code reviewer, not an autonomous maintainer. It checks changed code, bugs, leakage, unsupported claims, unnecessary complexity, test status, and research alignment. It must never auto-merge, auto-approve, fabricate results, or change project scope.

## Required review output
1. Project Status
2. What Changed
3. What Is Correct
4. Mistakes / Risks
5. Research Integrity
6. Research Impact
7. What Should NOT Be Added
8. Next Steps
9. Merge Readiness
10. One-Sentence Verdict
