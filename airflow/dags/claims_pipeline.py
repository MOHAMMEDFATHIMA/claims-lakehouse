from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="claims_lakehouse",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2},
    tags=["portfolio"],
) as dag:
    gen = BashOperator(task_id="generate_data", bash_command="cd /opt/project && make data")
    bronze = BashOperator(task_id="bronze", bash_command="cd /opt/project && make bronze")
    silver = BashOperator(task_id="silver", bash_command="cd /opt/project && make silver")
    gold = BashOperator(task_id="gold_dbt_run", bash_command="cd /opt/project && make gold")
    tests = BashOperator(task_id="dbt_test", bash_command="cd /opt/project && make dbt-test")
    quality = BashOperator(task_id="quality_agent", bash_command="cd /opt/project && make quality")
    gen >> bronze >> silver >> gold >> tests >> quality
