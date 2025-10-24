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
# Default API key (overridden by config if available)
DEFAULT_API_KEY = ''

try:  # Lazy import to avoid hard dependency on config during tests
    from config import API_KEY as CONFIG_API_KEY, CACHE_DURATION as CONFIG_CACHE_DURATION

    if CONFIG_API_KEY:
        DEFAULT_API_KEY = CONFIG_API_KEY

    # Ensure we only override when the config provides a truthy value
    if CONFIG_CACHE_DURATION:
        DEFAULT_CACHE_DURATION = int(CONFIG_CACHE_DURATION)
except Exception:
    # If config can't be imported (e.g., during certain tests), fall back to defaults
    pass

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
                if isinstance(cache, dict):
                    cache.setdefault('rates', {})
                    cache.setdefault('timestamp', 0)
                    cache.setdefault('source', 'unknown')
                return cache
        return {'rates': {}, 'timestamp': 0, 'source': 'unknown'}
    except Exception as e:
        print(f"Error loading cache: {e}")
        return {'rates': {}, 'timestamp': 0, 'source': 'unknown'}

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
            }, True
        
        # Using ExchangeRate API v6 with USD as base currency
        base_url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
        response = requests.get(base_url)
        
        if response.status_code == 200:
            data = response.json()
            # ExchangeRate API returns rates under 'conversion_rates'
            # We need to map this to a format with USD as base
            if data['result'] == 'success':
                return data['conversion_rates'], False
            else:
                print(f"API returned error: {data.get('error', 'Unknown error')}")
                return {}, False
        else:
            print(f"Error fetching exchange rates: {response.status_code} - {response.text}")
            # Return empty dict if request fails
            return {}, False
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return {}, False

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
    
    if cache_duration is None:
        cache_duration = DEFAULT_CACHE_DURATION

    if api_key is None:
        api_key = DEFAULT_API_KEY

    # Load cached rates
    cache = load_cache()
    current_time = time.time()
    cache_source = cache.get('source', 'unknown')
    cached_rates = cache.get('rates', {})

    # Treat "unknown" cache source as demo when an API key is supplied so we refresh once
    cache_is_demo = cache_source == 'demo' or (cache_source == 'unknown' and api_key)

    if (
        current_time - cache.get('timestamp', 0) < cache_duration
        and currency in cached_rates
        and not (cache_is_demo and api_key)
    ):
        # With ExchangeRate API, the rates are already USD to currency
        # so we don't need to invert them
        return 1.0 / cached_rates[currency]

    # Fetch new rates if cache is invalid
    rates, is_demo = fetch_exchange_rates(api_key)
    
    if rates:
        # Update cache
        cache = {
            'rates': rates,
            'timestamp': current_time,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S') if not is_demo else 'Demo rates - set API key',
            'source': 'demo' if is_demo else 'api'
        }
        save_cache(cache)
        
        # Return conversion rate
        if currency in rates and rates[currency]:
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
        if api_key is None:
            api_key = DEFAULT_API_KEY

        rates, is_demo = fetch_exchange_rates(api_key)
        
        if rates:
            # Update cache
            cache = {
                'rates': rates,
                'timestamp': time.time(),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S') if not is_demo else 'Demo rates - set API key',
                'source': 'demo' if is_demo else 'api'
            }
            save_cache(cache)
            # Return True for demo data only if no API key is configured
            return not is_demo or not api_key

        return False
    except Exception as e:
        print(f"Error refreshing rates: {e}")
        return False

def get_all_rates(api_key=None, cache_duration=None):
    """
    Get all available exchange rates.
    
    Args:
        api_key (str, optional): API key for the exchange rates service
        cache_duration (int, optional): Cache duration in seconds
        
    Returns:
        dict: Dictionary of all exchange rates
    """
    # Load cached rates
    if cache_duration is None:
        cache_duration = DEFAULT_CACHE_DURATION

    if api_key is None:
        api_key = DEFAULT_API_KEY

    cache = load_cache()
    current_time = time.time()
    cache_source = cache.get('source', 'unknown')

    # Treat "unknown" cache source as demo when an API key is supplied so we refresh once
    cache_is_demo = cache_source == 'demo' or (cache_source == 'unknown' and api_key)

    if (
        current_time - cache.get('timestamp', 0) < cache_duration
        and cache.get('rates')
        and not (cache_is_demo and api_key)
    ):
        return cache['rates']

    # Fetch new rates if cache is invalid
    rates, is_demo = fetch_exchange_rates(api_key)
    
    if rates:
        # Update cache
        cache = {
            'rates': rates,
            'timestamp': current_time,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S') if not is_demo else 'Demo rates - set API key',
            'source': 'demo' if is_demo else 'api'
        }
        save_cache(cache)

        return rates
    
    # If rates fetch failed, return empty dict
    return {}
