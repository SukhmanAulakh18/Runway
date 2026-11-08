"""AI layer for Runway. The engine computes every number; AI only reads and writes words.

Backends, in order:
  1. Gemini on Vertex AI  (env: GOOGLE_CLOUD_PROJECT, optional GOOGLE_CLOUD_LOCATION)
  2. Gemini API key       (env: GEMINI_API_KEY)
  3. Offline fallback     (rule-based parser + template writer), so the live demo never breaks
Model name is configurable with GEMINI_MODEL.
"""
from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def _load_env(path: Path) -> None:
    """KEY=value lines from a gitignored .env into os.environ, so nobody has to `source .env` on demo day.
    Real environment variables win; an unreadable file is ignored."""
    try:
        for line in path.read_text().splitlines():
            k, sep, v = line.strip().partition("=")
            if sep and k and not k.startswith("#"):
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))
    except OSError:
        pass


_load_env(Path(__file__).resolve().parent / ".env")
# gemini-2.5-flash returns 404 for new keys (Nov 2026); 3.7/3.8-flash were overloaded (503/504) in testing,
# 3.5/3.6-flash answered every call in 3-4 s.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
AI_TIMEOUT_S = 6.0   # on stage, never wait longer than this for Gemini: fall back to rules / template
_client = None
_backend = "offline"
_pool = ThreadPoolExecutor(max_workers=2)


def _generate(contents: str, config=None) -> str:
    """One Gemini call with a hard wall-clock limit. Raises on error or timeout so callers fall back."""
    from google.genai import types
    config = config or types.GenerateContentConfig()
    # default thinking made plan writing exceed the API's 10 s deadline; minimal: 2-3 s, still passes our checks
    config.thinking_config = config.thinking_config or types.ThinkingConfig(thinking_level="MINIMAL")
    return _pool.submit(_client.models.generate_content, model=MODEL, contents=contents, config=config).result(timeout=AI_TIMEOUT_S).text


def init() -> str:
    """Connect to Gemini if credentials exist. Returns the backend name."""
    global _client, _backend
    try:
        from google import genai
        from google.genai import types
        # 10 s is the API's minimum deadline; no retries, so a stuck call dies instead of hanging (we saw 92 s)
        http = types.HttpOptions(timeout=10_000, retry_options=types.HttpRetryOptions(attempts=1))
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            _client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"],
                                   location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"), http_options=http)
            _backend = f"Gemini on Vertex AI ({MODEL})"
        elif os.environ.get("GEMINI_API_KEY"):
            _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=http)
            _backend = f"Gemini API ({MODEL})"
    except Exception:
        _client, _backend = None, "offline"
    return _backend


def backend() -> str:
    return _backend


# ---------------------------------------------------------------- twist reader
SCENARIO_FIELDS = {
    "job_loss": "true if the customer loses their job / is laid off",
    "ei_rate": "share of usual income EI pays, e.g. 0.55 (default 0.55)",
    "ei_months": "months EI is paid (default 6)",
    "income_cut": "for a pay cut without job loss, the share lost, e.g. 0.2",
    "bills_increase_pct": "household bills / rent / utilities increase as a share, e.g. 0.15",
    "spending_increase": "extra monthly spending in dollars (negative for a cut)",
    "one_off_cost": "one-time cost in dollars, e.g. a $3,000 repair",
    "one_off_months_of_spending": "one-time cost expressed in months of typical spending, e.g. 1.0",
    "return_to_work_month": "month number they find a new job, or null",
}

# Typed output for Gemini (structured output): every field has a type, so the model can't return prose or strings.
_TWIST_SCHEMA = {"type": "object", "properties": {
    "job_loss": {"type": "boolean"}, "ei_rate": {"type": "number"}, "ei_months": {"type": "integer"},
    "income_cut": {"type": "number"}, "bills_increase_pct": {"type": "number"}, "spending_increase": {"type": "number"},
    "one_off_cost": {"type": "number"}, "one_off_months_of_spending": {"type": "number"},
    "return_to_work_month": {"type": "integer", "nullable": True}},
    "required": ["job_loss", "ei_rate", "ei_months", "income_cut", "bills_increase_pct", "spending_increase",
                 "one_off_cost", "one_off_months_of_spending"]}

