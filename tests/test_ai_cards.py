"""Twist-card stress test (task S2): unusual wording, typos and combinations for the offline parser."""
import pytest

import ai

JOB = {"job_loss": True}
CARDS = [
    # the README cards, word for word
    ("This customer was laid off. EI pays 55% of their usual income for 6 months. Do they make it?", {**JOB, "ei_rate": 0.55, "ei_months": 6}),
    ("The furnace dies, and the repair costs a full month of their typical spending.", {"one_off_months_of_spending": 1.0}),
    ("They lose their job (EI at 55%) and their household bills go up 15% in the same month.", {**JOB, "ei_rate": 0.55, "bills_increase_pct": 0.15}),
    # other ways to say job loss
    ("They lost their job, EI 55%", {**JOB, "ei_rate": 0.55}),
    ("She loses her job and EI pays 60%", {**JOB, "ei_rate": 0.60}),
    ("Lost job. EI at 50 %", {**JOB, "ei_rate": 0.50}),
    ("Job lost, EI 55% for 6 months", {**JOB, "ei_months": 6}),
    ("Made redundant; EI pays 55% for 4 months", {**JOB, "ei_months": 4}),
    ("They were let go. EI 55%", JOB),
    ("Laid-off, EI 55% for 9 months", {**JOB, "ei_months": 9}),
    # typos
    ("Customer got laid of, EI pays 55% for 6 months", JOB),
    ("laidoff with EI 45%", {**JOB, "ei_rate": 0.45}),
    # "their" must not be read as "EI"
    ("They lose their job and their household bills go up 15%", {**JOB, "ei_rate": 0.55, "bills_increase_pct": 0.15}),
    # percent written as a word
    ("Bills increase by 15 percent", {"bills_increase_pct": 0.15}),
    ("Laid off with EI at 55 per cent", {**JOB, "ei_rate": 0.55}),
    ("Their pay is cut by 20 percent", {"income_cut": 0.20}),
    # one-off costs in months of spending and in dollars
    ("Laid off. EI pays 55% for 6 months, and the furnace dies costing a month of typical spending", {**JOB, "one_off_months_of_spending": 1.0}),
    ("The roof leaks and the repair costs a month's spending", {"one_off_months_of_spending": 1.0}),
    ("The furnace breaks; repair = 2 months of their spending", {"one_off_months_of_spending": 2.0}),
    ("Roof repair costs $12,000", {"one_off_cost": 12000.0}),
    # combinations
    ("Rent goes up $300 a month and they lose their job with EI at 55%", {**JOB, "spending_increase": 300.0}),
    ("Laid off, EI at 55%, but they find a new job in month 4", {**JOB, "return_to_work_month": 4}),
]


@pytest.mark.parametrize("text,expect", CARDS)
def test_card(text, expect):
    s = ai.parse_twist_offline(text)
    for k, v in expect.items():
        assert s[k] == pytest.approx(v), f"{k}: got {s[k]!r}"


def test_no_shock_card_stays_empty():
    s = ai.parse_twist_offline("Nothing changes this month.")
    assert not s["job_loss"] and s["bills_increase_pct"] == 0 and s["one_off_cost"] == 0


def test_sanitize_llm_shaped_output():
    s = ai.parse_twist_offline("")
    s.update({"return_to_work_month": "4", "ei_rate": "0.55", "job_loss": 1})
    out = ai._sanitize(s)
    assert out["return_to_work_month"] == 4 and out["job_loss"] is True and out["ei_rate"] == 0.55
    s["return_to_work_month"] = 0
    assert ai._sanitize(s)["return_to_work_month"] is None


def test_twist_schema_builds():
    from google.genai import types
    types.GenerateContentConfig(response_mime_type="application/json", response_schema=ai._TWIST_SCHEMA, temperature=0)


def test_ai_engine_contract():
    """The seam between the engine session and the AI session: every field the AI reads must exist on Scenario."""
    import dataclasses
    import engine as E
    fields = {f.name for f in dataclasses.fields(E.Scenario)}
    assert set(ai.SCENARIO_FIELDS) <= fields
    assert set(ai.parse_twist_offline("laid off, EI 55% for 6 months")) <= fields
    E.Scenario(**ai._sanitize(ai.parse_twist_offline("laid off, back to work in month 4, bills up 15%")))



