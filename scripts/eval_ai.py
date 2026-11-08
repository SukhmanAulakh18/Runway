"""Evaluate the twist-card reader: Gemini (if configured) vs the offline rules, on tuned and held-out cards.

Run:  python scripts/eval_ai.py            -> prints a report and writes docs/AI_EVAL.md
A card counts as correct only if every expected field is right AND no other shock is invented (false positives count).
The tuned set is the cards the rules were fixed against (tests/test_ai_cards.py); the held-out set was written
afterwards and never used to tune anything, so it is the honest measure.
"""
from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tests"))
import ai                                   # noqa: E402
from test_ai_cards import CARDS as TUNED   # noqa: E402

JOB = {"job_loss": True}
HELD_OUT = [   # written after the rules were fixed; do not tune the rules to these
    ("Their hours are cut in half", {"income_cut": 0.5}),
    ("They're furloughed for three months with EI at 55%", {**JOB, "ei_months": 3}),
    ("An unexpected dental bill of $2,500", {"one_off_cost": 2500.0}),
    ("The car's transmission dies: $4,800", {"one_off_cost": 4800.0}),
    ("Rent jumps 8%", {"bills_increase_pct": 0.08}),
    ("Utilities go up ten percent", {"bills_increase_pct": 0.10}),
    ("Their partner loses their job; EI covers 55% for six months", {**JOB, "ei_months": 6}),
    ("They take a 15% pay cut", {"income_cut": 0.15}),
    ("Daycare adds $650 a month", {"spending_increase": 650.0}),
    ("Laid off in a downturn, EI 55%, back at work after 5 months", {**JOB, "return_to_work_month": 5}),
    ("Hydro bill rises 20% and the fridge breaks ($1,200)", {"bills_increase_pct": 0.20, "one_off_cost": 1200.0}),
    ("Nothing changes this year", {}),
    ("Job loss with EI at 55%, rent up 10%, and a $3,000 car repair", {**JOB, "bills_increase_pct": 0.10, "one_off_cost": 3000.0}),
    ("They lose half their income", {"income_cut": 0.5}),
    ("Their household bills double", {"bills_increase_pct": 1.0}),
    ("Fired. EI pays 55% for 6 months, and a vet bill of $900", {**JOB, "ei_months": 6, "one_off_cost": 900.0}),
]
SHOCK_DEFAULTS = {"job_loss": False, "income_cut": 0.0, "bills_increase_pct": 0.0, "spending_increase": 0.0,
                  "one_off_cost": 0.0, "one_off_months_of_spending": 0.0, "return_to_work_month": None}


def correct(got: dict, expect: dict) -> tuple[bool, list[str]]:
    wrong = []
    for k, v in expect.items():
        g = got.get(k)
        if isinstance(v, float) and isinstance(g, (int, float)) and abs(g - v) <= 1e-6 * max(1, abs(v)):
            continue
        if g != v:
            wrong.append(f"{k}: got {g!r}, want {v!r}")
    for k, v in SHOCK_DEFAULTS.items():          # no invented shocks
        if k not in expect and got.get(k) not in (v, None) and not (isinstance(v, float) and got.get(k) == 0):
            wrong.append(f"{k}: invented {got.get(k)!r}")
    return not wrong, wrong


def run(name: str, reader, cards) -> dict:
    ok, times, fails, sources = 0, [], [], {}
    for text, expect in cards:
        t = time.perf_counter(); got, src = reader(text); times.append(time.perf_counter() - t)
        sources[src] = sources.get(src, 0) + 1
        good, why = correct(got, expect)
        ok += good
        if not good:
            fails.append((text, why))
    return {"name": name, "n": len(cards), "correct": ok, "accuracy": ok / len(cards), "sources": sources,
            "median_s": statistics.median(times), "max_s": max(times), "fails": fails}


def main() -> None:
    backend = ai.init()
    rules = lambda t: (ai._sanitize(ai.parse_twist_offline(t)), "rules")   # noqa: E731
    live = lambda t: ai.parse_twist(t)                                         # Gemini if configured, else rules  # noqa: E731
    results = [run("Rules, tuned cards", rules, TUNED), run("Rules, held-out cards", rules, HELD_OUT)]
    if backend != "offline":
        results += [run(f"{backend}, tuned cards", live, TUNED), run(f"{backend}, held-out cards", live, HELD_OUT)]
    lines = ["# Twist-card reader evaluation", "",
             f"Backend: **{backend}**. A card is correct only if every expected field is right and no other shock is invented.",
             "Tuned cards are the ones the rules were fixed against; held-out cards were written afterwards and never used to tune.",
             "", "| Reader and card set | Correct | Accuracy | Answered by | Median time | Slowest |", "|---|---|---|---|---|---|"]
    for r in results:
        src = ", ".join(f"{k} {v}" for k, v in r["sources"].items())
        lines.append(f"| {r['name']} | {r['correct']} of {r['n']} | {r['accuracy']:.0%} | {src} | {r['median_s']:.2f} s | {r['max_s']:.2f} s |")
    lines += ["", "## Misses", ""]
    for r in results:
        for text, why in r["fails"]:
            lines.append(f"- **{r['name']}**: \"{text}\": {'; '.join(why)}")
    if backend == "offline":
        lines += ["", "_Gemini was not configured for this run. Run on a machine with `GOOGLE_CLOUD_PROJECT` (Vertex AI) set to add the AI rows._"]
    report = "\n".join(lines) + "\n"
    print(report)
    (ROOT / "docs" / "AI_EVAL.md").write_text(report)


if __name__ == "__main__":
    main()
