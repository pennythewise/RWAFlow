# pipeline/

Pulls saved Dune query results into local DuckDB tables.

## Setup

```bash
cp ../.env.example ../.env   # add DUNE_API_KEY (free: dune.com/settings/api)
pip install -r requirements.txt
```

## Two data sources

- **`bigquery_pull.py`** — FREE, no Dune needed. Pulls daily transfer
  counts for all configured assets from BigQuery's public
  `crypto_ethereum` dataset. Requires `gcloud auth application-default
  login` once + `pip install google-cloud-bigquery pandas db-dtypes`.
  Always dry-runs first and prints bytes scanned.
- **`dune_pull.py`** — pulls saved Dune query results via the API.
  Requires `DUNE_API_KEY` **and a paid/trial Dune plan** (free tier is
  view-only). Use during the 7-day trial; after it ends, rely on the
  BigQuery path.

## Steps (BigQuery path — recommended)

1. `gcloud auth application-default login`
2. `.venv/bin/python pipeline/bigquery_pull.py --dry-run` — check bytes
3. `.venv/bin/python pipeline/bigquery_pull.py` — writes
   `data/raw/bq_transfers_daily.csv`
4. `.venv/bin/python pipeline/load_duckdb.py`

## Steps (Dune API path — trial only)

1. Save each `sql/0*.sql` query on Dune → map names to query IDs in
   `config.yaml` → `dune.queries`
2. `.venv/bin/python pipeline/dune_pull.py`
3. `.venv/bin/python pipeline/load_duckdb.py`

No `DUNE_API_KEY`? `dune_pull.py` exits with instructions; you can still run
the SQL manually in the Dune UI and download CSVs into `data/raw/` — the
loader doesn't care where the CSVs came from.

## GitHub Actions

`.github/workflows/daily_refresh.yml` runs both scripts daily using the
`DUNE_API_KEY` repo secret. Add the secret under
Settings → Secrets and variables → Actions before expecting green runs.
