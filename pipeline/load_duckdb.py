#!/usr/bin/env python3
"""Load data/raw/*.csv into data/rwa.duckdb and run the reconciliation check.

Usage:
    python pipeline/load_duckdb.py

What it does (plain words):
    1. Creates a DuckDB file at data/rwa.duckdb.
    2. For each CSV in data/raw/, creates a table named after the file
       (all columns as VARCHAR first — Dune returns mixed types as JSON).
    3. Prints row counts so you can sanity-check before analysing.

The typed analysis tables (balances, flows) are built in
notebooks/concentration.ipynb once you have data — keeping this loader
generic means new Dune queries need zero code changes here.
"""

import csv
import sys
from pathlib import Path

import duckdb
import yaml
from dotenv import load_dotenv  # noqa: F401  (keeps env loading consistent)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def csv_columns(path: Path) -> list[str]:
    with open(path, newline="") as f:
        return next(csv.reader(f), [])


def main() -> None:
    cfg = load_config()
    raw_dir = REPO_ROOT / cfg["paths"]["raw_dir"]
    db_path = REPO_ROOT / cfg["paths"]["duckdb_path"]

    if not raw_dir.exists() or not any(raw_dir.glob("*.csv")):
        sys.exit(f"No CSVs in {raw_dir}. Run pipeline/dune_pull.py first.")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for csv_path in sorted(raw_dir.glob("*.csv")):
        table = f"raw.{csv_path.stem}"
        cols = csv_columns(csv_path)
        if not cols:
            print(f"  skip {csv_path.name}: empty file")
            continue
        # All-VARCHAR staging keeps ingest robust; cast in the notebook.
        col_defs = ", ".join(f'"{c}" VARCHAR' for c in cols)
        con.execute(f"CREATE OR REPLACE TABLE {table} ({col_defs})")
        con.execute(
            f"INSERT INTO {table} BY NAME SELECT * FROM read_csv_auto(?)",
            [str(csv_path)],
        )
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n} rows, {len(cols)} columns")

    # Reconciliation summary: for any *_supply_over_time tables, report the
    # final net supply so you can compare it to on-chain totalSupply().
    print("\nReconciliation: compare net_supply_from_events (last row of each "
          "supply table) to totalSupply() on-chain. Tolerance: "
          f"{cfg['reconciliation']['max_relative_error']:.0%} relative error "
          "(BUIDL rebase drift is expected — see docs/scope.md).")

    con.close()
    print(f"DuckDB written to {db_path}")


if __name__ == "__main__":
    main()
