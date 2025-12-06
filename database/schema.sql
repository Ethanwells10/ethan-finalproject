-- Market Monitor Database Schema
-- Database for financial dashboard application
-- Single user with basic auth, watchlists, and ticker notes

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS user_notes;
DROP TABLE IF EXISTS watchlist_items;
DROP TABLE IF EXISTS watchlists;
DROP TABLE IF EXISTS tickers;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
-- Stores user authentication information
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. TICKERS TABLE
-- ============================================================================
-- Master list of stock tickers/symbols
-- Stores static ticker information
CREATE TABLE tickers (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tickers_name (name),
    INDEX idx_tickers_sector (sector)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. WATCHLISTS TABLE
-- ============================================================================
-- User-created watchlists (portfolios/groups of stocks)
CREATE TABLE watchlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Foreign key with CASCADE delete: if user is deleted, delete all their watchlists
    CONSTRAINT fk_watchlists_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    -- Ensure unique watchlist names per user
    UNIQUE KEY unique_user_watchlist (user_id, name),
    INDEX idx_watchlists_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. WATCHLIST_ITEMS TABLE
-- ============================================================================
-- Junction table linking watchlists to specific tickers
-- Represents which stocks are in which watchlist
CREATE TABLE watchlist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    watchlist_id INT NOT NULL,
    ticker_symbol VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Foreign key with CASCADE: if watchlist deleted, remove all items
    CONSTRAINT fk_watchlist_items_watchlist
        FOREIGN KEY (watchlist_id)
        REFERENCES watchlists(id)
        ON DELETE CASCADE,
    -- Foreign key to tickers: ensure ticker exists
    CONSTRAINT fk_watchlist_items_ticker
        FOREIGN KEY (ticker_symbol)
        REFERENCES tickers(symbol)
        ON DELETE CASCADE,
    -- Prevent duplicate tickers in same watchlist
    UNIQUE KEY unique_watchlist_ticker (watchlist_id, ticker_symbol),
    INDEX idx_watchlist_items_watchlist (watchlist_id),
    INDEX idx_watchlist_items_ticker (ticker_symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. USER_NOTES TABLE
-- ============================================================================
-- User notes/comments on specific tickers
CREATE TABLE user_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticker_symbol VARCHAR(20) NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Foreign key with CASCADE: if user deleted, delete all their notes
    CONSTRAINT fk_user_notes_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    -- Foreign key to ensure ticker exists
    CONSTRAINT fk_user_notes_ticker
        FOREIGN KEY (ticker_symbol)
        REFERENCES tickers(symbol)
        ON DELETE CASCADE,
    INDEX idx_user_notes_user (user_id),
    INDEX idx_user_notes_ticker (ticker_symbol),
    INDEX idx_user_notes_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- EXAMPLE JOIN QUERY
-- ============================================================================
-- Get all watchlists for a user with ticker details and item count
-- This demonstrates a JOIN query combining multiple tables
/*
SELECT
    w.id AS watchlist_id,
    w.name AS watchlist_name,
    w.created_at AS watchlist_created,
    COUNT(wi.id) AS ticker_count,
    GROUP_CONCAT(t.symbol ORDER BY t.symbol SEPARATOR ', ') AS ticker_symbols,
    GROUP_CONCAT(t.name ORDER BY t.symbol SEPARATOR ' | ') AS ticker_names
FROM watchlists w
LEFT JOIN watchlist_items wi ON w.id = wi.watchlist_id
LEFT JOIN tickers t ON wi.ticker_symbol = t.symbol
WHERE w.user_id = ?
GROUP BY w.id, w.name, w.created_at
ORDER BY w.created_at DESC;
*/
