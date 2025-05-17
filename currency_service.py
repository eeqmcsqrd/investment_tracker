# currency_service.py
import requests
import time
import json
import os
from datetime import datetime

# File to cache exchange rates
CACHE_FILE = 'exchange_rates_cache.json'
# Default cache duration (24 hours)
DEFAULT_CACHE_DURATION = 86400

def load_cache():
    """
    Load exchange rates from cache file.
    
    Returns:
        dict: Cached exchange rates data
    """
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                return cache
        return {'rates': {}, 'timestamp': 0}
    except Exception as e:
        print(f"Error loading cache: {e}")
        return {'rates': {}, 'timestamp': 0}

def save_cache(cache):
    """
    Save exchange rates to cache file.
    
    Args:
        cache (dict): Exchange rates data to cache
    """
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def fetch_exchange_rates(api_key):
    """
    Fetch exchange rates from the ExchangeRate API (v6).
    
    Args:
        api_key (str): API key for the ExchangeRate API service
        
    Returns:
        dict: Exchange rates data (with USD as base)
    """
    try:
        # If no API key is provided, use a fallback approach
        if not api_key:
            # For demo purposes, return some hardcoded rates
            # In a production application, you would use a proper API
            return {
                'USD': 1.0,
                'EUR': 0.92,
                'GBP': 0.78,
                'CAD': 1.35,
                'AUD': 1.45,
                'JPY': 108.0,
                'CHF': 0.87,
                'CNY': 7.1,
                'INR': 83.5,
                'BRL': 5.2,
                'RUB': 72.5,
                'MXN': 19.8,
                'SGD': 1.34,
                'NZD': 1.55,
                'SEK': 10.2,
                'NOK': 10.5,
                'DKK': 6.85,
                'PLN': 4.2,
                'CLP': 850.0
            }
        
        # Using ExchangeRate API v6 with USD as base currency
        base_url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
        response = requests.get(base_url)
        
        if response.status_code == 200:
            data = response.json()
            # ExchangeRate API returns rates under 'conversion_rates'
            # We need to map this to a format with USD as base
            if data['result'] == 'success':
                return data['conversion_rates']
            else:
                print(f"API returned error: {data.get('error', 'Unknown error')}")
                return {}
        else:
            print(f"Error fetching exchange rates: {response.status_code} - {response.text}")
            # Return empty dict if request fails
            return {}
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return {}

def get_conversion_rate(currency, api_key=None, cache_duration=DEFAULT_CACHE_DURATION):
    """
    Get conversion rate for a currency to USD.
    
    Args:
        currency (str): Currency code (e.g., 'EUR', 'GBP')
        api_key (str, optional): API key for the exchange rates service
        cache_duration (int, optional): Cache duration in seconds
        
    Returns:
        float: Conversion rate to USD (USD to currency)
    """
    # For USD, return 1.0 directly
    if currency == 'USD':
        return 1.0
    
    # Load cached rates
    cache = load_cache()
    current_time = time.time()
    
    # Check if cache is valid
    if current_time - cache['timestamp'] < cache_duration and currency in cache['rates']:
        # With ExchangeRate API, the rates are already USD to currency
        # so we don't need to invert them
        return 1.0 / cache['rates'][currency]
    
    # Fetch new rates if cache is invalid
    rates = fetch_exchange_rates(api_key)
    
    if rates:
        # Update cache
        cache = {
            'rates': rates,
            'timestamp': current_time,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_cache(cache)
        
        # Return conversion rate
        if currency in rates:
            # ExchangeRate API returns rates as USD to currency
            # Since we want currency to USD, we need to invert the rate
            return 1.0 / rates[currency]
    
    # If currency not found or rates fetch failed, return 1.0 as fallback
    return 1.0

def refresh_rates(api_key=None):
    """
    Force refresh of exchange rates.
    
    Args:
        api_key (str, optional): API key for the exchange rates service
        
    Returns:
        bool: True if refresh was successful, False otherwise
    """
    try:
        rates = fetch_exchange_rates(api_key)
        
        if rates:
            # Update cache
            cache = {
                'rates': rates,
                'timestamp': time.time(),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            save_cache(cache)
            return True
        
        return False
    except Exception as e:
        print(f"Error refreshing rates: {e}")
        return False

def get_all_rates(api_key=None, cache_duration=DEFAULT_CACHE_DURATION):
    """
    Get all available exchange rates.
    
    Args:
        api_key (str, optional): API key for the exchange rates service
        cache_duration (int, optional): Cache duration in seconds
        
    Returns:
        dict: Dictionary of all exchange rates
    """
    # Load cached rates
    cache = load_cache()
    current_time = time.time()
    
    # Check if cache is valid
    if current_time - cache['timestamp'] < cache_duration and cache['rates']:
        return cache['rates']
    
    # Fetch new rates if cache is invalid
    rates = fetch_exchange_rates(api_key)
    
    if rates:
        # Update cache
        cache = {
            'rates': rates,
            'timestamp': current_time,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_cache(cache)
        
        return rates
    
    # If rates fetch failed, return empty dict
    return {}