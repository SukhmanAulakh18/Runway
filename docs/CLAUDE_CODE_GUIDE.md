# Claude Code guide: what to give it, how to watch it, how to track progress

---

## 1. What Claude Code needs (all already in this repo)

| What | Where | Why it matters |
|---|---|---|
| The rules | `CLAUDE.md` | Read automatically at the start of every session: maths only in the engine, stay in your files, never edit tests, never commit data |
| How the system works | `docs/ARCHITECTURE.md` | So it calls the right functions instead of inventing formulas |
| The data flow | `docs/DATA_PIPELINE.md` | Which file holds what; how to add a calculation |
| Your task, with a ready prompt | `docs/TASKS.md` | The exact instructions for each task |
| The maths spec | `docs/BUILD_GUIDE.md` | Formulas and edge cases (engine work) |
| Proof of correctness | `tests/` | Its definition of "done": the tests pass |
| The data | `data/` on **your** laptop | Needed to run the app and tests. Never committed. |

You don't paste any of this in. Start Claude Code inside the repo folder and it can read every file. Your only input is **the task**, and `/task F1` (below) does most of that for you.

## 2. Which IDE: see everything that's happening

**Recommended: VS Code + the Claude Code extension.**
1. Install VS Code.
2. Open the `runway` folder. VS Code offers the recommended extensions from `.vscode/extensions.json`; click **Install all**. These are:
   - Claude Code
   - Python and Pylance
   - the debugger
   - a CSV viewer
3. Choose the interpreter: **Ctrl/Cmd + Shift + P → "Python: Select Interpreter" → `.venv`**. On Windows, if VS Code can't find it, pick `.venv\Scripts\python.exe`.

**What to keep on screen while Claude Code works:**

