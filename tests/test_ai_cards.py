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
