"""
Markets/Explore Blueprint for Market Monitor
Shows market overview with visualizations and news
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.db_connect import execute_query
import yfinance as yf
import os
import requests

# Create blueprint
markets = Blueprint('markets', __name__)


@markets.route('/')
def index():
    """Markets overview page with visualizations and news"""
    return render_template('markets.html')


@markets.route('/api/watchlist-summary')
@login_required
def watchlist_summary():
    """
    API endpoint for watchlist visualizations
    Returns data for Chart.js pie/bar charts
    """

    # Get ticker count per watchlist
    query = """
        SELECT
            w.id,
            w.name,
            COUNT(wi.id) AS ticker_count
        FROM watchlists w
        LEFT JOIN watchlist_items wi ON w.id = wi.watchlist_id
        WHERE w.user_id = %s
        GROUP BY w.id, w.name
        ORDER BY ticker_count DESC
    """
    watchlist_data = execute_query(query, (current_user.id,), fetch=True)

    # Get sector breakdown from user's tickers
    sector_query = """
        SELECT
            t.sector,
            COUNT(DISTINCT wi.ticker_symbol) AS ticker_count
        FROM watchlist_items wi
        JOIN tickers t ON wi.ticker_symbol = t.symbol
        JOIN watchlists w ON wi.watchlist_id = w.id
        WHERE w.user_id = %s AND t.sector IS NOT NULL AND t.sector != 'N/A'
        GROUP BY t.sector
        ORDER BY ticker_count DESC
    """
    sector_data = execute_query(sector_query, (current_user.id,), fetch=True)

    # Get exchange breakdown
    exchange_query = """
        SELECT
            t.exchange,
            COUNT(DISTINCT wi.ticker_symbol) AS ticker_count
        FROM watchlist_items wi
        JOIN tickers t ON wi.ticker_symbol = t.symbol
        JOIN watchlists w ON wi.watchlist_id = w.id
        WHERE w.user_id = %s AND t.exchange IS NOT NULL AND t.exchange != 'N/A'
        GROUP BY t.exchange
        ORDER BY ticker_count DESC
    """
    exchange_data = execute_query(exchange_query, (current_user.id,), fetch=True)

    return jsonify({
        'watchlists': watchlist_data or [],
        'sectors': sector_data or [],
        'exchanges': exchange_data or []
    })


@markets.route('/api/news/search')
def search_news():
    """
    Search news by keyword
    Allows filtering of market news
    """
    keyword = request.args.get('q', 'stock market')
    api_key = os.getenv('NEWS_API_KEY')

    if not api_key or api_key == 'your-newsapi-key-here':
        return jsonify({
            'articles': [{
                'title': f'News search for: {keyword}',
                'description': 'Get your free NewsAPI key at newsapi.org for news filtering',
                'url': 'https://newsapi.org/register',
                'publishedAt': '2025-01-01T00:00:00Z',
                'source': {'name': 'Setup Required'}
            }]
        })

    try:
        response = requests.get(
            'https://newsapi.org/v2/everything',
            params={
                'q': keyword,
                'language': 'en',
                'sortBy': 'publishedAt',
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
        print(f"Error searching news: {e}")
        return jsonify({'articles': [], 'error': str(e)})
