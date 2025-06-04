from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import SubscriptionCreate
from app.models.user import Subscription
from app.database import get_db

router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.post("/")
def create_subscription(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    new_sub = Subscription(**sub.dict())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return {"message": "Subscription created", "id": new_sub.subscription_id}
