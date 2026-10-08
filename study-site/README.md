# IncidentIQ Participant + Coordinator Study Site

> **Do not distribute this site for the current final study without reconciling it with the current research contract.**

This folder contains the earlier 30-participant study interface (P01-P30, three arms, five cases). The current research harness defines the final controlled study as **three modes across six incident conditions** with participant-safe opaque assignments.

The older interface is retained for historical reproducibility and must not be presented as the current six-condition study.

## Research-integrity rule

Before any new participant launch:
- use the current research-harness participant assignments
- do not expose condition labels, condition rationales, evaluator ground truth, or source-case identifiers
- do not fabricate missing participant responses
- run the participant-safe validation and cohort checks first

The participant page and backend have been hardened so the legacy interface no longer sends condition labels in participant trial payloads, and the misleading case wording no longer states the injected root cause.

The current final study still requires a real participant-data collection run before new human-study results can be claimed.

## Legacy deployment notes

GitHub Pages is static hosting and cannot safely be the shared database. backend/Code.gs uses a Google Apps Script backend with a Google Sheet for shared state/results.

Before using this legacy interface for reproducibility testing: deploy the backend, set web/config.js API_BASE, publish the site, and test reserve/resume/save/finalize/coordinator/export.
