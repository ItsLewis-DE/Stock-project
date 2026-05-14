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

def transform_parquet_1():
    load_dotenv('/usr/local/.env')
    logger = logging.getLogger(__name__)
    current_date = pendulum.now(tz='Asia/Ho_Chi_Minh').strftime("%Y_%m_%d")
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
    query_create_stg = """
            CREATE TABLE IF NOT EXISTS stock_schema.company_stg
            LIKE stock_schema.company;
        """
    query_copy_into_stg = f"""
            COPY INTO stock_schema.company_stg
            FROM @s3_sto/parquet/company/{current_date}/company
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            FILE_FORMAT = (TYPE = PARQUET);
        """
    query_merge = """
            MERGE INTO stock_schema.company AS target
            USING stock_schema.company_stg AS source
            ON target.cik = source.cik
            AND target.ticker = source.ticker
            WHEN MATCHED THEN
            UPDATE SET
                target.company_name = source.company_name,
                target.ticker = source.ticker,
                target.cusip = source.cusip,
                target.exchange_id = source.exchange_id,
                target.isDelisted = source.isDelisted,
                target.industry_id = source.industry_id,
                target.location = source.location,
                target.currency = source.currency,
                target.category = source.category,
                target.sic_code = source.sic_code
            WHEN NOT MATCHED THEN 
            INSERT(
                company_id,
                company_name,
                ticker,
                cik,
                cusip,
                exchange_id,
                isDelisted,
                industry_id,
                location,
                currency,
                category,
                sic_code
            )
            VALUES(
                source.company_id,
                source.company_name,
                source.ticker,
                source.cik,
                source.cusip,
                source.exchange_id,
                source.isDelisted,
                source.industry_id,
                source.location,
                source.currency,
                source.category,
                source.sic_code
                )
        """
    query_truncate = """
            TRUNCATE TABLE stock_schema.company_stg;
        """
    cursor.execute(query_truncate)
    cursor.execute(query_create_stg)
    cursor.execute(query_copy_into_stg)
    cursor.execute(query_merge)
    cursor.execute(query_truncate)
    conn.commit()
    cursor.close()
    conn.close()