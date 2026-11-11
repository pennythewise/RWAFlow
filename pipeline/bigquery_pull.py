#!/usr/bin/env python3
"""Pull token transfer history from BigQuery's public crypto_ethereum dataset.

This is the FREE fallback for pipeline data — no Dune API needed.
Dune's free tier is view-only, so after the trial this is how data/raw/
gets populated (Dune API path stays in dune_pull.py for trial use).

Usage:
    pip install google-cloud-bigquery pandas db-dtypes
    gcloud auth application-default login        # one-time auth
    .venv/bin/python pipeline/bigquery_pull.py                    # all assets, 2025-01-01 -> now
    .venv/bin/python pipeline/bigquery_pull.py --days 30          # narrower window
    .venv/bin/python pipeline/bigquery_pull.py --dry-run          # bytes only, no charge

Output: data/raw/bq_transfers_daily.csv — daily transfers per token
(symbol, day, transfers, senders, receivers). Feed into DuckDB via
load_duckdb.py like any other raw CSV.

Cost note: dry-run first. BigQuery free tier = 1 TiB/month; this query
scans a few GB — effectively free, but check the printed bytes anyway.
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"

load_dotenv(REPO_ROOT / ".env")

BQ_PROJECT_DATASET = "bigquery-public-data.crypto_ethereum"
TABLE = f"{BQ_PROJECT_DATASET}.token_transfers"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def build_query(start: str, end: str, contracts: list[str]) -> str:
    # BigQuery stores addresses lowercase.
    addr_list = ",\n        ".join(f"'{c.lower()}'" for c in contracts)
    return f"""
SELECT
    token_address,
    DATE(block_timestamp) AS day,
    COUNT(*) AS transfers,
    COUNT(DISTINCT from_address) AS senders,
    COUNT(DISTINCT to_address) AS receivers
FROM `{TABLE}`
WHERE token_address IN (
        {addr_list}
    )
  AND block_timestamp >= TIMESTAMP('{start}')
  AND block_timestamp < TIMESTAMP('{end}')
GROUP BY token_address, day
ORDER BY token_address, day
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=None,
                        help="lookback window in days (default: all of 2025+)")
    parser.add_argument("--start", default="2025-01-01", help="start date YYYY-MM-DD")
    parser.add_argument("--end", default=str(date.today()), help="end date YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true",
                        help="print bytes scanned and exit without running")
    parser.add_argument("--out", default="data/raw/bq_transfers_daily.csv")
    args = parser.parse_args()

    try:
        from google.cloud import bigquery
    except ImportError:
        sys.exit("google-cloud-bigquery not installed. Run:\n"
                 "  .venv/bin/pip install google-cloud-bigquery pandas db-dtypes")

    cfg = load_config()
    contracts = [a["contract"] for a in cfg["assets"].values()
                 if isinstance(a, dict) and a.get("contract")]

    start = args.start
    if args.days:
        start = str(date.today() - timedelta(days=args.days))

    query = build_query(start, args.end, contracts)
    client = bigquery.Client()

    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    dry = client.query(query, job_config=job_config)
    gib = dry.total_bytes_processed / 2**30
    print(f"Dry run: {gib:.2f} GiB scanned "
          f"(~${dry.total_bytes_processed / 2**40 * 6.25:.4f} on-demand; "
          f"free tier covers 1 TiB/month)")
    if args.dry_run:
        return

    job = client.query(query)
    df = job.result().to_dataframe()
    print(f"Rows: {len(df)} | bytes processed: {job.total_bytes_processed:,}")

    # Attach symbol names for readability downstream.
    sym = {a["contract"].lower(): a["symbol"] for a in cfg["assets"].values()
           if isinstance(a, dict) and a.get("contract")}
    df["symbol"] = df["token_address"].str.lower().map(sym)
    df = df[["symbol", "token_address", "day", "transfers", "senders", "receivers"]]

    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
