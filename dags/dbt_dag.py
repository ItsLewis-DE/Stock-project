from cosmos.profiles import SnowflakeUserPasswordProfileMapping
from airflow.sdk import DAG
from cosmos import (
    DbtTaskGroup,
    ProjectConfig,
    ProfileConfig,
    ExecutionConfig,
    RenderConfig
)
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
execution_config=ExecutionConfig(dbt_executable_path=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt")
project_config = ProjectConfig("/usr/local/airflow/dags/dbt/stock_dbt")

with DAG(
    dag_id = "dbt_dag",
    schedule=None,
    start_date = pendulum.datetime(2025,1,1,tz='Asia/Ho_Chi_Minh'),
    catchup=True,
    default_args = {"retries":1},
) as dag:
    staging = DbtTaskGroup(
        group_id = 'staging',
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args= {
            "install_deps":True
        },
        render_config=RenderConfig(
            select=["+path:models/staging"],
            source_rendering_behavior ="all"
        )
    )
    marts = DbtTaskGroup(
        group_id="marts",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args={
            "install_deps": True
        },
        render_config=RenderConfig(
            select=['path:models/marts']
        )
    )

    staging >> marts