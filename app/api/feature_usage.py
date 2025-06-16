
# app/api/feature_usage.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import pika
import json
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import Subscription, PlanFeature

router = APIRouter(prefix="/feature", tags=["Feature Usage"])

# Define input schema
class FeatureUseRequest(BaseModel):
    subscription_id: int
    feature_id: int

def publish_feature_usage_event(subscription_id: int, feature_id: int):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        channel.queue_declare(queue='feature_usage_queue', durable=True)

        message = json.dumps({
            "subscription_id": subscription_id,
            "feature_id": feature_id
        })

        channel.basic_publish(
            exchange='',
            routing_key='feature_usage_queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()
        print(f"✅ Message sent to feature_usage_queue for Subscription {subscription_id}, Feature {feature_id}")
    except Exception as e:
        print(f"❌ Failed to publish feature usage event: {e}")
        raise HTTPException(status_code=500, detail="Internal queue error")

@router.post("/use/")
def use_feature(data: FeatureUseRequest, db: Session = Depends(get_db)):
    # Optional: validate subscription and feature existence
    subscription = db.query(Subscription).filter_by(subscription_id=data.subscription_id).first()
    feature = db.query(PlanFeature).filter_by(feature_id=data.feature_id, plan_id=subscription.plan_id).first()

    if not subscription or not feature:
        raise HTTPException(status_code=404, detail="Invalid subscription or feature")

    # Publish to queue
    publish_feature_usage_event(data.subscription_id, data.feature_id)

    return {"message": "Feature usage registered and sent to processing queue"}
