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
def trans_par(tablename,columns,col_conflict):
    load_dotenv('/usr/local/.env')
    logger = logging.getLogger(__name__)
    current_date = pendulum.now(tz='Asia/Ho_Chi_Minh').subtract(days=1).strftime("%Y_%m_%d")
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
        FROM @s3_sto/parquet/{tablename}/{current_date}/{tablename}
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        FILE_FORMAT = (TYPE = PARQUET);
    """
    columns_string = ', '.join([f"target.{col} = source.{col}" for col in columns])
    columns_insert_string =', '.join([f"{col}" for col in columns])
    columns_value_string = ', '.join([f"source.{col}" for col in columns])
    col_conflict = [f"target.{col} = source.{col}" for col in col_conflict]
    col_conflict = ' AND '.join(col_conflict)
    query_merge = f"""
        MERGE INTO stock_schema.{tablename} AS target
        USING stock_schema.{tablename}_stg AS source
        ON {col_conflict}
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
    cursor.execute(query_create_stg)
    cursor.execute(query_copy_into_stage)
    cursor.execute(query_merge)
    cursor.execute(query_truncate)
    conn.commit()
    cursor.close()
    conn.close()

def transform_parquet_1():
    #trans table company
    tablename = 'company'
    col_conflict = ['ticker','cik']
    columns = ['company_id','company_name','ticker','cik','cusip','exchange_id','isDelisted','industry_id','location','currency','category','sic_code']
    trans_par(tablename,columns,col_conflict)

    #trans table exchange
    tablename = 'exchange'
    col_conflict = ['exchange_name']
    columns = ['exchange_id','exchange_name','region_id']
    trans_par(tablename,columns,col_conflict)

    # #trans table fama_classification
    # tablename = 'fama_classification'
    # columns = ['fama_id','fama_industry','fama_sector']
    # trans_par(tablename,columns)

    # #trans table industry
    # tablename = 'industry'
    # columns = ['industry_id','industry_name','sector_name']
    # trans_par(tablename,columns)

    # #trans table news
    # tablename = 'news'
    # columns = ['title','url','time_published','authors','summary','banner_image','source','category_within_source','source_domain','topics','overall_sentiment_score','overall_sentiment_lable','ticker_sentiment']
    # trans_par(tablename,columns)

    # #trans table ohlc
    # table_name = 'ohlc'
    # columns = ['T','v','vw','o','h','l','t','n']
    # trans_par(tablename,columns)