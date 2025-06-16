from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.user import FeatureUsageRequest
from app.rabbitmq import publish_to_queue

class FeatureUsageService:
    @staticmethod
    def enqueue_feature_usage(db: Session, request: FeatureUsageRequest):
        sub = db.execute(
            text("SELECT wallet_id, plan_id FROM subscription WHERE subscription_id = :sid"),
            {"sid": request.subscription_id}
        ).fetchone()
        if not sub:
            raise ValueError("Subscription not found")

        feature = db.execute(
            text("""
                SELECT feature_id, points
                FROM plan_feature
                WHERE plan_id = :pid AND feature_name = :fname
            """),
            {"pid": sub.plan_id, "fname": request.feature_name}
        ).fetchone()
        if not feature:
            raise ValueError("Feature not available in plan")

        payload = {
            "wallet_id": sub.wallet_id,
            "transaction_type": "debit",
            "amount": feature.points,
            "source": "feature_usage",
            "remark": f"Used feature {request.feature_name}",
            "additional_info": f"subscription_id={request.subscription_id}, feature_id={feature.feature_id}"
        }
        publish_to_queue("feature_usage_queue", payload)
