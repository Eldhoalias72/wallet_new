from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import SettlementCreate
from app.models.user import Settlement
from app.database import get_db

router = APIRouter(prefix="/settlement", tags=["Settlement"])

@router.post("/")
def create_settlement(data: SettlementCreate, db: Session = Depends(get_db)):
    new_settlement = Settlement(**data.dict())
    db.add(new_settlement)
    db.commit()
    db.refresh(new_settlement)
    return {"message": "Settlement recorded", "id": new_settlement.settlement_id}
