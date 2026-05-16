from cosmos import DbtDag, ProjectConfig,ProfileConfig,ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping
import pendulum
import os
profile_config = ProfileConfig(
    profile_name = "default",
    target_name = "dev",
    profile_mapping = SnowflakeUserPasswordProfileMapping(
        conn_id = "snowflake_conn",
        profile_args = {'database':'stock_database','schema':'stock_schema'}
    )
)

basic_cosmos_dag = DbtDag(
        project_config = ProjectConfig("/usr/local/airflow/dags/dbt/stock_dbt"),
        profile_config = profile_config,
        operator_args = {
            "install_deps":True
        },
         execution_config=ExecutionConfig(dbt_executable_path=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt"),
        schedule = "@daily",
        start_date = pendulum.datetime(2025,1,1,tz='Asia/Ho_Chi_Minh'),
        catchup=False, 
        dag_id = "dbt_dag",
        default_args = {"retries":1} ,
)