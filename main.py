# ===========================
# IMPORTS
# ===========================
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict

# ===========================
# FASTAPI APP
# ===========================
app = FastAPI(
    title="Banking API",
    description="A simple Banking API with API key authentication",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# IN-MEMORY FAKE DATABASE
# ===========================
fake_users_db = {
    "user1": {"name":"user1","api_key": "user1_key", "balance": 20000, "currency": "PKR"},
    "user2": {"name":"user2","api_key": "user2_key", "balance": 50000, "currency": "PKR"},
}

# ===========================
# REQUEST MODEL
# ===========================
class Transaction(BaseModel):
    amount: float

class LoginRequest(BaseModel):
    username: str
    api_key: str

# ===========================
# AUTHENTICATION DEPENDENCY
# ===========================
def get_current_user(x_api_key: str = Header(..., alias="x-api-key")):
    """
    Validates the provided API key.
    """
    for username, data in fake_users_db.items():
        if data["api_key"] == x_api_key:
            return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key."
    )

# ===========================
# LOGIN ENDPOINT
# ===========================
@app.post("/login/")
def login(login_request: LoginRequest):
    username = login_request.username
    api_key = login_request.api_key
    
    if username in fake_users_db and fake_users_db[username]["api_key"] == api_key:
        user_data = fake_users_db[username]
        return {
            "token": user_data["api_key"],
            "user": username,
            "balance": user_data["balance"],
            "currency": user_data["currency"]
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or API Key."
    )

# ===========================
# GET BALANCE
# ===========================
@app.get("/balance/")
def get_balance(current_user: str = Depends(get_current_user)):
    user_data = fake_users_db[current_user]
    return {
        "user": current_user,
        "balance": user_data["balance"],
        "currency": user_data["currency"]
    }

# ===========================
# DEPOSIT MONEY
# ===========================
@app.post("/deposit/")
def deposit(transaction: Transaction, current_user: str = Depends(get_current_user)):

    if transaction.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be greater than zero."
        )

    fake_users_db[current_user]["balance"] += transaction.amount

    return {
        "message": "Deposit successful",
        "new_balance": fake_users_db[current_user]["balance"]
    }

# ===========================
# WITHDRAW MONEY
# ===========================
@app.post("/withdraw/")
def withdraw(transaction: Transaction, current_user: str = Depends(get_current_user)):

    if transaction.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal amount must be greater than zero."
        )

    if fake_users_db[current_user]["balance"] < transaction.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds."
        )

    fake_users_db[current_user]["balance"] -= transaction.amount

    return {
        "message": "Withdrawal successful",
        "new_balance": fake_users_db[current_user]["balance"]
    }

# ===========================
# ROOT ENDPOINT
# ===========================
@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI Banking App ??"}
