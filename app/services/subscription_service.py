from sqlalchemy.orm import Session
from sqlalchemy import text


class SubscriptionService:
    @staticmethod
    def handle_subscription(
        db: Session,
        wallet_id: int,
        plan_id: int,
        subscription_type: str
    ) -> str:
        if subscription_type == "new":
            result = db.execute(text("SELECT subscribe_to_plan(:wallet_id, :plan_id)"), {
                "wallet_id": wallet_id,
                "plan_id": plan_id
            }).fetchone()
        elif subscription_type == "renew":
            result = db.execute(text("SELECT renew_subscription(:wallet_id)"), {
                "wallet_id": wallet_id
            }).fetchone()
        elif subscription_type == "cancel":
            result = db.execute(text("SELECT cancel_subscription(:wallet_id)"), {
                "wallet_id": wallet_id
            }).fetchone()
        else:
            raise ValueError("Invalid subscription_type. Must be 'new', 'renew', or 'cancel'.")