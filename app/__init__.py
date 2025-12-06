from flask import Flask, g
from flask_login import LoginManager
from .app_factory import create_app
from .db_connect import close_db, get_db
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.blueprints.auth import User
    return User.get(user_id)

# Register Blueprints
from app.blueprints.examples import examples
from app.blueprints.watchlists import watchlists
from app.blueprints.tickers import tickers
from app.blueprints.auth import auth
from app.blueprints.markets import markets

app.register_blueprint(examples, url_prefix='/example')
app.register_blueprint(watchlists, url_prefix='/watchlists')
app.register_blueprint(tickers, url_prefix='/tickers')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(markets, url_prefix='/markets')

from . import routes

@app.before_request
def before_request():
    g.db = get_db()
    if g.db is None:
        print("Warning: Database connection unavailable. Some features may not work.")

# Setup database connection teardown
@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)