from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
import json
import pendulum
from dags.backend.extract.extract_companies import extract_companies
from dags.backend.extract.extract_markets import extract_markets
from dags.backend.transform.trans_to_db_1 import trans_to_db_1
from dags.backend.load.load_to_dp_1 import load_to_db_1
from dags.backend.transform.trans_to_db_2 import trans_to_db_2
from dags.backend.load.load_to_db_2 import load_to_db_2
from dags.backend.transform.trans_to_db_3 import trans_to_db_3
from dags.backend.load.load_to_db_3 import load_to_db_3
from dags.backend.transform.trans_to_db_4 import trans_to_db_4
from dags.backend.load.load_to_db_4 import load_to_db_4
default_args = {
    "owner" : 'phongthanh',
}

with DAG (
    dag_id='Extracing_API_and_load_data_to_database',
    default_args = default_args,
    schedule = '0 0 1 * *',
    start_date = pendulum.datetime(2026,5,18,tz='Asia/Ho_Chi_Minh'),
    catchup = True
) as dag:
    # with TaskGroup(group_id='extract_phase') as extract_group:
    #     extract_companies_task = PythonOperator(
    #         task_id = 'extract_companies',
    #         python_callable = extract_companies
    #     )
    #     extract_markets_task = PythonOperator(
    #         task_id = 'extract_markets',
    #         python_callable=extract_markets
    #     )
    #     [extract_companies_task,extract_markets_task]
    with TaskGroup(group_id = 'trans_and_load_1') as trans_and_load_1_group:
        trans_to_db_1_task = PythonOperator(
            task_id ='trans_to_db_1_task',
            python_callable = trans_to_db_1
        )
        load_to_db_1_task = PythonOperator(
            task_id = 'load_to_db_1_task',
            python_callable = load_to_db_1
        )
        trans_to_db_1_task >> load_to_db_1_task
    with TaskGroup(group_id = 'trans_and_load_2') as trans_and_load_2_group:
        trans_to_db_2_task = PythonOperator(
            task_id = 'transform_to_db_2_task',
            python_callable = trans_to_db_2
            )
        load_to_db_2_task = PythonOperator(
            task_id = 'load_to_db_2_task',
            python_callable = load_to_db_2
        )
        trans_to_db_2_task >> load_to_db_2_task
    with TaskGroup(group_id = 'trans_and_load_3') as trans_and_load_3_group:
        trans_to_db_3_task = PythonOperator(
            task_id = 'transform_to_db_3_task',
            python_callable = trans_to_db_3
        )
        load_to_db_3_task = PythonOperator(
            task_id = 'load_to_db_3_task',
            python_callable = load_to_db_3)
        trans_to_db_3_task >>load_to_db_3_task
    with TaskGroup(group_id = 'trans_and_load_4') as trans_and_load_4_group:
        trans_to_db_4_task = PythonOperator(
            task_id = 'trans_to_db_4_task',
            python_callable = trans_to_db_4
        )
        load_to_db_4_task = PythonOperator(
            task_id = 'load_to_db_4_task',
            python_callable = load_to_db_4
        )
        trans_to_db_4_task >>load_to_db_4_task
    # extract_group >> 
    trans_and_load_1_group >> trans_and_load_2_group >> trans_and_load_3_group >> trans_and_load_4_group