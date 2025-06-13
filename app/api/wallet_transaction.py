from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.schemas.user import WalletTransactionCreate
from app.models.user import WalletTransaction
from app.database import get_db
from app.services.wallet_service import WalletService
from pydantic import BaseModel, validator
from typing import Optional
import os
import razorpay
import hmac
import hashlib
from dotenv import load_dotenv
router = APIRouter(prefix="/wallet_transaction", tags=["WalletTransaction"])


load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))

class WalletTransactionRequest(BaseModel):
    wallet_id: int
    transaction_type: str  # 'credit' or 'debit'
    amount: float
    source: str
    remark: Optional[str] = None
    additional_info: Optional[str] = None
    
    @validator('transaction_type')
    def validate_transaction_type(cls, v):
        if v.lower() not in ['credit', 'debit']:
            raise ValueError('transaction_type must be either "credit" or "debit"')
        return v.lower()
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('amount must be greater than 0')
        return v

@router.post("/")
def process_wallet_transaction(request: WalletTransactionRequest, db: Session = Depends(get_db)):

    result = WalletService.process_transaction(
        db=db,
        wallet_id=request.wallet_id,
        transaction_type=request.transaction_type,
        amount=request.amount,
        source=request.source,
        remark=request.remark,
        additional_info=request.additional_info
    )
    
    if result["success"]:
        return {
            "message": f"Transaction processed successfully",
            "transaction_details": result
        }
    else:
        raise HTTPException(status_code=400, detail=result["error"])

@router.post("/legacy")
def create_transaction_legacy(txn: WalletTransactionCreate, db: Session = Depends(get_db)):
    """Legacy endpoint - creates transaction without stored procedure logic"""
    new_txn = WalletTransaction(**txn.dict())
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return {"message": "Transaction logged", "id": new_txn.transaction_id}

@router.get("/{wallet_id}/balance")
def get_wallet_balance(wallet_id: int, db: Session = Depends(get_db)):
    """Get current wallet balance details"""
    result = WalletService.get_wallet_balance(db, wallet_id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404, detail=result["error"])

@router.get("/{wallet_id}/transactions")
def get_wallet_transactions(wallet_id: int, db: Session = Depends(get_db)):
    """Get all transactions for a wallet"""
    transactions = db.query(WalletTransaction).filter(
        WalletTransaction.wallet_id == wallet_id
    ).order_by(WalletTransaction.updated_at.desc()).all()
    
    return {
        "wallet_id": wallet_id,
        "transactions": [
            {
                "transaction_id": txn.transaction_id,
                "transaction_type": txn.transaction_type,
                "amount": txn.amount,
                "previous_balance": txn.previous_balance,
                "current_balance": txn.current_balance,
                "source": txn.source,
                "remark": txn.remark,
                "additional_info": txn.additional_info,
                "updated_at": txn.updated_at
            }
            for txn in transactions
        ]
    }
class RazorpayOrderRequest(BaseModel):
    wallet_id: int
    amount: float  # in rupees (will be converted to paise on backend)

@router.post("/create_order")
def create_razorpay_order(request: RazorpayOrderRequest):
    """
    Create Razorpay order and return order_id, amount, key_id, etc.
    """
    try:
        amount_paise = int(request.amount * 100)

        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1
        })

        return {
            "key_id": RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "wallet_id": request.wallet_id,
            "input_amount": request.amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Razorpay order: {str(e)}")

class RazorpayCreditRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    wallet_id: int
    amount: float  # original amount entered by user


@router.post("/verify_and_credit")
def verify_and_credit_via_razorpay(request: RazorpayCreditRequest, db: Session = Depends(get_db)):
    """
    Verify Razorpay payment and credit wallet with amount * 10
    """
    try:
        # Step 1: Verify signature
        payload = f"{request.razorpay_order_id}|{request.razorpay_payment_id}"
        expected_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        if expected_signature != request.razorpay_signature:
            raise HTTPException(status_code=400, detail="Razorpay Signature Verification Failed")

        # Step 2: Process Wallet Credit
        result = WalletService.process_transaction(
            db=db,
            wallet_id=request.wallet_id,
            transaction_type="credit",
            amount=request.amount * 10,
            source="razorpay",
            remark="Credited via Razorpay payment",
            additional_info=f"Payment ID: {request.razorpay_payment_id}"
        )

        if result["success"]:
            return {
                "message": "Wallet credited successfully after Razorpay payment",
                "transaction_details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))