# Phase 0 — Scope

Date written: 2026-11-11
Status: **proposed — pending validation on Dune/BigQuery** (see checklist below)

## Chosen assets

| Asset | Symbol | Contract (checksummed) | Decimals | Why |
|---|---|---|---|---|
| USD Coin | USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | 6 | The dominant stablecoin. Gives a high-volume baseline so RWA metrics can be compared against "normal" token behaviour (exchange flows, DeFi collateral, churn). |
| BlackRock USD Institutional Digital Liquidity Fund | BUIDL | `0x7712c34205737192402172409a8F7ccef8aA2AEc` | 6 | Largest tokenized treasury fund by market cap (~$2B+ reported late 2025). Issued via Securitize. Institutional distribution story. |
| Ondo Short-Term U.S. Government Bond Fund | OUSG | `0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92` | 18 | Retail-accessible Ondo treasury token with instant mint/redeem. Contrast with BUIDL's permissioned model. |
| Ondo US Dollar Yield | USDY | `0x96F6eF951840721AdBF46Ac996b59E0235CB985C` | 18 | Optional 4th asset — yield-bearing, non-rebasing design. Include if Phase 1 queries stay cheap; drop if it adds noise. |

Address sources (verified 2026-11-11):
- USDC: canonical Circle contract.
- BUIDL: official list at blackrock.com/corporate/compliance/scams-and-fraud/blackrock-token-addresses and Etherscan token page.
- OUSG / USDY: docs.ondo.finance/addresses (official Ondo docs).

## Known caveats (be honest about these in the write-up)

- **BUIDL is permissioned and rebasing.** Transfers are restricted to whitelisted addresses (Securitize compliance), and balances rebase with accrued yield rather than sitting still. Consequences: few free wallets, "holder churn" will look artificially low, and `totalSupply` grows continuously without Transfer events. Supply-over-time queries must treat rebase accrual separately from mint/burn flows.
- **OUSG has transfer restrictions too** (Ondo whitelist via `OndoIDRegistry`), but is less institutionally walled than BUIDL.
- **USDC is a proxy contract** (FiatTokenV2) — always query the proxy address above, not an implementation address.
- Etherscan holder counts for these tokens are tiny (BUIDL ~50–60 reported holders) because most supply sits in a handful of custodial/issuer wallets. That *is* the finding for Q2 — document it, don't explain it away.

## The 5 questions (locked for the dashboard)

1. How fast is supply growing, and is growth driven by a few large mints or many small ones?
2. How concentrated is ownership: top 10 share, and who are the top holders?
3. Are holders sticky or churning: new vs returning wallets per week?
4. Where does the activity go: exchanges, DeFi collateral, or plain wallets?
5. What does this mean for a platform listing or distributing these assets: where is liquidity, who are the natural partners?

## Phase 0 checklist — run these yourself on Dune

> **Trial strategy (decided 2026-11-11):** Dune free tier is view-only;
> use the 7-day free trial to build + publish the dashboard (public
> dashboards stay free to view after the trial). Do all query runs inside
> the trial window. After it ends, the pipeline uses BigQuery, not the
> Dune API.

1. Create a Dune account → start the free trial.
2. Paste `sql/00_verify_tables.sql`, run it.
   - If it errors, the spellbook table names have changed — check https://dune.com/data (`tokens` schema) and update the `-- VERIFY:` comments at the top of every `sql/0*.sql` file before continuing.
3. Run `sql/01_daily_transfers.sql` for each of the 4 contracts (change the `params` token address). Confirm you get non-empty results for at least USDC, BUIDL and OUSG.
4. Approve/adjust the asset list (e.g. drop USDY if its Dune coverage is thin).
5. **Done when:** a sample query returns transfers for each kept asset.

## Phase 1 checklist — build the public dashboard

1. Save each `sql/0*.sql` as a Dune query (they're written to be pasted as-is; set the token parameter per query or duplicate per asset — Dune dashboards support one query per asset, so expect ~4 queries × key visuals, or use a union across assets with a `symbol` column where the query supports it).
2. Arrange dashboard blocks: daily transfers, mints/burns, supply over time, top holders, holder count, new-vs-returning.
3. Publish the dashboard **publicly** (Dune → dashboard → visibility → public).
4. Reconciliation check: in `sql/03_supply_over_time.sql`, compare cumulative mints−burns to `totalSupply` from `tokens.erc20_ethereum`. State the tolerance you observe in the write-up. For BUIDL expect drift — rebases don't emit Transfer events; document the delta rather than forcing it to zero.
