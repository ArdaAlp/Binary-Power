from .create_accounts_db import get_db_connection, close_db_connection
from .create_merchants_db import get_db_connection, close_db_connection
from fastapi import FastAPI, HTTPException
import sqlite3


class User:
    def __init__(self, user_id, name, phone, created_at):
        self.user_id = user_id
        self.username = name
        self.phone = phone
        self.created_at = created_at


class Account(User):
    def __init__(self, user_id, name, phone, created_at, balance=0):
        super().__init__(user_id, name, phone, created_at)
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount

    def transfer_sender(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount

    def transfer_reciever(self, amount):
        self.balance += amount


user1 = User(1, "Büşra", "5550555123", "2023-10-01")
account1 = Account(user1.user_id, user1.username,
                   user1.phone, user1.created_at, 500, 2000)

user2 = User(2, "Belkıs", "5550555124", "2023-08-05")
account2 = Account(user2.user_id, user2.username,
                   user2.phone, user2.created_at, 1000, 5000)

# app/main.py

app = FastAPI()

@app.post("/add_merchant/")
async def add_merchant(name: str, category: str):
    if category not in ['cafe', 'market', 'transport', 'other']:
        raise HTTPException(status_code=400, detail="Geçersiz kategori")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO merchants (name, category) VALUES (?, ?)",
            (name, category)
        )
        conn.commit()
        return {"message": "İşletme eklendi", "merchant_id": cursor.lastrowid}
    except sqlite3.IntegrityError as e:
        close_db_connection(conn)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        close_db_connection(conn)


@app.get("/merchants/")
async def list_merchants():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM merchants")
        rows = cursor.fetchall()
        return {"merchants": [{"id": row[0], "name": row[1], "category": row[2]} for row in rows]}
    finally:
        close_db_connection(conn)
