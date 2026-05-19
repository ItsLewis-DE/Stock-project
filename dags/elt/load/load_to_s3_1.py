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

def trans_data_into_parquet(dirpath,filename,savedirpath):
    date = pendulum.now(tz='Asia/Ho_Chi_Minh').strftime("%Y_%m_%d")
    dirpath = Path(dirpath)
    savedirpath = Path(savedirpath)
    savedirpath.mkdir(parents=True,exist_ok=True)
    savepath = savedirpath/f"{filename}_{date}.parquet"
    extension = '.json'
    newest_file = read_newest_file(dirpath,extension)
    with open(newest_file,'r') as file:
        data_json = json.load(file)
    df = pd.DataFrame(data_json)
    df.to_parquet(
        savepath,
        engine = "pyarrow",
        index = False
    )
def trans_df_into_parquet(df,filename,savedirpath):
    date = pendulum.now(tz='Asia/Ho_Chi_Minh').strftime("%Y_%m_%d")
    savedirpath = Path(savedirpath)
    savedirpath.mkdir(parents=True,exist_ok=True)
    savepath = savedirpath/f"{filename}_{date}.parquet"
    df.to_parquet(
        savepath,
        engine = 'pyarrow',
        index = False
    )
def trans_ohlc(dirpath,savepath):
    newest_file_ohlc = read_newest_file(dirpath,'.json')
    df = pd.read_json(newest_file_ohlc)
    df = df.rename(columns = {
        't':'t_time'
    })
    df.to_json(savepath,indent=2,orient='records')
def load_to_s3_1():
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    # load ohlc
    dirpath = '/usr/local/data/raw/ohlc'
    filename = 'ohlc'
    savedirpath = '/usr/local/data/parquet/ohlc'
    savepath = f'/usr/local/data/raw/ohlc/raw_ohlc_2026_05_14.json'
    trans_ohlc(dirpath,savepath)
    trans_data_into_parquet(dirpath,filename,savedirpath)   

    #load news
    dirpath = '/usr/local/data/raw/news'
    filename = 'news'
    savedirpath = '/usr/local/data/parquet/news'
    trans_data_into_parquet(dirpath,filename,savedirpath)

    #load company
    logger.info("Connecting to database")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    logger.info("Connect succesfully!")
    query = " SELECT * FROM stock_schema.company"
    df_company = pd.read_sql(query,engine) 
    filename = 'company'
    savedirpath = '/usr/local/data/parquet/company'
    trans_df_into_parquet(df_company,filename,savedirpath)

    #load exchange
    logger.info("Connecting to database")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    logger.info("Connect succesfully!")
    query = " SELECT * FROM stock_schema.exchange"
    df_company = pd.read_sql(query,engine) 
    filename = 'exchange'
    savedirpath = '/usr/local/data/parquet/exchange'
    trans_df_into_parquet(df_company,filename,savedirpath)


    #load fama_classification
    logger.info("Connecting to database")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    logger.info("Connect succesfully!")
    query = " SELECT * FROM stock_schema.fama_classification"
    df_company = pd.read_sql(query,engine) 
    filename = 'fama_classification'
    savedirpath = '/usr/local/data/parquet/fama_classification'
    trans_df_into_parquet(df_company,filename,savedirpath)

    #load industry
    logger.info("Connecting to database")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    logger.info("Connect succesfully!")
    query = " SELECT * FROM stock_schema.industry"
    df_company = pd.read_sql(query,engine) 
    filename = 'industry'
    savedirpath = '/usr/local/data/parquet/industry'
    trans_df_into_parquet(df_company,filename,savedirpath)

    #load region
    logger.info("Connecting to database")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    logger.info("Connect succesfully!")
    query = " SELECT * FROM stock_schema.region"
    df_company = pd.read_sql(query,engine) 
    filename = 'region'
    savedirpath = '/usr/local/data/parquet/region'
    trans_df_into_parquet(df_company,filename,savedirpath)

    #load sic_classification
    logger.info("Connecting to database")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    logger.info("Connect succesfully!")
    query = " SELECT * FROM stock_schema.sic_classification"
    df_company = pd.read_sql(query,engine) 
    filename = 'sic_classification'
    savedirpath = '/usr/local/data/parquet/sic'
    trans_df_into_parquet(df_company,filename,savedirpath)



