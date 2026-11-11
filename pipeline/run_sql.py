#!/usr/bin/env python3
"""Run any sql/*.sql file through the Dune API and print results — no UI needed.

Usage:
    .venv/bin/python pipeline/run_sql.py sql/00_verify_tables.sql
    .venv/bin/python pipeline/run_sql.py sql/01_daily_transfers.sql --limit 20
    .venv/bin/python pipeline/run_sql.py sql/01_daily_transfers.sql --save data/raw/test.csv

This executes AD-HOC SQL (not a saved query), so query IDs aren't needed.
Great for verifying queries before saving them on Dune for the dashboard.

Requires DUNE_API_KEY in .env. Free-tier note: each run consumes compute
credits; ad-hoc queries have a max runtime (~5 min on free tier).
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

BASE = "https://api.dune.com/api/v1"
PERFORMANCE = "medium"  # free tier max is usually 'medium'; lower if it fails


def api_key() -> str:
    key = os.environ.get("DUNE_API_KEY", "").strip()
    if not key:
        sys.exit("DUNE_API_KEY not set in .env")
    return key


def headers(key: str) -> dict:
    return {"X-DUNE-API-KEY": key, "Content-Type": "application/json"}


def execute_sql(key: str, sql: str) -> str:
    """POST ad-hoc SQL -> execution_id."""
    resp = requests.post(
        f"{BASE}/query",
        headers=headers(key),
        json={"sql": sql, "performance": PERFORMANCE},
        timeout=60,
    )
    if resp.status_code == 402:
        sys.exit("Dune quota/credits exhausted on free tier — try again tomorrow.")
    resp.raise_for_status()
    data = resp.json()
    exec_id = data.get("execution_id")
    if not exec_id:
        sys.exit(f"Unexpected response: {data}")
    return exec_id


def wait_done(key: str, exec_id: str) -> str:
    deadline = time.time() + 300
    while time.time() < deadline:
        resp = requests.get(f"{BASE}/execution/{exec_id}/status",
                            headers=headers(key), timeout=30)
        resp.raise_for_status()
        state = resp.json().get("state", "")
        if state == "QUERY_STATE_COMPLETED":
            return state
        if state in {"QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"}:
            sys.exit(f"Query {state} — fetch error details from the Dune UI "
                     f"(execution {exec_id}) or check the SQL.")
        time.sleep(5)
    sys.exit("Timed out after 5 min — query too heavy for ad-hoc; "
             "narrow the date range and retry.")


def fetch_rows(key: str, exec_id: str) -> list[dict]:
    resp = requests.get(f"{BASE}/execution/{exec_id}/results",
                        headers=headers(key), timeout=60)
    resp.raise_for_status()
    return resp.json().get("result", {}).get("rows", [])


def print_table(rows: list[dict], limit: int) -> None:
    if not rows:
        print("(no rows returned)")
        return
    cols = list(rows[0].keys())
    shown = rows[:limit]
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in shown))
              for c in cols}
    print(" | ".join(str(c).ljust(min(widths[c], 40)) for c in cols))
    print("-+-".join("-" * min(widths[c], 40) for c in cols))
    for r in shown:
        print(" | ".join(str(r.get(c, "")).ljust(min(widths[c], 40)) for c in cols))
    if len(rows) > limit:
        print(f"... ({len(rows) - limit} more rows)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sql_file", help="path to a .sql file, e.g. sql/01_daily_transfers.sql")
    p.add_argument("--limit", type=int, default=30, help="rows to print (default 30)")
    p.add_argument("--save", help="also write full results to this CSV path")
    args = p.parse_args()

    sql_path = Path(args.sql_file)
    if not sql_path.is_absolute():
        sql_path = REPO_ROOT / sql_path
    sql = sql_path.read_text()

    key = api_key()
    print(f"Executing {sql_path.name} on Dune (ad-hoc)...")
    exec_id = execute_sql(key, sql)
    print(f"  execution_id: {exec_id}")
    wait_done(key, exec_id)
    rows = fetch_rows(key, exec_id)
    print(f"  {len(rows)} rows returned\n")
    print_table(rows, args.limit)

    if args.save:
        out = Path(args.save)
        out.parent.mkdir(parents=True, exist_ok=True)
        if rows:
            cols = list(rows[0].keys())
            with open(out, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols)
                w.writeheader()
                w.writerows(rows)
        else:
            out.write_text("")
        print(f"\nSaved -> {out}")


if __name__ == "__main__":
    main()
