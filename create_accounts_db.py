import sqlite3
from datetime import datetime

# Veritabanı bağlantısı
conn = sqlite3.connect('accounts.db')
cursor = conn.cursor()

# Tabloyu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS account (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    created_at TEXT NOT NULL,
    balance REAL DEFAULT 0.0
)
""")

# Değişiklikleri kaydet
conn.commit()
conn.close()
