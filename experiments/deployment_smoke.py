"""Deployment smoke test for the standard-library IncidentIQ API."""
from __future__ import annotations
import json,subprocess,sys,time,urllib.request,os

proc=subprocess.Popen([sys.executable,"app.py"],env={**os.environ,"PORT":"8099"})
try:
    time.sleep(0.8)
    with urllib.request.urlopen("http://127.0.0.1:8099/health",timeout=3) as r:
        health=json.loads(r.read())
    assert health["status"]=="ok"

    payload={"evidence":[
        {"case_id":"smoke","source":"metrics","service":"checkoutservice",
         "observation":"CPU utilization increased during incident",
         "direction":"increase","magnitude":0.8,"evidence_strength":"strong",
         "availability":"available","signal":"cpu"}
    ]}
    req=urllib.request.Request("http://127.0.0.1:8099/analyze",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=3) as r:
        result=json.loads(r.read())
    assert "hypotheses" in result and "decision" in result
    print("deployment smoke test: PASS")
finally:
    proc.terminate()
    proc.wait(timeout=3)
