# IncidentIQ ML/NLP Analysis

## Purpose

This directory contains the reproducible ML/NLP feature-engineering pipeline for IncidentIQ.

## Current dataset

The currently available RCAEval validation dataset contains 3 incident cases:

- checkoutservice CPU stress
- checkoutservice memory stress
- user-service network packet loss

The dataset contains evidence-derived structured features and lightweight NLP indicators.

## NLP features

The NLP pipeline detects interpretable indicators for:

- uncertainty
- conflict
- errors
- network
- CPU
- memory
- latency

## Important limitation

Only 3 RCAEval cases are currently available locally.

Therefore, these data are used to validate the feature-engineering and NLP pipeline only.

No predictive ML model is claimed from these 3 cases.

The original IncidentIQ participant study requires the 27-participant / 135-trial dataset for valid participant-aware ML evaluation.

## Leakage prevention

Participant identifiers must not be used as predictive features.

When participant-level study data become available, train/test splitting must group trials by participantId using GroupKFold or StratifiedGroupKFold.

Ground-truth diagnosis must never be provided as an input feature.

## Research connection

The final participant dataset should evaluate associations between:

- evidence conditions and diagnostic correctness
- conflicting evidence and incorrect decisions
- misleading evidence and incorrect decisions
- uncertainty and elapsed diagnosis time
- evidence completeness and confidence
- AI following and correctness
- AI overriding and correctness

## Current outputs

- rcaeval_features.csv
- nlp_features.csv
- combined_features.csv
- rcaeval_analysis_features.csv
- dataset_summary.csv
- model_metrics.csv
- feature_importance.csv

## Status

RCAEval feature engineering and lightweight NLP validation completed.

Participant-level predictive ML is pending the original 135-trial study dataset.
