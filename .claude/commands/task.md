I'm starting task $ARGUMENTS from docs/TASKS.md.

1. Read CLAUDE.md, docs/ARCHITECTURE.md and the row and Claude Code prompt for task $ARGUMENTS in docs/TASKS.md.
2. Tell me in 3–5 bullets what you'll do and exactly which files you'll change. Only files owned by that task's person (see the ownership table) may change. If an engine change is needed, say what function is needed and stop.
3. Wait for my "go" before writing code.
4. After implementing: run `pytest -q` (and `pytest -q -m ui` if app.py or ui/ changed), then summarise the diff and list every changed file.