def _facts(acct=93172, asof="2024-12", sc=None):
    import engine as E
    d = E.load(); dd = {"monthly": d["monthly"][d["monthly"].month <= asof], "loans": d["loans"]}
    sc = sc or E.Scenario(job_loss=True, bills_increase_pct=0.15)
    p, r = E.profile(acct, dd), E.realistic_profile(acct, dd)
    return ai.plan_facts(E.make_plan(acct, dd, sc), E.runway(p, sc.to_answer_key_shock()), E.realistic_runway(r, sc),
                         E.simulate(acct, dd, sc), E.optimize_cuts(acct, dd, sc), E.overdraft_risk(acct, dd))


def test_plan_facts_lead_with_cushion_and_template_verifies():
    f = _facts()
    assert f["cushion"]["buffer"] > 0 and "chance_6_months_pct" not in f
    text = ai.template_plan(f)
    assert text.startswith("To stay out of overdraft") and "simulated futures" in text
    assert ai.verify_numbers(text, f) and ai.verify_wording(text, f)   # the template must pass our own checks


def test_wording_check_blocks_chance_for_simulation_counts():
    f = {"overdraft_risk_pct": None, "futures_lasting_6_months_of_10": 7}
    assert not ai.verify_wording("You have a 70% chance of lasting 6 months.", f)
    assert ai.verify_wording("7 of 10 simulated futures last 6 months.", f)
    assert ai.verify_wording("There is a 5.5% chance of a first overdraft.", {"overdraft_risk_pct": 5.5})


def test_chips_and_checked_parse_offline():
    out = ai.parse_twist_checked("They lose their job (EI at 55%) and their household bills go up 15% in the same month.")
    assert out["source"] == "rules" and out["disagree"] == []
    assert out["chips"] == ["Job loss: EI 55% for 6 months", "Household bills +15%"]
    assert ai.describe_scenario(ai.parse_twist_offline("")) == ["No shock"]
    assert ai.describe_scenario(ai.parse_twist_offline("The furnace dies, and the repair costs a full month of their typical spending.")) == \
        ["One-off cost: 1 month of typical money out"]


class _FakeGemini:
    """Stands in for google-genai so the AI code path (schema config, JSON parsing, checks) is tested offline."""
    def __init__(self, reply): self.reply = reply; self.models = self
    def generate_content(self, model, contents, config=None):
        self.config = config
        return type("R", (), {"text": self.reply})()


def test_gemini_path_flags_misread_card(monkeypatch):
    card = "They lose their job (EI at 55%) and their household bills go up 15% in the same month."
    fake = _FakeGemini('{"job_loss": true, "ei_rate": 0.55, "ei_months": 6, "income_cut": 0, "bills_increase_pct": 0.5,'
                       ' "spending_increase": 0, "one_off_cost": 0, "one_off_months_of_spending": 0, "return_to_work_month": "4"}')
    monkeypatch.setattr(ai, "_client", fake)
    out = ai.parse_twist_checked(card)
    assert out["source"] == "AI" and fake.config.response_schema == ai._TWIST_SCHEMA
    assert set(out["disagree"]) == {"bills_increase_pct", "return_to_work_month"}   # the advisor is told to check these
    assert out["settings"]["return_to_work_month"] == 4


def test_gemini_plan_rejected_when_it_says_chance(monkeypatch):
    f = {"realistic_runway": "0.8 months", "answer_key_runway": "no shortfall (120+)", "futures_lasting_6_months_of_10": 3,
         "overdraft_risk_pct": None, "saving": 100, "next_milestone": None, "best_lever": None, "cushion": None}
    monkeypatch.setattr(ai, "_client", _FakeGemini("You have a 30% chance of lasting 6 months."))
    text, source = ai.write_plan(f)
    assert source == "template" and "chance" not in text


@pytest.mark.slow
def test_template_plan_always_verifies():
    import numpy as np
    import engine as E
    d = E.load()
    for a in np.random.default_rng(11).choice(d["monthly"].account_id.unique(), 60, replace=False):
        for sc in (E.Scenario(job_loss=True), E.Scenario(one_off_months_of_spending=1.0), E.Scenario(job_loss=True, bills_increase_pct=0.15)):
            p, r = E.profile(a, d), E.realistic_profile(a, d)
            f = ai.plan_facts(E.make_plan(a, d, sc), E.runway(p, sc.to_answer_key_shock()), E.realistic_runway(r, sc),
                              E.simulate(a, d, sc), E.optimize_cuts(a, d, sc), E.overdraft_risk(a, d))
            t = ai.template_plan(f)
            assert ai.verify_numbers(t, f) and ai.verify_wording(t, f), (a, sc, t)
