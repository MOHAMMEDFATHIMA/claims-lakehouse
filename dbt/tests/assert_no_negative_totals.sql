-- Singular dbt test: fails if any gold row has negative incurred or paid totals.
select * from {{ ref('fct_claims_monthly') }}
where total_incurred < 0 or total_paid < 0
