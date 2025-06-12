# app/routes/payment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.razorpay_service import create_payment_order

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/create-order")
def create_payment(plan_id: int, db: Session = Depends(get_db)):
    return create_payment_order(db, plan_id)

# # app/routes/payment.py
# from fastapi import APIRouter

# router = APIRouter(prefix="/payment", tags=["Payment"])

# @router.post("/create-order")
# def create_order():
#     return {"message": "This works!"}
