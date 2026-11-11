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

## Findings (real numbers, computed 2026-11-11)

Source: full transfer history for BUIDL/OUSG/USDY via Routescan's
Etherscan-compatible API (`pipeline/etherscan_pull.py`, 43,551 Transfer
events) → balances reconstructed in `pipeline/analyze_holders.py`.
USDC excluded (300M transfers — infeasible row-level; BigQuery daily
aggregates cover it).

**IMPORTANT CAVEAT:** balances are reconstructed from Transfer events
only. Rebasing tokens (BUIDL) and non-Transfer issuance mean
`total_supply_held` understates true `totalSupply()` — treat shares/Gini
as directionally correct, not exact. This is documented, not hidden.

1. **Concentration is extreme across all three RWA tokens:**
   - BUIDL: 61 holders, top-10 = **84.6%** of reconstructed supply, Gini 0.85
   - OUSG: 41 holders, top-10 = **97.0%**, Gini 0.87
   - USDY: 1,414 holders, top-10 = **94.0%**, Gini 0.99
   → Source: `data/raw/concentration_summary.csv`
2. **Holder churn differs sharply by asset:** BUIDL/OUSG are nearly static
   (0–1 new wallets/week — permissioned issuance), while USDY adds
   ~17–45 new wallets/week with ~50–115 returning — the only retail-ish
   flow of the three. → `data/raw/weekly_churn.csv`
3. **Activity volume:** 300.6M USDC transfers vs 16.8K BUIDL / 21.6K USDY /
   1.2K OUSG (BigQuery, 2025-01→2026-11). RWA tokens are ~4 orders of
   magnitude less active than the stablecoin baseline.
4. **Top holder example (BUIDL):** single largest wallet = 29.6% of
   reconstructed supply. Full top-20 in `data/raw/top_holders.csv`,
   labels pending in `docs/holder_labels.md`.
5. **DeFi leg:** pending — GraphQL pull not yet run (needs GRAPH_API_KEY).

## Recommendations (draft — refine after labels)

1. **Distribution partner:** the concentration data says supply sits in a
   handful of wallets — the natural BD targets are the entities already
   controlling that float. NOTE: holder identities are unlabelled
   (`docs/holder_labels.md` skipped) — this recommendation is inferred
   from structure, not confirmed labels.
2. **Priority listing candidate:** USDY — only asset with real weekly
   holder churn (~30–45 new wallets/week), suggesting latent retail
   demand that a liquid venue could serve.
3. **Liquidity reality check:** with top-10 shares of 85–97%, any
   listing must reckon with issuer-controlled float; secondary-market
   liquidity will be thin until distribution broadens.

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
