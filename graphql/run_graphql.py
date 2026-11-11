#!/usr/bin/env python3
"""Run a GraphQL query against a The Graph subgraph and save JSON.

Usage:
    python graphql/run_graphql.py                       # run the default query
    python graphql/run_graphql.py graphql/aave_v3_reserves.graphql out.json
    python graphql/run_graphql.py --introspect           # print schema (debugging)

Endpoint: The Graph decentralized network gateway.
    https://gateway.thegraph.com/api/<GRAPH_API_KEY>/subgraphs/id/<DEPLOYMENT_ID>

GRAPH_API_KEY is free at https://thegraph.com/studio/apikeys/ — put it in
.env. Without a key the gateway rejects requests; there is no truly
keyless production endpoint anymore (the old hosted service was sunset).

DEPLOYMENT_ID for Aave v3 Ethereum (verify before use — IDs rotate):
    QmX2VfvEspbShTdcjefWeG3CKBVXKWm9naxH6TVhqPb9qY
Override with --deployment or SUBGRAPH_DEPLOYMENT env var.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUERY = Path(__file__).resolve().parent / "aave_v3_reserves.graphql"
DEFAULT_OUT = REPO_ROOT / "data" / "aave_v3_reserves.json"
DEFAULT_DEPLOYMENT = "QmX2VfvEspbShTdcjefWeG3CKBVXKWm9naxH6TVhqPb9qY"
GATEWAY = "https://gateway.thegraph.com/api/{key}/subgraphs/id/{deployment}"

load_dotenv(REPO_ROOT / ".env")

INTROSPECTION_QUERY = "{ __schema { queryType { fields { name } } } }"


def build_endpoint(deployment: str) -> str:
    key = os.environ.get("GRAPH_API_KEY", "").strip()
    if not key:
        sys.exit(
            "GRAPH_API_KEY not set. Get a free key at "
            "https://thegraph.com/studio/apikeys/ and add it to .env."
        )
    return GATEWAY.format(key=key, deployment=deployment)


def run_query(endpoint: str, query: str) -> dict:
    resp = requests.post(
        endpoint,
        json={"query": query},
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        # Print GraphQL errors — usually a renamed field or dead subgraph.
        sys.exit(f"GraphQL errors: {json.dumps(payload['errors'], indent=2)[:2000]}")
    return payload.get("data", {})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_file", nargs="?", default=str(DEFAULT_QUERY))
    parser.add_argument("output", nargs="?", default=str(DEFAULT_OUT))
    parser.add_argument("--deployment", default=os.environ.get("SUBGRAPH_DEPLOYMENT", DEFAULT_DEPLOYMENT))
    parser.add_argument("--introspect", action="store_true",
                        help="query the schema instead of the .graphql file")
    args = parser.parse_args()

    endpoint = build_endpoint(args.deployment)
    query = INTROSPECTION_QUERY if args.introspect else Path(args.query_file).read_text()
    data = run_query(endpoint, query)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"Saved {len(json.dumps(data))} bytes -> {out}")


if __name__ == "__main__":
    main()
