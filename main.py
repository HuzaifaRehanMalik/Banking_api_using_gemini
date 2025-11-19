# ===========================
# IMPORTS
# ===========================
# FastAPI for creating API routes
# Depends for dependency injection (API key validation)
# HTTPException for sending error responses
# status for standard HTTP status codes
# Header for reading request headers
from fastapi import FastAPI, Depends, HTTPException, status, Header

# BaseModel for validating request bodies
from pydantic import BaseModel

# Typing for type hints
from typing import Dict

# ===========================
# INITIALIZE FASTAPI APP
# ===========================
app = FastAPI()

# ===========================
# FAKE IN-MEMORY DATABASE
# ===========================
# This dictionary acts as a simple fake database.
# In real applications, you should replace this with a proper database.
fake_users_db = {
    "user1": {"api_key": "user1_key", "balance": 2000, "currency": "PKR"},
    "user2": {"api_key": "user2_key", "balance": 5000, "currency": "PKR"},
}

# ===========================
# REQUEST BODY MODEL
# ===========================
# Defines the expected structure of deposit/withdraw requests.
class Transaction(BaseModel):
    amount: float

# ===========================
# AUTHENTICATION DEPENDENCY
# ===========================
# This function will run before protected routes to check the API key.
def get_current_user(x_api_key: str = Header(...)):
    """
    Validates the API key provided in the request headers.
    Looks up the key in the fake database.
    Returns the username if valid, otherwise raises an error.
    """
    for user, data in fake_users_db.items():
        # Check if the provided API key matches any stored key
        if data["api_key"] == x_api_key:
            return user

    # If no valid API key found, return 401 Unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )

# ===========================
# ROUTE: GET BALANCE
# ===========================
@app.get("/balance/")
def get_balance(current_user: str = Depends(get_current_user)):
    """
    Returns the balance of the authenticated user.
    The current user is automatically determined from the API key.
    """
    user_data = fake_users_db[current_user]
    
    return {
        "user": current_user,
        "balance": user_data["balance"],
        "currency": user_data["currency"]
    }

# ===========================
# ROUTE: DEPOSIT MONEY
# ===========================
@app.post("/deposit/")
def deposit(transaction: Transaction, current_user: str = Depends(get_current_user)):
    """
    Deposit money into the authenticated user's account.
    Validates that the amount is positive.
    """
    # Reject negative or zero deposit
    if transaction.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be positive.",
        )

    # Increase user balance
    fake_users_db[current_user]["balance"] += transaction.amount

    return {
        "message": "Deposit successful",
        "new_balance": fake_users_db[current_user]["balance"]
    }

# ===========================
# ROUTE: WITHDRAW MONEY
# ===========================
@app.post("/withdraw/")
def withdraw(transaction: Transaction, current_user: str = Depends(get_current_user)):
    """
    Withdraw money from the authenticated user's account.
    Validates:
      - Amount must be positive
      - Sufficient balance must exist
    """
    # Reject invalid amount
    if transaction.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal amount must be positive.",
        )

    # Check sufficient balance
    if fake_users_db[current_user]["balance"] < transaction.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds.",
        )

    # Deduct amount
    fake_users_db[current_user]["balance"] -= transaction.amount

    return {
        "message": "Withdrawal successful",
        "new_balance": fake_users_db[current_user]["balance"]
    }

# ===========================
# ROOT ROUTE
# ===========================
@app.get("/")
def read_root():
    """
    Simple welcome route to verify the API is running.
    """
    return {"message": "Welcome to the FastAPI Banking App"}
