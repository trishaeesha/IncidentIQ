# IncidentIQ Experiment Protocol

## Fixed design

Three modes are unchanged:

1. human_only
2. generic_ai
3. incidentiq

Six researcher-validated conditions are unchanged:

1. clear
2. ambiguous
3. conflicting
4. incomplete
5. misleading
6. novel

A condition is an evaluator-side label only. Participants never see it.

## Case validation

Candidate cases must be based on observable telemetry/evidence. RCAEval metadata
may identify the benchmark case and telemetry availability, but it is not itself
evidence for a gray-area condition. A candidate remains UNVALIDATED unless its
researcher record contains evidence references and a condition-specific
rationale satisfying the conservative validation gate.

No case is created solely to satisfy a quota.

## Controlled case set

The intended pool is the RCAEval RE2 suite. The target of approximately 60–90
cases is a sampling target, not a quota. Selection stops when the validated
evidence pool is exhausted.

Repeated injections of the same system/service/fault conceptual group are not
treated as independent incidents by default. The researcher must provide a
repeat_group identifier; the case selector takes at most one case per group by
default.

The final case-set report must include:

- validated and unvalidated counts
- condition distribution
- systems
- fault types
- modality availability
- repeated-case handling

No case counts are reported until the actual RCAEval telemetry has been
inspected.

## Evaluator truth

Evaluator-only records contain:

- acceptable diagnosis or diagnoses
- correct diagnostic action IDs
- unnecessary action IDs
- incorrect action IDs
- evidence needed to justify an action
- condition
- condition rationale

Participant-facing data excludes these fields and all RCAEval ground-truth
labels.

## Human procedure

For every trial:

1. Show only the participant-safe incident observations.
2. Start the trial clock.
3. Record observations and first hypothesis.
4. Record every diagnostic action and its result.
5. Record hypothesis updates.
6. Record confidence and workload.
7. Stop the clock after final diagnosis and verification.

Record timestamps for:

- first hypothesis
- first diagnostic action
- first correct hypothesis
- first correct diagnostic action
- verification
- final diagnosis

The participant never receives the condition label.

## Generic AI baseline

The generic AI receives exactly the same underlying incident information
available to the participant. It does not receive IncidentIQ supporting,
contradicting, missing-evidence, uncertainty, or hypothesis-ranking fields.

For each interaction record:

- model and model version, if available
- fixed prompt
- temperature/settings, if available
- input evidence
- output
- timestamp
- extracted recommendation(s)

The prompt and settings are fixed before the study. Provider/model changes are
documented as protocol deviations rather than silently mixed.

## IncidentIQ mode

IncidentIQ receives the same underlying incident evidence through the existing
Evidence Engine and produces its existing hypothesis/decision outputs. The
evaluation layer only records what is presented to the participant.

No evaluator truth is passed into Friend 1 or Friend 2.

## Carryover prevention

Within one participant:

- a case is assigned to at most one mode
- conceptual repeat groups are not repeated
- case order is randomized from a preregistered seed
- mode assignment is balanced across participants when feasible

The deterministic trial ID is derived from participant, case, mode, and seed.

## Pilot

Before a larger study, run a small pilot only to test protocol mechanics:

- confusing instructions
- broken or missing telemetry
- impossible diagnostic actions
- timing and logging
- leakage
- too-easy cases
- impossibly difficult cases

Pilot observations are protocol-quality findings. They are not research outcomes
and must not be presented as evidence that one mode is better.

## Analysis

Report overall and condition-wise results for all three modes. Primary outcomes:

- final diagnosis accuracy
- time to correct hypothesis
- time to correct action
- unnecessary actions
- incorrect actions
- verification time

Secondary outcomes:

- confidence
- confidence error/calibration proxy
- AI-following
- AI-overriding
- incorrect AI-following
- correct AI-following
- correct AI-override
- workload

Do not predetermine a winning mode. Report estimates with sample sizes and
uncertainty, and avoid unsupported causal claims.

## Integrity checklist

Before analysis, verify:

- no ground-truth leakage
- no condition-label leakage
- no repeated-case leakage
- no train/test contamination
- no temporal leakage
- fair generic-AI input
- evidence-backed condition validation
- no fabricated participant results
- no unsupported statistical claims
- no duplicate conceptual cases
- missing telemetry is not automatically labeled incomplete
- evidence availability is not treated as evidence difficulty
