# app/services/razorpay_service.py
from app.config import razorpay_client
from sqlalchemy.orm import Session
from app.models.user import Plan  # assuming your model is named Plan
from fastapi import HTTPException

def create_payment_order(db: Session, plan_id: int):
    # Fetch plan from DB
    plan = db.query(Plan).filter(Plan.plan_id == plan_id, Plan.is_active == True).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or inactive")

    amount_paise = int(plan.price * 100)

    # Create Razorpay Order
    order_data = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {
            "plan_name": plan.plan_name,
            "plan_id": str(plan.plan_id),
        }
    }

    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        return {
            "order_id": razorpay_order["id"],
            "plan_name": plan.plan_name,
            "amount": plan.price,
            "currency": "INR"
        }
    except Exception as e:
        # Razorpay failed — log actual error response
        print("🔥 Razorpay error:", str(e))
        raise HTTPException(status_code=500, detail="Razorpay order creation failed")