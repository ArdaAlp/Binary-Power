import sqlite3

conn = sqlite3.connect('accounts.db')
cursor = conn.cursor()

# Tüm iş yerlerini çekme
cursor.execute("SELECT * FROM account")
rows = cursor.fetchall()

# Verileri yazdırma
for row in rows:
    print(f"ID: {row[0]}, İsim: {row[2]}, Telefon: {row[3]}, Bakiye: {row[5]}")

# Veritabanını kapat
conn.close(),
