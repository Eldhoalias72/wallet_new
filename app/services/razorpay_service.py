import razorpay
import os

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_order(amount_in_rupees: float, receipt_id: str):
    order_data = {
        "amount": int(amount_in_rupees * 100),  # Convert to paise
        "currency": "INR",
        "receipt": receipt_id,
        "payment_capture": 1  # automatic capture
    }
    return client.order.create(data=order_data)
