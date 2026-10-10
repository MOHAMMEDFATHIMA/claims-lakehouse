select
    date_trunc('month', loss_date)                       as loss_month,
    line_of_business,
    state,
    count(*)                                             as claim_count,
    sum(incurred_amount)                                 as total_incurred,
    sum(paid_amount)                                     as total_paid,
    avg(report_lag_days)                                 as avg_report_lag_days,
    sum(case when status = 'OPEN' then 1 else 0 end)     as open_claims
from {{ ref('stg_claims') }}
group by 1, 2, 3
