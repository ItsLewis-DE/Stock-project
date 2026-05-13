from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
import json
import pendulum
from dags.backend.extract.extract_companies import extract_companies
from dags.backend.extract.extract_markets import extract_markets
from dags.backend.transform.trans_to_db_1 import transform_to_db
from dags.backend.load.load_to_dp_1 import load_to_db_1
from dags.backend.transform.trans_to_db_2 import transform_to_db_2
from dags.backend.load.load_to_db_2 import load_to_db_2
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
    # extract_markets_task = PythonOperator(
    #     task_id = 'extract_markets',
    #     python_callable=extract_markets
    # )
    # transform_company_task = PythonOperator(
    #     task_id ='transform_company',
    #     python_callable = transform_to_db
    # )
    load_to_db_1_task = PythonOperator(
        task_id = 'load_to_db_1_task',
        python_callable = load_to_db_1
    )
        # transform_to_db_2_task = PythonOperator(
        #         task_id = 'transform_to_db_2',
        #         python_callable = transform_to_db_2
        # )
    load_to_db_2_task = PythonOperator(
        task_id = 'load_to_db_2',
        python_callable = load_to_db_2
    )

