import sqlite3
from datetime import datetime

def get_db_connection():
    """Veritabanı bağlantısı oluştur"""
    return sqlite3.connect('merchants.db')

def init_db():
    """Veritabanı ve tabloları oluştur"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabloyu oluştur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT CHECK (category IN ('cafe', 'market', 'transport', 'other'))
    )
    """)

    # Değişiklikleri kaydet
    conn.commit()
    conn.close()

# Veritabanını başlat
init_db()
