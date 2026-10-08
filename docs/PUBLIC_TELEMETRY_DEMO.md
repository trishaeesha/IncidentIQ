# IncidentIQ — Public Telemetry Demo

## Use real public RCAEval telemetry without exposing evaluator labels

RCAEval provides public multi-source microservice failure cases with metrics, logs and, for applicable systems, traces.

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install huggingface_hub
```

### 2. Fetch one demo case

```bash
python experiments/fetch_hf_demo_case.py
```

Default case:

```text
re2ob_checkoutservice_cpu_2
```

### 3. Run IncidentIQ on the telemetry

```bash
python experiments/run_real_rcaeval_case.py --data-root demo_data --case re2ob_checkoutservice_cpu_2
```

### 4. What to show in the presentation

Use the output to demonstrate:

1. real public telemetry enters IncidentIQ;
2. evidence is extracted with provenance;
3. multiple services/signals can be observed;
4. competing hypotheses are generated;
5. supporting, contradicting and missing evidence are surfaced;
6. the system can recommend a discriminating diagnostic check;
7. the human remains in control.

### Important distinction

This is **public benchmark telemetry**, not production telemetry.

The demo does not prove production performance. RCAEval ground-truth labels remain evaluator-only and are not passed into the IncidentIQ inference pipeline.

The public RCAEval dataset contains 735 failure cases across RE1, RE2 and RE3. RE2 contains 270 multi-source cases across Online Boutique, Sock Shop and Train Ticket.
