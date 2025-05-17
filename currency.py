import requests
import time
from config import API_KEY, CACHE_DURATION

conversion_cache = {}

def fetch_exchange_rates():
    response = requests.get(f'https://openexchangerates.org/api/latest.json?app_id={API_KEY}')
    data = response.json()
    return data['rates']

def get_conversion_rate(currency):
    if currency == 'USD':
        return 1
    current_time = time.time()
    if currency in conversion_cache and (time.time() - conversion_cache[currency]['timestamp'] < CACHE_DURATION):
        return conversion_cache[currency]['rate']
    rates = fetch_exchange_rates()
    rate = rates.get(currency, 1)
    conversion_cache[currency] = {'rate': 1/rate, 'timestamp': current_time}
    return 1/rate