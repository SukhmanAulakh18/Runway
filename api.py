"""Runway JSON API for the React dashboard (web/). No maths here.

Run:   uvicorn api:app --port 8000            (docs at http://localhost:8000/docs)

Every customer number comes from ui.context.build_context(), the same function the Streamlit app uses,
so the two frontends can never disagree. `asof` (Time Machine) cuts the data for every number.
"""
from __future__ import annotations

import dataclasses
import logging
import math
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore", message=".*No runtime found.*")   # st.cache_resource works without a Streamlit server
logging.getLogger("streamlit").setLevel(logging.ERROR)

import ai
import engine as E
from ui.context import build_context
from ui.data import ai_backend, load_all, pcurve, wl

ROOT = Path(__file__).resolve().parent
ASOF = Query(None, pattern=r"^202[0-5]-(0[1-9]|1[0-2])$", description="Time Machine month, e.g. 2024-12")
app = FastAPI(title="Runway API", version="2.0")
ai_backend()


def clean(x):
    """Engine output -> JSON (numpy, pandas, dataclasses; NaN/inf -> null)."""
    if dataclasses.is_dataclass(x):
        return clean(dataclasses.asdict(x))
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return clean(x.tolist())
    if isinstance(x, pd.DataFrame):
        return clean(x.to_dict(orient="records"))
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if (math.isnan(x) or math.isinf(x)) else float(x)
    if isinstance(x, pd.Timestamp):
        return x.strftime("%Y-%m-%d")
    return x


class ScenarioIn(BaseModel):
    job_loss: bool = False
    ei_rate: float = 0.55
    ei_months: int = 6
    ei_cap: bool = True
    income_cut: float = 0.0
    bills_increase_pct: float = 0.0
    spending_increase: float = 0.0
    one_off_cost: float = 0.0
    one_off_months_of_spending: float = 0.0
    return_to_work_month: Optional[int] = None
    employment_share: float = 1.0


class ShockReq(BaseModel):
    scenario: ScenarioIn = ScenarioIn()
    asof: Optional[str] = Field(None, pattern=r"^202[0-5]-(0[1-9]|1[0-2])$")


class PlanReq(ShockReq):
    max_cut_share: float = 0.5
    pessimistic: bool = True


class TwistReq(BaseModel):
    text: str


def ctx(acct: int, asof: Optional[str], sc: E.Scenario):
    d, people, EV, accounts = load_all()
    m = d["monthly"]
    if not ((m.account_id == acct) & (m.month <= (asof or "9999"))).any():
        raise HTTPException(404, f"Account {acct} has no data" + (f" up to {asof}" if asof else ""))
    return build_context(d, people, EV, accounts, acct, asof, sc)


@app.get("/api/health")
def health():
    return {"ok": True, "ai": ai_backend(), "accounts": len(load_all()[3])}


@app.get("/api/accounts")
def accounts():
    return [int(a) for a in load_all()[3]]


@app.get("/api/customer/{acct}")
def customer(acct: int, asof: Optional[str] = ASOF):
    """Know the customer: judges' numbers, our numbers, trough, calibrated risk, cushion, flags, history."""
    c = ctx(acct, asof, E.Scenario())
    hist = c.a_rows[["month", "money_in", "money_out", "avg_daily_balance", "min_balance", "month_end_balance",
                     "days_below_zero", "household_bills", "insurance", "loan_payments", "pension_in"]]
    out = {"account_id": acct, "asof": asof, "owner_age": c.age, "flags": c.flags,
           "profile": c.p, "standard_runway": c.key_res, "realistic": c.r, "realistic_runway": c.real_res,
           "trough": c.lt, "loan": c.LR, "risk": c.risk, "cushion": c.cushion, "committed": c.committed,
           "last_activity": c.a_rows.month.max(), "history": hist}
    if asof:
        out["what_happened_next"] = E.what_happened_next(acct, c.d_full, asof, 12)
    return clean(out)


