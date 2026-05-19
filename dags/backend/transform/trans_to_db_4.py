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
def trans_dataframe(df,col_conflict):
    return df.replace(r'^\s*$',np.nan,regex=True).drop_duplicates().dropna(subset=(col_conflict))
def df_to_file(df,dirname,filename,execution_date):
    logger = logging.getLogger(__name__)
    date = execution_date.strftime("%Y_%m_%d")
    dirname = Path(dirname)
    dirname.mkdir(parents=True,exist_ok=True)
    df.to_json(f'{dirname}/{filename}_{date}.json',orient='records',lines=True)
    logger.info("Saved to file successfully!")
def trans_to_db_4(**kwargs):
    execution_date = kwargs['logical_date']
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    dirpath = '/usr/local/data/raw/companies'
    extension = '.json'
    newest_file_comapnies = read_newest_file(dirpath,extension)
    df_company = pd.read_json(newest_file_comapnies)
    df_company = df_company.rename(columns = {
        'name':'company_name',
        'exchange':'exchange_name',
        'industry':'industry_name',
        'sic':'sic_code',
        'industry':'industry_name'
    })
    path_to_save = '/usr/local/data/processed/company'
    file_name = 'company_processed'
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    logger.info("Connecting to database!!")
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    query = " SELECT * FROM stock_schema.exchange"
    exchange_df = pd.read_sql(query,engine)

    query = " SELECT * FROM stock_schema.industry"
    industry_df = pd.read_sql(query,engine)

    query = "SELECT * FROM stock_schema.sic_classification"
    sic_df = pd.read_sql(query,engine)
    df_company = pd.merge(df_company,exchange_df,on = 'exchange_name',how='inner')
    df_company = pd.merge(df_company,industry_df,on='industry_name',how='inner')
    df_company = pd.merge(df_company,sic_df,on='sic_code',how='inner')
    col_conflict = ['cik','ticker']
    df_company = trans_dataframe(df_company[['company_name','ticker','cik','cusip','exchange_id','isDelisted','industry_id','location','currency','category','sic_code']],col_conflict)
    df_to_file(df_company,path_to_save,file_name,execution_date)