_PROMPT = """You convert a bank stress-test "twist card" into JSON settings. Return ONLY a JSON object
with these keys (use defaults or 0/false/null when the card doesn't mention something):
{fields}
Do not compute anything about the customer. Twist card:
\"\"\"{text}\"\"\""""


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def parse_twist_offline(text: str) -> dict:
    t = text.lower()
    out = {"job_loss": False, "ei_rate": 0.55, "ei_months": 6, "income_cut": 0.0,
           "bills_increase_pct": 0.0, "spending_increase": 0.0, "one_off_cost": 0.0,
           "one_off_months_of_spending": 0.0, "return_to_work_month": None}
    t = re.sub(r"\s*\bper ?cent\b", "%", t)   # "15 percent" -> "15%"
    if re.search(r"laid[\s-]*of+\b|lay[\s-]*off|\blos(?:e|es|t|ing)\s+(?:(?:their|his|her|the|a)\s+)?jobs?\b|"
                 r"jobs?\s+(?:loss|lost)|unemploy|fired|redundan|let go", t):
        out["job_loss"] = True
        m = re.search(r"\bei\b[^.%]*?(\d+(?:\.\d+)?)\s*%", t) or re.search(r"(\d+(?:\.\d+)?)\s*%[^.]*\bei\b", t)
        if m:
            out["ei_rate"] = _num(m.group(1)) / 100
        m = re.search(r"for (\d+) months", t)
        if m:
            out["ei_months"] = int(m.group(1))
        m = re.search(r"(?:new job|back to work|re-?employed)[^.]*?(?:month|after) (\d+)", t)
        if m:
            out["return_to_work_month"] = int(m.group(1))
    m = re.search(r"(?:pay|salary|income|hours) (?:is |are )?(?:cut|drops?|falls?|reduced)[^.%]*?(\d+(?:\.\d+)?)\s*%", t)
    if m and not out["job_loss"]:
        out["income_cut"] = _num(m.group(1)) / 100
    m = re.search(r"(?:bills?|rent|utilit\w*|household)[^.%$]*?(?:up|rise|rises|increase\w*|go up|goes up)[^.%$]*?(\d+(?:\.\d+)?)\s*%", t)
    if m:
        out["bills_increase_pct"] = _num(m.group(1)) / 100
    # Dollar amounts: "$400 a month" is monthly, anything else is one-off.
    monthly, oneoff = [], []
    for m in re.finditer(r"\$\s?([\d,]+(?:\.\d+)?)(\s*(?:a|per|/|each)\s*month|\s*monthly)?", t):
        (monthly if m.group(2) else oneoff).append(_num(m.group(1)))
    if monthly:
        out["spending_increase"] += sum(monthly)
    words = {"a full": 1, "one": 1, "a": 1, "two": 2, "three": 3, "half a": 0.5, "half": 0.5}
    m = re.search(r"(a full|half a|a|one|two|three|\d+(?:\.\d+)?)\s+months?(?:'s|\s+of)\s+(?:their\s+)?(?:typical\s+|usual\s+)?spending", t)
    if m:
        g = m.group(1)
        out["one_off_months_of_spending"] = words.get(g, None) or _num(g)
    elif oneoff and re.search(r"repair|furnace|roof|car|vet|dental|emergency|broke|breaks|dies|bill|cost", t):
        out["one_off_cost"] = sum(oneoff)
    return out


def parse_twist(text: str) -> tuple[dict, str]:
    """Returns (settings, source). Falls back to the offline parser on any problem."""
    if _client is not None:
        try:
            from google.genai import types
            prompt = _PROMPT.format(fields="\n".join(f"- {k}: {v}" for k, v in SCENARIO_FIELDS.items()), text=text)
            data = json.loads(_generate(prompt, types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=_TWIST_SCHEMA, temperature=0)))
            base = parse_twist_offline("")
            base.update({k: data[k] for k in base if k in data and data[k] is not None or k == "return_to_work_month" and k in data})
            return _sanitize(base), "AI"
        except Exception:
            pass
    return _sanitize(parse_twist_offline(text)), "rules"


