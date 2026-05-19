import json
import pendulum
import requests
import os,logging
from pathlib import Path
from dotenv import load_dotenv
import time
def save_data_to_file(dirpath,data,filename,total):
    logger = logging.getLogger(__name__)
    date = pendulum.now(tz='Asia/Ho_Chi_Minh').strftime('%Y_%m_%d')
    dirpath = Path(dirpath)
    dirpath.mkdir(parents =True,exist_ok=True)
    filepath = dirpath/f"{filename}_{date}.json"
    with open(filepath,'w',encoding = 'utf-8') as file:
        json.dump(data,file,indent=2)
    logger.info(f"Saved {total} to file successfully!")

def extract_ohlc():
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    yesterday = pendulum.now(tz='Asia/Ho_Chi_Minh').subtract(days=1).strftime("%Y-%m-%d")
    try :
        url = f'https://api.massive.com/v2/aggs/grouped/locale/us/market/stocks/{yesterday}'
        params = {
            'adjusted':'true',
            'include_otc':'true',
            'apikey':os.getenv("API_OHLC")
        }
        response = requests.get(url,params = params,timeout=30)
        response.raise_for_status()
        data = response.json()['results']
        total = len(data)
    except requests.exceptions.RequestException as e:
        logger.exception("There is an error while extracting data from API: {e}")
        raise
    logger.info("Extracting data successfully!")
    dirpath = '/usr/local/data/raw/ohlc'
    filename = 'raw_ohlc'
    save_data_to_file(dirpath,data,filename,total)    