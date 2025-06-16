from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy import text 

from app.database import get_db
from app.models.user import Subscription, Plan, Wallet

router = APIRouter(prefix="/subscription", tags=["Subscription"])

# Request schema for confirming subscription
class ConfirmSubscription(BaseModel):
    wallet_id: int
    plan_id: int

@router.post("/confirm/")
def confirm_subscription(data: ConfirmSubscription, db: Session = Depends(get_db)):
    # Fetch wallet and plan
    wallet = db.query(Wallet).filter(Wallet.wallet_id == data.wallet_id).first()
    plan = db.query(Plan).filter(Plan.plan_id == data.plan_id).first()

    if not wallet or not plan:
        raise HTTPException(status_code=404, detail="Invalid wallet or plan")

    # Set subscription time
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=plan.duration_in_days)

    # Create subscription entry
    subscription = Subscription(
        wallet_id=wallet.wallet_id,
        plan_id=plan.plan_id,
        subscription_type="paid",
        is_active=True,
        is_billed=True,
        start_time=start_time,
        end_time=end_time
    )
    db.add(subscription)

    # Add plan_amount (tokens) to monthly_balance
    wallet.monthly_balance += plan.plan_amount
    wallet.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(subscription)

    db.execute(
        text("CALL history(:sub_id)"),
        {"sub_id": subscription.subscription_id}
    )
    db.commit()

    return {
        "message": "Subscription activated and tokens added",
        "subscription_id": subscription.subscription_id,
        "new_monthly_balance": wallet.monthly_balance
    }
