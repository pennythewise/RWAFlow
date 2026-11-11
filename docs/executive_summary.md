# Executive summary — RWA Flow Tracker

One page. Three recommendations answering analysis question 5:
*where is liquidity, and who are the natural partners for a platform
listing or distributing these assets?*

> Skeleton — fill every number from a `sql/` query or a notebook cell.
> No number without a source.

## BigQuery run — completed 2026-11-11

Query: daily ERC-20 Transfer counts for USDC, BUIDL, OUSG, USDY from
`bigquery-public-data.crypto_ethereum.token_transfers`, 2025-01-01 →
2026-11-11. Script: `pipeline/bigquery_pull.py`.

- **Bytes scanned: 297,245,555,111 (~277 GiB)** — real number from the
  job's `total_bytes_processed`, within the 1 TiB/month free tier.
- **Rows returned: 2,175** daily aggregates → `data/raw/bq_transfers_daily.csv`
  → `data/rwa.duckdb` (`raw.bq_transfers_daily`).
- **Result:** 300.6M USDC transfers, 16.8K BUIDL, 21.6K USDY, 1.2K OUSG
  over the period — quantifies the "permissioned RWA tokens move far less
  on-chain than the stablecoin" finding.

## Findings (draft structure)

1. **Supply growth** — [asset]: supply grew X% over the period; growth was
   driven by [few large mints / many small mints] — source: `sql/02`, `sql/03`.
2. **Concentration** — top 10 holders control X% of [asset]; Gini = Y —
   source: `sql/07`, `notebooks/concentration.ipynb`.
3. **Holder behaviour** — Z% of weekly active wallets were new vs returning —
   source: `sql/06`. Note permissioned-token caveat for BUIDL/OUSG.
4. **Where supply sits** — X% of inflow went to [label category] —
   source: `sql/08` + `docs/holder_labels.md`.
5. **DeFi leg** — USDC supplied to Aave v3: $X total liquidity across
   reserves — source: `graphql/aave_v3_reserves.graphql`.

## Recommendations (fill in Phase 5)

1. [Partner/distributor insight 1 — e.g. which custodian or exchange
   wallets concentrate the float → natural distribution partner]
2. [Partner/distributor insight 2]
3. [Partner/distributor insight 3 — e.g. which asset has the stickiest
   holder base → priority for a listing]

## Numbers traceability

| Claim | Source |
|---|---|
| _every number in the summary_ | _sql file or notebook cell_ |
