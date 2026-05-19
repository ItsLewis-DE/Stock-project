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
import boto3
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
def load_parquet_to_s3(dirpath,filename,extension):
    logger = logging.getLogger(__name__)
    parquet_newest_file = read_newest_file(dirpath,extension)
    load_dotenv('/usr/local/.env')
    logger.info("Connecting to S3!!!")
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.getenv('ACCESS_KEY'),
        aws_secret_access_key = os.getenv('SECRET_KEY'),
        region_name = os.getenv('REGION')
    )
    logger.info("Connected successfully!")
    date = pendulum.now(tz='Asia/Ho_Chi_Minh').strftime("%Y_%m_%d")
    s3.upload_file(
        parquet_newest_file,
        'stock-bucket-phong-2026',
        f'parquet/{filename}/{date}/{filename}.parquet'
    )
    logger.info("Parquet saved to S3")
def load_to_s3_2():
    #company file
    dirpath = '/usr/local/data/parquet/company'
    extension = '.parquet'
    filename = 'company'
    load_parquet_to_s3(dirpath,filename,extension)
    
    #exchange file
    dirpath = '/usr/local/data/parquet/exchange'
    extension = '.parquet'
    filename = 'exchange'
    load_parquet_to_s3(dirpath,filename,extension)

    #fama_classification
    dirpath = '/usr/local/data/parquet/fama_classification'
    extension = '.parquet'
    filename = 'fama_classification'
    load_parquet_to_s3(dirpath,filename,extension)

    # industry file
    dirpath = '/usr/local/data/parquet/industry'
    extension = '.parquet'
    filename = 'industry'
    load_parquet_to_s3(dirpath,filename,extension)

    #news file
    dirpath = '/usr/local/data/parquet/news'
    extension = '.parquet'
    filename = 'news'
    load_parquet_to_s3(dirpath,filename,extension)

    #ohlc file
    dirpath = '/usr/local/data/parquet/ohlc'
    extension = '.parquet'
    filename = 'ohlc'
    load_parquet_to_s3(dirpath,filename,extension)

    #region
    dirpath = '/usr/local/data/parquet/region'
    extension = '.parquet'
    filename = 'region'
    load_parquet_to_s3(dirpath,filename,extension)

    #sic_classification
    dirpath = '/usr/local/data/parquet/sic'
    extension = '.parquet'
    filename = 'sic_classification'
    load_parquet_to_s3(dirpath,filename,extension)