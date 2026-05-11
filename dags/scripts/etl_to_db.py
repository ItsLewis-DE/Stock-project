from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
import json
import pendulum
from dags.backend.extract.extract_companies import extract_companies
from dags.backend.extract.extract_markets import extract_markets
default_args = {
    "owner" : 'phongthanh',
}

with DAG (
    dag_id = 'Extract_API',
    default_args = default_args,
    schedule = '0 0 1 * *',
    start_date = pendulum.datetime(2025,1,1,tz='Asia/Ho_Chi_Minh'),
    catchup = False
) as dag:
    # extract_companies_task = PythonOperator(
    #     task_id = 'extract_companies',
    #     python_callable = extract_companies
    # )
    extract_markets_task = PythonOperator(
        task_id = 'extract_markets',
        python_callable=extract_markets
    )