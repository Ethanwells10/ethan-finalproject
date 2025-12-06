-- Migration: Add industry column to tickers table
-- Run this on existing databases to add the industry column

ALTER TABLE tickers
ADD COLUMN industry VARCHAR(100) AFTER sector;

-- Verify the change
DESCRIBE tickers;
