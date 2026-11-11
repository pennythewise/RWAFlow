# AGENTS.md: RWA Flow Tracker

Instructions for the coding agent working in this repo. Read this file fully before doing anything, and re-read the "Rules" section before each phase.

## What this project is

A public on-chain analytics project: a Dune dashboard, a Python pipeline and a short write-up that analyse how tokenized real-world assets (tokenized treasury funds and one major stablecoin) move on Ethereum: who holds them, how concentrated supply is, and where mints, burns and transfers come from.

## How to work in this repo

- Explain each step in plain words before or after giving code. Keep explanations short; no lectures.
- Give runnable SQL and code, preferably in small steps rather than large dumps.
- Ask before choosing between options that change scope, cost or timeline.

## Repo layout

```
rwa-flow-tracker/
  AGENTS.md
  README.md            problem, findings, standards notes, how to run
  sql/                 every Dune query, one .sql file each, commented
  graphql/             subgraph queries (.graphql)
  pipeline/            dune_pull.py, bigquery_pull.py, etherscan_pull.py,
                       analyze_holders.py, load_duckdb.py, config.yaml
  notebooks/           concentration.ipynb, bigquery_run.ipynb
  data/                local DuckDB file and cached results (gitignored)
  .github/workflows/   scheduled refresh
  docs/                executive_summary.md, charts, scope, standards
  .env.example         names of required keys, no values
```

## Stack

| Layer | Tool |
| --- | --- |
| Query and dashboard | Dune (DuneSQL), BigQuery `crypto_ethereum` |
| Wallet labels | Nansen free tier, Arkham, or Etherscan labels |
| GraphQL | The Graph subgraph (e.g. Aave or Uniswap v3) |
| Transfer history | Routescan (Etherscan-compatible API, keyless) |
| Pipeline | Python 3.11, `requests`, `pandas`, `duckdb` |
| Storage | DuckDB locally (Supabase Postgres is an option) |
| Scheduling | GitHub Actions cron |
| Analysis | Jupyter, Plotly |
| Chain access | web3.py or ethers.js with a free RPC |

Free tiers only. If something needs a paid plan, stop and say so.

## Rules (non-negotiable)

1. **Verify before you assume.** Table names, schemas, API endpoints, rate limits and free-tier limits change. Before using any of them, check the current docs or run a test query. Do not write queries against table names from memory.
2. **Never commit secrets.** API keys (Dune, The Graph, RPC, BigQuery credentials) live in `.env` and GitHub Actions secrets. `.env` and `data/` are in `.gitignore` from the first commit. If you see a key in a file, say so — it must be rotated.
3. **Be honest about results and scale.** State real row counts and dataset sizes. Do not describe anything as "petabyte-scale" or "production" unless it is. No invented numbers, no placeholder results presented as findings.
4. **Label sources.** Every wallet label records where it came from (Nansen, Arkham, Etherscan, manual). If a label is a guess, mark it as a guess.
5. **Reproducible.** Every query is saved in `sql/` with a header comment (question answered, tables used, date written). Every script runs from a clean clone with documented commands.
6. **Read-only on chain.** Do not sign transactions, hold private keys or interact with contracts beyond reads and public queries.
7. **Small commits.** One logical change per commit, clear messages.
8. **No scope creep.** Do not add features outside the phases below without asking. Do not build a front end beyond the dashboard and notebooks.
9. **Stop and ask** when data is missing, a free tier blocks you, or results look wrong (for example supply that does not reconcile with mints minus burns).

## Phases and acceptance criteria

### Phase 0: scope
- Pick 2 or 3 tokenized treasury funds and 1 stablecoin on Ethereum.
- For each, confirm a verified ERC-20 contract and that it appears in on-chain transfer data.
- Write `docs/scope.md`: chosen assets with contract addresses (checksummed), why chosen, and the 5 questions below.
- **Done when:** the asset list is approved and a sample query returns transfers for each asset.

The 5 questions:
1. How fast is supply growing, and is growth driven by a few large mints or many small ones?
2. How concentrated is ownership: top 10 share, and who are they?
3. Are holders sticky or churning: new vs returning wallets per week?
4. Where does the activity go: exchanges, DeFi collateral, or plain wallets?
5. What does this mean for a platform listing or distributing these assets: where is liquidity, who are the natural partners?

### Phase 1: dashboard
- 6 to 8 queries: daily transfer count, mints and burns, circulating supply over time, top 20 holders, holder count over time, new vs returning holders.
- Each query saved in `sql/`. Dashboard published publicly.
- **Done when:** the public dashboard loads for a logged-out viewer, and the supply from mints minus burns reconciles with the token's `totalSupply` within a stated tolerance.

### Phase 2: tokenomics and labels
- Holder concentration: top 10 share and Gini coefficient, per asset, over time if feasible.
- Label top holders (exchange, issuer, fund, DeFi contract, unknown) and record the source.
- **Done when:** a table in `docs/` lists top holders with label and source, and the concentration numbers are in the dashboard or notebook.

### Phase 3: GraphQL
- Choose one protocol subgraph on The Graph that holds some of these assets (for example as collateral). Check the subgraph still exists and is queryable before committing to it.
- Save queries in `graphql/`. Join the result with holder data in a notebook.
- **Done when:** one GraphQL query runs from a script and its output is joined to holder data in `notebooks/`.

### Phase 4: pipeline and large-scale run
- `pipeline/`: pull results through APIs into DuckDB (`bigquery_pull.py`, `etherscan_pull.py`, `dune_pull.py`, `analyze_holders.py`, `load_duckdb.py`).
- GitHub Actions workflow refreshes on a schedule using repo secrets.
- One concentration query on BigQuery `crypto_ethereum`; record bytes scanned and dataset size honestly. Watch query cost; use dry runs first.
- README section explaining ERC-20 and ERC-4626 events, checksummed addresses, address labels and token metadata, in plain words.
- **Done when:** the workflow has run successfully on its own at least once, with no secrets in the repo history.

### Phase 5: write-up
- A ~600-word post with 3 charts, plus `docs/executive_summary.md`: one page, 3 recommendations, answering question 5.
- Final README: problem, findings, how to run, links to dashboard and post.
- **Done when:** every number in the write-up traces to a query in `sql/`, a pipeline output, or a notebook cell.

## Definition of done (whole project)

- [ ] Public dashboard is live and loads
- [ ] Top holders labelled, source of each label noted
- [ ] One GraphQL query runs and joins to holder data
- [ ] Pipeline refreshes on a schedule with no manual step
- [ ] BigQuery run documented, real dataset size stated
- [ ] README explains standards in plain words
- [ ] Write-up and executive summary done
- [ ] No API keys anywhere in the repo or its git history
- [ ] Public links ready to share

## At the end of each phase

Report three things: what was built, what changed in the README, and which results are new (with real numbers, no placeholders).
