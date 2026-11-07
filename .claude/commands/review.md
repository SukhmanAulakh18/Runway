Review my current changes (`git diff main...HEAD` plus uncommitted changes) before I open a pull request. Check each rule in CLAUDE.md and report pass/fail for:

- Only files owned by my task changed (docs/TASKS.md ownership table)
- No formulas or money calculations in app.py or ui/ (pages may only build Scenario objects and call engine functions)
- No existing test was edited
- Nothing in data/, no .env, keys or credentials
- Wording rules (money in/out, unlabelled outflows, no "closed", sentence case) and colours from ui/style.py
- Tests: run `pytest -q` and, if UI changed, `pytest -q -m ui`

Then draft a short PR description (what changed, which task, how I tested). Do not modify files.
