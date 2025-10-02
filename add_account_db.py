import sqlite3

conn = sqlite3.connect('accounts.db')
cursor = conn.cursor()

# Örnek veri ekleme
cursor.execute(
    "INSERT INTO account (user_id, name, phone, created_at, balance) VALUES (?, ?, ?, ?, ?)",
    ("303", "Salih", "+905525563473", "2028-02-22 12:02:07", 303.0)
)

print("Hesap eklendi.")

# Veritabanını kapat
conn.close()