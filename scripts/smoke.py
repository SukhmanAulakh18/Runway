"""Smoke-test a running Runway server (local, Docker or Cloud Run) against the answer key and the pitch numbers.

Run:  python scripts/smoke.py http://localhost:8080      -> one line per check, exit code 1 on any failure
"""
import json
import sys
import time
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")


def call(path, body=None):
    req = urllib.request.Request(BASE + path, json.dumps(body).encode() if body is not None else None,
                                 {"Content-Type": "application/json"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r) if "json" in r.headers.get("Content-Type", "") else r.read().decode(), time.time() - t


CHECKS = [
    ("health: 4,500 accounts", lambda: call("/api/health")[0]["accounts"] == 4500),
    ("dashboard page is served", lambda: "<div id=\"root\">" in call("/")[0]),
    ("answer key: 20111 job loss = 3.4 months",
     lambda: call("/api/shock/20111", {"scenario": {"job_loss": True}})[0]["standard"]["label"] == "3.4 months"),
    ("answer key: 20111 one month repair = 4.0 months",
     lambda: call("/api/shock/20111", {"scenario": {"one_off_months_of_spending": 1.0}})[0]["standard"]["label"] == "4.0 months"),
    ("pitch: 93172 at Dec 2024 looks fine, realistic 2.4 months",
     lambda: (lambda c: c["standard_runway"]["label"] == "no shortfall (120+)" and c["realistic_runway"]["label"] == "2.4 months")(
         call("/api/customer/93172?asof=2024-12")[0])),
    ("evidence: survival, challenger, buffer confidence present",
     lambda: all(k in call("/api/evidence")[0] for k in ("survival", "challenger", "buffer_confidence", "out_of_time"))),
    ("twist card reads job loss", lambda: call("/api/twist", {"text": "They lose their job"})[0]["settings"]["job_loss"]),
    ("plan answers in under 10 s", lambda: call("/api/plan/93172", {"scenario": {}, "asof": "2024-12"})[1] < 10),
]

failed = 0
for name, check in CHECKS:
    try:
        ok = bool(check())
    except Exception as exc:   # report and keep going: one broken endpoint shouldn't hide the others
        ok, name = False, f"{name} ({exc})"
    failed += not ok
    print(("PASS " if ok else "FAIL ") + name)
print(f"{len(CHECKS) - failed} of {len(CHECKS)} passed against {BASE}")
sys.exit(1 if failed else 0)
