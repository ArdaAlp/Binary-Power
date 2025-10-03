import sqlite3
from datetime import datetime

def get_db_connection():
    """Veritabanı bağlantısı oluştur"""
    conn = sqlite3.connect('accounts.db')
    conn.execute('PRAGMA encoding = "UTF-8"')
    return conn

def init_db():
    """Veritabanı ve tabloları oluştur"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabloyu oluştur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        created_at TEXT NOT NULL,
        balance REAL DEFAULT 0.0
    )
    """)

    # Değişiklikleri kaydet
    conn.commit()
    conn.close()

# Veritabanını başlat
init_db()
