# IncidentIQ Participant Run Guide

Use one participant-safe assignment at a time. Do not give participants researcher_pool, evaluator files, condition labels, or ground truth.

Launch:

`python experiments/study_server.py --manifest /path/to/P01/study_manifest_participant.json --port 8000`

Then open `http://127.0.0.1:8000`.

Each assignment contains five opaque trials. The server accepts only the participant-safe fields defined by the study protocol and writes raw records under the selected assignment directory.

After collection, copy the participant_results directories into one researcher-only records directory. Then run the evaluator scoring pipeline followed by `analyze_human_study.py`.

Never edit participant answers to make them fit the expected result. If a record is malformed, preserve it and document the exclusion.