from sqlalchemy.orm import Session
from app.models.user import Subscription
from sqlalchemy import text

class SubscriptionService:

    @staticmethod
    def complete_subscription(db: Session, subscription_id: int):
        query = text("CALL complete_subscription(:sub_id)")
        db.execute(query, {"sub_id": subscription_id})
        db.commit()
