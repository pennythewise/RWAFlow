# RWA Flow Tracker

Public on-chain analytics for tokenized real-world assets on Ethereum: who holds tokenized treasury funds and a major stablecoin, how concentrated supply is, and where mints, burns and transfers come from.

Built as a personal data-engineering project: a Python ETL pipeline (BigQuery `crypto_ethereum` + Routescan API → DuckDB), 43,551 on-chain Transfer events reconstructed into holder balances, concentration and churn metrics, a public findings dashboard, and a set of DuneSQL queries ready for Dune.

## Headline findings (2025-01 → 2026-11)

| Metric | Result |
|---|---|
| USDC transfers (BigQuery, 277 GiB scanned) | 300.6M |
| BUIDL / OUSG / USDY transfers | 16.8K / 1.2K / 21.6K |
| Top-10 holder share | BUIDL 84.6% · OUSG 97.0% · USDY 94.0% |
| Gini coefficient | 0.85 – 0.99 across all three |
| Weekly new wallets | USDY ~17–45 · BUIDL/OUSG ~0 (permissioned) |

Full write-up: `docs/executive_summary.md`

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
| USDY | `0x96F6eF951840721AdBF46Ac996b59E0235CB985C` | Ondo yield token |

See `docs/scope.md` for why these were chosen and known caveats (e.g. BUIDL is permissioned and rebasing — see `docs/standards.md`).

## Repo layout

```
sql/         DuneSQL queries — one file each, run in order (00 is a table-name probe)
pipeline/    bigquery_pull.py, etherscan_pull.py, analyze_holders.py,
             dune_pull.py, run_sql.py, load_duckdb.py, config.yaml
graphql/     The Graph subgraph query + runner
notebooks/   concentration.ipynb, bigquery_run.ipynb
docs/        scope, executive summary, standards notes, charts/
data/        local DuckDB + cached results (gitignored)
.github/     scheduled refresh workflow
```

## How it works

```
Routescan API ──► rwa_transfers.csv ──┐
(BigQuery)   ──► bq_transfers_daily ──┼──► load_duckdb.py ──► data/rwa.duckdb
                                     │         │
                                     │         ▼
                                     └──► analyze_holders.py ──► top_holders.csv
                                                                     concentration_summary.csv
                                                                     weekly_churn.csv
                                                                          │
                                                                          ▼
                                                          docs/charts/findings.html
                                                          (GitHub Pages)
```

## Quick start

```bash
source .venv/bin/activate        # or use .venv/bin/python for every command
pip install -r pipeline/requirements.txt
```

1. **Transfer history (RWA tokens):** `.venv/bin/python pipeline/etherscan_pull.py` — keyless Routescan API, full history, ~10 min.
2. **Daily aggregates (all 4 assets):** `.venv/bin/python pipeline/bigquery_pull.py --dry-run` then without `--dry-run`. Needs `gcloud auth application-default login` once.
3. **Analysis:** `.venv/bin/python pipeline/analyze_holders.py` → `data/raw/top_holders.csv`, `concentration_summary.csv`, `weekly_churn.csv`.
4. **Load to DuckDB:** `.venv/bin/python pipeline/load_duckdb.py`.
5. **Dashboard:** `docs/charts/findings.html` is committed — open it locally or serve `docs/` statically to view.

> **Dune note:** Dune's free tier is view-only (verified 2026-11), so the
> live analysis ran on BigQuery + Routescan instead — same methodology,
> zero cost. `sql/` contains 9 DuneSQL queries ready to run if a Dune
> trial/plan is available (`pipeline/run_sql.py` runs any `sql/` file via
> the API with `DUNE_API_KEY` in `.env`).

## Status

- [x] Analysis executed end-to-end (BigQuery + Routescan → DuckDB)
- [x] Findings dashboard generated (`docs/charts/findings.html`)
- [x] BigQuery run documented — 277 GiB scanned, real bytes recorded
- [x] Executive summary + recommendations (`docs/executive_summary.md`)
- [x] DuneSQL query set written (`sql/`)
- [ ] Public dashboard published (optional)
- [ ] Top holders labelled with sources (`docs/holder_labels.md` — addresses generated, labels pending)
- [ ] GraphQL query run (`graphql/` ready, needs `GRAPH_API_KEY`)
- [ ] Scheduled refresh verified on GitHub Actions

## Docs

- `docs/scope.md` — asset selection, caveats, validation checklist
- `docs/standards.md` — ERC-20/ERC-4626 events, checksummed addresses, labels (plain words)
- `docs/holder_labels.md` — top-holder label table with sources
- `docs/executive_summary.md` — one-page findings + 3 recommendations
