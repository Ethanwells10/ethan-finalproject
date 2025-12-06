"""
Real-time stock data using Alpha Vantage API
Free tier: 25 requests/day, 5 requests/minute (no credit card needed)
Get your free API key at: https://www.alphavantage.co/support/#api-key
"""
import requests
import os
import time
from datetime import datetime, timedelta

# Cache to avoid hitting API limits
_stock_cache = {}
_cache_ttl = 60  # Cache for 60 seconds for better performance

# Request configuration
REQUEST_TIMEOUT = 5  # 5 second timeout
MAX_RETRIES = 2  # Retry failed requests up to 2 times
RETRY_DELAY = 1  # 1 second delay between retries

def get_stock_quote(symbol):
    """
    Get real-time stock quote from Alpha Vantage
    Returns: dict with price, change, change_percent, open, high, low, prev_close, volume, etc.
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    # Check if API key is configured
    if not api_key:
        return None

    # Check cache first
    cache_key = f"quote_{symbol}"
    if cache_key in _stock_cache:
        cached_data, cached_time = _stock_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < _cache_ttl:
            return cached_data

    # Retry logic for failed requests
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Alpha Vantage API endpoint for real-time quote
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': api_key
            }

            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                data = response.json()

                # Alpha Vantage returns data in "Global Quote" key
                if 'Global Quote' in data and data['Global Quote']:
                    quote = data['Global Quote']

                    # Parse the response - extract ALL available fields
                    price = float(quote.get('05. price', 0)) if quote.get('05. price') else None
                    change = float(quote.get('09. change', 0)) if quote.get('09. change') else None
                    change_percent_str = quote.get('10. change percent', '0')
                    change_percent = float(change_percent_str.replace('%', '')) if change_percent_str else None

                    # Additional fields from Global Quote
                    open_price = float(quote.get('02. open', 0)) if quote.get('02. open') else None
                    high_price = float(quote.get('03. high', 0)) if quote.get('03. high') else None
                    low_price = float(quote.get('04. low', 0)) if quote.get('04. low') else None
                    prev_close = float(quote.get('08. previous close', 0)) if quote.get('08. previous close') else None
                    volume = int(quote.get('06. volume', 0)) if quote.get('06. volume') else None

                    result = {
                        'symbol': quote.get('01. symbol'),
                        'price': price,
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'change': change,
                        'change_percent': change_percent,
                        'prev_close': prev_close,
                        'volume': volume,
                        'timestamp': quote.get('07. latest trading day')
                    }

                    # Cache the result
                    _stock_cache[cache_key] = (result, datetime.now())
                    return result

            # If we didn't get valid data, retry
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return None

        except requests.Timeout:
            if attempt < MAX_RETRIES:
                print(f"Timeout fetching {symbol}, retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Timeout fetching quote for {symbol} after {MAX_RETRIES + 1} attempts")
            return None
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"Error fetching {symbol}, retrying ({attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    return None


def get_multiple_quotes(symbols):
    """
    Get quotes for multiple symbols
    Uses cache aggressively to avoid rate limits
    Returns: dict mapping symbol to quote data
    """
    result = {}

    for symbol in symbols:
        quote = get_stock_quote(symbol)
        if quote:
            result[symbol] = quote

    return result


def get_stock_profile(symbol):
    """
    Get company profile information from Alpha Vantage
    Returns: dict with company info (sector, exchange, market_cap, etc.)
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    if not api_key:
        return None

    # Check cache
    cache_key = f"profile_{symbol}"
    if cache_key in _stock_cache:
        cached_data, cached_time = _stock_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < _cache_ttl:
            return cached_data

    # Retry logic for failed requests
    for attempt in range(MAX_RETRIES + 1):
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': api_key
            }

            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                data = response.json()

                if data and 'Symbol' in data:
                    # Parse market cap (comes as string, convert to int)
                    market_cap_str = data.get('MarketCapitalization', '0')
                    try:
                        market_cap = int(market_cap_str) if market_cap_str else None
                    except (ValueError, TypeError):
                        market_cap = None

                    result = {
                        'symbol': data.get('Symbol'),
                        'name': data.get('Name'),
                        'exchange': data.get('Exchange'),
                        'sector': data.get('Sector'),
                        'industry': data.get('Industry'),
                        'description': data.get('Description'),
                        'market_cap': market_cap
                    }

                    # Cache the result
                    _stock_cache[cache_key] = (result, datetime.now())
                    return result

            # If we didn't get valid data, retry
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return None

        except requests.Timeout:
            if attempt < MAX_RETRIES:
                print(f"Timeout fetching profile for {symbol}, retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Timeout fetching profile for {symbol} after {MAX_RETRIES + 1} attempts")
            return None
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"Error fetching profile for {symbol}, retrying ({attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Error fetching profile for {symbol}: {e}")
            return None

    return None


