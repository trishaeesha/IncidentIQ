# IncidentIQ Participant + Coordinator Study Site

30-participant controlled human-AI decision study interface.

- P01-P10: human-only
- P11-P20: generic AI assistance
- P21-P30: IncidentIQ assistance
- 5 trials per participant
- Diagnosis: multiple-choice
- Confidence: selectable 1-5
- Workload: selectable 1-5
- AI follow/override recorded where applicable
- Server-side participant assignment and locking
- Coordinator: status + individual ZIP + combined ZIP

GitHub Pages is static hosting and cannot safely be the shared database. backend/Code.gs is a Google Apps Script backend using a Google Sheet for shared state/results.

Before distributing the QR: deploy the backend, set web/config.js API_BASE, publish the site, test reserve/resume/save/finalize/coordinator/export, then generate the QR.

This repository currently is private. On GitHub Free, Pages for private repositories is not available; make the repository public or use a plan that supports private Pages.
