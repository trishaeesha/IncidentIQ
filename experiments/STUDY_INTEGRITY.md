# IncidentIQ study integrity gate

The current participant harness must not be used for data collection yet.

Two concrete problems were found:

1. Participant-facing case IDs such as re2ob_checkoutservice_cpu_2 reveal the service and fault family.
2. The existing study_trials.json contains only three placeholders and does not contain the actual participant-safe telemetry evidence.

Required flow:

1. Run the real RCAEval case runner for selected cases.
2. Build an opaque participant manifest.
3. Validate every gray-area transformation against the original telemetry.
4. Enable only validated trials.
5. Randomize assignments so a participant does not see the same incident across multiple modes.
6. Collect real participant decisions.
7. Score against a separate evaluator-only answer key.
8. Report results only after actual participant records exist.

The target repeated design is 2 or more real RE2 cases × 6 conditions × 3 modes = 36 trials per complete repeated set.

The six conditions are clear, ambiguous, conflicting, incomplete, misleading, and novel.

Important: misleading and novel conditions must remain blocked until the required transformation is actually demonstrated and researcher-validated. A generated placeholder is not an experimental result.

Do not report an accuracy improvement, human study result, or deployment benefit until execution has produced auditable records.