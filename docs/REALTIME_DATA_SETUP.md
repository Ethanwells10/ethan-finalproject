# Real-Time Stock Data Setup Guide

## Get Your FREE Financial Modeling Prep API Key

Your app is now configured to use **real-time stock market data** instead of outdated fallback prices!

### Step 1: Get Free API Key (No Credit Card Required)

1. Go to: **https://site.financialmodelingprep.com/developer/docs**
2. Click "Get Your Free API Key Today"
3. Sign up with your email (takes 30 seconds)
4. You'll receive your API key immediately

**Free Tier Includes:**
- ✅ 250 API requests per day (enough for development & demos)
- ✅ Real-time stock quotes
- ✅ Company profiles
- ✅ No credit card required
- ✅ No expiration

### Step 2: Add API Key to Your Project

1. Open your `.env` file
2. Find the line: `FMP_API_KEY=your-fmp-api-key-here`
3. Replace `your-fmp-api-key-here` with your actual API key
4. Save the file

Example:
```
FMP_API_KEY=abc123def456ghi789jkl  # Your actual key here
```

### Step 3: Restart Flask Server

```bash
# Stop the server (Ctrl+C)
# Then start it again:
python3 app.py
```

### Step 4: Test Real-Time Data

1. **Login** to your app: demo@marketmonitor.com / password123
2. **Go to Dashboard** - You should see real-time ETF prices for SPY, QQQ, DIA, IWM
3. **Go to Watchlists** → Click any watchlist → See real-time prices for all stocks!

### What You'll See:

**Before (Old Fallback Data):**
- AAPL: ~$278 (static)
- MSFT: ~$508 (static)
- Prices never change

**After (Real-Time API Data):**
```
✓ Real-time data for AAPL: $241.84
✓ Real-time data for MSFT: $444.01
✓ Real-time data for GOOGL: $189.23
✓ Real-time data for META: $620.45
✓ Real-time data for NVDA: $140.12
```

Prices update every 60 seconds automatically!

### Troubleshooting

**If you see "No real-time data available":**
1. Check that your API key is correctly pasted in `.env`
2. Make sure there are no extra spaces
3. Restart the Flask server
4. Check Flask logs for errors

**Rate Limit Exceeded:**
- Free tier: 250 requests/day
- Each watchlist page = 1 request for all tickers
- Dashboard = 1 request for indices
- Cached for 60 seconds to save requests

### API Documentation

Full API docs: https://site.financialmodelingprep.com/developer/docs

### Cost Breakdown

- **Current Setup**: $0/month (FREE tier - 250 requests/day)
- **Upgrade Options**:
  - $14/month - 750 requests/day
  - $29/month - Unlimited requests

For your college project, the **FREE tier is more than enough!**
