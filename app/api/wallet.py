from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import WalletCreate
from app.models.user import Wallet
from app.database import get_db

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.post("/")
def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db)):
    new_wallet = Wallet(**wallet.dict())
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return {"message": "Wallet created", "id": new_wallet.wallet_id}
