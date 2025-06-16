# app/api/payment.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import Plan, Wallet, Subscription
from app.services.razorpay_service import create_order

router = APIRouter(prefix="/payment", tags=["Payment"])


from pydantic import BaseModel


print("✅ payment.py loaded")



class PlanOrderRequest(BaseModel):
    plan_id: int

# Create Razorpay order for plans
@router.post("/create-plan-order/")
def create_plan_order(data: PlanOrderRequest, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.plan_id == data.plan_id, Plan.is_active == True).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or inactive")

    order = create_order(plan.price, receipt_id=f"plan_{data.plan_id}")
    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "plan_id": data.plan_id
    }

# Create Razorpay order for tokens
@router.post("/create-token-order/")
def create_token_order(amount: float):
    order = create_order(amount, receipt_id="token_purchase")
    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"]
    }

# Pydantic schema for confirming plan purchase
class ConfirmPlanPayment(BaseModel):
    wallet_id: int
    plan_id: int
    razorpay_payment_id: str
    razorpay_order_id: str



# Confirm token purchase
class ConfirmTokenPayment(BaseModel):
    wallet_id: int
    razorpay_payment_id: str
    razorpay_order_id: str
    amount: float

@router.post("/confirm/token/")
def confirm_token_payment(data: ConfirmTokenPayment, db: Session = Depends(get_db)):
    print("🎯 confirm_token_payment route was triggered!")
    wallet = db.query(Wallet).filter(Wallet.wallet_id == data.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet.fixed_balance += data.amount
    wallet.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"{data.amount} tokens added to wallet"}
