"""Contract tests for api.py: the React dashboard must show the same numbers as the engine and Streamlit."""
import pytest
from fastapi.testclient import TestClient

import api

client = TestClient(api.app)
TWISTS = [({"job_loss": True}, "3.4 months"), ({"one_off_months_of_spending": 1.0}, "4.0 months"),
          ({"job_loss": True, "bills_increase_pct": 0.15}, "3.4 months")]


def test_health_and_accounts():
    assert client.get("/api/health").json()["accounts"] == 4500
    ids = client.get("/api/accounts").json()
    assert len(ids) == 4500 and 93172 in ids


@pytest.mark.parametrize("scenario,label", TWISTS)
def test_answer_key_20111(scenario, label):
    r = client.post("/api/shock/20111", json={"scenario": scenario}).json()
    assert r["standard"]["label"] == label


def test_time_machine_pitch_moment():
    c = client.get("/api/customer/93172", params={"asof": "2024-12"}).json()
    assert c["standard_runway"]["label"] == "no shortfall (120+)"
    assert c["trough"]["bottom_10"] and c["risk"]["validated_population"]
    assert c["risk"]["p_12m"] == pytest.approx(0.040, abs=0.002)
    assert c["history"][-1]["month"] == "2024-12"                       # no lookahead
    assert c["what_happened_next"][0]["days_below_zero"] == 13          # January 2025 reveal


def test_errors():
    assert client.get("/api/customer/1").status_code == 404
    assert client.get("/api/customer/20111", params={"asof": "2019-12"}).status_code == 422
    assert client.post("/api/shock/20111", json={"asof": "nope"}).status_code == 422


def test_plan_leads_with_cushion_and_writes_verified_text():
    p = client.post("/api/plan/93172", json={"scenario": {"job_loss": True}, "asof": "2024-12"}).json()
    assert p["cushion"]["buffer"] > 0 and "chance_6_months_pct" not in p["facts"]
    w = client.post("/api/write-plan", json=p["facts"]).json()
    assert w["source"] == "template" and w["text"].startswith("To stay out of overdraft")


def test_twist_card_chips():
    t = client.post("/api/twist", json={"text": "They lose their job (EI at 55%) and their household bills go up 15%"}).json()
    assert t["chips"] == ["Job loss: EI 55% for 6 months", "Household bills +15%"]


def test_watchlist_reveal_matches_evidence():
    w = client.get("/api/watchlist", params={"asof": "2024-12"}).json()
    assert len(w["rows"]) == 50 and w["reveal"]["top_hit"] == 14


def test_portfolio_and_evidence():
    pts = client.post("/api/portfolio", json={"scenario": {"job_loss": True}}).json()
    assert pts[0]["month"] == 0 and len(pts) == 25
    assert client.get("/api/evidence").json()["multiple_testing"]["survive"] == 28
