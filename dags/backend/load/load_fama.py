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
def read_newest_file(dirpath,extension):
    logger = logging.getLogger(__name__)
    path = Path(dirpath)
    if not path.exists():
        logger.error("Can not found file!!")
        raise
    files = [file for file in path.iterdir() 
             if file.is_file() and file.suffix == extension
            ]
    if not files:
        return None
    newest_file = max(
        files,
        key = lambda file : file.stat().st_mtime
    )
    return newest_file

def trans_dataframe(df):
    return df.replace(r'^\s*$',np.nan,regex=True).drop_duplicates().dropna()

def load_data_into_db(data_json,table_name,columns,schema,col_conflict):
    logger = logging.getLogger(__name__)
    logger.info("Connecting db....")
    conn = psycopg2.connect(
        host = os.getenv('POSTGRES_HOST'),
        database = os.getenv('POSTGRES_DB'),
        user = os.getenv('POSTGRES_USER'),
        password = os.getenv("POSTGRES_PASSWORD") ,
        port = os.getenv("POSTGRES_PORT")
    )
    logger.info("Connect succesfully !!")
    placeholders = ','.join(['%s'] * len(columns))
    columns_string = ', '.join(columns)
    updated_string = ', '.join(
        [f"{col} = EXCLUDED.{col}" for col in columns]
    )
    query = f"""
        INSERT INTO {schema}.{table_name} ({columns_string})
        VALUES ({placeholders})
        ON CONFLICT ({col_conflict})
        DO UPDATE SET
            {updated_string}
        """
    cursor = conn.cursor()
    for line in data_json:
        values = tuple(line[col] for col in columns)
        cursor.execute(query,values)
    conn.commit()

def load_fama():
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    extension = '.json'

    # fama table
    dirpath = '/usr/local/data/processed/fama_classification'
    fama_file = read_newest_file(dirpath,extension)
    with open(fama_file,"r") as file:
        data = [json.loads(line) for line in file if line.strip()]
    schema = 'stock_schema'
    col_conflict = 'fama_industry'
    load_data_into_db(data,'fama_classification',['fama_industry','fama_sector'],schema,col_conflict)

    #industry table

    dirpath = '/usr/local/data/processed/industry'
    industry_file = read_newest_file(dirpath,extension)
    with open(industry_file,'r') as file:
        data = [json.loads(line) for line in file if line.strip()]
    schema = 'stock_schema'
    col_conflict = 'industry_name'
    load_data_into_db(data,'industry',['industry_name','sector_name'],schema,col_conflict)        

