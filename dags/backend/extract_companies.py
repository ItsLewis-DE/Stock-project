import json
import pendulum
import requests
import os,logging
def extract_companies():
    exchanges = ['NYSE', 'NASDAQ', 'NYSEMKT', 'NYSEARCA', 'OTC', 'BATS', 'INDEX']
    for exchange in exchanges:
        params = {
            'exchange': exchange,
            'token':
        }
        url = 'https://api.sec-api.io/mapping/exchange/nasdaq?token=YOUR_API_KEY'