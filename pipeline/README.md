# pipeline/

Pulls saved Dune query results into local DuckDB tables.

## Setup

```bash
cp ../.env.example ../.env   # add DUNE_API_KEY (free: dune.com/settings/api)
pip install -r requirements.txt
```

## Steps

1. Save each `sql/0*.sql` query on Dune (dune.com → new query → paste → run → save).
2. Map query names to Dune query IDs in `config.yaml` → `dune.queries`
   (the ID is the number in `dune.com/queries/<id>`).
3. `python dune_pull.py` — executes each saved query via the API and writes
   `data/raw/<name>.csv`.
4. `python load_duckdb.py` — loads all CSVs into `data/rwa.duckdb` under the
   `raw` schema and prints row counts + the reconciliation reminder.

No `DUNE_API_KEY`? `dune_pull.py` exits with instructions; you can still run
the SQL manually in the Dune UI and download CSVs into `data/raw/` — the
loader doesn't care where the CSVs came from.

## GitHub Actions

`.github/workflows/daily_refresh.yml` runs both scripts daily using the
`DUNE_API_KEY` repo secret. Add the secret under
Settings → Secrets and variables → Actions before expecting green runs.
