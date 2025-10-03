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
    'S&P 500': '^GSPC',                 # price index (no dividends)
    'S&P 500 (Total Return)': '^SP500TR',  # includes dividends
    'NASDAQ Composite': '^IXIC',
    'Dow Jones': '^DJI',
    'Russell 2000': '^RUT',
    'FTSE 100': '^FTSE',
    'DAX': '^GDAXI',
    'Nikkei 225': '^N225',
    'Bitcoin': 'BTC-USD',
    'Gold': 'GC=F',
    '10-Yr Treasury Yield': '^TNX'      # note: yield level, not a return series
}


from json import JSONDecodeError

_cache_memory = None  # In-memory cache to avoid repeated disk reads

def load_cache() -> dict:
    """
    Safely load the benchmark-data cache from disk with in-memory caching.
    If the file is missing *or* corrupt we return a fresh, empty structure
    instead of propagating the JSONDecodeError.
    """
    global _cache_memory

    # Return from memory if already loaded
    if _cache_memory is not None:
        return _cache_memory

    if not os.path.exists(BENCHMARKS_CACHE_FILE):
        _cache_memory = {"benchmarks": {}, "timestamp": 0}
        return _cache_memory

    try:
        with open(BENCHMARKS_CACHE_FILE, "r", encoding="utf-8") as f:
            _cache_memory = json.load(f)
            return _cache_memory
    except JSONDecodeError:
        # Corrupted file – start over and avoid repeating the same console error
        print("⚠️  benchmarks_cache.json was corrupt – recreating from scratch")
        _cache_memory = {"benchmarks": {}, "timestamp": 0}
        return _cache_memory
    except Exception as exc:
        print(f"Error loading benchmark cache: {exc}")
        _cache_memory = {"benchmarks": {}, "timestamp": 0}
        return _cache_memory


def save_cache(cache: dict) -> None:
    """
    Write the cache to disk in a JSON-safe way.

    * Any non-serialisable values (e.g. pandas.Timestamp) are string-ified by the
      `default=str` hook.
    * We also pretty-print (`indent=2`) so a half-written file is easier to spot.
    """
    global _cache_memory
    try:
        with open(BENCHMARKS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, default=str, indent=2, ensure_ascii=False)
        _cache_memory = cache  # Update in-memory cache
    except Exception as exc:
        print(f"Error saving benchmark cache: {exc}")


