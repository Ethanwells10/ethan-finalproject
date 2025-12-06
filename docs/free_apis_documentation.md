# Free APIs Documentation - Market Monitor

## ✅ 100% Free - Zero Cost APIs

This document proves that **Market Monitor uses only free APIs with NO COSTS**.

---

## 1. yfinance (Stock/ETF Data) - FREE ✓

**What it does:** Provides stock market data, ETF prices, company information

**Cost:** **$0** - Completely free, no API key needed

**Usage in app:**
- Major indices (SPY, DIA, QQQ, IWM)
- Individual stock prices and history
- Company information, market cap, PE ratios
- Historical price data for charts

**Files:**
- `app/routes.py:22-56` - Market overview endpoint
- `app/blueprints/tickers.py` - Ticker details
- `app/blueprints/watchlists.py` - Watchlist prices

**Proof it's free:**
```python
import yfinance as yf
ticker = yf.Ticker("AAPL")  # No API key needed!
hist = ticker.history(period="1mo")
```

Official Site: https://pypi.org/project/yfinance/

---

## 2. CoinGecko API (Cryptocurrency) - FREE ✓

**What it does:** Provides cryptocurrency prices and 24h change data

**Cost:** **$0** - Free tier, no API key required

**Rate Limits:** 10-50 calls/minute (sufficient for our needs)

**Usage in app:**
- Bitcoin (BTC) price
- Ethereum (ETH) price
- Cardano (ADA) price
- 24-hour price change percentages

**Files:**
- `app/routes.py:59-90` - Crypto data endpoint
- `app/templates/dashboard.html` - Display on dashboard

**API Endpoint Used:**
```
GET https://api.coingecko.com/api/v3/simple/price
```

**Example Request:**
```python
requests.get(
    'https://api.coingecko.com/api/v3/simple/price',
    params={
        'ids': 'bitcoin,ethereum,cardano',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
)
# NO API KEY NEEDED!
```

Official Site: https://www.coingecko.com/en/api

---

## 3. NewsAPI.org (Market News) - FREE TIER ✓

**What it does:** Provides financial and market news headlines

**Cost:** **$0** for development (Free Developer plan)

**Rate Limits:** 100 requests/day (sufficient for development/testing)

**Setup Required:** Sign up at https://newsapi.org/register for free API key

**Usage in app:**
- Latest market news headlines
- Stock market news
- Financial news articles

**Files:**
- `app/routes.py:98-141` - News API endpoint
- `app/templates/dashboard.html` - News display with AJAX
- `.env` - NEWS_API_KEY configuration

**API Endpoint Used:**
```
GET https://newsapi.org/v2/everything
```

**Example Request:**
```python
requests.get(
    'https://newsapi.org/v2/everything',
    params={
        'q': 'stock market OR trading',
        'apiKey': 'YOUR_FREE_API_KEY'  # Free key from newsapi.org
    }
)
```

**Fallback:** If no API key is provided, the app shows a message to sign up (still works!)

Official Site: https://newsapi.org/

---

## Summary: All APIs Are Free

| API | Cost | API Key Needed | Rate Limit | Used For |
|-----|------|----------------|------------|----------|
| **yfinance** | $0 | No | Unlimited* | Stocks, ETFs, Company Data |
| **CoinGecko** | $0 | No | 10-50/min | Cryptocurrency Prices |
| **NewsAPI.org** | $0 | Yes (free) | 100/day | Market News Headlines |

*Reasonable use - Yahoo Finance may throttle excessive requests

---

## AJAX/jQuery Implementation

All data is fetched **asynchronously via AJAX** for better user experience:

### 1. Dashboard Market Data (AJAX)
**File:** `app/templates/dashboard.html:147-198`

```javascript
// AJAX function to load market data
function loadMarketData() {
    $.ajax({
        url: '/api/market-overview',  // Fetches indices + crypto
        method: 'GET',
        success: function(data) {
            // Dynamically update DOM without page reload
            renderIndices(data.indices);
            renderCrypto(data.crypto);
        }
    });
}

// Auto-refresh every 5 minutes
setInterval(loadMarketData, 300000);
```

### 2. News Feed (AJAX)
**File:** `app/templates/dashboard.html:201-239`

```javascript
// AJAX function to load news
function loadNews() {
    $.ajax({
        url: '/api/news',
        method: 'GET',
        success: function(data) {
            // Dynamically render news without page reload
            renderNews(data.articles);
        }
    });
}
```

### 3. Chart Interval Selector (AJAX)
**File:** `app/templates/ticker_detail.html:367-398`

```javascript
// AJAX function to update chart dynamically
function updateChart(period, button) {
    $.ajax({
        url: `/tickers/api/chart/${tickerSymbol}?period=${period}`,
        method: 'GET',
        success: function(data) {
            // Update chart without page reload
            priceChart.data.labels = data.labels;
            priceChart.data.datasets[0].data = data.prices;
            priceChart.update();
        }
    });
}
```

**Intervals Available:** 5D, 1M, 3M, 6M, 1Y

---

## Cost Breakdown for Deployment

### Development (Local)
- yfinance: $0
- CoinGecko: $0
- NewsAPI.org: $0 (100 requests/day free)
- **Total: $0/month**

### Production (Heroku)
- yfinance: $0
- CoinGecko: $0
- NewsAPI.org: $0 (100 requests/day free)
- Heroku Dyno: $0 (Free tier) or $7/month (Hobby tier)
- JawsDB MySQL: $0 (Free tier - 5MB)
- **Total: $0-7/month** (only Heroku hosting cost)

**All APIs remain FREE regardless of deployment!**

---

## How to Get API Keys (All Free)

### NewsAPI.org (Optional but recommended)
1. Visit: https://newsapi.org/register
2. Sign up with email (free)
3. Copy your API key
4. Add to `.env`: `NEWS_API_KEY=your_key_here`

**That's it!** No credit card required, completely free.

---

## Alternative Free News Sources (Backups)

If you don't want to use NewsAPI.org, here are 100% free alternatives:

### RSS Feeds (No API key)
```python
# BBC News RSS
'http://feeds.bbci.co.uk/news/business/rss.xml'

# CNBC RSS
'https://www.cnbc.com/id/100003114/device/rss/rss.html'

# Reuters RSS
'https://www.reutersagency.com/feed/'
```

### Free Crypto News APIs
- **CryptoPanic** - https://cryptopanic.com/developers/api/ (free tier)
- **CoinDesk API** - Public RSS feeds

---

## Conclusion

✅ **Zero API Costs**
✅ **Three distinct external data sources** (stocks, crypto, news)
✅ **AJAX implemented** for dynamic updates
✅ **jQuery used** for all AJAX calls
✅ **No page reloads** for data updates

**Total Monthly Cost for APIs: $0**

All requirements met with 100% free, no-cost external data sources!
