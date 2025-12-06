from flask import render_template, jsonify, request
from . import app
from app.stock_api import get_multiple_quotes, clear_cache as clear_stock_cache
import yfinance as yf
import requests
import os
import time
from datetime import datetime, timedelta

# Simple in-memory cache to avoid rate limiting
_market_cache = {
    'data': None,
    'timestamp': None,
    'ttl_seconds': 60  # Cache for 60 seconds for better performance
}

# Request timeout
MARKET_API_TIMEOUT = 5  # 5 second timeout for market API calls

def clear_market_cache():
    """Clear the market overview cache"""
    global _market_cache
    _market_cache['data'] = None
    _market_cache['timestamp'] = None
    print("Market cache cleared")

@app.route('/')
def index():
    """Dashboard with major indices and market overview"""
    return render_template('dashboard.html')

@app.route('/api/market-overview')
def market_overview():
    """
    API endpoint for market data (AJAX-friendly)
    Returns major indices and crypto prices
    100% FREE APIs - no costs
    Cached for 60 seconds to avoid rate limiting
    Supports ?refresh=1 to force fresh data
    """
    # Check if force refresh requested
    force_refresh = request.args.get('refresh') is not None

    if force_refresh:
        print("Force refresh requested - clearing cache")
        clear_market_cache()
        clear_stock_cache()

    # Check cache first
    now = datetime.now()
    if (_market_cache['data'] is not None and
        _market_cache['timestamp'] is not None and
        (now - _market_cache['timestamp']).total_seconds() < _market_cache['ttl_seconds']):
        print("Returning cached market data")
        return jsonify(_market_cache['data'])

    print("Fetching fresh market data...")
    data = {}

    try:
        # Market Snapshot via Alpha Vantage API (REAL-TIME DATA)
        index_symbols = ['SPY', 'QQQ', 'DIA']
        index_names = {
            'SPY': 'S&P 500 ETF',
            'QQQ': 'NASDAQ 100 ETF',
            'DIA': 'Dow Jones ETF'
        }

        # Get real-time quotes for all indices at once
        quotes = get_multiple_quotes(index_symbols)

        indices_data = []
        for symbol in index_symbols:
            if symbol in quotes and quotes[symbol]:
                quote = quotes[symbol]
                indices_data.append({
                    'symbol': symbol,
                    'name': index_names[symbol],
                    'price': round(quote.get('price', 0), 2),
                    'change': round(quote.get('change', 0), 2),
                    'change_percent': round(quote.get('change_percent', 0), 2)
                })
                print(f"✓ Real-time index data for {symbol}: ${quote.get('price')}")

        # If no API data (API key not configured), show message
        if len(indices_data) == 0:
            print("✗ No real-time market data - ALPHA_VANTAGE_API_KEY not configured")
            indices_data = [{
                'symbol': 'INFO',
                'name': 'Set up ALPHA_VANTAGE_API_KEY for real-time data',
                'price': 0,
                'change': 0,
                'change_percent': 0
            }]

        data['indices'] = indices_data

        # Cryptocurrency Prices via CoinGecko (FREE - no API key needed!)
        crypto_response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin,ethereum,cardano',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            },
            timeout=5
        )

        if crypto_response.status_code == 200:
            crypto_data = crypto_response.json()
            cryptos = []

            crypto_names = {
                'bitcoin': 'Bitcoin',
                'ethereum': 'Ethereum',
                'cardano': 'Cardano'
            }

            for key, name in crypto_names.items():
                if key in crypto_data:
                    cryptos.append({
                        'name': name,
                        'price': crypto_data[key]['usd'],
                        'change_percent': round(crypto_data[key].get('usd_24h_change', 0), 2)
                    })

            data['crypto'] = cryptos
        else:
            data['crypto'] = []

    except Exception as e:
        print(f"Error fetching market data: {e}")
        data['error'] = 'Unable to fetch market data'

    # Update cache
    _market_cache['data'] = data
    _market_cache['timestamp'] = now

    return jsonify(data)

@app.route('/api/news')
def get_news():
    """
    API endpoint for market news (AJAX-friendly)
    Uses NewsAPI.org FREE tier (100 requests/day)
    """
    api_key = os.getenv('NEWS_API_KEY')

    if not api_key or api_key == 'your-newsapi-key-here':
        # Fallback to mock data if no API key
        return jsonify({
            'articles': [
                {
                    'title': 'Get your free NewsAPI key at newsapi.org',
                    'description': 'Sign up for free at https://newsapi.org to get market news',
                    'url': 'https://newsapi.org/register',
                    'publishedAt': '2025-01-01T00:00:00Z',
                    'source': {'name': 'Setup Required'}
                }
            ]
        })

    try:
        # NewsAPI.org - FREE tier: 100 requests/day
        # Use top-headlines with business category for relevant financial news
        response = requests.get(
            'https://newsapi.org/v2/top-headlines',
            params={
                'category': 'business',
                'language': 'en',
                'pageSize': 20,
                'apiKey': api_key
            },
            timeout=10
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'articles': [], 'error': 'News unavailable'})

    except Exception as e:
        print(f"Error fetching news: {e}")
        return jsonify({'articles': [], 'error': str(e)})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/trending')
def trending():
    """
    Trending Stocks page - Top 10 stocks by 24hr trading volume
    Uses a curated list of popular stocks to avoid excessive API calls
    """
    return render_template('trending.html')

@app.route('/education')
def education():
    """
    Market Education page - Learn about major market indices
    Static page explaining S&P 500, NASDAQ, and DOW
    """
    return render_template('education.html')