def parse_twist_checked(text: str) -> dict:
    """parse_twist plus a safety net for the live demo: when Gemini read the card, list the fields where the
    offline rules read it differently, so the advisor checks those chips before running."""
    settings, source = parse_twist(text)
    disagree = []
    if source == "AI":
        rules = _sanitize(parse_twist_offline(text))
        disagree = [k for k in rules if (rules[k] != settings.get(k)) and not (
            isinstance(rules[k], float) and isinstance(settings.get(k), (int, float)) and abs(rules[k] - settings[k]) < 1e-6)]
    return {"settings": settings, "source": source, "disagree": disagree, "chips": describe_scenario(settings)}


def describe_scenario(s: dict) -> list[str]:
    """Plain-English chips for parsed settings, so the judge can confirm the card was read right (no maths)."""
    chips = []
    if s.get("job_loss"):
        chips.append(f"Job loss: EI {s.get('ei_rate', 0.55):.0%} for {s.get('ei_months', 6)} months")
        if s.get("return_to_work_month"):
            chips.append(f"Back to work in month {s['return_to_work_month']}")
    if s.get("income_cut"):
        chips.append(f"Pay cut {s['income_cut']:.0%}")
    if s.get("bills_increase_pct"):
        chips.append(f"Household bills +{s['bills_increase_pct']:.0%}")
    if s.get("spending_increase"):
        v = s["spending_increase"]
        chips.append(f"{'Extra' if v > 0 else 'Cut'} ${abs(v):,.0f} a month money out")
    if s.get("one_off_cost"):
        chips.append(f"One-off cost ${s['one_off_cost']:,.0f}")
    if s.get("one_off_months_of_spending"):
        m = s["one_off_months_of_spending"]
        chips.append(f"One-off cost: {m:g} month{'s' if m != 1 else ''} of typical money out")
    return chips or ["No shock"]


def _sanitize(s: dict) -> dict:
    s["job_loss"] = bool(s["job_loss"])
    for k in ["ei_rate", "income_cut", "bills_increase_pct", "one_off_months_of_spending"]:
        s[k] = float(min(max(float(s[k] or 0), 0.0), 5.0))
    s["ei_months"] = int(min(max(int(s["ei_months"] or 0), 0), 12))   # EI regular benefits last at most 45 weeks
    s["spending_increase"] = float(s["spending_increase"] or 0)
    s["one_off_cost"] = float(max(float(s["one_off_cost"] or 0), 0))
    rtw = s.get("return_to_work_month")   # LLMs sometimes send "4" or 0; the simulation needs an int month or None
    s["return_to_work_month"] = int(min(max(int(float(rtw)), 1), 24)) if rtw not in (None, "", 0, "0") else None
    return s


# ---------------------------------------------------------------- plan writer
_PLAN_PROMPT = """Write a short, warm plan (4-6 sentences, plain English, second person "you") for a bank
customer, using ONLY the numbers in the facts below. Do not invent, round differently or calculate new
numbers. Start with the no-risk steps: an alert when the balance drops below the alert level, then an automatic
transfer from savings of the buffer amount; a small overdraft limit is offered only after a conversation. Then the shock result, the first milestone they haven't reached, and the
single most useful backup action. "futures_lasting_6_months_of_10" is a count of simulated futures: say
"N of 10 simulated futures", never "chance" or "%". Only overdraft_risk_pct may be called a chance, written as
"a X% chance of a first overdraft in the next 12 months". Write dollar amounts with $ and commas ($6,527).
next_milestone.months is how many months of saving `saving` it takes to reach that milestone (not months of runway).
Never mention field names. No headings, no bullet points.
FACTS (JSON):
{facts}"""


