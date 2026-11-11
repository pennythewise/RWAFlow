# AGENTS.md: RWA Flow Tracker

Instructions for the coding agent working in this repo. Read this file fully before doing anything, and re-read the "Rules" section before each phase.

## What this project is

A public on-chain analytics project: a Dune dashboard, a Python pipeline and a short write-up that analyse how tokenized real-world assets (tokenized treasury funds and one major stablecoin) move on Ethereum: who holds them, how concentrated supply is, and where mints, burns and transfers come from.

**Why it exists.** The owner (Kan Penny, Data Science student, Universiti Malaya) is applying to Binance's On-Chain Data Analyst internship and has gaps against the job description. Every task here must close one of those gaps with evidence she can show and defend in an interview. Secondary use: supports her TradFi BD application (tokenized assets and RWA).

**Success = she can open a public link, walk a recruiter through the work, and explain every query and script herself.**

## The owner and how to work with her

- Strong: SQL, Python, Pandas, FastAPI, Supabase/Postgres, Solidity and Hardhat basics (has deployed contracts on Ethereum Sepolia and Monad Testnet), React/TypeScript.
- New to: Dune, Nansen, GraphQL/The Graph, tokenomics analysis, BigQuery, ERC-4626.
- Explain each step in plain words before or after giving code. She must be able to defend it in an interview. Short explanations; no lectures.
- Give her SQL and code she can run. Prefer small, runnable steps over large dumps.
- Ask before choosing between options that change scope, cost or timeline.

## Gap map (what each deliverable proves)

| JD requirement | Deliverable | Phase |
| --- | --- | --- |
| Dune analytics | Public Dune dashboard, 6 to 8 queries | 1 |
| Nansen or similar | Top holders labelled, source of each label recorded | 2 |
| Tokenomics, DeFi knowledge | Supply, concentration and flow analysis plus write-up | 2, 5 |
| SQL, GraphQL, Python | One subgraph query on The Graph joined with Dune data | 3 |
| Data engineering, ETL, APIs | Python pipeline: Dune API to DuckDB, daily refresh | 4 |
| Addressing and metadata standards | README section: ERC-20, ERC-4626, checksummed addresses, labels | 4 |
| Large-scale data | One BigQuery query on the Ethereum public dataset, size stated | 4 |
| Executive communication | One-page summary with 3 recommendations | 5 |

## Stack

| Layer | Tool |
| --- | --- |
| Query and dashboard | Dune (DuneSQL) |
| Wallet labels | Nansen free tier, Arkham, or Etherscan labels |
| GraphQL | The Graph subgraph (e.g. Aave or Uniswap v3) |
| Large-scale SQL | BigQuery public dataset `crypto_ethereum` |
| Pipeline | Python 3.11, `requests`, `pandas`, `duckdb` |
| Storage | DuckDB locally (Supabase Postgres is an option) |
| Scheduling | GitHub Actions cron |
| Analysis | Jupyter, Plotly |
| Chain access | web3.py or ethers.js with a free RPC |

Free tiers only. If something needs a paid plan, stop and tell her.

## Repo layout

```
rwa-flow-tracker/
  AGENTS.md
  README.md            problem, findings, standards notes, how to run
  sql/                 every Dune query, one .sql file each, commented
  graphql/             subgraph queries (.graphql)
  pipeline/            dune_pull.py, load_duckdb.py, config.yaml
  notebooks/           concentration.ipynb, bigquery_run.ipynb
  data/                local DuckDB file and cached results (gitignored)
  .github/workflows/   daily refresh
  docs/                executive_summary.md, charts
  .env.example         names of required keys, no values
```

## Rules (non-negotiable)

