-- Market Monitor Seed Data
-- Sample data for development and testing

-- ============================================================================
-- 1. INSERT SAMPLE USER
-- ============================================================================
-- Password is 'password123' (will be properly hashed in the application)
-- This is just a placeholder - actual password hashing happens in Flask with werkzeug
INSERT INTO users (email, password_hash) VALUES
('demo@marketmonitor.com', 'placeholder_hash');

-- ============================================================================
-- 2. INSERT POPULAR TICKERS
-- ============================================================================
-- Common stocks for testing
INSERT INTO tickers (symbol, name, exchange, sector) VALUES
-- Tech Giants
('AAPL', 'Apple Inc.', 'NASDAQ', 'Technology'),
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'Technology'),
('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'Technology'),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'Consumer Cyclical'),
('META', 'Meta Platforms Inc.', 'NASDAQ', 'Technology'),
('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'Technology'),
('TSLA', 'Tesla Inc.', 'NASDAQ', 'Consumer Cyclical'),

-- Financial
('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'Financial Services'),
('BAC', 'Bank of America Corp.', 'NYSE', 'Financial Services'),
('V', 'Visa Inc.', 'NYSE', 'Financial Services'),

-- Consumer
('WMT', 'Walmart Inc.', 'NYSE', 'Consumer Defensive'),
('PG', 'Procter & Gamble Co.', 'NYSE', 'Consumer Defensive'),
('KO', 'The Coca-Cola Company', 'NYSE', 'Consumer Defensive'),

-- Healthcare
('JNJ', 'Johnson & Johnson', 'NYSE', 'Healthcare'),
('UNH', 'UnitedHealth Group Inc.', 'NYSE', 'Healthcare'),

-- Index ETFs
('SPY', 'SPDR S&P 500 ETF Trust', 'NYSE', 'ETF'),
('QQQ', 'Invesco QQQ Trust', 'NASDAQ', 'ETF'),
('VOO', 'Vanguard S&P 500 ETF', 'NYSE', 'ETF');

-- ============================================================================
-- 3. INSERT SAMPLE WATCHLISTS
-- ============================================================================
-- Create a few sample watchlists for the demo user (user_id = 1)
INSERT INTO watchlists (user_id, name) VALUES
(1, 'Tech Favorites'),
(1, 'Long-term Holdings'),
(1, 'Market Indices');

-- ============================================================================
-- 4. INSERT WATCHLIST ITEMS
-- ============================================================================
-- Tech Favorites watchlist (watchlist_id = 1)
INSERT INTO watchlist_items (watchlist_id, ticker_symbol) VALUES
(1, 'AAPL'),
(1, 'MSFT'),
(1, 'GOOGL'),
(1, 'NVDA'),
(1, 'META');

-- Long-term Holdings watchlist (watchlist_id = 2)
INSERT INTO watchlist_items (watchlist_id, ticker_symbol) VALUES
(2, 'AAPL'),
(2, 'JPM'),
(2, 'JNJ'),
(2, 'V'),
(2, 'WMT');

-- Market Indices watchlist (watchlist_id = 3)
INSERT INTO watchlist_items (watchlist_id, ticker_symbol) VALUES
(3, 'SPY'),
(3, 'QQQ'),
(3, 'VOO');

-- ============================================================================
-- 5. INSERT SAMPLE NOTES
-- ============================================================================
-- Add some sample notes on tickers
INSERT INTO user_notes (user_id, ticker_symbol, note_text) VALUES
(1, 'AAPL', 'Strong quarterly earnings. Watch for new product launches in Q2.'),
(1, 'MSFT', 'Cloud growth continues. Azure performing well against competitors.'),
(1, 'TSLA', 'High volatility. Consider taking profits on next rally above $250.'),
(1, 'NVDA', 'AI chip demand remains strong. Monitor data center revenue.'),
(1, 'SPY', 'Market benchmark. Good for portfolio comparison.');
