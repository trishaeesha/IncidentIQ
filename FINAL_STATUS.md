# IncidentIQ Final Submission Status

Updated: 2026-10-08

This matrix reflects the repository and GitHub Actions evidence actually verified during the final audit. It does not promote unverified experiments to results.

| Area | Status | Factual reason |
|---|---|---|
| Core architecture | VERIFIED | Evidence -> hypotheses -> decision-support runtime is integrated and documented as human-controlled. |
| Deterministic evidence engine | VERIFIED | Evidence extraction/provenance path is implemented and covered by CI tests. |
| Hypothesis engine | VERIFIED | Competing hypotheses, support/contradiction/missing evidence, uncertainty, and diagnostic checks are implemented. |
| Decision engine | VERIFIED | Human-controlled selection/abstention and discriminating action recommendation are implemented. |
| Human control | VERIFIED | Runtime explicitly requires human review and performs no autonomous remediation. |
| Browser runtime | VERIFIED | Existing runtime/browser verification is recorded in RESEARCH_STATUS.md. |
| API runtime | VERIFIED | /health and /analyze were previously executed successfully; latest CI also passes. |
| NLI | VERIFIED RUNTIME / EXPERIMENTAL SEMANTICS | Runtime inference was observed locally; three controlled examples are recorded. Broad NLI benchmark quality is not claimed. |
| Participant audit | VERIFIED | Raw export audit reproduced 30 raw participant files, 140 raw trials, 27 complete participants, 3 incomplete, and 135 valid analysis trials. |
| Statistics | VERIFIED BOUNDED | Descriptive and previously executed inferential results are recorded; missing statistics are not invented. |
| Calibration | VERIFIED BOUNDED | Confidence/correctness patterns are reported descriptively; the 1-5 scale is not treated as probability calibration. |
| AI follow/override | VERIFIED BOUNDED | Observed difference was not statistically significant; no causal improvement claim is made. |
| Participant-level analysis | VERIFIED | Participant accuracy range and complete/incorrect participant counts are documented. |
| Exploratory ML | VERIFIED BOUNDED | Grouped CV AUC results are treated as exploratory and non-deployable. |
| Participant leakage | VERIFIED AFTER FIX | Public participant page no longer ships the stale hardcoded case-condition block or explicit root-cause wording; a regression test now guards this. |
| FNRD research harness | VERIFIED | Research-validation workflow passed compilation, report regression, prototype smoke test, telemetry validation, pool construction, and cohort validation. |
| RCAEval loader | VERIFIED | Local loader and evaluator-separated runner are implemented and tested. |
| RCAEval five-case evaluation | VERIFIED | GitHub Actions run 37799770349 executed five real RE2-OB cases and evaluator scoring completed successfully: 2/5 exact root-service matches (40% overall), 2 incorrect selections, and 1 abstention. Non-abstained exact-match accuracy was 2/4 (50%). |
| Sixth novel/historical-mismatch condition | BLOCKED / EXCLUDED | No independent historical-similarity/reference corpus was validated; the experiment freeze explicitly excludes this condition rather than manufacturing it. |
| Real production telemetry | BLOCKED | No production telemetry source is connected or independently verified. Simulated/live-demo evidence remains clearly bounded. |
| Current participant study | PARTIALLY VERIFIED | A real 30-participant five-case historical study exists and is audited. It is not the final six-condition study defined by the research contract. |
| CI | VERIFIED | Latest IncidentIQ CI run on integration/incidentiq-complete succeeded after the participant-page fix sequence; new commits trigger the same gate. |
| Documentation | PARTIALLY VERIFIED | Core research status and position documents were aligned with verified evidence; final paper/submission narrative still needs the bounded five-condition participant-study limitation carried through. |
| Final report | READY FOR FINAL NARRATIVE | The verified five-case RCAEval result, participant-study boundary, and production-telemetry limitation are now recorded. A final narrative/report can be prepared without adding new scientific claims. |
| Submission package | READY WITH EXPLICIT LIMITATIONS | Source/tests/docs are present. Submission must disclose the 40% five-case RCAEval result, no production telemetry, and the legacy five-condition participant-study boundary. |

## Non-negotiable final claims

Allowed:
- IncidentIQ is evidence-grounded human-AI decision support.
- IncidentIQ preserves competing hypotheses and recommends discriminating diagnostic checks.
- NLI runtime integration was verified experimentally.
- The five gray-area telemetry cells were validated from actual RCAEval telemetry in GitHub Actions.
- The 30-participant historical five-condition dataset was audited and analyzed within its evidence boundary.

Not established:
- AI following improves accuracy.
- IncidentIQ improves human accuracy causally.
- NLI determines root cause reliably.
- The novel/historical-mismatch condition is validated.
- Production real-time telemetry is validated.
- Autonomous remediation is supported.

## Open repository hygiene note

Several older PRs remain open for historical work. The current integration branch must remain the source of truth; divergent research branches must not be merged wholesale merely to close those PRs.
