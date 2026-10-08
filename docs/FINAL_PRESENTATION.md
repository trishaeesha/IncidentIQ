# IncidentIQ — Final Presentation Story

## Slide 1 — Title

**IncidentIQ**
### Evidence-Grounded Human-AI Decision Support for Software Incident Troubleshooting

**One-line pitch:** IncidentIQ helps engineers investigate competing incident explanations using traceable evidence, contradictory signals, missing information, and targeted diagnostic checks—while keeping the final decision with the human.

**Presenter message:** “We are not building another autonomous RCA bot. We are studying and engineering the decision-support layer between raw telemetry and a human engineer's final diagnosis.”

## Slide 2 — The Problem

### Why incident diagnosis is difficult

Modern incidents rarely provide one clean signal.

Engineers may face noisy metrics, incomplete logs, conflicting telemetry, multiple plausible causes, misleading evidence, and uncertainty about what to check next.

A system that simply outputs a root cause can hide why a hypothesis was selected, what evidence contradicts it, what information is missing, and what diagnostic check would distinguish competing explanations.

**Key message:** The challenge is not only finding an answer. It is supporting a defensible diagnostic decision.

## Slide 3 — Research Question

> Under what software-incident conditions does evidence-grounded AI assistance improve or degrade human engineers' diagnostic decision-making?

### Planned comparison
1. Human only
2. Human + generic AI
3. Human + IncidentIQ

### Planned incident conditions
- Clear
- Ambiguous
- Conflicting
- Incomplete
- Misleading
- Novel / historical mismatch

**Evidence boundary:** The existing human study covers five historical conditions. The sixth condition was excluded because an independent historical-similarity/reference corpus was not validated.

## Slide 4 — IncidentIQ Architecture

### Evidence -> Hypotheses -> Decision Support -> Human

Incident telemetry -> Evidence extraction + provenance -> Supporting / contradicting / neutral / missing evidence -> Competing hypotheses -> Uncertainty + discriminating diagnostic checks -> Human decision

### Design principle
**No autonomous remediation.**

IncidentIQ can recommend what to investigate next, but the engineer remains responsible for the final diagnostic decision.

## Slide 5 — Evidence Layer

For each candidate hypothesis, IncidentIQ can expose:
- evidence that supports it
- evidence that contradicts it
- evidence that is neutral
- evidence that is unavailable
- uncertainty
- the next diagnostic check that could distinguish hypotheses

**Example:** checkoutservice resource saturation can have supporting CPU evidence, contradictory normal-CPU evidence, neutral request-activity evidence, and unavailable memory telemetry.

**Key message:** The system does not hide conflicting evidence just to produce a confident answer.

## Slide 6 — NLI / ML Role

A lightweight NLI component was integrated as an **experimental evidence-relation layer**. Controlled examples produced contradiction and neutral relations, including a semantically related but non-equivalent statement that remained neutral.

Exploratory participant-level grouped cross-validation was also evaluated. These models are **not claimed as deployable RCA systems**.

**Message:** Technology earns its place through evidence. We did not stack models merely to make the project look more complex.

## Slide 7 — Human Study Evidence

### Audited historical study
- 30 raw participant files
- 27 complete participants
- 3 incomplete participants
- 135 valid analysis trials
- 5 historical conditions
- 27 trials per condition

### Established project results
- Accuracy: **54.8%**
- Mean decision time: **27.3 s**
- Median decision time: **11 s**
- Mean confidence: **3.52 / 5**
- Mean workload: **3.50 / 5**
- AI followed: **63.0%**
- AI overridden: **23.7%**
- Misleading-condition accuracy: **44.4%**

### Limitation
This does not establish that IncidentIQ causally improves human accuracy because an authoritative human-only comparison is not available from this export.

## Slide 8 — Real RCAEval Validation

### Final five-case evaluation
Five real RE2-OB cases were executed through the participant-safe pipeline.

**Result:**
- 5 cases
- 2 exact root-service matches
- 2 incorrect selections
- 1 abstention
- **40% exact-match accuracy overall**
- **50% among non-abstained cases**

This is a **small case-specific benchmark result**, not general RCA accuracy, production performance, or evidence that NLI reliably identifies root cause.

**Important message:** The evaluation exposes failure and abstention cases instead of hiding them.

## Slide 9 — Research Integrity

### Controls implemented
- evaluator-only RCAEval ground truth
- no raw participant exports committed
- participant-facing leakage fix
- regression test for participant-page integrity
- no autonomous remediation
- no fabricated benchmark results
- no fabricated production telemetry
- explicit separation of verified vs unverified evidence
- research-contract scope guardrails

The project treats reproducibility and claim discipline as part of the engineering contribution.

## Slide 10 — What We Can Defensibly Claim

### Established
IncidentIQ is:
- an executable evidence-grounded human-AI decision-support workflow
- capable of representing competing hypotheses
- able to expose supporting, contradicting, neutral, and missing evidence
- able to recommend discriminating diagnostic checks
- experimentally integrated with an NLI evidence-relation layer
- validated on five gray-area telemetry conditions
- evaluated on a small five-case RCAEval execution
- supported by an audited historical five-condition participant dataset

### Not established
- causal improvement in human accuracy
- general RCA accuracy
- production telemetry validation
- validated sixth condition
- autonomous remediation

## Slide 11 — Demo Flow

1. Open the IncidentIQ browser prototype.
2. Optionally load a real public RCAEval telemetry case using `experiments/fetch_hf_demo_case.py`.
3. Introduce the incident with multiple signals.
4. Show observations and provenance.
5. Point out supporting, contradictory, and missing evidence.
6. Show the competing hypotheses.
7. Ask which next diagnostic check would distinguish them.
8. Make the human decision or abstain.
9. Emphasize: **the system supports the decision; it does not execute remediation.**

## Slide 12 — Closing

> **IncidentIQ is not trying to replace the incident engineer. It is trying to make the engineer's diagnostic reasoning more evidence-grounded, inspectable, and testable.**

### Future research
- independent historical-similarity corpus
- six-condition human study
- larger RCAEval evaluation
- production telemetry validation
- stronger controlled causal human-AI comparison

**Closing sentence:** “Our current evidence is intentionally bounded, but the system and evaluation framework are executable, auditable, and ready for the next research stage.”
