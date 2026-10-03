# Scripts

Scripts in this directory must be reproducible and safe to run locally.

Rules:
- Never hard-code credentials.
- Never commit raw RCAEval telemetry.
- Read local paths from configs/local.yaml or command-line arguments.
- Keep downloads and generated artifacts outside tracked source files.
- Every script should clearly state whether it downloads data, transforms data, or runs an experiment.
