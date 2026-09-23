# Results store (DuckDB + Parquet)

`src/elicitsec/store/results_store.py` provides a queryable results store that
sits alongside the canonical JSON run manifests.

## Layout

Within a results directory (e.g. `results/local`):

- `run-<CASE>-<id>.json`   canonical run manifest (unchanged, portable)
- `elicitsec.duckdb`       DuckDB database with a flat `runs` table
- `parquet/{runs,metrics,per_case}.parquet`  Parquet exports for tooling/regression

## Schema

The `runs` table flattens each RunManifest into one row keyed by `run_id`
(upsert: re-running a case with the same id replaces the row). Columns cover
case metadata, target/model policy hashes, the final classification and its
component flags, and evidence *counts* (raw transcript/authorization content
stays in the JSON manifests; the store records metadata only to stay lean).

## Usage

```sh
elicitsec run --suites suites --adapter mock --behavior safe --out results/local
elicitsec store --from results/local            # metrics + parquet export
elicitsec store --from results/local --sql "SELECT case_id, classification FROM runs"
elicitsec report --from results/local --query-store --out report.md
```

Query methods return rows as dicts (no pandas/numpy required); Parquet is
written natively by DuckDB.
