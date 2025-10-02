import sqlite3

conn = sqlite3.connect('merchants.db')
cursor = conn.cursor()

# Örnek veri ekleme
cursor.execute(
    "INSERT INTO merchant (name, category) VALUES (?, ?)",
    ("Cafe A", "cafe")
)

conn.commit()

# Veritabanını kapat
conn.close()