1. **Verify before you assume.** Table names, schemas, API endpoints, rate limits and free-tier limits change. Before using any of them, check the current docs or run a test query. Do not write queries against table names from memory.
2. **Never commit secrets.** API keys (Dune, The Graph, RPC, BigQuery credentials) live in `.env` and GitHub Actions secrets. `.env` and `data/` are in `.gitignore` from the first commit. If you see a key in a file she gives you, tell her to rotate it.
3. **Be honest about results and scale.** State real row counts and dataset sizes. Do not describe anything as "petabyte-scale" or "production" unless it is. No invented numbers, no placeholder results presented as findings.
4. **Label sources.** Every wallet label records where it came from (Nansen, Arkham, Etherscan, manual). If a label is a guess, mark it as a guess.
5. **Reproducible.** Every query is saved in `sql/` with a header comment (question answered, tables used, date written). Every script runs from a clean clone with documented commands.
6. **Read-only on chain.** Do not sign transactions, hold private keys or interact with contracts beyond reads and public queries.
7. **Small commits.** One logical change per commit, clear messages.
8. **No scope creep.** Do not add features outside the phases below without asking. Do not build a front end beyond the Dune dashboard and notebooks.
9. **Stop and ask** when data is missing, a free tier blocks you, or results look wrong (for example supply that does not reconcile with mints minus burns).

## Phases and acceptance criteria

### Phase 0: scope (about 1 hour)
- Pick 2 or 3 tokenized treasury funds and 1 stablecoin on Ethereum.
- For each, confirm a verified ERC-20 contract and that it appears in Dune's token transfer data.
- Write `docs/scope.md`: chosen assets with contract addresses (checksummed), why chosen, and the 5 questions below.
- **Done when:** she has approved the asset list and a sample query returns transfers for each asset.

The 5 questions:
1. How fast is supply growing, and is growth driven by a few large mints or many small ones?
2. How concentrated is ownership: top 10 share, and who are they?
3. Are holders sticky or churning: new vs returning wallets per week?
4. Where does the activity go: exchanges, DeFi collateral, or plain wallets?
5. What does this mean for a platform like Binance listing or distributing these assets: where is liquidity, who are the natural partners?

### Phase 1: Dune dashboard (4 to 6 hours)
- 6 to 8 queries: daily transfer count, mints and burns, circulating supply over time, top 20 holders, holder count over time, new vs returning holders.
- Each query saved in `sql/`. Dashboard published publicly.
- **Done when:** the public dashboard loads for a logged-out viewer, and the supply from mints minus burns reconciles with the token's `totalSupply` within a stated tolerance.

### Phase 2: tokenomics and labels (3 to 4 hours)
- Holder concentration: top 10 share and Gini coefficient, per asset, over time if feasible.
- Label top holders (exchange, issuer, fund, DeFi contract, unknown) and record the source.
- **Done when:** a table in `docs/` lists top holders with label and source, and the concentration numbers are in the dashboard or notebook.

### Phase 3: GraphQL (3 to 4 hours)
- Choose one protocol subgraph on The Graph that holds some of these assets (for example as collateral). Check the subgraph still exists and is queryable before committing to it.
- Save queries in `graphql/`. Join the result with Dune holder data in a notebook.
- **Done when:** one GraphQL query runs from a script and its output is joined to Dune data in `notebooks/`.

### Phase 4: pipeline and large-scale run (1 to 2 days)
- `pipeline/dune_pull.py`: pull saved Dune query results through the API. `pipeline/load_duckdb.py`: clean and load into DuckDB.
- GitHub Actions workflow refreshes daily using repo secrets.
- One concentration query on BigQuery `crypto_ethereum`; record bytes scanned and dataset size honestly. Watch query cost; use dry runs first.
- README section explaining ERC-20 and ERC-4626 events, checksummed addresses, address labels and token metadata, in plain words.
- **Done when:** the workflow has run successfully on its own at least once, with no secrets in the repo history.

### Phase 5: write-up (3 to 4 hours)
- A 600-word post with 3 charts, plus `docs/executive_summary.md`: one page, 3 recommendations, answering question 5.
- Final README: problem, findings, how to run, links to dashboard and post.
- **Done when:** every number in the write-up traces to a query in `sql/` or a notebook cell.

## Definition of done (whole project)

- [ ] Dune dashboard is public and loads
- [ ] Top holders labelled, source of each label noted
- [ ] One GraphQL query runs and joins to Dune data
- [ ] Pipeline refreshes daily with no manual step
- [ ] BigQuery run documented, real dataset size stated
- [ ] README explains standards in plain words
- [ ] Write-up and executive summary done
- [ ] No API keys anywhere in the repo or its git history
- [ ] Links ready for CV, GitHub and LinkedIn

## At the end of each phase

Tell her three things: what was built, what to put in the README, and what to add to her CV (with real numbers, no placeholders).
