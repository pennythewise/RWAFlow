# RWA Flow Tracker

Public on-chain analytics for tokenized real-world assets on Ethereum: who holds tokenized treasury funds and a major stablecoin, how concentrated supply is, and where mints, burns and transfers come from.

Built as a portfolio project for on-chain data analysis: DuneSQL dashboard queries, a Python pipeline (Dune API → DuckDB), a GraphQL pull from The Graph, one BigQuery run on `crypto_ethereum`, and a short write-up.

## The 5 questions

1. How fast is supply growing, and is growth driven by a few large mints or many small ones?
2. How concentrated is ownership: top 10 share, and who are the top holders?
3. Are holders sticky or churning: new vs returning wallets per week?
4. Where does the activity go: exchanges, DeFi collateral, or plain wallets?
5. What does this mean for a platform listing or distributing these assets: where is liquidity, who are the natural partners?

## Assets analysed

| Asset | Contract (Ethereum, checksummed) | Type |
|---|---|---|
| USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | Stablecoin (baseline) |
| BUIDL | `0x7712c34205737192402172409a8F7ccef8aA2AEc` | BlackRock tokenized treasury fund |
| OUSG | `0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92` | Ondo short-term Treasury fund |
| USDY | `0x96F6eF951840721AdBF46Ac996b59E0235CB985C` | Ondo yield token (optional) |

See `docs/scope.md` for why these were chosen and known caveats (e.g. BUIDL is permissioned and rebasing — see `docs/standards.md`).

## Repo layout

```
sql/         DuneSQL queries — one file each, run in order (00 is a table-name probe)
pipeline/    dune_pull.py (Dune API → CSV) and load_duckdb.py (CSV → DuckDB)
graphql/     The Graph subgraph queries + runner
notebooks/   concentration.ipynb, bigquery_run.ipynb
docs/        scope, holder labels, executive summary, standards notes
data/        local DuckDB + cached results (gitignored)
.github/     daily refresh workflow
```

## Quick start

```bash
source .venv/bin/activate        # or use .venv/bin/python for every command
pip install -r pipeline/requirements.txt
```

> **Dune pricing note (verified 2026-11):** Dune's free tier is now
> view-only — running queries needs a 7-day trial or paid plan. Published
> dashboards stay free to view forever. Strategy: build the dashboard
> during the trial; the Python pipeline uses BigQuery (free) as its data
> source instead of the Dune API.

1. **Phase 0–1 (Dune):** paste `sql/00_verify_tables.sql` into Dune first to confirm table names, then each `sql/0*.sql` query. Publish the dashboard publicly from the Dune UI. (Or run them via API during the trial: `.venv/bin/python pipeline/run_sql.py sql/00_verify_tables.sql` — needs `DUNE_API_KEY` in `.env`.)
2. **Phase 4 (pipeline):** `.venv/bin/python pipeline/bigquery_pull.py` (free, no key beyond `gcloud auth`) or `python pipeline/dune_pull.py` during the Dune trial — then `python pipeline/load_duckdb.py`.
3. **Phase 3 (GraphQL):** `python graphql/run_graphql.py` — uses the public Aave v3 subgraph; set `SUBGRAPH_URL` in `graphql/config` notes inside the script if the endpoint changed.
4. **Analysis:** open `notebooks/concentration.ipynb` once `data/rwa.duckdb` exists.
5. **BigQuery:** open `notebooks/bigquery_run.ipynb` — it dry-runs first and prints bytes scanned before spending anything.

Full phase-by-phase checklist for the account-bound steps: `docs/scope.md` and each phase section in `AGENTS.md`.

## Status

- [ ] Dune dashboard published (needs Dune account — see checklist in `docs/scope.md`)
- [ ] Top holders labelled with sources (`docs/holder_labels.md`)
- [ ] GraphQL query joined to Dune data
- [ ] Daily GitHub Actions refresh running
- [ ] BigQuery run documented with real bytes scanned
- [ ] Write-up + executive summary (`docs/executive_summary.md`)

## Docs

- `docs/scope.md` — asset selection, caveats, Phase 0 checklist
- `docs/standards.md` — ERC-20/ERC-4626 events, checksummed addresses, labels (plain words)
- `docs/holder_labels.md` — top-holder label table with sources
- `docs/executive_summary.md` — one-page findings + 3 recommendations
