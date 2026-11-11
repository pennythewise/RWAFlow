#!/usr/bin/env python3
"""Pull full ERC-20 transfer history for the RWA tokens via Routescan's
free Etherscan-compatible API — no key required.

Why this exists: BigQuery's free quota can't afford row-level pulls for
holder reconstruction, and Dune's free tier is view-only. Routescan gives
keyless access to the same tokentx data Etherscan serves. RWA token volumes
are small (thousands of transfers), so this is cheap and complete.

NOTE: the API caps results at ~10K records per contract query, so we
chunk by block range (1M blocks ≈ 4 months) and paginate inside each chunk.

Usage:
    .venv/bin/python pipeline/etherscan_pull.py            # all RWA assets in config
    .venv/bin/python pipeline/etherscan_pull.py --symbol OUSG

Output: data/raw/rwa_transfers.csv  (one row per Transfer event)
Then:    .venv/bin/python pipeline/analyze_holders.py     # balances, Gini, churn
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"
OUT_PATH = REPO_ROOT / "data" / "raw" / "rwa_transfers.csv"

BASE = ("https://api.routescan.io/v2/network/mainnet/evm/1"
        "/etherscan/api")
RPC = "https://ethereum-rpc.publicnode.com"   # free, no key, for block number
PAGE = 1000          # records per request
MAX_PAGES_PER_CHUNK = 10   # API caps ~10K records per query
CHUNK_BLOCKS = 1_000_000   # ~4 months of Ethereum blocks

load_dotenv(REPO_ROOT / ".env")

FIELDS = [
    "blockNumber", "timeStamp", "hash", "from", "to", "value",
    "contractAddress", "tokenName", "tokenSymbol", "tokenDecimal",
]


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def latest_block() -> int:
    resp = requests.post(RPC, json={
        "jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
        "params": []}, timeout=30)
    resp.raise_for_status()
    return int(resp.json()["result"], 16)


def fetch_chunk(contract: str, start: int, end: int) -> list[dict]:
    rows: list[dict] = []
    for page in range(1, MAX_PAGES_PER_CHUNK + 1):
        params = {
            "module": "account", "action": "tokentx",
            "contractaddress": contract,
            "startblock": start, "endblock": end,
            "sort": "asc", "offset": PAGE, "limit": PAGE, "page": page,
        }
        for attempt in range(3):
            resp = requests.get(BASE, params=params, timeout=60)
            if resp.status_code == 429 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            break
        payload = resp.json()
        result = payload.get("result")
        if payload.get("status") != "1" or not isinstance(result, list):
            msg = payload.get("message", "")
            if "No transactions found" in str(msg) or result == []:
                break
            sys.exit(f"API error for {contract} blocks {start}-{end}: {payload}")
        rows.extend(result)
        if len(result) < PAGE:
            break
        time.sleep(0.25)
    return rows


def fetch_token(symbol: str, contract: str, decimals: int,
                head: int) -> list[dict]:
    rows: list[dict] = []
    start = 0
    chunk_no = 0
    while start <= head:
        end = min(start + CHUNK_BLOCKS - 1, head)
        chunk_no += 1
        got = fetch_chunk(contract, start, end)
        if got:
            rows.extend(got)
            print(f"  {symbol}: chunk {chunk_no} "
                  f"(blocks {start}-{end}) -> {len(got)} rows")
        start = end + 1
        time.sleep(0.2)
    for r in rows:
        r["symbol"] = symbol
        r["decimals"] = decimals
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", help="only this asset symbol")
    args = parser.parse_args()

    cfg = load_config()
    assets = {k: v for k, v in cfg["assets"].items()
              if isinstance(v, dict) and v.get("contract")}
    if args.symbol:
        assets = {k: v for k, v in assets.items()
                  if v.get("symbol", "").upper() == args.symbol.upper()}
        if not assets:
            sys.exit(f"Unknown symbol {args.symbol}")

    # USDC has ~300M transfers — impossible via this API. RWA tokens only.
    assets = {k: v for k, v in assets.items()
              if v.get("symbol") != "USDC"}

    head = latest_block()
    print(f"Latest Ethereum block: {head}")

    all_rows: list[dict] = []
    for key, a in assets.items():
        print(f"[{key}] fetching {a['symbol']} {a['contract']}")
        all_rows.extend(fetch_token(a["symbol"], a["contract"],
                                    a["decimals"], head))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + ["symbol", "decimals"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nSaved {len(all_rows)} transfers -> {OUT_PATH}")


if __name__ == "__main__":
    main()
