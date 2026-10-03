# IncidentIQ Research Contract

## Research identity

Project: IncidentIQ — Human-AI Decision Support for Evidence-Grounded Software Incident Troubleshooting

Research question:

> Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

One-line objective:

> IncidentIQ investigates when evidence-grounded AI assistance improves or degrades human engineers' diagnostic decision-making across different software-incident conditions.

## Experimental comparison

The core experiment compares three modes:

A. Human only
B. Human + generic AI assistance
C. Human + IncidentIQ evidence-grounded assistance

Do not collapse these into a single automated-RCA benchmark.

## Incident conditions

The controlled evaluation must cover six conditions:

1. Clear / straightforward evidence
2. Ambiguous evidence with multiple plausible causes
3. Conflicting telemetry
4. Incomplete / missing evidence
5. Misleading evidence
6. Novel fault / historical mismatch

These conditions are experimental labels. They must be constructed and validated from telemetry/evidence. They must not be inferred solely from RCAEval metadata such as fault type, modality, or faulty ratio.

## Main hypotheses

H1:
Evidence-grounded AI assistance will provide the greatest decision-efficiency benefit for ambiguous, conflicting, or incomplete incidents, while providing limited or negative benefit for straightforward or misleading incidents.

H2:
Explicit supporting, contradictory, and missing-evidence presentation will reduce inappropriate reliance on AI recommendations compared with answer-oriented generic AI assistance.

These are hypotheses, not established findings. Never write them as results before experiments are run.

## Dataset

Primary controlled incident source:
RCAEval RE2.

Known dataset facts:
- 270 RE2 cases.
- Online Boutique, Sock Shop, and Train Ticket.
- Fault families include CPU, memory, disk, delay, loss, and socket.
- Depending on the system, RE2 contains metrics and logs, and some systems also contain traces.

RCAEval provides incident ground truth, not complete human troubleshooting trajectories. Human decision trajectories must be collected experimentally rather than fabricated.

Ground-truth fields such as root_cause_service, fault, and fault_description are evaluator-only labels.

Never expose:
- root_cause_service
- fault
- fault_description
- ground_truth
- labels

to participants, generic AI, IncidentIQ inference, or participant-facing manifests.

## Evidence architecture

Incident -> Evidence -> Evidence structuring -> Candidate hypotheses -> Decision support -> Human diagnostic decision -> Targeted test/action -> Result -> Updated decision.

Evidence extraction is observational. It must not claim causality.

Evidence Engine responsibilities:
- preserve raw telemetry-derived observations
- represent metric/log/trace evidence
- represent telemetry availability
- preserve temporal context
- avoid root-cause inference

Hypothesis/Decision Engine responsibilities:
- interpret evidence relative to candidate explanations
- distinguish supporting, contradicting, and unavailable evidence
- expose uncertainty
- recommend a discriminating diagnostic check where appropriate
- preserve human control

## NLP / ML / DL rule

Technology must earn its place.

Do not add BERT + LSTM + Random Forest or other stacked models merely to satisfy an internship requirement.

The current transparent deterministic/rule baseline is acceptable.

A learned NLP/Transformer component should only be introduced if an experiment demonstrates that the baseline cannot adequately represent the relevant contextual evidence.

ML may be justified later for predicting when AI assistance is likely to help or hurt, but only after the decision-impact dataset exists.

Deep learning is not required merely because the project title mentions DL.

## Evaluation metrics

Primary:
- final diagnosis accuracy
- time to correct hypothesis
- time to correct diagnostic action
- unnecessary diagnostic actions
- incorrect diagnostic actions
- verification time

Human-AI interaction:
- AI-following rate
- AI override rate
- confidence
- calibration
- workload

Do not report only final RCA accuracy.

## Gray-area evaluation

The project succeeds or fails on the difficult conditions, not only easy incidents.

Every experiment report must separate:
- overall performance
- performance by each of the six conditions
- failure cases
- confidence/calibration
- inappropriate reliance
- unnecessary/incorrect actions

Never invent gray-area labels, measurements, or results.

## Research-integrity rules

Never:
- leak ground-truth labels
- use root-cause labels as model features
- tune on the test set
- claim causal evidence from temporal correlation alone
- treat repeated injections as independent unrelated incidents
- fabricate test results
- claim novelty without checking related work
- change the research question, six conditions, three modes, dataset, or core architecture without explicit project-owner approval

If execution is unavailable, report:
"Execution not verified."

## Scope guardrails

Do NOT add by default:
- autonomous remediation
- multi-agent swarm
- generic chatbot
- Slack/Teams bot
- giant observability dashboard
- vector database/RAG solely for novelty
- generic LSTM/GRU/autoencoder anomaly detector
- cost-aware tool-selection algorithm
- another standalone abstention algorithm
- autonomous RCA agent

These may be discussed only if a concrete experiment establishes a necessary role.

## Automated AI reviewer role

The GitHub AI reviewer is a research/code reviewer, not an autonomous maintainer.

It must:
- inspect changed code and repository structure
- compare changes against this contract
- identify bugs and research-integrity risks
- flag leakage
- flag unsupported claims
- distinguish verified execution from unverified execution
- identify unnecessary complexity
- recommend the smallest justified next step
- never modify project scope automatically
- never auto-merge or auto-approve changes

## Required review output

Every automated review should contain:

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

Use evidence from the repository. If something cannot be verified, say so explicitly.
