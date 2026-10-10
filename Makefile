.PHONY: data bronze silver gold dbt-run dbt-test quality test all
data:
	python src/generate_claims.py --rows 1000000 --out data/raw/claims.csv
bronze:
	python spark/bronze.py
silver:
	python spark/silver.py
gold:
	cd dbt && dbt run --profiles-dir . --target duckdb
dbt-test:
	cd dbt && dbt test --profiles-dir . --target duckdb
quality:
	python quality_agent/drift_detector.py --baseline data/baseline_schema.json --data data/silver
test:
	pytest -q
all: data bronze silver gold dbt-test quality
