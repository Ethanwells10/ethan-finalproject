"""
Database connection module for Market Monitor
Uses mysql.connector with prepared statements for security
Manages connection lifecycle with Flask's g object
"""

import mysql.connector
from mysql.connector import Error
from flask import g
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """
    Get database connection from Flask's g object
    Creates new connection if needed or if connection is closed
    Returns: mysql.connector connection object or None on failure
    """
    if 'db' not in g or not is_connection_open(g.db):
        print("Re-establishing closed database connection.")
        try:
            g.db = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                port=int(os.getenv('DB_PORT', 3306)),
                # Connection settings for reliability
                autocommit=False,  # Manual transaction control
                use_pure=True,     # Use pure Python implementation
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            print(f"Database connection established to {os.getenv('DB_HOST')}")
        except Error as e:
            print(f"Database connection failed: {e}")
            g.db = None
            return None
    return g.db

def is_connection_open(conn):
    """
    Check if database connection is still alive
    Args: conn - mysql.connector connection object
    Returns: True if connected, False otherwise
    """
    try:
        return conn is not None and conn.is_connected()
    except:
        return False

def close_db(exception=None):
    """
    Close database connection and remove from Flask g object
    Called automatically at end of each request via teardown_appcontext
    Args: exception - any exception that occurred during request
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            if db.is_connected():
                # Rollback any uncommitted transactions
                if exception:
                    db.rollback()
                    print(f"Database rollback due to exception: {exception}")
                print("Closing database connection.")
                db.close()
        except Error as e:
            print(f"Error closing database: {e}")

def execute_query(query, params=None, fetch=True):
    """
    Execute a SQL query with prepared statements
    Args:
        query - SQL query string with %s placeholders
        params - tuple of parameters for prepared statement
        fetch - if True, return results; if False, return lastrowid
    Returns: list of dicts (DictCursor) or lastrowid for INSERT
    """
    db = get_db()
    if db is None:
        print("No database connection available")
        return None

    cursor = None
    try:
        cursor = db.cursor(dictionary=True)  # Returns rows as dictionaries
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            return result
        else:
            db.commit()
            return cursor.lastrowid
    except Error as e:
        print(f"Database query error: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        db.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
