"""IncidentIQ product prototype server.

Serves a small, RCAEval-derived demonstration set and runs the existing
HypothesisEngine + DecisionEngine on the evidence. No evaluator ground truth
is loaded into the diagnostic pipeline.
"""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "prototype" / "demo_cases.json"
HTML = Path(__file__).resolve().parent / "prototype.html"
sys.path.insert(0, str(ROOT))
from src.models import HypothesisEngine, DecisionEngine

CASES = json.loads(DATA.read_text(encoding="utf-8"))["cases"]
# Prefer the complete validated study evidence when the generated pool exists.
# The committed demo file remains the offline fallback.
POOL = ROOT / "experiments" / "participant_pool_assisted.json"
if POOL.exists():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    complete = {}
    for trial in pool.get("trials", []):
        complete.setdefault(trial["public_case_id"], {"public_case_id": trial["public_case_id"], "evidence": trial.get("evidence", [])})
    if len(complete) == len(CASES):
        CASES = list(complete.values())
CASE_MAP = {c["public_case_id"]: c for c in CASES}

def investigate(case):
    evidence = case["evidence"]
    hypotheses = HypothesisEngine().infer(evidence)
    decision = DecisionEngine().decide(hypotheses)
    return {
        "public_case_id": case["public_case_id"],
        "evidence": evidence,
        "hypothesis_status": hypotheses.get("status"),
        "hypotheses": hypotheses.get("hypotheses", []),
        "decision": decision,
        "research_integrity": {
            "ground_truth_in_pipeline": False,
            "human_control_required": decision.get("human_control_required", True),
            "demo_evidence_is_sample": True,
        },
    }

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/health":
            self.send_json(200, {"status": "ok", "cases": len(CASES)})
            return
        if self.path == "/api/cases":
            self.send_json(200, {
                "schema_version": 1,
                "source": "validated RCAEval-derived evidence samples",
                "cases": [{"public_case_id": c["public_case_id"],
                           "evidence_count": len(c["evidence"])} for c in CASES],
            })
            return
        if self.path.startswith("/api/investigate/"):
            case_id = self.path.rsplit("/", 1)[-1]
            case = CASE_MAP.get(case_id)
            if not case:
                self.send_json(404, {"error": "unknown case"})
                return
            self.send_json(200, investigate(case))
            return
        self.send_json(404, {"error": "not found"})

if __name__ == "__main__":
    print("IncidentIQ prototype: http://127.0.0.1:8010")
    HTTPServer(("127.0.0.1", 8010), Handler).serve_forever()
