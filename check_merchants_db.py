import sqlite3

conn = sqlite3.connect('merchants.db')
cursor = conn.cursor()

# Tüm iş yerlerini çekme
cursor.execute("SELECT * FROM merchant")
rows = cursor.fetchall()

# Verileri yazdırma
for row in rows:
    print(f"ID: {row[0]}, İsim: {row[1]}, Kategori: {row[2]}")

# Veritabanını kapat
conn.close(),
