import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
NEWSLETTER_DB_PATH = os.path.join(os.path.dirname(__file__), 'newsletter.db')

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_newsletter_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    conn = sqlite3.connect(NEWSLETTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def db_execute(conn, query, params=()):
    is_pg = hasattr(conn, 'cursor_factory')
    if is_pg:
        query = query.replace('?', '%s')
        query = query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor

def init_db():
    conn = get_db_connection()
    db_execute(conn, '''
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
    db_execute(conn, '''
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
