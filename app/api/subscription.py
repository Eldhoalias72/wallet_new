import razorpay
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import SubscriptionCreate
from app.services.subscription_service import SubscriptionService
from app.models.user import Plan  # assuming your Plan model is here
from app.database import get_db
from typing import Dict, Any
import os
from dotenv import load_dotenv
router = APIRouter(prefix="/subscription", tags=["Subscription"])

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))

@router.post("/create_order", response_model=Dict[str, Any])
def create_order(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.plan_id == sub.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    amount_paise = int(plan.price * 100)  # Razorpay takes amount in paise

    # Create order in Razorpay
    razorpay_order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": "1"
    })

    return {
        "order_id": razorpay_order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID,
        "wallet_id": sub.wallet_id,
        "plan_id": sub.plan_id,
        "subscription_type": sub.subscription_type
    }


@router.post("/verify_and_subscribe", response_model=Dict[str, Any])
def verify_and_subscribe(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    try:
        # Razorpay verification
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": payload["razorpay_order_id"],
            "razorpay_payment_id": payload["razorpay_payment_id"],
            "razorpay_signature": payload["razorpay_signature"]
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Razorpay Signature Verification Failed")

    # If verification passes, call your subscription procedure
    result = SubscriptionService.handle_subscription(
        db=db,
        wallet_id=payload["wallet_id"],
        plan_id=payload["plan_id"],
        subscription_type=payload["subscription_type"]
    )
    return {"message": "Subscription processed", "result": result}