def plan_facts(plan: dict, key_res: dict, real_res: dict, sim: dict, opt: dict, risk: dict | None = None) -> dict:
    """The only numbers the plan writer may use, picked and rounded from engine outputs (no new maths).
    plan = engine.make_plan(), key_res = engine.runway(), real_res = engine.realistic_runway(),
    sim = engine.simulate(), opt = engine.optimize_cuts(), risk = engine.overdraft_risk()."""
    g, levers, cu = plan["goal"], plan["backup"]["levers"], plan.get("cushion")
    best = max([l for l in levers if l.get("gain")], key=lambda l: l["gain"], default=None)
    nxt = next((m for m in g["milestones"] if not m["done"]), None)
    return {
        "cushion": ({"buffer": round(cu["buffer"]), "alert_level": round(cu["alert_level"]),
                     "top_up_now": round(cu["top_up_now"]),
                     "dip_day": cu["dip_day"] if cu.get("dip_day_reliable") else None} if cu else None),
        "overdraft_risk_pct": (round(risk["p_12m"] * 100, 1) if risk and risk.get("validated_population") else None),
        "realistic_runway": real_res["label"], "answer_key_runway": key_res["label"],
        "futures_lasting_6_months_of_10": round(sim["p_survive_6"] * 10),
        "next_milestone": ({"name": nxt["name"], "need": round(nxt["need"]),
                            "months": round(nxt["months_stretch"] or nxt["months_steady"] or 0) or None} if nxt else None),
        "saving": round(g["stretch_saving"]),
        "best_lever": ({"action": best["action"], "runway": best["runway"]} if best else None),
        "optimised_plan": {"months_safe_without_changes": opt["base_months"], "months_safe_with_cuts": opt["protected_months"],
                           "average_monthly_cut": round(opt["avg_monthly_cut"])},
    }


