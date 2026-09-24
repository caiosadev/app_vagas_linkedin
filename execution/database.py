import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
NEWSLETTER_DB_PATH = os.path.join(os.path.dirname(__file__), 'newsletter.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_newsletter_db_connection():
    conn = sqlite3.connect(NEWSLETTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            linkedin_url TEXT,
            resume_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_newsletter_db():
    conn = get_newsletter_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            frequency TEXT NOT NULL,
            areas TEXT DEFAULT 'Todas',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    init_newsletter_db()
    print("Databases initialized.")
