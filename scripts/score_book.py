"""Score a book of accounts from a monthly summary CSV and write the advisor call list.

Run:  python scripts/score_book.py monthly_summary.csv --out call_list.csv [--asof 2024-12]

The CSV must follow the data contract in docs/BANK_READINESS.md (one row per account per month; the columns in
engine.REQUIRED_MONTHLY). The file is checked first: any problem is printed and nothing is scored. The output has one
row per account: whole-book tier and action, trough, how much riskier than the book, haircut, months of history.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import engine as E  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("monthly", help="monthly summary CSV (see the data contract)")
    ap.add_argument("--out", default="runway_call_list.csv")
    ap.add_argument("--asof", help="score as of this month (YYYY-MM); default: the latest month in the file")
    a = ap.parse_args()
    df = pd.read_csv(a.monthly, dtype={"month": str})
    problems = E.check_monthly_contract(df)
    if problems:
        print(f"{a.monthly} does not meet the data contract; nothing was scored:")
        for p in problems:
            print(f"  - {p}")
        return 1
    out = E.score_book(df, a.asof)
    out.to_csv(a.out, index=False)
    print(f"Scored {len(out):,} accounts (as of {a.asof or df.month.max()}) -> {a.out}")
    print(out.groupby(["tier", "tier_label"], sort=False).size().rename("accounts").to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
