"""
Authentication Blueprint for Market Monitor
Handles user registration, login, and logout with Flask-Login
Uses werkzeug for password hashing
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db_connect import execute_query
import re

# Create blueprint
auth = Blueprint('auth', __name__)


class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, id, email):
        self.id = id
        self.email = email

    @staticmethod
    def get(user_id):
        """Get user by ID"""
        query = "SELECT id, email FROM users WHERE id = %s"
        result = execute_query(query, (user_id,), fetch=True)
        if result:
            return User(result[0]['id'], result[0]['email'])
        return None

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        query = "SELECT id, email, password_hash FROM users WHERE email = %s"
        result = execute_query(query, (email,), fetch=True)
        if result:
            return result[0]
        return None


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Server-side validation
        if not email or not password or not password_confirm:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')

        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Invalid email address', 'error')
            return render_template('auth/register.html')

        # Password validation
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('auth/register.html')

        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')

        # Check if email already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')

        # Hash password using werkzeug
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert new user with prepared statement
        query = "INSERT INTO users (email, password_hash) VALUES (%s, %s)"
        user_id = execute_query(query, (email, password_hash), fetch=False)

        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error creating account. Please try again.', 'error')
            return render_template('auth/register.html')

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'

        # Server-side validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')

        # Get user from database
        user_data = User.get_by_email(email)

        if not user_data:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')

        # Verify password using werkzeug
        if not check_password_hash(user_data['password_hash'], password):
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')

        # Create user object and log in
        user = User(user_data['id'], user_data['email'])
        login_user(user, remember=remember)

        flash(f'Welcome back, {email}!', 'success')

        # Redirect to next page or home
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))
