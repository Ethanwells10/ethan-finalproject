# Market Monitor - Database Requirements Compliance

## ✅ Requirement 1: Foreign Keys, Uniqueness, and NOT NULL Constraints

### Foreign Keys with CASCADE
All foreign key relationships are properly enforced with appropriate CASCADE rules:

```sql
-- watchlists.user_id → users.id
CONSTRAINT fk_watchlists_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE

-- watchlist_items.watchlist_id → watchlists.id
CONSTRAINT fk_watchlist_items_watchlist
    FOREIGN KEY (watchlist_id) REFERENCES watchlists(id)
    ON DELETE CASCADE

-- watchlist_items.ticker_symbol → tickers.symbol
CONSTRAINT fk_watchlist_items_ticker
    FOREIGN KEY (ticker_symbol) REFERENCES tickers(symbol)
    ON DELETE CASCADE

-- user_notes.user_id → users.id
CONSTRAINT fk_user_notes_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE

-- user_notes.ticker_symbol → tickers.symbol
CONSTRAINT fk_user_notes_ticker
    FOREIGN KEY (ticker_symbol) REFERENCES tickers(symbol)
    ON DELETE CASCADE
```

**Location:** `database/schema.sql` lines 49-52, 69-77, 96-104

---

### UNIQUE Constraints
Multiple UNIQUE constraints ensure data integrity:

```sql
-- Users table: unique email addresses
email VARCHAR(255) NOT NULL UNIQUE

-- Watchlists: unique watchlist names per user
UNIQUE KEY unique_user_watchlist (user_id, name)

-- Watchlist Items: prevent duplicate tickers in same watchlist
UNIQUE KEY unique_watchlist_ticker (watchlist_id, ticker_symbol)

-- Tickers: symbol is PRIMARY KEY (inherently unique)
symbol VARCHAR(20) PRIMARY KEY
```

**Location:** `database/schema.sql` lines 18, 30, 54, 79

---

### NOT NULL Constraints
All critical fields enforce NOT NULL:

**users table:**
- `email VARCHAR(255) NOT NULL UNIQUE`
- `password_hash VARCHAR(255) NOT NULL`

**tickers table:**
- `name VARCHAR(255) NOT NULL`

**watchlists table:**
- `user_id INT NOT NULL`
- `name VARCHAR(100) NOT NULL`

**watchlist_items table:**
- `watchlist_id INT NOT NULL`
- `ticker_symbol VARCHAR(20) NOT NULL`

**user_notes table:**
- `user_id INT NOT NULL`
- `ticker_symbol VARCHAR(20) NOT NULL`
- `note_text TEXT NOT NULL`

**Location:** Throughout `database/schema.sql`

---

## ✅ Requirement 2: JOIN Queries Combining Multiple Tables

### Example 1: Watchlist Overview (3-Table JOIN)
**Location:** `app/blueprints/watchlists.py:24-35`

```python
query = """
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
    WHERE w.user_id = %s
    GROUP BY w.id, w.name, w.created_at
    ORDER BY w.created_at DESC
"""
```

**Purpose:** Combines `watchlists`, `watchlist_items`, and `tickers` tables to show:
- Watchlist details
- Count of tickers in each watchlist
- List of ticker symbols and names

---

### Example 2: Watchlist Detail View (2-Table JOIN)
**Location:** `app/blueprints/watchlists.py:62-72`

```python
tickers_query = """
    SELECT
        wi.id AS item_id,
        t.symbol,
        t.name,
        t.exchange,
        t.sector,
        wi.created_at
    FROM watchlist_items wi
    JOIN tickers t ON wi.ticker_symbol = t.symbol
    WHERE wi.watchlist_id = %s
    ORDER BY t.symbol
"""
```

**Purpose:** Joins `watchlist_items` and `tickers` to display detailed ticker information for a specific watchlist.

---

### Example 3: User Notes with Ticker Info (2-Table JOIN)
**Location:** `app/blueprints/tickers.py:62-73`

```python
notes_query = """
    SELECT
        un.id,
        un.note_text,
        un.created_at,
        un.updated_at,
        t.symbol,
        t.name
    FROM user_notes un
    JOIN tickers t ON un.ticker_symbol = t.symbol
    WHERE un.user_id = %s AND un.ticker_symbol = %s
    ORDER BY un.created_at DESC
"""
```

**Purpose:** Joins `user_notes` and `tickers` to show notes with associated ticker information.

---

### Example 4: Remove Ticker with Ownership Verification (3-Table JOIN)
**Location:** `app/blueprints/watchlists.py:244-251`

```python
query = """
    SELECT wi.watchlist_id, t.symbol
    FROM watchlist_items wi
    JOIN watchlists w ON wi.watchlist_id = w.id
    JOIN tickers t ON wi.ticker_symbol = t.symbol
    WHERE wi.id = %s AND w.user_id = %s
"""
```

**Purpose:** Verifies user ownership before allowing ticker removal by joining all three tables.

