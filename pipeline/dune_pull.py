#!/usr/bin/env python3
"""Pull saved Dune query results through the Dune API into data/raw/.

Usage:
    cp .env.example .env   # add DUNE_API_KEY
    # save each sql/0*.sql as a Dune query, put the query IDs in
    # pipeline/config.yaml under dune.queries
    python pipeline/dune_pull.py                # pull all configured queries
    python pipeline/dune_pull.py --query top_holders_buidl   # pull just one

How it works (plain words):
    1. POST /query/{id}/execute  -> Dune starts running your saved query.
    2. Poll GET /execution/{exec_id}/status until it succeeds.
    3. GET /execution/{exec_id}/results -> CSV rows -> data/raw/<name>.csv.

Docs: https://docs.dune.com/api-reference (endpoints change — if a call
404s, check the current docs and update the paths below).
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"

load_dotenv(REPO_ROOT / ".env")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def get_api_key() -> str:
    key = os.environ.get("DUNE_API_KEY", "").strip()
    if not key:
        sys.exit(
            "DUNE_API_KEY not set. Get a free key at https://dune.com/settings/api, "
            "put it in .env (copy .env.example), and re-run."
        )
    return key


def dune_request(method: str, url: str, api_key: str, **kwargs) -> requests.Response:
    headers = {"X-DUNE-API-KEY": api_key, "Content-Type": "application/json"}
    resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    if resp.status_code == 429:
        sys.exit("Dune rate limit hit (429). Wait and retry — free tier is limited.")
    resp.raise_for_status()
    return resp


def execute_query(base_url: str, api_key: str, query_id: int) -> str:
    """Start execution of a saved Dune query; return the execution id."""
    resp = dune_request("POST", f"{base_url}/query/{query_id}/execute", api_key)
    data = resp.json()
    # Response shape: {"execution_id": "...", "state": "QUERY_STATE_..."}
    exec_id = data.get("execution_id")
    if not exec_id:
        sys.exit(f"Unexpected execute response: {data}")
    return exec_id


def wait_for_completion(base_url: str, api_key: str, exec_id: str, cfg: dict) -> None:
    interval = cfg["dune"].get("poll_interval_seconds", 10)
    deadline = time.time() + cfg["dune"].get("max_wait_seconds", 600)
    url = f"{base_url}/execution/{exec_id}/status"
    while time.time() < deadline:
        state = dune_request("GET", url, api_key).json().get("state", "")
        if state == "QUERY_STATE_COMPLETED":
            return
        if state in {"QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"}:
            sys.exit(f"Dune execution {exec_id} ended in state {state}")
        time.sleep(interval)
    sys.exit(f"Timed out waiting for Dune execution {exec_id}")


def fetch_results(base_url: str, api_key: str, exec_id: str) -> list[dict]:
    resp = dune_request("GET", f"{base_url}/execution/{exec_id}/results", api_key)
    data = resp.json()
    # Response shape: {"result": {"rows": [...]}} — rows are dicts keyed by column.
    rows = data.get("result", {}).get("rows")
    if rows is None:
        sys.exit(f"No rows in results payload: {list(data.keys())}")
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {len(rows)} rows -> {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="pull only this named query from config")
    args = parser.parse_args()

    cfg = load_config()
    queries: dict[str, int] = cfg["dune"].get("queries") or {}
    if not queries:
        sys.exit(
            "No queries configured. Save your sql/0*.sql queries on Dune, "
            "then map query names to query IDs in pipeline/config.yaml."
        )
    if args.query:
        if args.query not in queries:
            sys.exit(f"Unknown query '{args.query}'. Configured: {sorted(queries)}")
        queries = {args.query: queries[args.query]}

    api_key = get_api_key()
    base_url = cfg["dune"]["base_url"].rstrip("/")
    raw_dir = REPO_ROOT / cfg["paths"]["raw_dir"]

    for name, query_id in queries.items():
        print(f"[{name}] executing Dune query {query_id} ...")
        exec_id = execute_query(base_url, api_key, int(query_id))
        wait_for_completion(base_url, api_key, exec_id, cfg)
        rows = fetch_results(base_url, api_key, exec_id)
        write_csv(rows, raw_dir / f"{name}.csv")

    print("Done. Next: python pipeline/load_duckdb.py")


if __name__ == "__main__":
    main()
