# Market Monitor

A TradingView-inspired financial dashboard for retail investors and finance students. Track stocks, manage watchlists, analyze price charts, and stay informed with real-time market data—all powered by free APIs.

## Overview

Market Monitor is a web-based stock market dashboard that provides retail investors and finance students with essential tools to track and analyze financial markets. Users can create custom watchlists, view interactive price charts, monitor major market indices, and read the latest financial news—all in one clean, intuitive interface.

## Why This Exists

This project was built as a full-stack portfolio application to demonstrate practical software development skills including:

- **User Authentication & Authorization** - Secure login/registration with session management
- **CRUD Operations** - Create, read, update, and delete watchlists, tickers, and notes
- **External API Integration** - Real-time data fetching from multiple free financial APIs
- **Data Visualization** - Interactive charts using Chart.js
- **Relational Database Design** - Multi-table MySQL schema with proper foreign key relationships
- **Responsive UI/UX** - Clean, modern interface built with Bootstrap

Unlike paid platforms like Bloomberg Terminal or premium stock analysis tools, Market Monitor uses 100% free data sources, making it accessible for students and individual investors learning about markets.

## Key Features

### 🔐 User Authentication
- Secure registration and login with password hashing
- Session-based authentication using Flask-Login
- User-specific data isolation

### 📊 Stock Watchlists
- Create and manage multiple custom watchlists
- Add/remove tickers with real-time price updates
- View sector and industry breakdown
- See price changes with color-coded indicators

### 📈 Interactive Charts
- Historical price charts with multiple timeframes (1M, 3M, 6M, 1Y, 5Y)
- Dynamic chart updates via AJAX
- Clean Chart.js visualizations
- Key metrics display (price, market cap, volume, previous close)

### 📰 Market News
- Latest financial news headlines
- Stock-specific news for individual tickers
- Powered by NewsAPI with relevancy filtering

### 🌐 Market Overview
- Real-time data for major indices (S&P 500, NASDAQ, Dow Jones)
- Cryptocurrency prices (Bitcoin, Ethereum, Cardano)
- Market status dashboard with quick glance indicators

### 📝 Notes & Research
- Add personal notes to any ticker
- Track your analysis and investment thesis
- Edit and delete notes as needed

### 🏠 Personalized Dashboard
- Quick access to all major features
- Your watchlists summary
- Market status at a glance
- Popular tickers quick links
- One-click ticker search

## Tech Stack

### Backend
- **Python 3** - Core programming language
- **Flask** - Lightweight web framework
- **Flask-Login** - User session management
- **MySQL** - Relational database
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5/CSS3** - Page structure and styling
- **Bootstrap 5** - Responsive UI framework
- **JavaScript (jQuery)** - Dynamic interactions and AJAX
- **Chart.js** - Interactive data visualizations
- **Font Awesome** - Icons

### APIs
- **Alpha Vantage** - Stock quotes, company profiles, historical data
- **NewsAPI** - Financial news headlines
- **CoinGecko** - Cryptocurrency prices

## Data Sources (Free APIs)

All market data is sourced from free-tier APIs:

1. **Alpha Vantage** (Stock Data)
   - Real-time quotes and historical prices
   - Company profiles (sector, industry, market cap)
   - Free tier: 25 requests/day, 5 requests/minute
   - Get your free key: https://www.alphavantage.co/support/#api-key

2. **NewsAPI** (Financial News)
   - Business headlines and stock-specific news
   - Free tier: 100 requests/day
   - Get your free key: https://newsapi.org/register

3. **CoinGecko** (Cryptocurrency)
   - Live crypto prices with 24-hour changes
   - No API key required
   - Completely free

## Local Setup

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or compatible database
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ethan-finalproject
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```env
   # Database Configuration
   DB_HOST=your-database-host
   DB_USER=your-database-user
   DB_PASSWORD=your-database-password
   DB_NAME=your-database-name
   DB_PORT=3306

   # Flask Configuration
   SECRET_KEY=your-secret-key-here

   # API Keys (Get free keys from the links above)
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
   NEWS_API_KEY=your-newsapi-key
   ```

5. **Initialize the database**
   ```bash
   mysql -u your-user -p your-database < database/schema.sql
   ```

6. **Run the application**
   ```bash
   python3 app.py
   ```

7. **Access the application**

   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### Demo Account

For quick testing, a demo account is pre-configured:
- **Username:** EthanWells10
- **Password:** GenerativeAI

## Project Structure

```
ethan-finalproject/
├── app/
│   ├── blueprints/         # Feature modules (auth, watchlists, tickers, markets)
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   ├── db_connect.py      # Database connection handling
│   ├── stock_api.py       # Alpha Vantage API integration
│   ├── news_api.py        # NewsAPI integration
│   └── routes.py          # Main application routes
├── database/
│   ├── schema.sql         # Database schema
│   └── seed_data.sql      # Sample data (optional)
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── app.py                # Application entry point
└── README.md             # This file
```

## Screenshots

*Coming soon - placeholder for application screenshots*

- Dashboard overview
- Watchlist management
- Interactive stock charts
- Market overview page
- News feed

## Roadmap

Future enhancements planned for this project:

- [ ] **Portfolio Tracking** - Track actual holdings with cost basis and P&L
- [ ] **Price Alerts** - Email/SMS notifications for price targets
- [ ] **Technical Indicators** - Add RSI, MACD, moving averages to charts
- [ ] **Advanced Filtering** - Filter watchlists by sector, performance, etc.
- [ ] **Export Functionality** - Export watchlists and data to CSV/Excel
- [ ] **Dark Mode** - Theme toggle for better viewing experience
- [ ] **Mobile App** - React Native companion app
- [ ] **Social Features** - Share watchlists and analysis with other users
- [ ] **Backtesting** - Test trading strategies on historical data
- [ ] **API Rate Optimization** - Implement better caching and batch requests

## Contributing

This is a portfolio/educational project, but suggestions and feedback are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests with improvements
- Fork the project for your own learning

## License

This project is open source and available for educational purposes.

## Acknowledgments

- Built with free-tier APIs from Alpha Vantage, NewsAPI, and CoinGecko
- UI inspired by modern financial dashboards like TradingView and Yahoo Finance
- Created as a portfolio project to demonstrate full-stack development skills

---

**Note:** This application is for educational and informational purposes only. It is not financial advice. Always do your own research before making investment decisions.
