import json
import pendulum
import requests
import pathlib,logging
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
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
    return df.replace(r'^\s*$',np.nan,regex=True).drop_duplicates().dropna(how='all')
def df_to_file(df,dirname,filename,execution_date):
    logger = logging.getLogger(__name__)
    date = execution_date.strftime("%Y_%m_%d")
    dirname = Path(dirname)
    dirname.mkdir(parents=True,exist_ok=True)
    df.to_json(f'{dirname}/{filename}_{date}.json',orient='records',lines=True)
    logger.info("Saved to file successfully!")

def trans_to_db_3(**kwargs):
    execution_date = kwargs['logical_date']
    #exchange table
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    dirpath = '/usr/local/data/raw/markets'
    extension = '.json'
    newest_market = read_newest_file(dirpath,extension)
    market_df = pd.read_json(newest_market)
    market_df = market_df[['region','primary_exchanges']]
    market_df = market_df.rename(columns={
        'region':'region_name',
        'primary_exchanges':'exchange_name'
    })
    market_df['exchange_name'] = market_df['exchange_name'].str.split(', ')
    market_df = market_df.explode('exchange_name').reset_index(drop=True)
    exchange_df =market_df

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    logger.info("Connecting to database!!")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    query = " SELECT * FROM stock_schema.region"
    region_df = pd.read_sql(query,con=engine)
    exchange_df = pd.merge(exchange_df, region_df,on='region_name',how='inner')
    exchange_df = exchange_df[['region_id','exchange_name']]
    dirname = '/usr/local/data/processed/exchange'
    df_to_file(exchange_df,dirname,'exchange_processed',execution_date)