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
def transform_to_db_2():
    dirpath = '/usr/local/data/raw/markets'
    extension = '.json'
    newest_market = read_newest_file(dirpath,extension)
    market_df = pd.read_json(newest_market)
    region_df = trans_dataframe(
        market_df[['region','market_type','local_open','local_close']]
    )
    path_to_file = '/usr/local/data/processed/region'
    filename = 'region_processed'
    df_to_file(region_df,path_to_file,filename)
