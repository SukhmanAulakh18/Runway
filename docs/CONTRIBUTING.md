# Contributing: getting started, Git, and Claude Code

Follow this top to bottom the first time. It takes about 15 minutes.

---

## Part 1 · P1 only: create the repo (once)

1. Unzip the base into a folder called `runway`.
2. Put the Tangerine CSVs in `runway/data/`. `.gitignore` already excludes this folder.
3. Check it works locally (see Part 2, steps 3–5).
4. Make the first commit:
   ```bash
   cd runway
   git init -b main
   git add .
   git status            # make sure NO data/ files and NO .env are listed
   git commit -m "Base: working Runway app, engine, tests, docs"
   ```
5. Create an **empty public** repo on GitHub named `runway`, with no README, so it doesn't conflict. Then push:
   ```bash
   git remote add origin https://github.com/<your-username>/runway.git
   git push -u origin main
   ```
   (With the GitHub CLI: `gh repo create runway --public --source=. --push`.)
6. Invite teammates: **Settings → Collaborators → Add people.**
   Then create the task issues: `gh auth login`, then `bash scripts/create_issues.sh`.
7. Recommended: **Settings → Branches → Add rule for `main` → Require a pull request before merging.** Nobody pushes straight to `main`.
8. Share with the team:
   - the repo link
   - how to get the data (Tangerine Drive folder or zip)
   - who owns what (docs/TASKS.md)

## Part 2 · Everyone: get it running

1. **Clone:**
   ```bash
   git clone https://github.com/<owner>/runway.git && cd runway
   ```
2. **Data:** copy the Tangerine CSVs into `runway/data/`. Never commit them.
3. **Python environment** (Python 3.11+):
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Check setup, then tests:**
   ```bash
   python scripts/check_setup.py   # fixes listed if anything is wrong
   pytest -q            # expect: 34 passed
   pytest -q -m ui      # expect: 6 passed (clicks through the whole app)
   ```
5. **Run it:**
   ```bash
   streamlit run app.py   # opens http://localhost:8501
   ```

If tests fail with "file not found", your data folder is in the wrong place. Use `runway/data/monthly_summary.csv`, or run `export RUNWAY_DATA=/full/path/to/data`.

## Part 3 · Install Claude Code (everyone)

Official docs: https://code.claude.com/docs/en/overview (quickstart: https://code.claude.com/docs/en/quickstart)

| System | Command |
|---|---|
| macOS / Linux / WSL | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Homebrew | `brew install --cask claude-code` |
| Windows (PowerShell) | `irm https://claude.ai/install.ps1 \| iex` |
| Windows (WinGet) | `winget install Anthropic.ClaudeCode` |

Then, inside the repo folder:
```bash
claude
```
Log in when prompted. Claude Code reads **`CLAUDE.md`** automatically at the start of every session, so it already knows our rules: maths only in the engine, never edit tests to pass, never commit data, and so on.

## Part 4 · The workflow for every task

```bash
# 1. Start from the latest main
git switch main
git pull

# 2. Make a branch named after you and the task
git switch -c p2/demo-mode          # p<your number>/<short-task-name>

# 3. Do the task with Claude Code (see Part 5), then test
pytest -q
pytest -q -m ui                     # if you touched app.py or ui/

# 4. Commit only your files
git status                          # check: only files you own, no data/, no .env
git add ui/pages/know.py            # add files by name
git commit -m "Know: customer summary sentence"

# 5. Push and open a pull request
git push -u origin p2/demo-mode
# GitHub shows a "Compare & pull request" button. Fill in the template, then ask P1 to review.

# 6. After P1 merges it
git switch main
git pull
```

**Small and often wins.** One task = one branch = one PR. A PR that changes 30 lines merges in 2 minutes; a PR that changes 500 lines causes conflicts at 3 AM.

## Part 5 · Working with Claude Code in this repo

Full guide (IDE, tracking, prompt library): [CLAUDE_CODE_GUIDE.md](CLAUDE_CODE_GUIDE.md). The short version: type `/task <ID>` to start, `/check` to test, and `/review` before a PR.

**For each task:**
1. Run `claude` in the repo folder, on your task branch.
2. Paste the task's prompt from `docs/TASKS.md`. Every prompt starts with "Read CLAUDE.md …".
3. Ask for a plan first if the task is bigger than a few lines: "Plan this first; don't write code yet." Check the plan only touches your files.
4. Let it implement, then make sure it ran the tests. If not, say: "Run `pytest -q` and `pytest -q -m ui` and show me the results."
5. **Read the diff** before committing (`git diff`). Look for:
   - files outside your ownership
   - maths added to a page
   - a changed test
   - anything in `data/`
6. Use `/clear` before starting the next task, so old context doesn't leak in.

**Useful things to say to Claude Code:**

| When | Say |
|---|---|
| It wants to edit a test to pass | "Don't change the test. Fix the code." |
| It's editing someone else's file | "Only edit `ui/pages/shock.py`. If you need an engine change, tell me what and stop." |
| It adds a library | "Use only what's in requirements.txt unless it's essential; explain why." |
| It over-engineers | "Simplest version that passes the tests. No new abstractions." |
| You're unsure what it did | "Summarise the diff in 5 bullets and list every file changed." |
| A Streamlit error about changing a widget after it's created | "Move that state change into an on_click callback in ui/state.py." |

**Need an engine change?** Don't edit `engine.py`. Message P1: "engine: I need `<what>` for `<page>`, returning `<shape>`." P1 adds it with a test.

## Part 6 · Pull request rules

The PR template asks you to confirm:
- [ ] `pytest -q` passes (and `pytest -q -m ui` if UI changed)
- [ ] Only files I own changed
- [ ] No formulas in `app.py` or `ui/`
- [ ] No `data/`, `.env`, keys or credentials
- [ ] Screenshot attached if it changes what the user sees

P1 reviews, runs the tests on `main` after merging, and keeps `main` always working.

## Part 7 · When things go wrong

| Problem | Fix |
|---|---|
| Merge conflict | `git switch main && git pull && git switch <your-branch> && git merge main`. Fix the marked lines, run the tests, commit. If it's not your file, ask its owner. |
| You committed data or a key | **Tell P1 immediately.** Remove the file, rotate the key, and rewrite history before the repo goes public. |
| The app works locally but a test fails | Read the failing test's name; it says which number or click broke. Paste the error into Claude Code: "Fix the code so this passes; don't change the test." |
| Streamlit "cannot modify after instantiated" | Programmatic widget changes must happen in a callback (`on_click=` / `on_select=`) defined in `ui/state.py`. |
| The app is slow | Something loops over all 4,500 accounts on each click. Move it into a cached function in `ui/data.py` (ask P1 if it needs engine work). |

## Part 8 · Never

- Commit `data/`, `.env`, API keys or `gcloud` credentials.
- Put a formula in `app.py` or `ui/`.
- Edit a test to make it pass.
- Push straight to `main`.
- Change code after the Sunday 12 PM deadline. The event disqualifies changes made after it.
