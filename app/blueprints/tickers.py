"""
Ticker Blueprint for Market Monitor
Displays ticker details, price charts (Chart.js), and user notes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.db_connect import execute_query
from app.stock_api import get_stock_quote, get_stock_profile, get_historical_data
from app.news_api import get_stock_news
from datetime import datetime, timedelta

# Create blueprint
tickers = Blueprint('tickers', __name__)


@tickers.route('/')
def index():
    """Main ticker search page"""
    return render_template('tickers.html')


@tickers.route('/view/<symbol>')
def view_ticker(symbol):
    """
    View detailed ticker information with chart (public access)
    Uses Alpha Vantage API for reliable data
    """
    symbol = symbol.upper()

    try:
        # Fetch historical chart data from Alpha Vantage
        chart_data = get_historical_data(symbol, period='1mo')

        if not chart_data:
            flash(f'Unable to fetch chart data for {symbol}. Please check the ticker symbol or try again later.', 'error')
            return redirect(url_for('tickers.index'))

        # Get current quote data
        quote = get_stock_quote(symbol)

        # Get company profile
        profile = get_stock_profile(symbol)

        # Get or create ticker in database
        ticker_query = "SELECT * FROM tickers WHERE symbol = %s"
        ticker_db = execute_query(ticker_query, (symbol,), fetch=True)

        if not ticker_db and profile:
            # Insert new ticker
            insert_query = """
                INSERT INTO tickers (symbol, name, exchange, sector, industry)
                VALUES (%s, %s, %s, %s, %s)
            """
            execute_query(insert_query, (
                symbol,
                profile.get('name', symbol),
                profile.get('exchange', 'N/A'),
                profile.get('sector', 'N/A'),
                profile.get('industry', 'N/A')
            ), fetch=False)

        # Get news for this ticker (2-3 relevant headlines)
        company_name = profile.get('name') if profile else None
        news = get_stock_news(symbol, company_name, limit=3)

        # Get user notes for this ticker (only if logged in)
        notes = []
        if current_user.is_authenticated:
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
            notes = execute_query(notes_query, (current_user.id, symbol), fetch=True)

        # Prepare ticker info combining quote and profile data
        current_price = None
        previous_close = None
        change_percent = 0

        if quote:
            current_price = quote.get('price')
            change_percent = quote.get('change_percent', 0)
            # Calculate previous close from current price and change
            if current_price and quote.get('change'):
                previous_close = current_price - quote.get('change')

        # If no current price from quote, use latest close from chart
        if not current_price and chart_data and chart_data['prices']:
            current_price = chart_data['prices'][-1]

        ticker_info = {
            'symbol': symbol,
            'name': profile.get('name', symbol) if profile else symbol,
            'exchange': profile.get('exchange', 'N/A') if profile else 'N/A',
            'sector': profile.get('sector', 'N/A') if profile else 'N/A',
            'industry': profile.get('industry', 'N/A') if profile else 'N/A',
            'current_price': current_price,
            'previous_close': previous_close,
            'change_percent': change_percent,
            'day_low': None,  # Alpha Vantage doesn't provide intraday highs/lows in free tier
            'day_high': None,
            'fifty_two_week_low': None,
            'fifty_two_week_high': None,
            'volume': quote.get('volume') if quote else None,
            'market_cap': profile.get('market_cap') if profile else None,
            'pe_ratio': None,  # Not available in Alpha Vantage free tier
            'dividend_yield': None,  # Not available in Alpha Vantage free tier
            'description': profile.get('description', 'No description available.') if profile else 'No description available.'
        }

        return render_template('ticker_detail.html',
                             ticker=ticker_info,
                             chart_data=chart_data,
                             notes=notes,
                             news=news)

    except Exception as e:
        print(f"Error fetching ticker {symbol}: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Unable to load data for {symbol}. The ticker may not exist or the API is temporarily unavailable. Please try another ticker.', 'error')
        return redirect(url_for('tickers.index'))


@tickers.route('/api/chart/<symbol>')
def get_chart_data(symbol):
    """
    API endpoint to get chart data for a ticker
    Returns JSON for Chart.js
    Uses Alpha Vantage API
    """
    symbol = symbol.upper()
    period = request.args.get('period', '1mo')  # Default 1 month

    try:
        # Get historical data from Alpha Vantage
        hist_data = get_historical_data(symbol, period=period)

        if not hist_data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 400

        # Format for Chart.js
        chart_data = {
            'labels': hist_data['dates'],
            'prices': hist_data['prices']
        }

        return jsonify(chart_data)

    except Exception as e:
        print(f"Error fetching chart data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 400


@tickers.route('/add_note/<symbol>', methods=['POST'])
@login_required
def add_note(symbol):
    """Add a note for a ticker"""
    symbol = symbol.upper()
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

    # Insert note with prepared statement
    insert_query = """
        INSERT INTO user_notes (user_id, ticker_symbol, note_text)
        VALUES (%s, %s, %s)
    """
    result = execute_query(insert_query, (current_user.id, symbol, note_text), fetch=False)

    if result is not None:
        flash('Note added successfully!', 'success')
    else:
        flash('Error adding note', 'error')

    return redirect(url_for('tickers.view_ticker', symbol=symbol))


@tickers.route('/edit_note/<int:note_id>', methods=['POST'])
@login_required
def edit_note(note_id):
    """Edit an existing note"""
    note_text = request.form.get('note_text', '').strip()

    # Validation
    if not note_text:
        flash('Note text is required', 'error')
        return redirect(request.referrer or url_for('tickers.index'))

    # Verify ownership
    check_query = """
        SELECT ticker_symbol FROM user_notes
        WHERE id = %s AND user_id = %s
    """
    note = execute_query(check_query, (note_id, current_user.id), fetch=True)

    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('tickers.index'))

    symbol = note[0]['ticker_symbol']

    # Update note with prepared statement
    update_query = """
        UPDATE user_notes
        SET note_text = %s, updated_at = NOW()
        WHERE id = %s AND user_id = %s
    """
    result = execute_query(update_query, (note_text, note_id, current_user.id), fetch=False)

    if result is not None:
        flash('Note updated successfully!', 'success')
    else:
        flash('Error updating note', 'error')

    return redirect(url_for('tickers.view_ticker', symbol=symbol))


@tickers.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    """Delete a note"""
    # Verify ownership and get ticker symbol
    check_query = """
        SELECT ticker_symbol FROM user_notes
        WHERE id = %s AND user_id = %s
    """
    note = execute_query(check_query, (note_id, current_user.id), fetch=True)

    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('tickers.index'))

    symbol = note[0]['ticker_symbol']

    # Delete note with prepared statement
    delete_query = "DELETE FROM user_notes WHERE id = %s AND user_id = %s"
    result = execute_query(delete_query, (note_id, current_user.id), fetch=False)

    if result is not None:
        flash('Note deleted successfully!', 'success')
    else:
        flash('Error deleting note', 'error')

    return redirect(url_for('tickers.view_ticker', symbol=symbol))


@tickers.route('/search')
def search():
    """Search for a ticker and redirect to detail page"""
    symbol = request.args.get('symbol', '').strip().upper()

    if not symbol:
        flash('Please enter a ticker symbol', 'error')
        return redirect(url_for('tickers.index'))

    return redirect(url_for('tickers.view_ticker', symbol=symbol))
