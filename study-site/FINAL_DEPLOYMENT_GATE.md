# IncidentIQ Study — Final Deployment Gate

## What is already in this repository

- One participant entry page for all 30 participants.
- P01-P10: human-only.
- P11-P20: generic AI assistance.
- P21-P30: IncidentIQ assistance.
- Participants never see the assistance category.
- Exactly 5 trials per participant.
- Exactly 2 diagnosis options per trial.
- Confidence 1-5 and workload 1-5 are required.
- AI follow/override is recorded for assistance arms.
- Participant IDs are server-assigned and locked.
- Each participant gets a unique order of the five case types.
- Test mode uses ?mode=test and does not consume a participant slot.
- Resume continues at the first incomplete trial.
- Coordinator tracker shows P01-P30 and internal assistance category.
- Coordinator can release an unused reserved slot.
- Individual ZIP: Pxx.zip containing Pxx.json.
- Combined ZIP: IncidentIQ_all_participants.zip containing P01.json through P30.json.

## Required human deployment actions

The connected GitHub account is currently showing the repository as private. GitHub Pages is available on GitHub Free for public repositories; therefore, if the account remains on Free, the repository must be made public before GitHub Pages can publish it.

1. Open repository Settings → General → change repository visibility to Public.
2. Open Settings → Pages.
3. Under Build and deployment, select GitHub Actions.
4. Create a Google Sheet owned by the coordinator.
5. Open Extensions → Apps Script.
6. Paste study-site/backend/Code.gs.
7. Replace PASTE_GOOGLE_SHEET_ID_HERE with the Sheet ID.
8. Replace CHANGE_THIS_COORDINATOR_KEY with a private coordinator key.
9. In Apps Script: Deploy → New deployment → Web app.
10. Execute as: Me.
11. Who has access: Anyone.
12. Copy the Web App URL ending in /exec.
13. Put that URL into study-site/web/config.js as API_BASE.
14. Commit/push the changed config.js.
15. Wait for the GitHub Pages deployment to finish.
16. Open the participant Pages URL and test using ?mode=test.
17. Test the coordinator page separately with the coordinator key.
18. Only after both tests pass, use the normal participant URL to reserve a real slot.
19. Generate/distribute the QR only for the normal participant URL, never the test URL.

## Important

Do not put the Google Sheet ID or coordinator key into public chat, screenshots, or participant instructions.
The QR is intentionally not finalized until the public Pages URL and Apps Script /exec backend have both been verified. A QR to an unconfigured URL would be misleading.