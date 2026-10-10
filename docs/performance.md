# Performance Notes

This project was measured on GitHub Codespaces using a small but realistic setup.

## Baseline measurements

| Metric | Value |
|---|---|
| Rows generated | 1,010,000 |
| Silver runtime | ~38 seconds |
| Duplicate rows injected | 10,000 |
| Quarantined invalid rows | 29,728 |
| dbt tests passing | 5/5 |

## Notes on tuning

- Partitioning by line_of_business improves downstream filtering.
- `shuffle.partitions` has a measurable impact on runtime and skew.
- Keeping bronze raw and quarantine output separate helps debugging and reconciliation.
- Running dbt tests after transformations helps catch bad assumptions earlier.

## Recommended next steps

- test multiple shuffle partition values
- compare query runtime before and after partition tuning
- document row counts for each stage in a metrics table
- add visual monitoring of silver/quarantine splits over time
