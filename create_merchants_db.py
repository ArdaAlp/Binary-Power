import sqlite3
from datetime import datetime

# Veritabanı bağlantısı
conn = sqlite3.connect('merchants.db')
cursor = conn.cursor()

# Tabloyu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS merchant (
    merchant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT CHECK (category IN ('cafe', 'market', 'transport', 'other'))
)
""")

# Değişiklikleri kaydet
conn.commit()
conn.close()
