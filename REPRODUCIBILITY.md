# Reproducibility Guide

## Purpose

This document describes how to reproduce the IncidentIQ research analysis.

## Environment

- Python 3.x
- pytest
- pandas
- scikit-learn
- NumPy
- matplotlib

## Participant Analysis

The participant analysis uses validated trial-level participant data.

Primary target:
- diagnosis_correct

Secondary measures:
- elapsedSeconds
- confidence
- workload
- aiFollowed
- aiOverridden

Participant identity is used only for grouped evaluation and is not used as a predictive feature.

## Validation

Run:

python -m pytest -q tests

Run participant analysis:

python .\ml\src\participant_analysis.py

Run condition analysis:

python .\ml\src\condition_analysis.py

Run research relationships:

python .\ml\src\research_relationships.py

Run participant ML analysis:

python .\ml\src\participant_ml.py

Run visualizations:

python .\ml\src\participant_visualizations.py

## RCAEval

RCAEval cases are used for evidence and telemetry analysis.

Only cases actually available and successfully executed should be reported as executed.

No RCAEval ground-truth metadata is used as telemetry input.

## NLP

The NLP component provides lightweight evidence-to-hypothesis analysis.

NLI results must be recorded from actual execution and must not be changed to match an expected outcome.

## Reproducibility Rules

- Do not fabricate experimental results.
- Do not claim execution when a component was not executed.
- Do not use participant identifiers as predictive features.
- Do not claim causal effects from exploratory analysis.
- Do not claim autonomous root-cause analysis.
- Keep raw participant and study configuration data private.