---

## ✅ Requirement 3: Server-Side Validation

### Validation 1: Watchlist Creation
**Location:** `app/blueprints/watchlists.py:107-115`

```python
def create_watchlist():
    name = request.form.get('name', '').strip()

    # Server-side validation
    if not name:
        flash('Watchlist name is required', 'error')
        return redirect(url_for('watchlists.index'))

    if len(name) > 100:
        flash('Watchlist name must be 100 characters or less', 'error')
        return redirect(url_for('watchlists.index'))
```

**Validates:**
- Required field (name)
- Maximum length (100 characters)
- Database will also enforce UNIQUE constraint

---

### Validation 2: Add Ticker to Watchlist
**Location:** `app/blueprints/watchlists.py:163-172`

```python
def add_ticker(watchlist_id):
    symbol = request.form.get('symbol', '').strip().upper()

    # Validation
    if not symbol:
        flash('Ticker symbol is required', 'error')
        return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))

    # Verify watchlist ownership
    check_query = "SELECT id FROM watchlists WHERE id = %s AND user_id = %s"
    watchlist = execute_query(check_query, (watchlist_id, CURRENT_USER_ID), fetch=True)

    if not watchlist:
        flash('Watchlist not found', 'error')
        return redirect(url_for('watchlists.index'))

    # Validate ticker exists via yfinance API
    try:
        yf_ticker = yf.Ticker(symbol)
        info = yf_ticker.info
        if not info or 'symbol' not in info:
            flash(f'Invalid ticker symbol: {symbol}', 'error')
            return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))
    except Exception as e:
        flash(f'Error fetching ticker data: {str(e)}', 'error')
        return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))
```

**Validates:**
- Required field (symbol)
- Ownership verification (user owns the watchlist)
- External validation via yfinance API (ticker exists)
- Database UNIQUE constraint prevents duplicate tickers in same watchlist

---

### Validation 3: Add/Edit Notes
**Location:** `app/blueprints/tickers.py:130-141`

```python
def add_note(symbol):
    note_text = request.form.get('note_text', '').strip()

    # Server-side validation
    if not note_text:
        flash('Note text is required', 'error')
        return redirect(url_for('tickers.view_ticker', symbol=symbol))

    if len(note_text) > 5000:
        flash('Note is too long (max 5000 characters)', 'error')
        return redirect(url_for('tickers.view_ticker', symbol=symbol))

    # Ensure ticker exists
    ticker_query = "SELECT symbol FROM tickers WHERE symbol = %s"
    ticker = execute_query(ticker_query, (symbol,), fetch=True)

    if not ticker:
        flash('Ticker not found', 'error')
        return redirect(url_for('tickers.index'))
```

**Validates:**
- Required field (note_text)
- Maximum length (5000 characters)
- Foreign key validation (ticker must exist)

---

### Validation 4: Delete Operations with Ownership Verification
**Location:** `app/blueprints/watchlists.py:135-143` and `app/blueprints/tickers.py:204-213`

```python
def delete_watchlist(watchlist_id):
    # Verify ownership before delete
    check_query = "SELECT name FROM watchlists WHERE id = %s AND user_id = %s"
    watchlist = execute_query(check_query, (watchlist_id, CURRENT_USER_ID), fetch=True)

    if not watchlist:
        flash('Watchlist not found', 'error')
        return redirect(url_for('watchlists.index'))
```

**Validates:**
- Ownership verification (user owns the resource)
- Prevents unauthorized deletions
- Applies to watchlists, watchlist items, and notes

---

## Security: Prepared Statements

All queries use **prepared statements with parameterized queries** to prevent SQL injection:

```python
# Example from db_connect.py
def execute_query(query, params=None, fetch=True):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())  # Parameterized query
```

**Usage throughout application:**
```python
# Safe: Parameters passed separately
execute_query("INSERT INTO watchlists (user_id, name) VALUES (%s, %s)",
              (CURRENT_USER_ID, name), fetch=False)

# NOT used: String concatenation (vulnerable to SQL injection)
# cursor.execute(f"INSERT INTO watchlists VALUES ({user_id}, '{name}')")
```

---

## Summary

### ✅ All Requirements Met:

1. **Foreign Keys:** 5 FK relationships with CASCADE
2. **UNIQUE Constraints:** 3 unique constraints enforced
3. **NOT NULL:** All critical fields marked NOT NULL
4. **JOIN Queries:** 4+ multi-table JOIN queries implemented
5. **Server-Side Validation:** Input validation on all forms
6. **Prepared Statements:** SQL injection prevention throughout

### Database Tables:
1. ✅ `users` - Authentication
2. ✅ `tickers` - Stock symbols
3. ✅ `watchlists` - User watchlists
4. ✅ `watchlist_items` - Watchlist-ticker relationships
5. ✅ `user_notes` - User notes on tickers

**All tables have proper constraints, relationships, and validation!**
