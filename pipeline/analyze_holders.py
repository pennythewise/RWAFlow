#!/usr/bin/env python3
"""Compute holder balances, concentration and churn from rwa_transfers.csv.

Reconstructs each address's balance as sum(in) - sum(out) over ALL
transfers (mints from 0x0 count as inflow automatically). Then computes:
  - top-10 share of supply
  - Gini coefficient
  - weekly new vs returning wallets
  - top-20 holder table -> data/raw/top_holders.csv (feed holder_labels.md)

Usage: .venv/bin/python pipeline/analyze_holders.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_PATH = REPO_ROOT / "data" / "raw" / "rwa_transfers.csv"
OUT_HOLDERS = REPO_ROOT / "data" / "raw" / "top_holders.csv"
OUT_SUMMARY = REPO_ROOT / "data" / "raw" / "concentration_summary.csv"
OUT_CHURN = REPO_ROOT / "data" / "raw" / "weekly_churn.csv"
ZERO = "0x0000000000000000000000000000000000000000"


def gini(x: pd.Series) -> float:
    """Gini coefficient, 0 = equal, 1 = concentrated."""
    xs = x.sort_values().to_numpy()
    n = len(xs)
    if n == 0 or xs.sum() == 0:
        return float("nan")
    i = np.arange(1, n + 1)
    return float((2 * (i * xs).sum()) / (n * xs.sum()) - (n + 1) / n)


def analyze(df: pd.DataFrame):
    df = df.copy()
    df["decimals"] = df["decimals"].astype(int)
    df["value"] = df["value"].astype(float)
    df["amount"] = df.apply(lambda r: r["value"] / 10 ** r["decimals"], axis=1)
    df["ts"] = pd.to_datetime(df["timeStamp"], unit="s", utc=True)
    df["week"] = df["ts"].dt.to_period("W").dt.start_time

    summary_rows, top_frames, churn_frames = [], [], []

    for sym, g in df.groupby("symbol"):
        inflow = g[g["to"] != ZERO].groupby("to")["amount"].sum()
        outflow = g[g["from"] != ZERO].groupby("from")["amount"].sum()
        bal = (inflow.subtract(outflow, fill_value=0)
               .sort_values(ascending=False))
        bal = bal[bal > 0]

        total = bal.sum()
        summary_rows.append({
            "symbol": sym,
            "holders": len(bal),
            "total_supply_held": round(total, 6),
            "top10_share_pct": round(100 * bal.head(10).sum() / total, 2) if total else None,
            "gini": round(gini(bal), 4),
        })

        top = (bal.head(20).rename("balance").reset_index()
               .rename(columns={"to": "address", "index": "address"}))
        top.insert(0, "symbol", sym)
        top["pct_of_supply"] = (100 * top["balance"] / total).round(4)
        top_frames.append(top)

        parts = pd.concat([
            g.loc[g["to"] != ZERO, ["to", "week"]].rename(columns={"to": "addr"}),
            g.loc[g["from"] != ZERO, ["from", "week"]].rename(columns={"from": "addr"}),
        ])
        first = parts.groupby("addr")["week"].min()
        weekly = parts.drop_duplicates(["addr", "week"]).copy()
        weekly["is_new"] = weekly["addr"].map(first) == weekly["week"]
        churn = (weekly.groupby("week")
                 .agg(active=("addr", "nunique"), new=("is_new", "sum"))
                 .reset_index())
        churn["symbol"] = sym
        churn["returning"] = churn["active"] - churn["new"]
        churn_frames.append(churn[["symbol", "week", "active", "new", "returning"]])

    return (pd.DataFrame(summary_rows),
            pd.concat(top_frames, ignore_index=True),
            pd.concat(churn_frames, ignore_index=True))


def main() -> None:
    if not IN_PATH.exists():
        sys.exit(f"{IN_PATH} missing — run pipeline/etherscan_pull.py first")
    df = pd.read_csv(IN_PATH)
    print(f"Loaded {len(df)} transfers")

    summary, top, churn = analyze(df)
    print("\n=== Concentration summary ===")
    print(summary.to_string(index=False))
    print("\n=== Top holders (head) ===")
    print(top.head(10).to_string(index=False))
    print("\n=== Weekly churn (latest weeks per asset) ===")
    print(churn.sort_values(["symbol", "week"]).groupby("symbol").tail(4)
          .to_string(index=False))

    OUT_HOLDERS.parent.mkdir(parents=True, exist_ok=True)
    top.to_csv(OUT_HOLDERS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    churn.to_csv(OUT_CHURN, index=False)
    print(f"\nSaved -> {OUT_HOLDERS}, {OUT_SUMMARY}, {OUT_CHURN}")


if __name__ == "__main__":
    main()