| Panel | Shows you | How to open |
|---|---|---|
| Claude Code panel | What it's doing; proposed edits as diffs to accept or reject | Claude icon in the sidebar (or run `claude` in the terminal) |
| **Source Control** | Every changed file, line by line | Ctrl/Cmd + Shift + G |
| **Testing** | All tests with green/red, one click to rerun | Beaker icon in the sidebar |
| Terminal | `pytest`, `streamlit`, `git` | Ctrl/Cmd + ` |
| Browser tab | The app at http://localhost:8501. Streamlit offers "Rerun" when files change; turn on **Always rerun** in its menu. | `streamlit run app.py`, or **Run and Debug → "Run Runway app"** |

**Alternatives:**
- **Terminal + any editor:** run `claude` in a terminal, and use `git diff` or your editor to see changes.
- **PyCharm:** has a Claude Code plugin.
- **Cursor:** can install the same extension.

Official docs: https://code.claude.com/docs/en/overview

## 3. The workflow for one task (10–40 minutes)

```bash
git switch main && git pull                 # latest code
git switch -c p2/demo-mode                  # your branch
claude                                      # or open the Claude Code panel in VS Code
```

Inside Claude Code:
```
/task F1
```
It reads the rules and the task, tells you its plan and which files it'll touch, and **waits for your "go"**.

1. **Check the plan:** only your files? no engine changes? Then reply `go`.
2. **Watch:** accept or reject diffs in VS Code; keep the app open in the browser and click around as it changes.
3. **Check:** type `/check` to run both test suites with a plain summary.
4. **Review:** type `/review` to check against every repo rule and draft your PR description.
5. **Commit and PR** (see `docs/CONTRIBUTING.md` Part 4).
6. **Next task:** type `/clear` first, so the old context doesn't confuse the new task.

## 4. The project slash commands (in `.claude/commands/`)

Type `/` in Claude Code to see them.

| Command | What it does |
|---|---|
| `/task <ID>` | Starts a task from `docs/TASKS.md` (e.g. `/task S3`): reads the rules and the prompt, proposes a plan, waits for "go", then implements and tests |
| `/check` | Runs `pytest -q` and `pytest -q -m ui` and explains any failure in plain words. Changes nothing. |
| `/review` | Checks your diff against every rule (ownership, no formulas in pages, no test edits, no data or keys, wording) and drafts the PR description. Changes nothing. |

## 5. Tracking progress as a team

| What | How |
|---|---|
| **Who's doing what** | P1 runs `bash scripts/create_issues.sh` once (needs the GitHub CLI: `gh auth login`). It creates one GitHub issue per task, labelled P1–P4 and by priority. Assign yourself; close the issue with your PR (write "Closes #12" in the PR description). |
| **What's done** | GitHub → Pull requests (merged = done). Optional: a GitHub Project board with columns To do / Doing / Review / Done. |
| **Is `main` healthy?** | After each merge, P1 runs `pytest -q && pytest -q -m ui`. Green means safe to demo. |
| **Is the data right on my laptop?** | `python scripts/check_setup.py` |
| **What changed overnight?** | `git log --oneline -20` or the GitHub commits page |
| **Handing over at a sleep shift** | Ask Claude Code: "Summarise what this branch changed and what's left for task F3, in 5 bullets", and paste it into the team chat |

## 6. Prompt library (copy, edit the bits in <>)

**Starting:**
- `/task <ID>` (preferred)
- "Read CLAUDE.md and docs/ARCHITECTURE.md. I own <files>. Plan <goal> first; list the files you'll change; wait for go."

**Keeping it on track:**
- "Only edit `<file>`. If you need an engine change, describe the function you need and stop."
- "Don't change the test. Fix the code so it passes."
- "Smallest change that works. No new abstractions, no new libraries."
- "Explain in 5 bullets what you changed and why, and list every file."

**UI work:**
- "In `ui/pages/<page>.py`, make <thing> clearer for a judge seeing it for 5 seconds. Use colours from ui/style.py. Run pytest -q -m ui."
- "This Streamlit error happens when I click <button>: <paste>. Fix it using a callback in ui/state.py."
- "Make every chart title on this page a sentence that states the takeaway, using values already in `c`."

**Understanding:**
- "Explain how `<function>` in engine.py works, in plain English, with one worked example for account 20111."
- "Where does the number <X> on the Shock tab come from? Trace it from the CSV to the screen."

**Before a PR:** `/review`

## 7. Things to watch for (and what to say)

| You see | Say |
|---|---|
| It edits `engine.py` from a frontend task | "Revert engine.py. Tell me what function you need instead." |
| It edits a test | "Revert the test change. Fix the code." |
| It creates files in `data/` or writes keys into code | "Remove that. Data and keys never go in the repo." |
| It adds a library | "Is that essential? Use what's in requirements.txt if possible." |
| A huge diff for a small task | "Too big. Undo and do the minimum for task <ID>." |
| It says tests pass but you didn't see them run | "Run /check and show me the output." |

## 8. Should we install the softaworks/agent-toolkit skills?

Optional, and not much. Our `CLAUDE.md`, docs and slash commands already cover what this project needs. **Spend at most 10 minutes on it.** A few may help:

| Skill | Useful for us? | Why |
|---|---|---|
| `commit-work` | **Yes** | Clean commit messages at 3 AM |
| `session-handoff` | **Yes** | Handing a half-done task to a teammate at a sleep shift |
| `marp-slide` | Later | If we want slides for the pitch |
| `mermaid-diagrams` | Maybe | Our docs already use Mermaid |
| `qa-test-planner` | Maybe | Planning extra UI checks; our smoke test already covers the basics |
| `codex`, `gemini`, `perplexity` | No | They call other paid tools or keys |
| `react-dev`, `mui`, `openapi-to-typescript` | No | We use Streamlit, not React |
| `jira`, `datadog-cli`, `meme-factory` | No | Not relevant |

How to install one, from their README:
- **Inside Claude Code:** run `/plugin marketplace add softaworks/agent-toolkit`, then `/plugin install commit-work@agent-toolkit`.
- **Manually:** copy the skill folder into `~/.claude/skills/`.

**Before installing,** open the skill's `SKILL.md` (and any `scripts/`) on GitHub and read it. It's third-party code that runs with your permissions. Only the person who needs it should install it.
