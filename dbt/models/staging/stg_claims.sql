select
    claim_id,
    policy_id,
    line_of_business,
    state,
    loss_date,
    report_date,
    status,
    incurred_amount,
    paid_amount,
    date_diff('day', loss_date, report_date) as report_lag_days
from {{ source('silver', 'claims') }}
