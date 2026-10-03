# IncidentIQ Team Workflow

## Goal
All team members work from the same GitHub repository and the same codebase. Raw RCAEval telemetry stays on local machines and is never committed.

## Repository
- Remote: trishaeesha/IncidentIQ
- Main branch: main
- Work must happen on feature branches.
- Do not directly edit main for implementation work.

## Branch naming
Use:
- feature/<short-name>
- fix/<short-name>
- experiment/<short-name>

Examples:
- feature/data-loader
- feature/evidence-engine
- feature/web-ui
- experiment/gray-area-evaluation

## Data sharing
Do NOT upload:
- *.parquet
- raw logs
- raw traces
- large telemetry archives
- secrets or API keys

Share only:
- case IDs
- lightweight metadata/manifests
- preprocessing code
- experiment configuration
- derived small results when appropriate

## Team split
Suggested responsibilities:
1. Core pipeline: data loading + preprocessing
2. Evidence: evidence extraction + support/contradiction/missing representation
3. Models: hypothesis/decision components
4. Evaluation/UI: evaluation pipeline + prototype interface

Everyone pulls the latest main branch before starting work.

## Integration rule
A feature is not considered complete until:
1. code runs locally,
2. tests or a reproducible manual check exist,
3. no raw dataset is added to Git,
4. the branch is pushed,
5. a pull request is opened against main.

## Research rule
Do not change the agreed IncidentIQ research setup without recording the reason and discussing the evidence first.
