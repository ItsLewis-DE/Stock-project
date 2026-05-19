import json
import pendulum
import requests
import pathlib,logging
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import psycopg2
import os
import pyarrow
from sqlalchemy import create_engine
import snowflake.connector
def trans_par(tablename,columns,col_conflict,execution_date):
    load_dotenv('/usr/local/.env')
    logger = logging.getLogger(__name__)
    current_date = execution_date.strftime("%Y_%m_%d")
    logger.info("Connecting to snowflake!")
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password = os.getenv("SNOWFLAKE_PASSWORD"),
        account = os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE"),
        database = os.getenv("SNOWFLAKE_DATABASE"),
        schema = os.getenv("SNOWFLAKE_SCHEMA"),
        role = os.getenv("SNOWFLAKE_ROLE")
    )
    cursor = conn.cursor()
    logger.info("Connect succesfully!!!!")
    query_create_stg = f"""
        CREATE TABLE IF NOT EXISTS stock_schema.{tablename}_stg
        LIKE stock_schema.{tablename};
    """
    query_copy_into_stage = f"""
        COPY INTO stock_schema.{tablename}_stg
        FROM @s3_sto/parquet/{tablename}/{current_date}/{tablename}.parquet
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        FILE_FORMAT = (TYPE = PARQUET);
    """
    columns_string = ', '.join([f'target.{col} = source.{col}' for col in columns if col not in col_conflict])
# 1. Giữ nguyên cấu trúc các cột insert như cũ
    columns_insert_string = ', '.join([f'{col}' for col in columns]) + ', inserted_at'
    
    # 2. Đổi 'DATEADD(...)' thành 'source.inserted_at_value'
    columns_value_string = ', '.join([f'source.{col}' for col in columns]) + ', source.inserted_at_value'
    
    conflict_conditions = [f'target.{col} = source.{col}' for col in col_conflict]
    col_conflict_string = ' AND '.join(conflict_conditions)
    
    # 3. Thay đổi mệnh đề USING: Thay vì dùng trực tiếp bảng _stg, 
    # chúng ta SELECT từ _stg và thêm một cột động chứa thời gian.
    # Format execution_date for Snowflake
    exec_date_str = execution_date.strftime("%Y-%m-%d %H:%M:%S")
    query_merge = f"""
        MERGE INTO stock_schema.{tablename} AS target
        USING (
            SELECT *, '{exec_date_str}'::TIMESTAMP_NTZ AS inserted_at_value 
            FROM stock_schema.{tablename}_stg
        ) AS source
        ON {col_conflict_string}
        WHEN MATCHED THEN
        UPDATE SET
                {columns_string}
        WHEN NOT MATCHED THEN 
        INSERT(
            {columns_insert_string}
            )
        VALUES(
            {columns_value_string}
            )
        """
    query_truncate = f"""
            TRUNCATE TABLE stock_schema.{tablename}_stg;
        """
    query_drop = f"""
            DROP TABLE stock_schema.{tablename}_stg;
    """

    cursor.execute(query_create_stg)
    cursor.execute(query_copy_into_stage)
    cursor.execute(query_merge)
    cursor.execute(query_truncate)
    cursor.execute(query_drop)
    conn.commit()
    cursor.close()
    conn.close()

def transform_parquet_1(**kwargs):
    # Lấy logical_date (execution date) từ Airflow context
    execution_date = kwargs['logical_date']
    
    # trans table company
    tablename = 'company'
    col_conflict = ['ticker','cik']
    columns = ['company_id','company_name','ticker','cik','cusip','exchange_id','isDelisted','industry_id','location','currency','category','sic_code']
    trans_par(tablename,columns,col_conflict,execution_date)

    #trans table exchange
    tablename = 'exchange'
    col_conflict = ['exchange_name']
    columns = ['exchange_id','exchange_name','region_id']
    trans_par(tablename,columns,col_conflict,execution_date)

    # trans table fama_classification
    tablename = 'fama_classification'
    columns = ['fama_id','fama_industry']
    col_conflict = ['fama_industry']
    trans_par(tablename,columns,col_conflict,execution_date)

    #trans table industry
    tablename = 'industry'
    columns = ['industry_id','industry_name','sector_name']
    col_conflict = ['industry_name']
    trans_par(tablename,columns,col_conflict,execution_date)

    #trans table news
    tablename = 'news'
    columns = ['title','url','time_published','authors','summary','banner_image','source','category_within_source','source_domain','topics','overall_sentiment_score','overall_sentiment_label','ticker_sentiment']
    col_conflict = ['title']
    trans_par(tablename,columns,col_conflict,execution_date)

    # #trans table ohlc
    tablename = 'ohlc'
    columns = ['T','v','vw','o','c','h','l','t_time','n']
    col_conflict = ['T','t_time']
    trans_par(tablename,columns,col_conflict,execution_date)

    #trans table sic_classification
    tablename = 'sic_classification'
    columns = ['sic_code','sic_industry','sic_sector','fama_id']
    col_conflict = ['sic_code']
    trans_par(tablename,columns,col_conflict,execution_date)

    #trans table region
    tablename = 'region'
    columns = ['region_id','region_name','market_type','local_open','local_close']
    col_conflict = ['region_name']
    trans_par(tablename,columns,col_conflict,execution_date)