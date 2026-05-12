import json
import pendulum
import requests
import pathlib,logging
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np
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
def df_to_file(df,dirname,filename):
    logger = logging.getLogger(__name__)
    date = pendulum.now(tz='Asia/Ho_Chi_Minh').strftime("%Y_%m_%d")
    dirname = Path(dirname)
    dirname.mkdir(parents=True,exist_ok=True)
    df.to_json(f'{dirname}/{filename}_{date}.json',orient='records',lines=True)
    logger.info("Saved to file successfully!")
def transform_to_db():
    dirpath = '/usr/local/data/raw/companies'
    extension = '.json'
    newest_file = read_newest_file(dirpath,extension)
    df = pd.read_json(newest_file)
    df_fama = trans_dataframe(df[['famaIndustry','famaSector']])
    df_fama = df.rename(columns={
        'famaIndustry':'fama_industry',
        'famaSector':'fama_sector'
    })
    dirname = '/usr/local/data/processed/fama_classification'
    df_to_file(df_fama,dirname,'fama_processed')
    df_industry = trans_dataframe(df[['industry','sector']])
    df_industry = df_industry.rename(columns={
        'industry':'industry_name',
        'sector':'sector_name'
    })
    dirname = '/usr/local/data/processed/industry'
    df_to_file(df_industry,dirname,'industry_processed')

