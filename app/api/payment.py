# app/routes/payment.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.razorpay_service import create_payment_order, verify_payment, handle_webhook
from pydantic import BaseModel

router = APIRouter(prefix="/payment", tags=["Payment"])

class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    user_id: int

@router.post("/create-order")
def create_payment(plan_id: int, db: Session = Depends(get_db)):
    return create_payment_order(db, plan_id)

@router.post("/verify")
def verify_payment_endpoint(
    payment_data: PaymentVerificationRequest, 
    db: Session = Depends(get_db)
):
    """Verify payment after user completes payment on frontend"""
    return verify_payment(db, payment_data)

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhooks for automatic payment updates"""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    return handle_webhook(db, body, signature)

