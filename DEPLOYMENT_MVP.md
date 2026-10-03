# IncidentIQ deployment MVP

## Scope

Read-only incident decision support.

### Input
- incident identifier
- metrics
- logs
- traces
- injection/deployment time when available

### Pipeline
1. normalize telemetry
2. extract factual evidence
3. generate candidate hypotheses
4. classify supporting / contradicting / missing evidence
5. estimate qualitative uncertainty
6. select a hypothesis only above the safety threshold
7. otherwise abstain and surface discriminating checks

### Safety boundary

IncidentIQ does not:
- execute production remediation
- expose evaluator-only labels
- claim causality from temporal correlation alone
- treat confidence as calibrated probability

### MVP API

POST /incident/analyze

Returns:
- structured evidence
- candidate hypotheses
- uncertainty
- selected hypothesis or abstention
- next diagnostic check
- provenance references

### Monitoring

Track:
- abstention rate
- incorrect-selection rate
- evidence extraction failures
- latency
- schema violations
- telemetry modality availability

### Human control

Every recommendation is reviewable. The system cannot autonomously apply remediation.
