"""Minimal dependency-free local study server.

This serves participant-safe incident trials and records only participant
decisions. Evaluator labels stay outside the participant payload.
"""
from __future__ import annotations
import json, time, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HTML=(ROOT/"study.html").read_text(encoding="utf-8")
TRIALS=(ROOT/"study_trials.json").read_text(encoding="utf-8")

class Handler(BaseHTTPRequestHandler):
    def _send(self,status,body,ctype="application/json"):
        b=body.encode()
        self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=="/":
            self._send(200,HTML,"text/html; charset=utf-8")
        elif self.path=="/api/trials":
            self._send(200,TRIALS)
        elif self.path=="/api/health":
            self._send(200,json.dumps({"status":"ok","participant_safe":True}))
        else: self._send(404,json.dumps({"error":"not found"}))
    def do_POST(self):
        if self.path!="/api/trial":
            return self._send(404,json.dumps({"error":"not found"}))
        n=int(self.headers.get("Content-Length","0")); payload=json.loads(self.rfile.read(n))
        payload["server_received_at"]=time.time()
        payload["record_id"]=uuid.uuid4().hex
        Path("participant_results").mkdir(exist_ok=True)
        with open(Path("participant_results")/(payload["record_id"]+".json"),"w",encoding="utf-8") as f:
            json.dump(payload,f,indent=2)
        self._send(201,json.dumps({"record_id":payload["record_id"]}))

if __name__=="__main__":
    HTTPServer(("127.0.0.1",8000),Handler).serve_forever()
