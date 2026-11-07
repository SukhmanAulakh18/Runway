"""Setup doctor: run this first. It tells you exactly what's wrong and how to fix it.

    python scripts/check_setup.py
"""
import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OK, BAD = "  [ok]  ", "  [FIX] "
problems = 0


def check(cond, good, fix):
    global problems
    print((OK + good) if cond else (BAD + fix))
    problems += 0 if cond else 1
    return cond


print("\n1. Python")
check(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]}",
      f"Python {sys.version.split()[0]} is too old. Install Python 3.11+ and recreate .venv.")
if sys.prefix != sys.base_prefix or os.environ.get("CONDA_DEFAULT_ENV"):
    print(OK + "running inside a virtual environment")
else:
    print("  [--]  not in a virtual environment (recommended: python -m venv .venv && source .venv/bin/activate)")

print("\n2. Packages (pip install -r requirements.txt)")
for pkg in ["pandas", "numpy", "scipy", "sklearn", "statsmodels", "streamlit", "plotly", "pytest"]:
    try:
        mod = importlib.import_module(pkg)
        check(True, f"{pkg} {getattr(mod, '__version__', '')}", "")
    except ImportError:
        check(False, "", f"{pkg} missing. Run: pip install -r requirements.txt")
try:
    importlib.import_module("google.genai")
    check(True, "google-genai (optional, for Gemini)", "")
except ImportError:
    print("  [--]  google-genai not installed (optional; the app works offline without it)")

print("\n3. Data folder")
data = Path(os.environ.get("RUNWAY_DATA", ROOT / "data"))
expected = {"monthly_summary.csv": 185_326, "loans.csv": 682, "accounts.csv": 4_500, "clients.csv": 5_369,
            "dispositions.csv": 5_369, "cards.csv": 892, "standing_orders.csv": 6_471, "districts.csv": 77}
if check(data.is_dir(), f"found {data}",
         f"No data folder at {data}. Copy the Tangerine CSVs into runway/data/ or export RUNWAY_DATA=/path/to/data"):
    for name, rows in expected.items():
        f = data / name
        if not f.exists():
            check(False, "", f"{name} missing from {data}")
            continue
        with open(f, encoding="utf-8") as fh:
            n = sum(1 for _ in fh) - 1
        check(n == rows, f"{name}: {n:,} rows", f"{name} has {n:,} rows, expected {rows:,}. Re-download the Tangerine data.")
    tx = data / "transactions.csv"
    print(("  [ok]  " if tx.exists() else "  [--]  ") + "transactions.csv " + ("present (not needed by the app)" if tx.exists() else "absent (fine: the app doesn't need it)"))

print("\n4. Git safety")
gi = (ROOT / ".gitignore").read_text() if (ROOT / ".gitignore").exists() else ""
check("data/" in gi, ".gitignore excludes data/", "Add 'data/' to .gitignore before committing anything")
check(not (ROOT / ".env").exists() or ".env" in gi, ".env is not committable", "Add '.env' to .gitignore")

print("\n5. Engine smoke check")
if problems == 0:
    try:
        import engine as E
        d = E.load()
        r = E.runway(E.profile(20111, d), E.Shock(income_factor=0.55))["runway"]
        check(r == 3.4, "account 20111, EI 55% -> 3.4 months (matches the answer key)",
              f"account 20111 gave {r}, expected 3.4. engine.py was changed incorrectly.")
    except Exception as exc:
        check(False, "", f"engine failed to run: {exc!r}")
else:
    print("  [--]  skipped until the problems above are fixed")

print("\n6. AI (optional)")
if os.environ.get("GOOGLE_CLOUD_PROJECT"):
    print(f"  [ok]  GOOGLE_CLOUD_PROJECT={os.environ['GOOGLE_CLOUD_PROJECT']} (Vertex AI); the sidebar will confirm")
elif os.environ.get("GEMINI_API_KEY"):
    print("  [ok]  GEMINI_API_KEY set")
else:
    print("  [--]  no AI configured: the app uses the offline twist-card rules (fine)")

print("\n" + ("All good. Next: pytest -q   then   streamlit run app.py" if problems == 0
              else f"{problems} thing(s) to fix above, then run this again."))
sys.exit(1 if problems else 0)
