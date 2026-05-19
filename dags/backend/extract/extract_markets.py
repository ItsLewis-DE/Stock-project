import json
import pendulum
import requests
import os,logging
from dotenv import load_dotenv

def extract_markets(**kwargs):
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    # Sử dụng logical_date từ Airflow context thay vì pendulum.now()
    execution_date = kwargs['logical_date']
    try:
        params = {
            'function':'MARKET_STATUS',
            'apikey': os.getenv('API_MARKETS')
        }
        url = 'https://www.alphavantage.co/query'
        logger.info("Extracting data .....")
        response  = requests.get(url,params = params,timeout =30 )
        response.raise_for_status()
        data = response.json()['markets']
        total = len(data)
        logger.info("Extracting data successfully!")
    except requests.exceptions.RequestException as e:
        logger.exception(f"There is an error while extracting data from API : {e}")
    date = execution_date.strftime("%Y_%m_%d")
    path = f'/usr/local/data/raw/markets/raw_markets_{date}.json'
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,"w",encoding = 'utf-8') as file:
        json.dump(data,file,indent=2)
    logger.info(f"Extracting {total} into file!")
    
        