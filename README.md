# Claims Lakehouse: PySpark + Airflow + dbt + Data Quality Agent

An end-to-end, synthetic-data platform in the style of an insurance-claims lakehouse,
built to show how raw business data can be generated, validated, transformed, modeled,
and monitored in a production-like workflow. No client or real customer data is used anywhere.

## Overview

This project simulates a modern analytics pipeline for insurance claims:

- raw claims data is generated with intentional quality issues
- Spark ingests the raw data into a bronze layer
- the silver layer cleans, types, validates, and quarantines bad records
- dbt creates a gold reporting model and enforces tests
- a data-quality agent detects drift and anomalies over time
- Airflow and GitHub Actions automate orchestration and CI

This repository is useful for demonstrating practical data engineering skills in a clean, reproducible way.

## Architecture

```text
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
   Airflow DAG orchestrates every step; GitHub Actions runs tests + a small end-to-end run
```

## Why this project matters

It combines the main building blocks of a real analytics stack:

- data generation and ingestion
- transformation and validation
- quality enforcement and quarantine
- modeling with dbt
- schema monitoring and anomaly detection
- automation and continuous integration

This is the kind of end-to-end project interviewers and hiring managers can understand quickly because it maps directly to real-world data platform work.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all           # data -> bronze -> silver -> gold -> dbt tests -> quality check
pytest -q          # unit tests (generator + drift detector)
```

Needs Java 11+/17 for Spark.

## Key design decisions

- Bronze keeps everything as strings. Typing happens in silver so a bad value does not break ingestion.
- Quarantine, do not silently drop. Invalid rows are sent to the quarantine path and accounted for during reconciliation.
- Silver uses partitioning by line of business to support downstream analytics and efficient filtering.
- dbt tests cover uniqueness, nulls, accepted values, and negative totals.
- The same dbt models can run on DuckDB locally or Snowflake by switching the target.
- LLM support is optional and explanatory only; the core detection logic remains deterministic and rule-based.

## Results and measured checks

Measured on GitHub Codespaces with 2 cores, Spark 3.5, Java 17, and Python 3.11.

| Metric | Value |
|---|---|
| Rows processed | 1,010,000 (1M generated + 10,000 injected duplicates) |
| Silver / quarantine / duplicates removed | 970,272 / 29,728 / 10,000 |
| Reconciliation | bronze = silver + quarantine + duplicates removed (passes) |
| Silver runtime (16 shuffle partitions) | about 38 seconds |
| dbt tests | 5 of 5 passing |
| Drift detector | no drift on clean data; flags changed column types |

## Repository layout

```text
claims-lakehouse/
├── airflow/              # orchestration DAG
├── data/                 # raw, bronze, silver, gold artifacts
├── dbt/                  # dbt models and tests
├── docs/                 # project documentation and notes
├── quality_agent/        # schema drift and anomaly detection
├── spark/                # PySpark transformation scripts
├── src/                  # synthetic data generator
├── tests/                # Python unit tests
├── Makefile              # local pipeline commands
├── pytest.ini            # pytest configuration
├── requirements.txt      # project dependencies
├── README.md             # project overview
└── .github/workflows/    # CI automation
```

## Status

This project runs end-to-end on GitHub Codespaces: generator, Spark bronze and silver, dbt gold models and tests (DuckDB), and the drift detector. The Airflow DAG is included and ready for orchestration, while the Snowflake target is configured for compatibility but not executed locally.

## Best interview talking points

- end-to-end data engineering workflow
- lakehouse-style architecture with bronze/silver/gold layers
- Spark-based data cleaning and validation
- dbt modeling and testing
- schema drift and anomaly detection
- real-world data quality concerns handled in a controlled, synthetic environment
- automation with CI and orchestration
