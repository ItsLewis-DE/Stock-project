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
def transform_company():
    dirpath = '/usr/local/data/raw/companies'
    extension = '.json'
    newest_file = read_newest_file(dirpath,extension)
    with open(newest_file,"r") as file:
        data = json.load(file)
    name = []
    ticker = []
    cik=[]
    cusip=[]
    exchange=[]
    isDelisted=[]
    category=[]
    sector=[]
    industry=[]
    sic=[]
    sicSector=[]
    sicIndustry=[]
    famaSector=[]
    famaIndustry=[]
    currency=[]
    location=[]
    for record in data:
        name.append(record['name'])
        ticker.append(record['ticker'])
        cik.append(record['cik'])
        cusip.append(record['cusip'])
        exchange.append(record['exchange'])
        isDelisted.append(record['isDelisted'])
        category.append(record['category'])
        sector.append(record['sector'])
        industry.append(record['industry'])
        sic.append(record['sic'])
        sicSector.append(record['sicSector'])
        sicIndustry.append(record['sicIndustry'])
        famaSector.append(record['famaSector'])
        famaIndustry.append(record['famaIndustry'])
        currency.append(record['currency'])
        location.append(record['location'])

    df_fama_classification = trans_dataframe(pd.DataFrame(
        {
            'fama_industry':famaIndustry,
            'fama_sector':famaSector
        }
    ))
    dirname = '/usr/local/data/processed/fama_classification'
    df_to_file(df_fama_classification,dirname,'fama_processed')