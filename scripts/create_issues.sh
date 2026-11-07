#!/usr/bin/env bash
# Creates one GitHub issue per task in docs/TASKS.md, labelled by owner, so progress is visible.
# Needs the GitHub CLI (https://cli.github.com) and `gh auth login`. Run once, from the repo folder:
#     bash scripts/create_issues.sh
set -euo pipefail

for l in P1 P2 P3 P4 P0-must P1-should P2-nice; do
  gh label create "$l" --force >/dev/null 2>&1 || true
done

issue () {  # owner priority id title
  gh issue create --title "[$3] $4" --label "$1" --label "$2" \
    --body "Task $3 from docs/TASKS.md. In Claude Code, type /task $3 to start. Done when: see the task row in docs/TASKS.md." >/dev/null
  echo "created [$3] $4"
}

issue P1 P0-must   E1 "Create repo, push base, invite team, protect main"
issue P1 P0-must   E2 "Hand-check the judges' formula on 5 accounts"
issue P1 P1-should E3 "Benjamini-Hochberg correction in evidence.py"
issue P1 P1-should E4 "Confounder check for the trough"
issue P1 P0-must   E7 "Rehearse the live twist on 10 accounts"
issue P2 P0-must   F1 "Demo mode button in the sidebar"
issue P2 P0-must   F2 "Customer summary sentence on Know"
issue P2 P1-should F3 "Watchlist filters by reason + highlight current account"
issue P2 P1-should F4 "Chart titles that state the takeaway"
issue P2 P1-should F5 "Style pass (colours, number formats, 1280px)"
issue P2 P0-must   F6 "Fallback screenshots"
issue P3 P0-must   S1 "Turn on Gemini via Vertex AI"
issue P3 P0-must   S2 "20 twist-card tests + parser fixes"
issue P3 P0-must   S3 "Judge check expander on Shock"
issue P3 P1-should S4 "Scenario comparison on Plan"
issue P3 P2-nice   S5 "Download the plan button"
issue P4 P0-must   D1 "Devpost draft + Tangerine track by Sat 8 PM"
issue P4 P1-should D2 "Evidence charts on Why trust it"
issue P4 P0-must   D3 "Repo public and clean (no data, no keys)"
issue P4 P0-must   D4 "Devpost write-up draft"
issue P4 P0-must   D5 "2-minute video"
echo "Done. Assign each issue to its owner on GitHub (or: gh issue edit <n> --add-assignee <user>)."
