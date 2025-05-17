# benchmark_service.py
# Service for fetching and managing benchmark data

import pandas as pd # type: ignore
import numpy as np # type: ignore
import os
import json
from datetime import datetime, timedelta
import requests # type: ignore
import time

# File to cache benchmark data
BENCHMARKS_CACHE_FILE = 'benchmarks_cache.json'
# Default cache duration (24 hours)
DEFAULT_CACHE_DURATION = 86400

# Define standard benchmarks and their symbols
STANDARD_BENCHMARKS = {
    'S&P 500': '^GSPC',
    'NASDAQ Composite': '^IXIC',
    'Dow Jones': '^DJI',
    'Russell 2000': '^RUT',
    'FTSE 100': '^FTSE',
    'DAX': '^GDAXI',
    'Nikkei 225': '^N225',
    'Bitcoin': 'BTC-USD',
    'Gold': 'GC=F',
    '10-Yr Treasury Yield': '^TNX'
}

from json import JSONDecodeError

def load_cache() -> dict:
    """
    Safely load the benchmark-data cache from disk.
    If the file is missing *or* corrupt we return a fresh, empty structure
    instead of propagating the JSONDecodeError.
    """
    if not os.path.exists(BENCHMARKS_CACHE_FILE):
        return {"benchmarks": {}, "timestamp": 0}

    try:
        with open(BENCHMARKS_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except JSONDecodeError:
        # Corrupted file – start over and avoid repeating the same console error
        print("⚠️  benchmarks_cache.json was corrupt – recreating from scratch")
        return {"benchmarks": {}, "timestamp": 0}
    except Exception as exc:
        print(f"Error loading benchmark cache: {exc}")
        return {"benchmarks": {}, "timestamp": 0}


def save_cache(cache: dict) -> None:
    """
    Write the cache to disk in a JSON-safe way.

    * Any non-serialisable values (e.g. pandas.Timestamp) are string-ified by the
      `default=str` hook.
    * We also pretty-print (`indent=2`) so a half-written file is easier to spot.
    """
    try:
        with open(BENCHMARKS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, default=str, indent=2, ensure_ascii=False)
    except Exception as exc:
        print(f"Error saving benchmark cache: {exc}")


def fetch_benchmark_data(symbol, start_date, end_date, api_key=None):
    """
    Fetch historical benchmark data from a financial API.
    In a production app, you would use a service like Alpha Vantage, Yahoo Finance, etc.
    
    For demo purposes without requiring an actual API key, this function returns simulated data.
    
    Args:
        symbol (str): Benchmark symbol (e.g., '^GSPC' for S&P 500)
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        api_key (str, optional): API key for the data service
        
    Returns:
        pandas.DataFrame: Historical data for the benchmark
    """
    try:
        # Convert dates to string format
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # For demo purposes, generate synthetic data
        # In a real application, you would call an API here
        
        # Check if we have the data in cache
        cache = load_cache()
        cache_key = f"{symbol}_{start_str}_{end_str}"

        if cache_key in cache.get('benchmarks', {}) and time.time() - cache['timestamp'] < DEFAULT_CACHE_DURATION:
            # Return cached copy
            cached_df = pd.DataFrame(cache['benchmarks'][cache_key])
            cached_df['Date'] = pd.to_datetime(cached_df['Date'])
            return cached_df

        # ------------------------------------------------------------------
        # Generate a simple random-walk price series to fill the requested
        # date range when we have no cached data.
        # ------------------------------------------------------------------
        # Business-day date index
        date_range = pd.date_range(start=start_date, end=end_date, freq="B")

        # Pick a plausible starting level per asset class
        seed_levels = {
            "BTC-USD": 30_000,
            "GC=F": 1_800,
            "^TNX": 2.0,
        }
        base_value = seed_levels.get(symbol, 3_000)   # fallback for equities

        # Pseudo-random daily %-moves ~N(0, 1%)
        rng = np.random.default_rng(abs(hash(symbol)) % 2**32)
        daily_changes = rng.normal(loc=0, scale=0.01, size=len(date_range))
        prices = base_value * (1 + daily_changes).cumprod()

        # Create DataFrame
        df = pd.DataFrame(
            {
                "Date": date_range,
                "Close": prices,
            }
        )


        # ... (code to add market events) ...

        # --- FIX APPLIED HERE on save: Convert Date column to string BEFORE saving ---
        # Copy df to avoid modifying the original DataFrame returned by the function
        df_to_cache = df.copy()
        if 'Date' in df_to_cache.columns:
            df_to_cache['Date'] = df_to_cache['Date'].dt.strftime('%Y-%m-%d')

        # Cache the data
        if 'benchmarks' not in cache:
            cache['benchmarks'] = {}

        cache['benchmarks'][cache_key] = df_to_cache.to_dict(orient='records')
        cache['timestamp'] = time.time()
        save_cache(cache)

        # Return the original DataFrame with Timestamp objects
        return df
    
    except Exception as e:
        print(f"Error fetching benchmark data: {e}")
        # Return empty DataFrame in case of error
        return pd.DataFrame(columns=['Date', 'Close'])

def get_benchmark_performance(benchmark_name, start_date, end_date):
    """
    Get performance data for a specific benchmark.
    
    Args:
        benchmark_name (str): Name of the benchmark (e.g., 'S&P 500')
        start_date (datetime): Start date for analysis
        end_date (datetime): End date for analysis
        
    Returns:
        pandas.DataFrame: Performance data with dates and values
    """
    # Get the symbol for the benchmark
    symbol = STANDARD_BENCHMARKS.get(benchmark_name)
    
    if not symbol:
        print(f"Unknown benchmark: {benchmark_name}")
        return pd.DataFrame(columns=['Date', 'Value'])
    
    # Fetch the data
    benchmark_data = fetch_benchmark_data(symbol, start_date, end_date)
    
    if benchmark_data.empty:
        return pd.DataFrame(columns=['Date', 'Value'])
    
    # Rename columns to match our expected format
    result = benchmark_data.rename(columns={'Close': 'Value'})
    
    # Add benchmark column
    result['Benchmark'] = benchmark_name
    
    return result

def get_all_benchmarks():
    """
    Get list of all available benchmarks.
    
    Returns:
        list: List of benchmark names
    """
    return list(STANDARD_BENCHMARKS.keys())

def refresh_benchmark_data(start_date, end_date, benchmarks=None):
    """
    Force refresh of benchmark data for specified date range.
    
    Args:
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        benchmarks (list, optional): List of benchmarks to refresh. If None, all benchmarks are refreshed.
        
    Returns:
        bool: True if refresh was successful, False otherwise
    """
    try:
        if benchmarks is None:
            benchmarks = get_all_benchmarks()
        
        for benchmark in benchmarks:
            symbol = STANDARD_BENCHMARKS.get(benchmark)
            if symbol:
                print(f"Refreshing data for {benchmark}...")
                fetch_benchmark_data(symbol, start_date, end_date, api_key=None)
        
        return True
    except Exception as e:
        print(f"Error refreshing benchmark data: {e}")
        return False

def calculate_benchmark_returns(benchmark_data):
    """
    Calculate percentage returns for benchmark data.
    
    Args:
        benchmark_data (pandas.DataFrame): Benchmark data with Date and Value columns
        
    Returns:
        pandas.DataFrame: Benchmark data with added returns columns
    """
    if benchmark_data.empty or 'Value' not in benchmark_data.columns:
        return benchmark_data
    
    # Sort by date
    benchmark_data = benchmark_data.sort_values('Date')
    
    # Calculate daily returns
    benchmark_data['DailyReturn'] = benchmark_data['Value'].pct_change() * 100
    
    # Calculate cumulative returns (indexed to 100 at start)
    first_value = benchmark_data['Value'].iloc[0]
    benchmark_data['CumulativeReturn'] = (benchmark_data['Value'] / first_value - 1) * 100
    
    return benchmark_data

# Example usage:
# start_date = datetime(2022, 1, 1)
# end_date = datetime(2022, 12, 31)
# sp500_data = get_benchmark_performance('S&P 500', start_date, end_date)
# sp500_with_returns = calculate_benchmark_returns(sp500_data)