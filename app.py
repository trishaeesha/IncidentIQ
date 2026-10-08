"""IncidentIQ interactive decision-support runtime."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from src.models import DecisionEngine, HypothesisEngine
try:
    from src.nlp.nli_evidence import NLIEvidenceInterpreter
except Exception:
    NLIEvidenceInterpreter = None
INDEX = Path(__file__).resolve().parent / "static" / "index.html"

class Handler(BaseHTTPRequestHandler):
    def _send(self,status,payload,content_type="application/json"):
        body = payload.encode() if content_type=="text/html" else json.dumps(payload,indent=2).encode()
        self.send_response(status); self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path in ("/","/index.html"):
            return self._send(200,INDEX.read_text(encoding="utf-8"),"text/html") if INDEX.exists() else self._send(404,{"error":"frontend_not_found"})
        if self.path=="/health":
            return self._send(200,{"status":"ok","service":"incidentiq","nlp_available":NLIEvidenceInterpreter is not None})
        self._send(404,{"error":"not_found"})
    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length","0")); payload=json.loads(self.rfile.read(n))
        except Exception as e: return self._send(400,{"error":f"invalid_json: {e}"})
        if self.path=="/analyze":
            try:
                evidence=payload.get("evidence",[])
                if not isinstance(evidence,list): raise ValueError("evidence must be a list")
                h=HypothesisEngine().infer(evidence); d=DecisionEngine().decide(h)
                return self._send(200,{"hypotheses":h,"decision":d})
            except Exception as e: return self._send(400,{"error":str(e)})
        if self.path=="/nli":
            if NLIEvidenceInterpreter is None:
                return self._send(503,{"error":"NLI unavailable","message":"Install requirements-nlp.txt"})
            try:
                r=NLIEvidenceInterpreter().classify(str(payload.get("evidence","")).strip(),str(payload.get("hypothesis","")).strip())
                return self._send(200,{"evidence":r.evidence,"hypothesis":r.hypothesis,"relation":r.relation,"score":r.score})
            except Exception as e: return self._send(503,{"error":str(e)})
        self._send(404,{"error":"not_found"})
    def log_message(self,format,*args): pass

if __name__=="__main__":
    import os
    ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),Handler).serve_forever()
