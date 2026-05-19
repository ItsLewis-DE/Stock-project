import json
import pendulum
import requests
import os,logging
from dotenv import load_dotenv

def extract_companies(**kwargs):
    logger = logging.getLogger(__name__)
    load_dotenv('/usr/local/.env')
    # Sử dụng logical_date từ Airflow context thay vì pendulum.now()
    execution_date = kwargs['logical_date']
    exchanges = ['NYSE', 'NASDAQ', 'NYSEMKT', 'NYSEARCA', 'OTC', 'BATS', 'INDEX']
    result = []
    total =0
    for exchange in exchanges:
        try:
            params = {
                'token': os.getenv('API_COMPANIES')
            }
            url = f'https://api.sec-api.io/mapping/exchange/{exchange}'
            logger.info("Extracting data......")
            response = requests.get(url,params = params,timeout = 30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.exception('There are an error while extracting data from API!')
            raise
        result.extend(data)
        total += len(data)
    date = execution_date.strftime("%Y_%m_%d")
    path = f'/usr/local/data/raw/companies/raw_companies_{date}.json'
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,'w',encoding = 'utf-8') as file:
        json.dump(result,file,indent=2)
    logger.info(f"Extracting {total} successffuly!")
