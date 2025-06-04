from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import PartnerTransactionCreate
from app.models.user import PartnerTransaction
from app.database import get_db

router = APIRouter(prefix="/partner_transaction", tags=["PartnerTransaction"])

@router.post("/")
def create_partner_txn(txn: PartnerTransactionCreate, db: Session = Depends(get_db)):
    new_txn = PartnerTransaction(**txn.dict())
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return {"message": "Partner transaction logged", "id": new_txn.partner_transaction_id}
