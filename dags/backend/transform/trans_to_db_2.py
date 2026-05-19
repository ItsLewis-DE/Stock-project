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
def trans_to_db_2(**kwargs):
    execution_date = kwargs['logical_date']

    #transform region

    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    dirpath = '/usr/local/data/raw/markets'
    extension = '.json'
    newest_market = read_newest_file(dirpath,extension)
    market_df = pd.read_json(newest_market)
    region_df = trans_dataframe(
        market_df[['region','market_type','local_open','local_close']]
    )
    region_df = region_df.rename(columns = 
        {
            'region':'region_name'
        }
    )
    path_to_file = '/usr/local/data/processed/region'
    filename = 'region_processed'
    df_to_file(region_df,path_to_file,filename,execution_date)

    #transform sic_classification

    dirpath = '/usr/local/data/raw/companies'
    extension = '.json'
    newest_file = read_newest_file(dirpath,extension)
    df = pd.read_json(newest_file)
    sic_df = trans_dataframe(df[['sic','sicIndustry','sicSector','famaIndustry']])
    sic_df['sicIndustry'].replace('\/','and',inplace = True)
    sic_df = sic_df.rename(columns={
        'sic':'sic_code',
        'sicIndustry':'sic_industry',
        'sicSector':'sic_sector',
        'famaIndustry':'fama_industry',
        'famaSector':'fama_sector'
    })

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    logger.info("Connecting to database!!")

    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(db_url)
    query = " SELECT * FROM stock_schema.fama_classification"
    df_fama = pd.read_sql(query,engine)
    sic_df = pd.merge(sic_df,df_fama,on = ['fama_industry'],how='inner')
    sic_df = sic_df[['sic_code','fama_id','sic_industry','sic_sector']]
    dirname = '/usr/local/data/processed/sic'
    df_to_file(sic_df,dirname,'sic_processed',execution_date)




    