@app.post("/api/shock/{acct}")
def shock(acct: int, req: ShockReq):
    """Take a shock: both runways, why they differ, Monte Carlo bands."""
    sc = E.Scenario(**req.scenario.model_dump())
    c = ctx(acct, req.asof, sc)
    return clean({"scenario": sc, "standard": c.key_res, "realistic": c.real_res,
                  "why_different": E.explain_difference(c.p, c.r, sc), "simulation": c.sim,
                  "judge_check": {"I": c.p.income, "S": c.p.spending, "B": c.p.buffer, "H": c.p.household_bills}})


@app.post("/api/plan/{acct}")
def plan(acct: int, req: PlanReq):
    """Make a plan: dip cushion first, then optimised cuts, backup levers and job-loss milestones."""
    sc = E.Scenario(**req.scenario.model_dump())
    c = ctx(acct, req.asof, sc)
    pl = E.make_plan(acct, c.d, sc)
    pl["cushion"] = c.cushion                        # same cushion as the customer view (includes the dip day)
    opt = E.optimize_cuts(acct, c.d, sc, max_cut_share=req.max_cut_share, pessimistic=req.pessimistic)
    return clean({"cushion": c.cushion, "goal": pl["goal"], "backup": pl["backup"], "optimiser": opt,
                  "facts": ai.plan_facts(pl, c.key_res, c.real_res, c.sim, opt, c.risk)})


@app.post("/api/write-plan")
def write_plan(facts: dict):
    text, source = ai.write_plan(facts)
    return {"text": text, "source": source}


def _facts(acct: int, asof: Optional[str]) -> dict:
    c = ctx(acct, asof, E.Scenario())
    return ai.customer_facts(acct, c.p, c.r, c.lt, c.risk, c.cushion, c.key_res, c.real_res, c.flags, c.committed, asof)


@app.post("/api/ai/brief/{acct}")
def brief(acct: int, asof: Optional[str] = ASOF):
    """3-sentence advisor briefing; every number verified against the engine, or a template."""
    text, source = ai.advisor_brief(_facts(acct, asof))
    return {"text": text, "source": source}


@app.post("/api/ai/message/{acct}")
def message(acct: int, asof: Optional[str] = ASOF, lang: str = Query("en", pattern="^(en|fr)$")):
    """A message the advisor could send the customer, English or French. No risk numbers reach the customer."""
    text, source = ai.customer_message(_facts(acct, asof), lang)
    return {"text": text, "source": source, "lang": lang}


@app.post("/api/twist")
def twist(req: TwistReq):
    return clean(ai.parse_twist_checked(req.text))


@app.get("/api/watchlist")
def watchlist(asof: Optional[str] = ASOF, early_only: bool = True, limit: int = Query(50, ge=1, le=500)):
    w = wl(asof)
    w = w[w.scorable & (~w.ever_negative.fillna(False) if early_only else True)]
    top = w.head(limit)
    out = {"asof": asof, "n_in_view": len(w), "rows": top.rename_axis("account_id").reset_index()}
    if asof:
        out["reveal"] = {"top_hit": int(top.overdraft_next_12m.fillna(False).sum()),
                         "base_rate": float(w.overdraft_next_12m.fillna(False).mean())}
    return clean(out)


@app.post("/api/portfolio")
def portfolio(req: ShockReq):
    """Bank view (today's data): share of all customers still above zero each month, standard vs realistic."""
    return clean(pcurve(tuple(sorted(req.scenario.model_dump().items()))))


@app.get("/api/evidence")
def evidence():
    EV = load_all()[2]
    if EV is None:
        raise HTTPException(404, "evidence.json missing: run python evidence.py")
    return clean(EV)


if (ROOT / "web" / "dist").exists():   # production: one server for the API and the built React app
    app.mount("/", StaticFiles(directory=ROOT / "web" / "dist", html=True), name="web")
