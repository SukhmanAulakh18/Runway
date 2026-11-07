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

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
_client = None
_backend = "offline"


def init() -> str:
    """Connect to Gemini if credentials exist. Returns the backend name."""
    global _client, _backend
    try:
        from google import genai
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            _client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"],
                                   location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"))
            _backend = f"Gemini on Vertex AI ({MODEL})"
        elif os.environ.get("GEMINI_API_KEY"):
            _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
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
            resp = _client.models.generate_content(
                model=MODEL, contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0))
            data = json.loads(resp.text)
            base = parse_twist_offline("")
            base.update({k: data[k] for k in base if k in data and data[k] is not None or k == "return_to_work_month" and k in data})
            return _sanitize(base), "AI"
        except Exception:
            pass
    return _sanitize(parse_twist_offline(text)), "rules"


def _sanitize(s: dict) -> dict:
    s["job_loss"] = bool(s["job_loss"])
    for k in ["ei_rate", "income_cut", "bills_increase_pct", "one_off_months_of_spending"]:
        s[k] = float(min(max(float(s[k] or 0), 0.0), 5.0))
    s["ei_months"] = int(min(max(int(s["ei_months"] or 0), 0), 12))   # EI regular benefits last at most 45 weeks
    s["spending_increase"] = float(s["spending_increase"] or 0)
    s["one_off_cost"] = float(max(float(s["one_off_cost"] or 0), 0))
    return s


# ---------------------------------------------------------------- plan writer
_PLAN_PROMPT = """Write a short, warm plan (4-6 sentences, plain English, second person "you") for a bank
customer, using ONLY the numbers in the facts below. Do not invent, round differently or calculate new
numbers. Mention the shock result, the first milestone they haven't reached, and the single most useful
backup action. No headings, no bullet points.
FACTS (JSON):
{facts}"""


def _numbers(text: str) -> list[float]:
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
    allowed |= {1.0, 2.0, 3.0, 6.0, 12.0}  # small counting words like "3 months" milestones
    return all(round(x, 1) in allowed for x in _numbers(text))


def template_plan(f: dict) -> str:
    s = [f"Under this shock your realistic runway is {f['realistic_runway']}, versus {f['answer_key_runway']} on the standard formula."]
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
            resp = _client.models.generate_content(
                model=MODEL, contents=_PLAN_PROMPT.format(facts=json.dumps(facts, default=str)))
            text = resp.text.strip()
            if verify_numbers(text, facts):
                return text, "AI (numbers verified)"
        except Exception:
            pass
    return template_plan(facts), "template"
