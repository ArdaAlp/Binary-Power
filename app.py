from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import sqlite3
import os
from create_accounts_db import get_db_connection as get_account_db
from create_merchants_db import get_db_connection as get_merchant_db

# FastAPI uygulama tanımlaması
app = FastAPI(
    title="Binary Power Payment API",
    description="Ödeme sistemi için RESTful API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc"
)

# Static dosyalar ve templates için ayarlar
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Auth Models
class LoginRequest(BaseModel):
    user_id: int = Field(..., description="Kullanıcı ID")

# Para yükleme modeli
class TopUpRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Yüklenecek tutar")

class TopUpResponse(BaseModel):
    success: bool
    message: str
    new_balance: float

# Transfer Models
class MoneyTransferRequest(BaseModel):
    to_user_id: int = Field(..., description="Alıcı kullanıcı ID")
    amount: float = Field(..., gt=0, description="Gönderilecek tutar")

class MoneyTransferResponse(BaseModel):
    success: bool
    message: str
    new_balance: float

# Para yükleme endpoint'i
@app.post("/api/topup", response_model=TopUpResponse)
async def top_up_balance(topup: TopUpRequest, request: Request):
    user_info = request.cookies.get("user_info")
    if not user_info:
        raise HTTPException(status_code=401, detail="Oturum bulunamadı")
    
    user_id, user_name, balance = user_info.split(":")
    user_id = int(user_id)
    
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        # Bakiye güncelle
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (topup.amount, user_id)
        )
        
        # Yeni bakiyeyi al
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (user_id,))
        new_balance = cursor.fetchone()[0]
        
        conn.commit()
        
        # Cookie'yi güncelle
        response = JSONResponse(content={
            "success": True,
            "message": "Para yükleme işlemi başarılı",
            "new_balance": new_balance
        })
        response.set_cookie(
            key="user_info",
            value=f"{user_id}:{user_name}:{new_balance}",
            max_age=3600,
            httponly=True
        )
        return response
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Transfer endpoint
@app.post("/api/transfer", response_model=MoneyTransferResponse)
async def transfer_money(transfer: MoneyTransferRequest, request: Request):
    user_info = request.cookies.get("user_info")
    if not user_info:
        raise HTTPException(status_code=401, detail="Oturum bulunamadı")
    
    from_user_id, user_name, balance = user_info.split(":")
    from_user_id = int(from_user_id)
    current_balance = float(balance)
    
    if transfer.amount > current_balance:
        raise HTTPException(status_code=400, detail="Yetersiz bakiye")
    
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        # Alıcı hesabı kontrol et
        cursor.execute("SELECT id FROM accounts WHERE id = ?", (transfer.to_user_id,))
        receiver = cursor.fetchone()
        if not receiver:
            raise HTTPException(status_code=404, detail="Alıcı hesap bulunamadı")
        
        # Transfer işlemleri
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (transfer.amount, from_user_id)
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (transfer.amount, transfer.to_user_id)
        )
        
        # Yeni bakiyeyi al
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_user_id,))
        new_balance = cursor.fetchone()[0]
        
        # Transfer kaydını oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                amount REAL,
                created_at TEXT,
                FOREIGN KEY (from_user_id) REFERENCES accounts (id),
                FOREIGN KEY (to_user_id) REFERENCES accounts (id)
            )
        """)
        
        cursor.execute(
            "INSERT INTO transfers (from_user_id, to_user_id, amount, created_at) VALUES (?, ?, ?, ?)",
            (from_user_id, transfer.to_user_id, transfer.amount, datetime.now().isoformat())
        )
        
        conn.commit()
        
        # Cookie'yi güncelle
        response = JSONResponse(content={
            "success": True,
            "message": "Transfer başarıyla gerçekleşti",
            "new_balance": new_balance
        })
        response.set_cookie(
            key="user_info",
            value=f"{from_user_id}:{user_name}:{new_balance}",
            max_age=3600,
            httponly=True
        )
        return response
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Debug endpoint - sadece geliştirme sırasında kullanılacak
@app.post("/debug/create-test-user")
async def create_test_user():
    test_users = [
        ("Şükrü Şahin", "5551234567", 1000.0),
        ("Özge Çelik", "5551234568", 1500.0),
        ("İsmail Ülker", "5551234569", 2000.0),
        ("Gül Öztürk", "5551234570", 2500.0)
    ]
    
    conn = get_account_db()
    cursor = conn.cursor()
    created_users = []
    try:
        for name, phone, balance in test_users:
            cursor.execute(
                "INSERT INTO accounts (name, phone, created_at, balance) VALUES (?, ?, ?, ?)",
                (name, phone, datetime.now().isoformat(), balance)
            )
            created_users.append({
                "id": cursor.lastrowid,
                "name": name,
                "phone": phone,
                "balance": balance
            })
        conn.commit()
        return {"success": True, "created_users": created_users}
    finally:
        conn.close()

# Pydantic models for request/response
class MerchantBase(BaseModel):
    name: str = Field(..., description="İşletme adı")
    category: str = Field(..., description="İşletme kategorisi (cafe, market, transport, other)")

class MerchantResponse(MerchantBase):
    id: int = Field(..., description="İşletme ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Starbucks",
                "category": "cafe"
            }
        }


class UserBase(BaseModel):
    name: str = Field(..., description="Kullanıcı adı")
    phone: str = Field(..., description="Telefon numarası")
    created_at: datetime = Field(default_factory=datetime.now, description="Hesap oluşturma tarihi")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int = Field(..., description="Kullanıcı ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Ahmet Yılmaz",
                "phone": "5551234567",
                "created_at": "2023-10-03T12:00:00"
            }
        }

class AccountBase(UserBase):
    balance: float = Field(default=0.0, ge=0.0, description="Hesap bakiyesi")

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int = Field(..., description="Hesap ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Ahmet Yılmaz",
                "phone": "5551234567",
                "created_at": "2023-10-03T12:00:00",
                "balance": 1000.0
            }
        }


# Account related endpoints
@app.post(
    "/accounts/",
    response_model=AccountResponse,
    summary="Yeni hesap oluştur",
    description="Yeni bir kullanıcı hesabı oluşturur"
)
async def create_account(account: AccountCreate):
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO accounts (name, phone, created_at, balance) VALUES (?, ?, ?, ?)",
            (account.name, account.phone, account.created_at.isoformat(), account.balance)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return AccountResponse(
            id=new_id,
            name=account.name,
            phone=account.phone,
            created_at=account.created_at,
            balance=account.balance
        )
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get(
    "/accounts/",
    response_model=List[AccountResponse],
    summary="Tüm hesapları listele",
    description="Sistemdeki tüm hesapları listeler"
)
async def list_accounts():
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM accounts")
        rows = cursor.fetchall()
        return [
            AccountResponse(
                id=row[0],
                name=row[1],
                phone=row[2],
                created_at=datetime.fromisoformat(row[3]),
                balance=row[4]
            )
            for row in rows
        ]
    finally:
        conn.close()

@app.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    summary="Hesap detaylarını getir",
    description="Belirli bir hesabın detaylarını getirir"
)
async def get_account(
    account_id: int = Path(..., description="Hesap ID")
):
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Hesap bulunamadı")
        return AccountResponse(
            id=row[0],
            name=row[1],
            phone=row[2],
            created_at=datetime.fromisoformat(row[3]),
            balance=row[4]
        )
    finally:
        conn.close()

# Transfer models
class TransferBase(BaseModel):
    from_account_id: int = Field(..., description="Gönderen hesap ID")
    to_account_id: int = Field(..., description="Alıcı hesap ID")
    amount: float = Field(..., gt=0, description="Transfer miktarı")

class TransferCreate(TransferBase):
    pass

class TransferResponse(TransferBase):
    id: int = Field(..., description="Transfer ID")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "from_account_id": 1,
                "to_account_id": 2,
                "amount": 100.0,
                "created_at": "2023-10-03T12:00:00"
            }
        }

@app.post(
    "/merchants/",
    response_model=MerchantResponse,
    summary="Yeni işletme ekle",
    description="Sisteme yeni bir işletme ekler. İşletme kategorisi belirtilen değerlerden biri olmalıdır."
)
async def add_merchant(merchant: MerchantBase):
    if merchant.category not in ['cafe', 'market', 'transport', 'other']:
        raise HTTPException(
            status_code=400,
            detail="Geçersiz kategori. Geçerli kategoriler: cafe, market, transport, other"
        )

    conn = get_merchant_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO merchants (name, category) VALUES (?, ?)",
            (merchant.name, merchant.category)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return MerchantResponse(id=new_id, name=merchant.name, category=merchant.category)
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# Login ve yönlendirme endpoint'leri
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="user_info")
    return response

@app.post("/login")
async def login(login_request: LoginRequest):
    print(f"Login attempt with user_id: {login_request.user_id}")  # Debug log
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, balance FROM accounts WHERE id = ?", (login_request.user_id,))
        user = cursor.fetchone()
        print(f"Database query result: {user}")  # Debug log
        if user:
            from fastapi.responses import JSONResponse
            response = JSONResponse(content={
                "success": True, 
                "redirect_url": "/dashboard",
                "user_id": user[0],
                "user_name": user[1],
                "balance": user[2]
            })
            response.set_cookie(
                key="user_info",
                value=f"{user[0]}:{user[1]}:{user[2]}",
                max_age=3600,
                httponly=True
            )
            return response
        else:
            raise HTTPException(status_code=404, detail=f"ID: {login_request.user_id} olan kullanıcı bulunamadı")
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Giriş işlemi sırasında hata: {str(e)}")
    finally:
        conn.close()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_info = request.cookies.get("user_info")
    if not user_info:
        return RedirectResponse(url="/")
        
    user_id, user_name, balance = user_info.split(":")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user_name": user_name,
            "balance": float(balance)
        }
    )

@app.get("/send-money", response_class=HTMLResponse)
async def send_money(request: Request):
    user_info = request.cookies.get("user_info")
    if not user_info:
        return RedirectResponse(url="/")
        
    user_id, user_name, balance = user_info.split(":")
    return templates.TemplateResponse(
        "send-money.html",
        {
            "request": request,
            "user_name": user_name,
            "balance": float(balance)
        }
    )

@app.post(
    "/transfers/",
    response_model=TransferResponse,
    summary="Para transferi yap",
    description="Bir hesaptan diğerine para transferi gerçekleştirir"
)
async def create_transfer(transfer: TransferCreate):
    conn = get_account_db()
    cursor = conn.cursor()
    try:
        # İlk olarak gönderen hesabı kontrol et
        cursor.execute("SELECT balance FROM accounts WHERE id = ?", (transfer.from_account_id,))
        sender = cursor.fetchone()
        if not sender:
            raise HTTPException(status_code=404, detail="Gönderen hesap bulunamadı")
        
        # Alıcı hesabı kontrol et
        cursor.execute("SELECT id FROM accounts WHERE id = ?", (transfer.to_account_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Alıcı hesap bulunamadı")

        # Bakiye kontrolü
        if sender[0] < transfer.amount:
            raise HTTPException(status_code=400, detail="Yetersiz bakiye")

        # Transfer işlemleri
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (transfer.amount, transfer.from_account_id)
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (transfer.amount, transfer.to_account_id)
        )
        
        # Transfer kaydını oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account_id INTEGER,
                to_account_id INTEGER,
                amount REAL,
                created_at TEXT,
                FOREIGN KEY (from_account_id) REFERENCES accounts (id),
                FOREIGN KEY (to_account_id) REFERENCES accounts (id)
            )
        """)
        
        created_at = datetime.now()
        cursor.execute(
            "INSERT INTO transfers (from_account_id, to_account_id, amount, created_at) VALUES (?, ?, ?, ?)",
            (transfer.from_account_id, transfer.to_account_id, transfer.amount, created_at.isoformat())
        )
        
        conn.commit()
        return TransferResponse(
            id=cursor.lastrowid,
            from_account_id=transfer.from_account_id,
            to_account_id=transfer.to_account_id,
            amount=transfer.amount,
            created_at=created_at
        )
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get(
    "/merchants/",
    response_model=List[MerchantResponse],
    summary="Tüm işletmeleri listele",
    description="Sistemdeki tüm işletmeleri listeler"
)
async def list_merchants():
    conn = get_merchant_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM merchants")
        rows = cursor.fetchall()
        return [
            MerchantResponse(id=row[0], name=row[1], category=row[2])
            for row in rows
        ]
    finally:
        conn.close()
