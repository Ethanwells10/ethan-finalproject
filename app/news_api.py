"""
News API integration for stock-related news
Free tier: 100 requests/day
"""
import requests
import os
from datetime import datetime, timedelta

# Cache for news data
_news_cache = {}
_cache_ttl = 1800  # Cache for 30 minutes

REQUEST_TIMEOUT = 5
MAX_RETRIES = 2
RETRY_DELAY = 1


def get_stock_news(symbol, company_name=None, limit=3):
    """
    Get recent news articles related to a stock symbol

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        company_name: Company name for better search results (optional)
        limit: Number of articles to return (default 3)

    Returns:
        List of news articles with title, description, url, source, publishedAt
    """
    api_key = os.getenv('NEWS_API_KEY')

    if not api_key:
        return []

    # Check cache first
    cache_key = f"news_{symbol}"
    if cache_key in _news_cache:
        cached_data, cached_time = _news_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < _cache_ttl:
            return cached_data[:limit]

    try:
        # Build targeted search query for better relevance
        # Include ticker symbol AND financial terms for precision
        if company_name:
            # Use company name + stock/shares for more relevant results
            query = f'"{company_name}" AND (stock OR shares OR earnings OR revenue)'
        else:
            query = f'{symbol} AND (stock OR shares OR earnings)'

        # Calculate date for last 7 days
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': api_key,
            'language': 'en',
            'sortBy': 'relevancy',  # Sort by relevance, not date
            'from': from_date,  # Only last 7 days
            'pageSize': limit * 2  # Get more to filter out irrelevant ones
        }

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            data = response.json()

            if data.get('status') == 'ok' and data.get('articles'):
                articles = []

                for article in data['articles']:
                    # Filter out articles with missing critical info
                    if not article.get('title') or article.get('title') == '[Removed]':
                        continue
                    if not article.get('url'):
                        continue

                    # Parse published date
                    published_at = article.get('publishedAt')
                    published_date = None

                    if published_at:
                        try:
                            published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                        except:
                            published_date = None

                    # Check if article is actually relevant (mentions symbol or company)
                    title_lower = article.get('title', '').lower()
                    desc_lower = (article.get('description') or '').lower()

                    # Skip if neither title nor description mention the company/symbol
                    company_lower = company_name.lower() if company_name else symbol.lower()
                    if company_lower not in title_lower and company_lower not in desc_lower and symbol.lower() not in title_lower:
                        continue

                    articles.append({
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'source': article.get('source', {}).get('name'),
                        'published_at': published_date,
                        'image_url': article.get('urlToImage')
                    })

                    # Stop after we have enough relevant articles
                    if len(articles) >= limit:
                        break

                # Cache the results
                _news_cache[cache_key] = (articles, datetime.now())
                return articles

        return []

    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []


def clear_news_cache():
    """Clear all cached news data to force fresh API requests"""
    global _news_cache
    _news_cache.clear()
    print("News cache cleared - next requests will fetch fresh data")
