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
    assert c["risk"]["p_12m"] == pytest.approx(0.138, abs=0.002)   # was 0.040 before its new $4,638/month loan was counted (Nov 8)
    assert c["realistic_runway"]["label"] == "2.4 months"              # was 26.7 months: the new loan payment is now owed
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


def test_committed_outflows_today_only():
    today = client.get("/api/customer/93172").json()["committed"]
    assert today is None or today["total"] > 0
    assert client.get("/api/customer/93172", params={"asof": "2024-12"}).json()["committed"] is None   # 2025 snapshot: no lookahead


@pytest.mark.parametrize("lang", ["en", "fr"])
def test_brief_and_message_offline_templates_verify(lang):
    import ai
    b = client.post("/api/ai/brief/93172", params={"asof": "2024-12"}).json()
    m = client.post("/api/ai/message/93172", params={"asof": "2024-12", "lang": lang}).json()
    assert b["source"] == m["source"] == "template" and "$6,527" in b["text"]
    facts = api._facts(93172, "2024-12")
    assert ai.verify_numbers(b["text"], facts) and ai.verify_wording(b["text"], facts)
    msg_facts = {k: facts[k] for k in ("lowest_balance_6_months", "cushion")}
    assert ai.verify_numbers(m["text"], msg_facts) and ai.verify_wording(m["text"], msg_facts)
    assert "%" not in m["text"]   # no risk numbers go to the customer
    assert client.post("/api/ai/message/93172", params={"lang": "de"}).status_code == 422


def test_shock_includes_verdict():
    v = client.post("/api/shock/20111", json={"scenario": {"job_loss": True, "bills_increase_pct": 0.15}}).json()["verdict"]
    assert v["answer"] == "no" and v["headline"].startswith("No.") and "1 of 10" in v["futures"]


def test_repeat_uses_no_future_rates():
    today = client.get("/api/customer/93172").json()["repeat"]
    assert today["tested_on"] == "2024 -> 2025"
    # Dec 2024 view of an account overdrawn in 2024 must use 2023 -> 2024 rates only
    import engine as E
    m = api.load_all()[0]["monthly"]
    acct = int(m[(m.month.between("2024-01", "2024-12")) & (m.days_below_zero > 0)].account_id.iloc[0])
    past = client.get(f"/api/customer/{acct}", params={"asof": "2024-12"}).json()["repeat"]
    assert past is not None and past["tested_on"] == "2023 -> 2024"


def test_future_loans_hidden_in_time_machine():
    """A loan granted in 2025 must not appear in the Dec 2024 view (it was unknown to the bank then)."""
    assert client.get("/api/customer/55447", params={"asof": "2024-12"}).json()["loan"] is None   # loan starts 2025-04-02
    assert client.get("/api/customer/55447").json()["loan"]["amount"] > 0


def test_loan_check_on_customer():
    lc = client.get("/api/customer/93172", params={"asof": "2024-12"}).json()["loan_check"]
    assert lc["hold"] and lc["data_up_to"] == "2024-11"


def test_watchlist_is_a_call_list():
    w = client.get("/api/watchlist", params={"asof": "2024-12"}).json()
    row = next(r for r in w["rows"] if r["account_id"] == 93172)
    assert row["cause"] == "Money in is falling" and row["action"] == "Call this week"
    assert sum(w["calls"].values()) == len(w["rows"])


def test_book_covers_every_customer_without_lookahead():
    b = client.get("/api/book", params={"asof": "2024-12"}).json()
    assert sum(t["customers"] for t in b["tiers"]) == b["customers"]
    assert b["tested_on"] == "Dec 2023 → 2024"                 # Dec 2024 view: rates from a year already over
    tiers = {t["tier"]: t for t in b["tiers"]}
    assert tiers["stable"]["tested_rate"] < 0.01 < tiers["act"]["tested_rate"] < tiers["overdrawn"]["tested_rate"]
    assert client.get("/api/book").json()["tested_on"] == "Dec 2024 → 2025"


