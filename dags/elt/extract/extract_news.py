import json
import pendulum
import requests
import os,logging
from pathlib import Path
from dotenv import load_dotenv
import time
def extract_timezone(timezone,execution_date):
    yesterday = execution_date.subtract(days=1)
    if timezone == 1:
        time_from = yesterday.strftime("%Y%m%dT" + "0000")
        time_to = yesterday.strftime("%Y%m%dT" + "0959")
    else:
        time_from = yesterday.strftime("%Y%m%dT" + "1000")
        time_to = yesterday.strftime("%Y%m%dT" + "2359")
    return time_from,time_to
def save_data_to_file(dirpath,data,filename,total,execution_date):
    logger = logging.getLogger(__name__)
    date = execution_date.strftime('%Y_%m_%d')
    dirpath = Path(dirpath)
    dirpath.mkdir(parents =True,exist_ok=True)
    filepath = dirpath/f"{filename}_{date}.json"
    with open(filepath,'w',encoding = 'utf-8') as file:
        json.dump(data,file,indent=2)
    logger.info(f"Saved {total} to file successfully!")
def extract_news(**kwargs):
    execution_date = kwargs['logical_date']
    logger = logging.getLogger(__name__)
    yesterday = execution_date.subtract(days=1)
    load_dotenv('/usr/local/.env')
    data_json = []
    total = 0
    for timezone in [1,2]:
        time_from,time_to = extract_timezone(timezone,execution_date)
        params = {
        'sort':'latest',
        'limit':50,
        'apikey':os.getenv("API_NEWS"),
        'function':'NEWS_SENTIMENT',
        'time_from':time_from,
        'time_to':time_to
        }
        try:
            logger.info("Extracting data from API")
            url = 'https://www.alphavantage.co/query'
            response = requests.get(url,params,timeout=30)
            response.raise_for_status()
            data_json.extend(response.json()['feed'])
        except requests.exceptions.RequestException as e:
            logger.exception(f"There is an error while extracting data from API: {e}")
            raise
        total +=len(data_json)
        time.sleep(5)
    logger.info("Succesfully")
    dirpath = '/usr/local/data/raw/news'
    filename = 'raw_news'
    save_data_to_file(dirpath,data_json,filename,total,execution_date)