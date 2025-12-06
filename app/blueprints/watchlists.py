"""
Watchlist Blueprint for Market Monitor
Handles CRUD operations for watchlists and watchlist items
Demonstrates JOIN queries combining multiple tables
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.db_connect import execute_query, get_db
from app.stock_api import get_stock_quote, get_multiple_quotes, get_stock_profile, get_comprehensive_metrics, clear_cache
from app.routes import clear_market_cache
from datetime import datetime
import yfinance as yf

# Create blueprint
watchlists = Blueprint('watchlists', __name__)


def normalize_capitalization(text):
    """
    Normalize sector/industry capitalization for consistency.
    Converts to Title Case, except for known acronyms.
    """
    if not text or text == 'N/A':
        return text

    # List of acronyms that should stay uppercase
    acronyms = ['ETF', 'IT', 'AI', 'CEO', 'CFO', 'IPO', 'REIT']

    # If it's a known acronym, keep it as-is
    if text.upper() in acronyms:
        return text.upper()

    # Convert to title case for everything else
    return text.title()


@watchlists.route('/')
@login_required
def index():
    """
    Display all watchlists for the current user with JOIN query
    Shows watchlist details with ticker counts and symbols
    """
    # JOIN query combining watchlists, watchlist_items, and tickers tables
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

    watchlists_data = execute_query(query, (current_user.id,), fetch=True)

    return render_template('watchlists.html', watchlists=watchlists_data)


@watchlists.route('/<int:watchlist_id>')
@login_required
def view_watchlist(watchlist_id):
    """
    View a specific watchlist - fast HTML skeleton only
    Price data loads via AJAX after page render
    """
    # Get watchlist info
    watchlist_query = """
        SELECT id, name, created_at
        FROM watchlists
        WHERE id = %s AND user_id = %s
    """
    watchlist = execute_query(watchlist_query, (watchlist_id, current_user.id), fetch=True)

    if not watchlist:
        flash('Watchlist not found', 'error')
        return redirect(url_for('watchlists.index'))

    watchlist = watchlist[0]

    # Get tickers in this watchlist with JOIN - DB data only, no API calls
    # Try with industry column first, fall back if column doesn't exist
    tickers_query = """
        SELECT
            wi.id AS item_id,
            t.symbol,
            t.name,
            t.exchange,
            t.sector,
            t.industry,
            wi.created_at
        FROM watchlist_items wi
        JOIN tickers t ON wi.ticker_symbol = t.symbol
        WHERE wi.watchlist_id = %s
        ORDER BY t.symbol
    """
    tickers = execute_query(tickers_query, (watchlist_id,), fetch=True)

    # If query failed (returns None), try without industry column
    if tickers is None:
        print("Warning: industry column not found, using fallback query")
        tickers_query = """
            SELECT
                wi.id AS item_id,
                t.symbol,
                t.name,
                t.exchange,
                t.sector,
                NULL as industry,
                wi.created_at
            FROM watchlist_items wi
            JOIN tickers t ON wi.ticker_symbol = t.symbol
            WHERE wi.watchlist_id = %s
            ORDER BY t.symbol
        """
        tickers = execute_query(tickers_query, (watchlist_id,), fetch=True)

    # Return fast - no API calls during page render
    return render_template('watchlist_detail.html', watchlist=watchlist, tickers=tickers)


@watchlists.route('/<int:watchlist_id>/data')
@login_required
def get_watchlist_data(watchlist_id):
    """
    AJAX endpoint - fetch ONLY price/change data for watchlist (free-API friendly)
    Returns JSON with minimal data: price, change, change_percent
    Metadata (sector, industry, name) stored in DB, not refreshed
    Supports ?refresh=1 to force fresh data
    """
    # Check if force refresh requested
    force_refresh = request.args.get('refresh') is not None

    if force_refresh:
        print(f"Force refresh requested for watchlist {watchlist_id} - clearing cache")
        clear_cache()
        clear_market_cache()

    # Verify ownership
    check_query = "SELECT id FROM watchlists WHERE id = %s AND user_id = %s"
    watchlist = execute_query(check_query, (watchlist_id, current_user.id), fetch=True)

    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404

    # Get ticker symbols for this watchlist
    symbols_query = """
        SELECT t.symbol
        FROM watchlist_items wi
        JOIN tickers t ON wi.ticker_symbol = t.symbol
        WHERE wi.watchlist_id = %s
    """
    ticker_rows = execute_query(symbols_query, (watchlist_id,), fetch=True)
    symbols = [row['symbol'] for row in ticker_rows]

    # Fetch ONLY quotes (price, change, change_percent) - minimal API calls
    # Uses get_multiple_quotes which has built-in caching and retry logic
    quotes = get_multiple_quotes(symbols)

    # Format response with only essential fields
    result = {}
    for symbol in symbols:
        if symbol in quotes and quotes[symbol]:
            result[symbol] = {
                'symbol': symbol,
                'price': quotes[symbol].get('price'),
                'change': quotes[symbol].get('change'),
                'change_percent': quotes[symbol].get('change_percent'),
                'timestamp': quotes[symbol].get('timestamp')
            }
            print(f"✓ Got quote for {symbol}: ${quotes[symbol].get('price')}")
        else:
            # Still return symbol even if quote fails (Promise.allSettled pattern)
            result[symbol] = None
            print(f"✗ Failed to get quote for {symbol}")

    return jsonify({
        'quotes': result,
        'timestamp': datetime.now().isoformat()
    })


@watchlists.route('/create', methods=['POST'])
@login_required
def create_watchlist():
    """Create a new watchlist"""
    name = request.form.get('name', '').strip()

    # Server-side validation
    if not name:
        flash('Watchlist name is required', 'error')
        return redirect(url_for('watchlists.index'))

    if len(name) > 100:
        flash('Watchlist name must be 100 characters or less', 'error')
        return redirect(url_for('watchlists.index'))

    # Insert with prepared statement
    query = "INSERT INTO watchlists (user_id, name) VALUES (%s, %s)"
    result = execute_query(query, (current_user.id, name), fetch=False)

    if result:
        flash(f'Watchlist "{name}" created successfully!', 'success')
    else:
        flash('Error creating watchlist. Name may already exist.', 'error')

    return redirect(url_for('watchlists.index'))


@watchlists.route('/edit/<int:watchlist_id>', methods=['POST'])
@login_required
def edit_watchlist(watchlist_id):
    """Edit a watchlist name"""
    name = request.form.get('name', '').strip()

    # Server-side validation
    if not name:
        flash('Watchlist name is required', 'error')
        return redirect(url_for('watchlists.index'))

    if len(name) > 100:
        flash('Watchlist name must be 100 characters or less', 'error')
        return redirect(url_for('watchlists.index'))

    # Verify ownership
    check_query = "SELECT name FROM watchlists WHERE id = %s AND user_id = %s"
    watchlist = execute_query(check_query, (watchlist_id, current_user.id), fetch=True)

    if not watchlist:
        flash('Watchlist not found', 'error')
        return redirect(url_for('watchlists.index'))

    # Update watchlist name
    update_query = "UPDATE watchlists SET name = %s WHERE id = %s AND user_id = %s"
    result = execute_query(update_query, (name, watchlist_id, current_user.id), fetch=False)

    if result is not None:
        flash(f'Watchlist renamed to "{name}"', 'success')
    else:
        flash('Error updating watchlist. Name may already exist.', 'error')

    return redirect(url_for('watchlists.index'))


@watchlists.route('/delete/<int:watchlist_id>', methods=['POST'])
@login_required
def delete_watchlist(watchlist_id):
    """
    Delete a watchlist (CASCADE will automatically delete watchlist_items)
    """
    # First verify ownership
    check_query = "SELECT name FROM watchlists WHERE id = %s AND user_id = %s"
    watchlist = execute_query(check_query, (watchlist_id, current_user.id), fetch=True)

    if not watchlist:
        flash('Watchlist not found', 'error')
        return redirect(url_for('watchlists.index'))

    # Delete watchlist (CASCADE deletes items automatically)
    delete_query = "DELETE FROM watchlists WHERE id = %s AND user_id = %s"
    result = execute_query(delete_query, (watchlist_id, current_user.id), fetch=False)

    if result is not None:
        flash(f'Watchlist "{watchlist[0]["name"]}" deleted successfully', 'success')
    else:
        flash('Error deleting watchlist', 'error')

    return redirect(url_for('watchlists.index'))


@watchlists.route('/<int:watchlist_id>/add_ticker', methods=['POST'])
@login_required
def add_ticker(watchlist_id):
    """
    Add a ticker to a watchlist
    Validates ticker exists and creates it if needed using yfinance
    """
    symbol = request.form.get('symbol', '').strip().upper()

    # Validation
    if not symbol:
        flash('Ticker symbol is required', 'error')
        return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))

    # Verify watchlist ownership
    check_query = "SELECT id FROM watchlists WHERE id = %s AND user_id = %s"
    watchlist = execute_query(check_query, (watchlist_id, current_user.id), fetch=True)

    if not watchlist:
        flash('Watchlist not found', 'error')
        return redirect(url_for('watchlists.index'))

    # Check if ticker exists in tickers table
    ticker_query = "SELECT symbol FROM tickers WHERE symbol = %s"
    existing_ticker = execute_query(ticker_query, (symbol,), fetch=True)

    # If ticker doesn't exist, fetch metadata from API and store in DB (one-time only)
    if not existing_ticker:
        try:
            # Get stock profile from API to populate metadata
            profile = get_stock_profile(symbol)

            if not profile:
                # Try getting basic quote if profile fails
                quote = get_stock_quote(symbol)
                if quote:
                    profile = {
                        'symbol': symbol,
                        'name': symbol,
                        'exchange': 'N/A',
                        'sector': 'N/A',
                        'industry': 'N/A'
                    }
                else:
                    flash(f'Invalid ticker symbol or API unavailable: {symbol}', 'error')
                    return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))

            # Insert new ticker with metadata (stored once, not refreshed)
            # Normalize sector and industry for consistent capitalization
            sector = normalize_capitalization(profile.get('sector', 'N/A'))
            industry = normalize_capitalization(profile.get('industry', 'N/A'))

            # Try with industry column first, fall back if column doesn't exist
            try:
                insert_ticker = """
                    INSERT INTO tickers (symbol, name, exchange, sector, industry)
                    VALUES (%s, %s, %s, %s, %s)
                """
                execute_query(insert_ticker, (
                    symbol,
                    profile.get('name', symbol),
                    profile.get('exchange', 'N/A'),
                    sector,
                    industry
                ), fetch=False)
            except:
                # Fallback if industry column doesn't exist
                print(f"Warning: industry column not found, inserting {symbol} without industry")
                insert_ticker = """
                    INSERT INTO tickers (symbol, name, exchange, sector)
                    VALUES (%s, %s, %s, %s)
                """
                execute_query(insert_ticker, (
                    symbol,
                    profile.get('name', symbol),
                    profile.get('exchange', 'N/A'),
                    profile.get('sector', 'N/A')
                ), fetch=False)

        except Exception as e:
            flash(f'Error fetching ticker data: {str(e)}', 'error')
            return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))

    # Add ticker to watchlist
    add_query = """
        INSERT INTO watchlist_items (watchlist_id, ticker_symbol)
        VALUES (%s, %s)
    """
    result = execute_query(add_query, (watchlist_id, symbol), fetch=False)

    if result is not None:
        flash(f'Ticker {symbol} added to watchlist', 'success')
    else:
        flash(f'Ticker {symbol} may already be in this watchlist', 'error')

    return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))


@watchlists.route('/remove_ticker/<int:item_id>', methods=['POST'])
@login_required
def remove_ticker(item_id):
    """Remove a ticker from a watchlist"""
    # Get item info and verify ownership
    query = """
        SELECT wi.watchlist_id, t.symbol
        FROM watchlist_items wi
        JOIN watchlists w ON wi.watchlist_id = w.id
        JOIN tickers t ON wi.ticker_symbol = t.symbol
        WHERE wi.id = %s AND w.user_id = %s
    """
    item = execute_query(query, (item_id, current_user.id), fetch=True)

    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('watchlists.index'))

    watchlist_id = item[0]['watchlist_id']
    symbol = item[0]['symbol']

    # Delete item
    delete_query = "DELETE FROM watchlist_items WHERE id = %s"
    result = execute_query(delete_query, (item_id,), fetch=False)

    if result is not None:
        flash(f'Ticker {symbol} removed from watchlist', 'success')
    else:
        flash('Error removing ticker', 'error')

    return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))


@watchlists.route('/refresh')
@login_required
def refresh_all():
    """Clear all caches and refresh watchlists index"""
    clear_cache()  # Clear stock data cache
    clear_market_cache()  # Clear market overview cache
    flash('Data refreshed successfully!', 'success')
    return redirect(url_for('watchlists.index'))


@watchlists.route('/<int:watchlist_id>/refresh')
@login_required
def refresh_watchlist(watchlist_id):
    """Clear all caches and refresh specific watchlist"""
    clear_cache()  # Clear stock data cache
    clear_market_cache()  # Clear market overview cache
    flash('Prices refreshed successfully!', 'success')
    return redirect(url_for('watchlists.view_watchlist', watchlist_id=watchlist_id))
