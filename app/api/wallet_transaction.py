from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import WalletTransactionCreate
from app.models.user import WalletTransaction
from app.database import get_db

router = APIRouter(prefix="/wallet_transaction", tags=["WalletTransaction"])

@router.post("/")
def create_transaction(txn: WalletTransactionCreate, db: Session = Depends(get_db)):
    new_txn = WalletTransaction(**txn.dict())
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return {"message": "Transaction logged", "id": new_txn.transaction_id}