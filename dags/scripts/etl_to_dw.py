from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
import json
import pendulum
from dags.elt.extract.extract_news import extract_news
from dags.elt.extract.extract_ohlc import extract_ohlc
from dags.elt.load.load_to_s3_1 import load_to_s3_1
from dags.elt.load.load_to_s3_2 import load_to_s3_2
from dags.elt.transform.transform_parquet_1 import transform_parquet_1
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
default_args = {
    "owner" : 'phongthanh',
}

with DAG (
    dag_id='Extracing_API_and_load_data_data_warehouse',
    default_args = default_args,
    schedule = '0 12 * * *',
    start_date = pendulum.datetime(2025,1,1,tz='Asia/Ho_Chi_Minh'),
    catchup = True
) as dag:
    with TaskGroup(group_id="extract_phase") as extract_group:
        extract_news_task = PythonOperator(
            task_id = 'extract_news_task',
            python_callable = extract_news
        )
        extract_ohlc_task = PythonOperator(
            task_id = 'extract_ohlc_task',
            python_callable = extract_ohlc
        )
        [extract_news_task,extract_ohlc_task]
    with TaskGroup(group_id="load_phase") as load_group:
        load_to_s3_1_task = PythonOperator(
            task_id = 'load_to_s3_1_task',
            python_callable = load_to_s3_1
        )
        load_to_s3_2_task = PythonOperator(
            task_id='load_to_s3_2_task',
            python_callable = load_to_s3_2
        )
        load_to_s3_1_task >> load_to_s3_2_task 
    with TaskGroup(group_id="transform_phase") as transform_group:
        transform_to_parquet_1_task = PythonOperator(
            task_id = 'transform_to_parquet_1_task',
            python_callable = transform_parquet_1
        )
    trigger_dbt_dag = TriggerDagRunOperator(
        task_id = "trigger_dbt_dag",
        trigger_dag_id="dbt_dag",
        wait_for_completion=False
    )
    extract_group >> load_group >> transform_group >> trigger_dbt_dag
