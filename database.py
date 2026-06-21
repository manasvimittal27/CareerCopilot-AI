import sqlite3
import json
import os

DB_NAME = "career_copilot.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            credits INTEGER DEFAULT 100,
            parsed_profile TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert a default demo user if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, credits) VALUES ('demo_user', 100)")
        
    conn.commit()
    conn.close()

def get_user(username="demo_user"):
    """Fetches user data."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_profile(parsed_profile_dict, username="demo_user"):
    """Saves the parsed profile JSON into the database."""
    conn = get_db_connection()
    profile_json = json.dumps(parsed_profile_dict)
    conn.execute(
        "UPDATE users SET parsed_profile = ?, updated_at = CURRENT_TIMESTAMP WHERE username = ?",
        (profile_json, username)
    )
    conn.commit()
    conn.close()

def deduct_credits(amount, username="demo_user"):
    """Deducts a specified amount of credits from the user."""
    conn = get_db_connection()
    user = get_user(username)
    if user and user['credits'] >= amount:
        new_balance = user['credits'] - amount
        conn.execute("UPDATE users SET credits = ? WHERE username = ?", (new_balance, username))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False