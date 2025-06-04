from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import PartnerCreate
from app.models.user import Partner
from app.database import get_db

router = APIRouter(prefix="/partner", tags=["Partner"])

@router.post("/")
def create_partner(partner: PartnerCreate, db: Session = Depends(get_db)):
    # Optional: check if email or phone already exists
    existing = db.query(Partner).filter_by(partner_email=partner.partner_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Partner already exists with this email")

    db_partner = Partner(**partner.dict())
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return {"message": "Partner created successfully", "partner_id": db_partner.partner_id}
