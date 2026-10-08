# IncidentIQ Research Expansion Status

Updated: 2026-10-08

## 1. Expanded RCAEval benchmark

The previous verified benchmark contained five RE2-OB cases.

The GitHub Actions workflow has now been expanded to select **18 real RE2 cases at runtime**:
- RE2-OB: one case for each of the six fault types
- RE2-SS: one case for each of the six fault types
- RE2-TT: one case for each of the six fault types

Selection is deterministic from the public RCAEval case index and requires telemetry-backed cases with logs. Ground-truth labels are used only by the evaluator and are not passed into the IncidentIQ inference command.

### Status

**Infrastructure complete. Execution result pending verification.**

Do not report an 18-case accuracy number until the GitHub Actions execution completes successfully and the evaluator artifact has been inspected.

## 2. Sixth condition

The sixth research condition is:

**Novel / historical mismatch**

The project will only call this condition validated when:
1. an independent historical/reference corpus exists;
2. the reference corpus is separated from the evaluation cases;
3. similarity is computed without using evaluator-only root-cause labels;
4. the candidate case has traceable telemetry provenance;
5. the mismatch threshold is fixed before evaluation;
6. researcher review confirms the candidate represents a genuine historical mismatch rather than simply a different fault label.

### Status

**Candidate validation remains a scientific evidence step, not a documentation blocker.**

No synthetic case is being relabeled as validated.

## 3. Six-condition human study

The existing participant export remains a completed five-condition historical study:
- 30 raw participant files
- 27 complete participants
- 3 incomplete participants
- 135 valid analysis trials

The six-condition study cannot be honestly marked complete without a validated sixth condition and a new participant collection.

### What is already ready

- participant-safe architecture
- evaluator-only ground truth boundary
- three experimental arms in the research contract
- condition-level outcome schema
- participant leakage regression test
- export/audit workflow

### What remains

- validate the sixth condition
- freeze six-condition case manifest
- deploy a new six-condition study configuration
- collect new participants
- analyze the new dataset

## 4. Production telemetry

Production telemetry cannot be completed from the repository alone because no independently authorized production telemetry source is currently connected.

The correct next implementation is a telemetry adapter against a real source, followed by schema/security/runtime validation. Until then, simulated/live-demo evidence must remain explicitly labeled as simulated.

## Claim discipline

The expanded benchmark and study preparation must never be reported as completed experimental evidence until execution or participant collection has actually occurred.
