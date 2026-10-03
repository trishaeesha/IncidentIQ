"""Minimal IncidentIQ decision-support API using only the standard library."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from src.models import DecisionEngine, HypothesisEngine


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "service": "incidentiq"})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/analyze":
            self._send(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            evidence = payload.get("evidence", [])
            if not isinstance(evidence, list):
                raise ValueError("evidence must be a list")
            hypotheses = HypothesisEngine().infer(evidence)
            decision = DecisionEngine().decide(hypotheses)
            self._send(200, {"hypotheses": hypotheses, "decision": decision})
        except Exception as exc:
            self._send(400, {"error": str(exc)})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