def fetch_benchmark_data(symbol, start_date, end_date, api_key=None):
    """
    Fetch daily closes from Yahoo Finance's 'chart' endpoint and cache them.
    Robust to rate-limiting (429) via throttling + exponential backoff.
    No third-party dependencies (urllib + json).

    Behavior:
    - Anchors to the first available trading day *inside* [start_date, end_date].
    - Uses 'adjclose' when present; falls back to 'close'.
    - Caches per symbol+window so subsequent app runs don't refetch.
    """
    import json, time, random
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    # Return from cache if present
    cache = load_cache()
    cache_key = f"{symbol}|{pd.to_datetime(start_date).date()}|{pd.to_datetime(end_date).date()}"
    if cache and isinstance(cache, dict):
        cached = cache.get("benchmarks", {}).get(cache_key)
        if cached:
            df_cached = pd.DataFrame(cached)
            df_cached["Date"] = pd.to_datetime(df_cached["Date"])
            return df_cached

    # Small buffer around the window to capture first/last trading day
    p1_dt = pd.to_datetime(start_date) - pd.Timedelta(days=5)
    p2_dt = pd.to_datetime(end_date)   + pd.Timedelta(days=2)

    # Convert to unix seconds (UTC)
    p1 = int(p1_dt.tz_localize("UTC").timestamp())
    p2 = int(p2_dt.tz_localize("UTC").timestamp())

    base_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": p1,
        "period2": p2,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }
    full_url = base_url + "?" + urlencode(params)

    # Simple cross-run throttle to avoid 429s if multiple benchmarks are requested
    if not hasattr(fetch_benchmark_data, "_last_req_ts"):
        fetch_benchmark_data._last_req_ts = 0.0

    def sleep_until_allowed(min_interval=2.5):
        now = time.time()
        wait = min_interval - (now - fetch_benchmark_data._last_req_ts)
        if wait > 0:
            time.sleep(wait)

    attempts, max_attempts = 0, 6
    backoff_base = 1.5  # grows 1.5^n with jitter

    while attempts < max_attempts:
        attempts += 1
        sleep_until_allowed()

        req = Request(
            full_url,
            headers={
                # Some endpoints are pickier without a UA
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/plain, */*",
                "Connection": "close",
            },
        )

        try:
            with urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            fetch_benchmark_data._last_req_ts = time.time()

            results = payload.get("chart", {}).get("result", [])
            if not results:
                raise ValueError("No 'result' in Yahoo response")

            res = results[0]
            ts = res.get("timestamp", [])
            inds = res.get("indicators", {})
            adj = (inds.get("adjclose") or [{}])[0].get("adjclose")
            close = (inds.get("quote") or [{}])[0].get("close")

            values = adj if (isinstance(adj, list) and any(v is not None for v in adj)) else close
            if not values or not ts:
                raise ValueError("Missing close series or timestamps in Yahoo response")

            df = pd.DataFrame({
                "Date": pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None),
                "Close": values,
            }).dropna(subset=["Close"])

            # Keep only requested window
            df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
            df = df.sort_values("Date").reset_index(drop=True)

            # Cache (store Date as ISO strings)
            cache = load_cache()
            cache.setdefault("benchmarks", {})
            cache["benchmarks"][cache_key] = df.assign(Date=df["Date"].dt.strftime("%Y-%m-%d")).to_dict(orient="records")
            cache["timestamp"] = time.time()
            save_cache(cache)

            return df

        except HTTPError as e:
            fetch_benchmark_data._last_req_ts = time.time()
            # Respect Retry-After if present, otherwise backoff
            retry_after = 0.0
            try:
                retry_after = float(e.headers.get("Retry-After", "0"))
            except Exception:
                retry_after = 0.0

            if e.code == 429 and attempts < max_attempts:
                delay = max(retry_after, (backoff_base ** attempts)) + random.uniform(0, 0.5)
                time.sleep(delay)
                continue  # retry
            elif attempts < max_attempts:
                time.sleep((backoff_base ** attempts) + random.uniform(0, 0.25))
                continue  # retry
            else:
                print(f"Error fetching benchmark data for {symbol}: {e}")
                return pd.DataFrame(columns=["Date", "Close"])

        except URLError as e:
            fetch_benchmark_data._last_req_ts = time.time()
            if attempts < max_attempts:
                time.sleep((backoff_base ** attempts) + random.uniform(0, 0.25))
                continue
            else:
                print(f"Error fetching benchmark data for {symbol}: {e}")
                return pd.DataFrame(columns=["Date", "Close"])

        except Exception as e:
            fetch_benchmark_data._last_req_ts = time.time()
            print(f"Error fetching benchmark data for {symbol}: {e}")
            return pd.DataFrame(columns=["Date", "Close"])



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
    Add DailyReturn (%) and CumulativeReturn (%) anchored to the first available
    trading day *inside the window* (i.e., the first non-NaN 'Value' in the frame).
    Optimized with vectorized operations.
    """
    if benchmark_data.empty or "Value" not in benchmark_data.columns:
        return benchmark_data

    df = benchmark_data.copy()

    # Optimize: only sort if not already sorted
    if not df["Date"].is_monotonic_increasing:
        df = df.sort_values("Date")

    df = df.dropna(subset=["Value"])

    if df.empty:
        return benchmark_data

    anchor = df["Value"].iat[0]  # iat is faster than iloc for single value

    # Vectorized operations
    values = df["Value"].values
    df["DailyReturn"] = df["Value"].pct_change() * 100.0
    df["CumulativeReturn"] = (values / anchor - 1.0) * 100.0

    return df


# Example usage:
# start_date = datetime(2022, 1, 1)
# end_date = datetime(2022, 12, 31)
# sp500_data = get_benchmark_performance('S&P 500', start_date, end_date)
# sp500_with_returns = calculate_benchmark_returns(sp500_data)