def test_book_sentence_uses_one_population():
    s = client.get("/api/book").json()["summary"]             # today: tested on the Dec 2024 cohort -> 2025
    # was 0.085 / 0.60 before the new-account tier was added (Nov 8): overdrawn + act + new_hot
    assert s["tested_focus_customer_share"] == pytest.approx(0.101, abs=0.003)
    assert s["tested_focus_overdraft_share"] == pytest.approx(0.684, abs=0.01) and s["tested_stable_rate"] < 0.01



def test_customer_tier_for_new_account():
    t = api._tiers("2024-12"); a = int(t[t == "new_hot"].index[0])
    c = client.get(f"/api/customer/{a}", params={"asof": "2024-12"}).json()
    assert c["tier"]["key"] == "new_hot" and not c["trough"]["scorable"]


# ---------------------------------------------------------------- Screens read only what the engine sends (Nov 8)
def test_every_evidence_section_a_screen_reads_exists():
    """Parse the React screens for e.<section> reads and check /api/evidence serves each one (a renamed section fails here)."""
    import re
    from pathlib import Path
    screens = Path(api.__file__).parent / "web" / "src" / "screens"
    ev = client.get("/api/evidence").json()
    read = set(re.findall(r"\be\.([a-z_]+)", (screens / "Evidence.tsx").read_text()))      # e = the evidence on that screen
    read |= {k for p in screens.glob("*.tsx") for k in re.findall(r"\bev\.data\?\.([a-z_]+)", p.read_text())}
    assert read and not (read - set(ev)), f"screens read evidence sections the API does not send: {read - set(ev)}"


def test_customer_finance_fields_on_screen():
    c = client.get("/api/customer/93172", params={"asof": "2024-12"}).json()
    assert c["trough"]["haircut"] == pytest.approx(1 - c["trough"]["ltr"])          # Customer: haircut
    assert c["cushion"]["buffer_conservative"] >= c["cushion"]["buffer"] > 0         # Plan: conservative buffer
    w = c["when"]                                                                     # Customer: "When?" (cohort 2022-12)
    assert w["group"] == "riskiest 10%" and w["cohort"].startswith("scored 2022-12") and 0 < w["within_6"] <= w["within_24"]
    assert c["tier"]["key"] == "act" and c["loan_check"]["hold"]


def test_plan_carries_cost_and_cushion():
    p = client.post("/api/plan/93172", json={"scenario": {}, "asof": "2024-12"}).json()
    assert p["cushion"]["alert_level"] == p["cushion"]["buffer"]                     # alert at their own dip, not $100
    assert p["limit_cost"]["total"] > 0 and p["optimiser"]["horizon"] == 12


def test_unforecast_customers_get_their_tiers_tested_rate():
    """93172 at Dec 2023 is too new for a forecast; 85080 today was overdrawn before. Both show their tier's tested rate."""
    for acct, asof in ((93172, "2023-12"), (85080, None)):
        c = client.get(f"/api/customer/{acct}", params={"asof": asof} if asof else {}).json()
        assert not c["risk"]["validated_population"] and c["repeat"] is None
        assert 0 < c["tier"]["tested_rate"] < 1 and c["tier"]["tested_on"]
    assert client.get("/api/customer/93172", params={"asof": "2023-12"}).json()["tier"]["tested_on"] == "Dec 2022 → 2023"   # no lookahead


def test_not_found_says_what_to_do():
    r = client.get("/api/customer/77040", params={"asof": "2023-12"})
    assert r.status_code == 404 and "later date" in r.json()["detail"]
    assert "isn't in the data" in client.get("/api/customer/1").json()["detail"]


def test_measured_ai_accuracy_is_served_when_present():
    ev = client.get("/api/evidence").json()
    if "ai_eval" in ev:   # written by scripts/eval_ai.py; the Stress screen shows it next to the twist card
        a = ev["ai_eval"]
        assert a["held_out_cards"] == 16 and 0 <= a["rules_correct"] <= 16 and (a["ai_correct"] is None or 0 <= a["ai_correct"] <= 16)
