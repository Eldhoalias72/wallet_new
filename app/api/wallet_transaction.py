from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import WalletTransactionCreate
from app.models.user import WalletTransaction
from app.database import get_db
from app.services.wallet_service import WalletService
from pydantic import BaseModel, validator
from typing import Optional

router = APIRouter(prefix="/wallet_transaction", tags=["WalletTransaction"])

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
    """
    Process wallet transaction with automatic balance management.
    
    Business Rules:
    - Credit: Adds amount to fixed_balance
    - Debit: Deducts from monthly_balance first, then fixed_balance
    - All balance changes are automatically computed and stored
    """
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