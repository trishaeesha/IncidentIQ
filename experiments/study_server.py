"""Dependency-free participant study server.

Only a generated participant-safe manifest is served. Ground truth and gray-area
labels must remain in researcher-only files.
"""
from __future__ import annotations
import json
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/"study_manifest_participant.json"
HTML=ROOT/"study.html"

if not MANIFEST.exists():
    raise SystemExit("Missing study_manifest_participant.json. Build and validate the study manifest first.")

TRIALS=json.loads(MANIFEST.read_text(encoding="utf-8"))
if not TRIALS.get("participant_safe"):
    raise SystemExit("Participant manifest is not marked participant_safe.")

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
        payload["server_received_at"]=time.time()
        payload["record_id"]=uuid.uuid4().hex
        Path("participant_results").mkdir(exist_ok=True)
        out=Path("participant_results")/(payload["record_id"]+".json")
        out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
        self.send_json(201,{"record_id":payload["record_id"]})

if __name__=="__main__":
    HTTPServer(("127.0.0.1",8000),Handler).serve_forever()