def _numbers(text: str) -> list[float]:
    # French formats: "6 527 $" (space thousands) -> 6527; "4,0 %" (comma decimal, 1-2 digits) -> 4.0. English "6,527" unchanged.
    text = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}\b)", "", text)
    text = re.sub(r"(\d),(\d{1,2})\b", r"\1.\2", text)
    return [_num(x) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


def verify_numbers(text: str, facts: dict) -> bool:
    """Every number in the AI text must appear in the facts (as given, or rounded)."""
    allowed = set()
    def walk(v):
        if isinstance(v, dict):
            [walk(x) for x in v.values()]
        elif isinstance(v, (list, tuple)):
            [walk(x) for x in v]
        elif isinstance(v, (int, float)) and v is not None:
            for x in (v, round(v), round(v, 1), abs(v), round(abs(v)), round(abs(v), 1), round(v * 100), round(v * 100, 1)):
                allowed.add(round(float(x), 1))
        elif isinstance(v, str):
            for x in _numbers(v):
                allowed.add(round(x, 1))
    walk(facts)
    allowed |= {1.0, 2.0, 3.0, 6.0, 10.0, 12.0}  # counting words: "3 months" milestones, "N of 10 simulated futures"
    return all(round(x, 1) in allowed for x in _numbers(text))


def verify_wording(text: str, facts: dict) -> bool:
    """Simulation counts are not probabilities: 'chance' is only allowed when a calibrated risk is in the facts."""
    return facts.get("overdraft_risk_pct") is not None or not re.search(r"\bchance|\bprobab|\blikel(y|ihood)", text.lower())


def template_plan(f: dict) -> str:
    s = []
    cu = f.get("cushion")
    if cu:
        s.append(f"To stay out of overdraft, set an alert for when your balance drops below ${cu['alert_level']:,.0f}, and keep "
                 f"${cu['buffer']:,.0f} within reach: an automatic transfer from savings first, or a small overdraft limit after a conversation.")
        if cu.get("top_up_now"):
            s.append(f"Move ${cu['top_up_now']:,.0f} into chequing now to be covered this month.")
        if cu.get("dip_day"):
            s.append(f"Your balance usually bottoms out around day {cu['dip_day']} of the month.")
    s.append(f"Under this shock your realistic runway is {f['realistic_runway']}, versus {f['answer_key_runway']} on the standard formula.")
    if f.get("futures_lasting_6_months_of_10") is not None:
        s.append(f"{f['futures_lasting_6_months_of_10']} of 10 simulated futures last 6 months.")
    nxt = f.get("next_milestone")
    if nxt:
        s.append(f"Your next goal is the {nxt['name']} milestone: ${nxt['need']:,.0f} more, "
                 + (f"about {nxt['months']:.0f} months if you save ${f['saving']:,.0f} a month." if nxt.get("months") else
                    "which starts with closing your monthly gap."))
    else:
        s.append("You already have a full six-month EI cushion; keep it topped up.")
    if f.get("best_lever"):
        b = f["best_lever"]
        s.append(f"If the shock hits, the most useful step is to {b['action'].lower()}, which takes your runway to {b['runway']} months.")
    return " ".join(s)


def write_plan(facts: dict) -> tuple[str, str]:
    """Returns (text, source). AI text is used only if every number checks out."""
    if _client is not None:
        try:
            text = _generate(_PLAN_PROMPT.format(facts=json.dumps(facts, default=str))).strip()
            if verify_numbers(text, facts) and verify_wording(text, facts):
                return text, "AI (numbers verified)"
        except Exception:
            pass
    return template_plan(facts), "template"


# ---------------------------------------------------------------- advisor brief + customer message
def customer_facts(acct, p, r, lt, risk, cushion, key_res, real_res, flags, committed=None, asof=None, diagnosis=None) -> dict:
    """The only numbers the brief / message may use, picked and rounded from engine outputs (no new maths)."""
    scored = bool(lt and lt.get("scorable"))
    return {
        "account": acct, "as_of": asof or "2025-12",
        "money_in_per_month": round(r.income), "money_out_per_month": round(getattr(r, "spending_history", 0) or r.spending),
        "average_balance": round(p.buffer),
        "new_loan_payment_per_month": round(r.loan_payments) if getattr(r, "loan_adjust", 0) >= 1 else None,
        "first_action": ({"title": diagnosis["primary"]["title"], "action": diagnosis["primary"]["action"], "why": diagnosis["primary"]["why"],
                          "is_cushion": diagnosis["primary"]["code"] == "dip"} if diagnosis else None),
        "lowest_balance_6_months": round(lt["min_balance"]) if lt else None,
        "lowest_as_pct_of_average": round(lt["ltr"] * 100, 1) if lt else None,
        "riskiest_pct_of_customers": round(lt["pct_rank"] * 100, 1) if scored else None,
        "overdraft_risk_pct": round(risk["p_12m"] * 100, 1) if risk and risk.get("validated_population") else None,
        "standard_runway": key_res["label"], "realistic_runway": real_res["label"],
        "cushion": {"amount": round(cushion["buffer"]), "move_now": round(cushion["top_up_now"]),
                    "dip_day": cushion["dip_day"] if cushion.get("dip_day_reliable") else None},
        "committed_by_standing_order_per_month": round(committed["total"]) if committed else None,
        "flags": flags,
    }


_BRIEF_PROMPT = """You brief a bank advisor before they contact a customer. Write exactly 3 short sentences, plain English:
1) who this customer is in money terms (money in, money out, average balance);
2) the risk and why: their balance dips close to $0 even though the average looks fine (use lowest_balance_6_months,
   riskiest_pct_of_customers and overdraft_risk_pct if present; overdraft_risk_pct is "a X% chance of a first overdraft in
   the next 12 months");
3) what to do first: if first_action is present, say first_action.action (because of first_action.why); if first_action is
   not the cushion, then also set an alert and offer an automatic transfer from savings of cushion.amount (a small overdraft limit only after the call). If there is
   no first_action, offer the cushion, plus moving cushion.move_now now if it is above 0. If new_loan_payment_per_month is
   present, say it in its own sentence ("A new loan now costs $X a month.") and do not link it to the cushion with
   "since" or "because".
Use ONLY numbers that appear in the facts. Dollars with $ and commas. Never mention field names. No headings or bullets.
FACTS (JSON):
{facts}"""

_MESSAGE_PROMPT = {
    "en": """Write a short, warm message (3 sentences, second person "you") that a bank advisor could send to this customer.
Say their balance has been dipping close to $0 during the month (lowest_balance_6_months), offer to set up an alert before
the balance gets that low and an automatic transfer from their savings of cushion.amount, and invite them
to reply. Do not mention risk, chance, percentages, simulations or runways. Use ONLY numbers in the facts, dollars with $ and
commas. Never mention field names. No subject line, no signature.
FACTS (JSON):
{facts}""",
    "fr": """Rédige un message court et chaleureux (3 phrases, vouvoiement) qu'un conseiller bancaire pourrait envoyer à ce client.
Dis que son solde descend près de 0 $ pendant le mois (lowest_balance_6_months), propose de mettre en place une alerte
avant que le solde descende aussi bas et un virement automatique de cushion.amount depuis son épargne, et
invite-le à répondre. Ne parle pas de risque, de probabilité, de pourcentages, de simulations ni de « runway ».
Utilise UNIQUEMENT les nombres des faits; écris les montants sans séparateur de milliers, ainsi : 6527 $.
Ne mentionne jamais les noms des champs. Pas d'objet, pas de signature.
FAITS (JSON) :
{facts}""",
}


def template_brief(f: dict) -> str:
    s = [f"Brings in about ${f['money_in_per_month']:,} a month, sends out ${f['money_out_per_month']:,}, "
         f"and averages ${f['average_balance']:,} in the account."]
    if f.get("lowest_balance_6_months") is not None:
        s.append(f"But the balance dipped to ${f['lowest_balance_6_months']:,}, {f['lowest_as_pct_of_average']}% of the average"
                 + (f", putting them in the riskiest {f['riskiest_pct_of_customers']}% of customers" if f.get("riskiest_pct_of_customers") is not None else "")
                 + (f", with a {f['overdraft_risk_pct']}% chance of a first overdraft in the next 12 months." if f.get("overdraft_risk_pct") is not None else "."))
    if f.get("new_loan_payment_per_month"):
        s.append(f"A new loan now costs ${f['new_loan_payment_per_month']:,} a month.")
    fa, cu = f.get("first_action"), f["cushion"]
    if fa and not fa["is_cushion"]:
        s.append(f"First, {fa['title'].lower()}: {fa['why']} {fa['action']}")
        s.append(f"Then set an alert and offer an automatic transfer of ${cu['amount']:,} from savings (a small overdraft limit only after the call).")
    else:
        s.append(f"Set an alert and offer an automatic transfer of ${cu['amount']:,} from savings (a small overdraft limit only after a call)"
                 + (f" and suggest moving ${cu['move_now']:,} into chequing now." if cu["move_now"] else "."))
    return " ".join(s)


def template_message(f: dict, lang: str = "en") -> str:
    cu, low = f["cushion"], f.get("lowest_balance_6_months")
    if lang == "fr":
        s = [f"Bonjour, nous avons remarqué que votre solde descend parfois jusqu'à {low} $ en cours de mois." if low is not None
             else "Bonjour, nous avons regardé l'évolution de votre solde en cours de mois."]
        s.append(f"Nous pouvons mettre en place une alerte avant que votre solde ne descende aussi bas, et un virement "
                 f"automatique de {cu['amount']} $ depuis votre épargne.")
        s.append("Répondez simplement à ce message si cela vous intéresse.")
    else:
        s = [f"Hi, we noticed your balance sometimes dips as low as ${low:,} during the month." if low is not None
             else "Hi, we've been looking at how your balance moves during the month."]
        s.append(f"We can set up an alert before your balance gets that low, and an automatic transfer of "
                 f"${cu['amount']:,} from your savings.")
        s.append("Just reply to this message if you'd like us to set it up.")
    return " ".join(s)


def _write(prompt: str, facts: dict, fallback: str) -> tuple[str, str]:
    if _client is not None:
        try:
            text = _generate(prompt.format(facts=json.dumps(facts, default=str, ensure_ascii=False))).strip()
            if verify_numbers(text, facts) and verify_wording(text, facts):
                return text, "AI (numbers verified)"
        except Exception:
            pass
    return fallback, "template"


def advisor_brief(facts: dict) -> tuple[str, str]:
    """3-sentence advisor briefing. AI text only if every number checks out, otherwise a template."""
    return _write(_BRIEF_PROMPT, facts, template_brief(facts))


def customer_message(facts: dict, lang: str = "en") -> tuple[str, str]:
    """A message the advisor could send, in English or French. No risk numbers go to the customer."""
    lang = "fr" if lang == "fr" else "en"
    f = {k: facts[k] for k in ("lowest_balance_6_months", "cushion")}   # the customer sees only these
    return _write(_MESSAGE_PROMPT[lang], f, template_message(f, lang))
