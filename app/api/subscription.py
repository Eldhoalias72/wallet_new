from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import SubscriptionCreate
from app.models.user import Subscription
from app.database import get_db
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.post("/")
def create_subscription(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    # Step 1: Create subscription with wallet_id and plan_id only
    new_sub = Subscription(wallet_id=sub.wallet_id, plan_id=sub.plan_id)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    # Step 2: Call procedure to complete it
    SubscriptionService.complete_subscription(db, new_sub.subscription_id)

    return {"message": "Subscription created and billed", "id": new_sub.subscription_id}
