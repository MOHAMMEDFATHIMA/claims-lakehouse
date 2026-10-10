# Claims Lakehouse: PySpark + Airflow + dbt + Data Quality Agent

An end-to-end, **synthetic-data** data platform in the style of an insurance-claims lakehouse
(bronze, silver, gold) with orchestration, tested transformations, CI, and an automated
schema-drift / anomaly detector. No client or real customer data is used anywhere.

## Architecture

```
generate_claims.py ──> data/raw (CSV, 1M+ rows, deliberately dirty)
        │
   Spark: bronze.py ──> data/bronze  (raw as-is + ingestion metadata)
        │
   Spark: silver.py ──> data/silver  (typed, de-duplicated, validated;
        │                              bad rows -> quarantine; reconciliation assert)
   dbt (DuckDB or Snowflake) ──> gold: fct_claims_monthly  (+ dbt tests)
        │
   quality_agent/drift_detector.py ──> schema drift, null spikes, mean shifts
        │                              (+ optional LLM explanation hook)
   Airflow DAG orchestrates every step;  GitHub Actions runs tests + a small end-to-end run
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all           # data -> bronze -> silver -> gold -> dbt tests -> quality check
pytest -q          # unit tests (generator + drift detector)
```
Needs Java 11+/17 for Spark.

## Design decisions (talk about these in interviews)

- **Bronze keeps everything as strings.** Typing happens in silver, so a bad value never breaks ingestion.
- **Quarantine, don't drop.** Invalid rows go to `claims_quarantine`; silver asserts
  `bronze = silver + quarantine + duplicates_removed`, a count reconciliation that fails the run if rows go missing.
- **Partitioning:** silver is partitioned by `line_of_business`. Document your own measurements
  (file counts, query times) in `docs/performance.md` after you try different partitioning and `shuffle.partitions`.
- **dbt tests** cover uniqueness, nulls, accepted values, and a singular test for negative totals.
- **Same dbt models run on DuckDB (local) or Snowflake** by switching `--target`.
- **LLM only explains; rules detect.** Drift detection is deterministic; the optional LLM hook
  (Snowflake Cortex or any model) summarizes findings and recommends fixes.

## Results (measured on GitHub Codespaces, 2 cores, Spark 3.5, Java 17, Python 3.11)

| Metric | Value |
|---|---|
| Rows processed | 1,010,000 (1M generated + 10,000 injected duplicates) |
| Silver / quarantine / duplicates removed | 970,272 / 29,728 / 10,000 |
| Reconciliation | bronze = silver + quarantine + duplicates removed (passes) |
| Silver runtime (16 shuffle partitions) | about 38 seconds |
| dbt tests | 5 of 5 passing |
| Drift detector | no drift on clean data; flags changed column types |

## Status

Run end to end on GitHub Codespaces: generator, Spark bronze and silver, dbt gold models and tests (DuckDB),
and the drift detector. Airflow DAG is included but not run locally. Snowflake target is configured but not run.