def get_historical_data(symbol, period='1mo'):
    """
    Get historical price data for chart rendering
    Alpha Vantage provides up to 100 data points with TIME_SERIES_DAILY

    Args:
        symbol: Stock ticker symbol
        period: Time period ('1mo', '3mo', '6mo', '1y', '5y')
                Note: Alpha Vantage TIME_SERIES_DAILY gives last 100 days
                For longer periods, use TIME_SERIES_WEEKLY or TIME_SERIES_MONTHLY

    Returns: dict with 'dates' and 'prices' lists for Chart.js
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    if not api_key:
        return None

    # Check cache
    cache_key = f"hist_{symbol}_{period}"
    if cache_key in _stock_cache:
        cached_data, cached_time = _stock_cache[cache_key]
        # Cache historical data for 5 minutes (less frequently changing)
        if (datetime.now() - cached_time).total_seconds() < 300:
            return cached_data

    # Map period to Alpha Vantage function
    # 1mo, 3mo = daily data (last 100 days)
    # 6mo, 1y = weekly data
    # 5y = monthly data
    if period in ['1mo', '3mo']:
        function = 'TIME_SERIES_DAILY'
        outputsize = 'compact'  # Last 100 data points
    elif period in ['6mo', '1y']:
        function = 'TIME_SERIES_WEEKLY'
        outputsize = 'compact'
    else:  # 5y
        function = 'TIME_SERIES_MONTHLY'
        outputsize = 'full'

    # Retry logic
    for attempt in range(MAX_RETRIES + 1):
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': outputsize
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Determine the key for time series data
                time_series_key = None
                if 'Time Series (Daily)' in data:
                    time_series_key = 'Time Series (Daily)'
                elif 'Weekly Time Series' in data:
                    time_series_key = 'Weekly Time Series'
                elif 'Monthly Time Series' in data:
                    time_series_key = 'Monthly Time Series'

                if time_series_key and data[time_series_key]:
                    time_series = data[time_series_key]

                    # Parse dates and closing prices
                    dates = []
                    prices = []

                    # Sort by date (oldest first for chart)
                    sorted_dates = sorted(time_series.keys())

                    # Limit data points based on period
                    period_limits = {
                        '1mo': 30,
                        '3mo': 90,
                        '6mo': 26,  # ~26 weeks in 6 months
                        '1y': 52,   # 52 weeks in a year
                        '5y': 60    # 60 months in 5 years
                    }

                    limit = period_limits.get(period, 100)
                    sorted_dates = sorted_dates[-limit:]  # Get last N data points

                    for date_str in sorted_dates:
                        day_data = time_series[date_str]
                        dates.append(date_str)
                        prices.append(float(day_data['4. close']))

                    result = {
                        'dates': dates,
                        'prices': prices
                    }

                    # Cache the result
                    _stock_cache[cache_key] = (result, datetime.now())
                    return result

            # If we didn't get valid data, retry
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return None

        except requests.Timeout:
            if attempt < MAX_RETRIES:
                print(f"Timeout fetching historical data for {symbol}, retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Timeout fetching historical data for {symbol} after {MAX_RETRIES + 1} attempts")
            return None
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"Error fetching historical data for {symbol}, retrying ({attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Error fetching historical data for {symbol}: {e}")
            return None

    return None


def get_comprehensive_metrics(symbol):
    """
    Get comprehensive ticker metrics combining quote, profile, and historical data
    Returns all available metrics for display:
    - Real-time quote data (price, change, volume, etc.)
    - Company profile (name, sector, exchange, market_cap)
    - 52-week range (calculated from weekly historical data)
    """
    # Get quote data (price, change, open, high, low, prev_close, volume)
    quote = get_stock_quote(symbol)

    # Get company profile (name, sector, exchange, market_cap, PE, etc.)
    profile = get_stock_profile(symbol)

    # Get 52-week high/low from historical data
    week52_data = get_52week_range(symbol)

    # Combine all data
    metrics = {
        'symbol': symbol,
        # Quote data
        'price': quote.get('price') if quote else None,
        'change': quote.get('change') if quote else None,
        'change_percent': quote.get('change_percent') if quote else None,
        'open': quote.get('open') if quote else None,
        'high': quote.get('high') if quote else None,  # Day high
        'low': quote.get('low') if quote else None,    # Day low
        'prev_close': quote.get('prev_close') if quote else None,
        'volume': quote.get('volume') if quote else None,
        # 52-week range
        'week52_high': week52_data.get('high') if week52_data else None,
        'week52_low': week52_data.get('low') if week52_data else None,
        # Profile data
        'name': profile.get('name') if profile else symbol,
        'exchange': profile.get('exchange') if profile else None,
        'sector': profile.get('sector') if profile else None,
        'industry': profile.get('industry') if profile else None,
        'market_cap': profile.get('market_cap') if profile else None,
        'description': profile.get('description') if profile else None,
        # Timestamp
        'timestamp': quote.get('timestamp') if quote else datetime.now().strftime('%Y-%m-%d'),
        # Note: PE ratio, EPS, dividend yield not available in Alpha Vantage free tier
        'pe_ratio': None,
        'eps': None,
        'dividend_yield': None
    }

    return metrics


def get_52week_range(symbol):
    """
    Calculate 52-week high/low from historical weekly data
    Uses TIME_SERIES_WEEKLY to get last year of data
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    if not api_key:
        return None

    # Check cache (cache for 1 hour since 52w range changes slowly)
    cache_key = f"52w_{symbol}"
    if cache_key in _stock_cache:
        cached_data, cached_time = _stock_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < 3600:  # 1 hour
            return cached_data

    # Retry logic
    for attempt in range(MAX_RETRIES + 1):
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_WEEKLY',
                'symbol': symbol,
                'apikey': api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if 'Weekly Time Series' in data:
                    time_series = data['Weekly Time Series']

                    # Get last 52 weeks of data
                    sorted_dates = sorted(time_series.keys(), reverse=True)[:52]

                    if sorted_dates:
                        highs = []
                        lows = []

                        for date in sorted_dates:
                            week_data = time_series[date]
                            highs.append(float(week_data['2. high']))
                            lows.append(float(week_data['3. low']))

                        result = {
                            'high': max(highs) if highs else None,
                            'low': min(lows) if lows else None
                        }

                        # Cache the result
                        _stock_cache[cache_key] = (result, datetime.now())
                        return result

            # If we didn't get valid data, retry
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return None

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"Error fetching 52w range for {symbol}, retrying ({attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Error fetching 52w range for {symbol}: {e}")
            return None

    return None


def clear_cache():
    """
    Clear all cached stock data to force fresh API requests
    """
    global _stock_cache
    _stock_cache.clear()
    print("Stock cache cleared - next requests will fetch fresh data")
