"""Dependency-free participant study server.

Only a generated participant assignment is served. It must contain an opaque
TRIAL identifier and participant_id; condition labels and evaluator truth are
never accepted from the browser.
"""
from __future__ import annotations
import json
import time
import uuid
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DEFAULT_MANIFEST=ROOT/"study_manifest_participant.json"
HTML=ROOT/"study.html"

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',type=Path,default=DEFAULT_MANIFEST)
    p.add_argument('--port',type=int,default=8000)
    return p.parse_args()

ARGS=parse_args()
MANIFEST=ARGS.manifest.resolve()

if not MANIFEST.exists():
    raise SystemExit("Missing study_manifest_participant.json. Build the researcher manifest and create a participant assignment first.")

TRIALS=json.loads(MANIFEST.read_text(encoding="utf-8"))
if not TRIALS.get("participant_safe") or not TRIALS.get("participant_id"):
    raise SystemExit("Participant assignment is missing participant_safe or participant_id.")

for trial in TRIALS.get("trials", []):
    trial_id=str(trial.get("trial_id",""))
    if not trial_id.startswith("TRIAL-"):
        raise SystemExit("Participant assignment contains a non-opaque trial ID.")
    if "condition" in trial or "condition_rationale" in trial:
        raise SystemExit("Participant assignment leaks experimental condition metadata.")

class Handler(BaseHTTPRequestHandler):
    def send_json(self,status,payload):
        body=json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path=="/":
            body=HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path=="/api/trials":
            self.send_json(200,TRIALS)
        elif self.path=="/api/health":
            self.send_json(200,{"status":"ok","participant_safe":True,"trial_count":TRIALS.get("trial_count",0)})
        else:
            self.send_json(404,{"error":"not found"})

    def do_POST(self):
        if self.path!="/api/trial":
            return self.send_json(404,{"error":"not found"})
        length=int(self.headers.get("Content-Length","0"))
        payload=json.loads(self.rfile.read(length))
        if payload.get("participant_id") != TRIALS["participant_id"]:
            return self.send_json(400,{"error":"participant mismatch"})
        allowed={"trial_id","participant_id","public_case_id","mode","start_time","end_time",
                 "elapsed_seconds","final_diagnosis","confidence","diagnostic_actions",
                 "decision_events","workload_score","actions_followed","actions_overridden"}
        payload={k:v for k,v in payload.items() if k in allowed}
        payload["server_received_at"]=time.time()
        payload["record_id"]=uuid.uuid4().hex
        results_dir=MANIFEST.parent/"participant_results"
        results_dir.mkdir(exist_ok=True)
        out=results_dir/(payload["record_id"]+".json")
        out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
        self.send_json(201,{"record_id":payload["record_id"]})

if __name__=="__main__":
    print(f"Participant study server: http://127.0.0.1:{ARGS.port}")
    HTTPServer(("127.0.0.1",ARGS.port),Handler).serve_forever()
