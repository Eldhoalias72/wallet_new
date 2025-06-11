from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    @staticmethod
    def handle_subscription(
        db: Session,
        wallet_id: int,
        plan_id: Optional[int],
        subscription_type: str
    ) -> Dict[str, Any]:
        try:
            if subscription_type == "new":
                if plan_id is None:
                    raise ValueError("plan_id is required for new subscriptions")
                    
                result = db.execute(
                    text("SELECT * FROM subscribe_to_plan(:wallet_id, :plan_id)"),
                    {"wallet_id": wallet_id, "plan_id": plan_id}
                ).fetchone()
                
                if result is None:
                    raise Exception("Failed to create subscription - no result returned")
                
                # Convert result to dictionary
                subscription_data = {
                    'subscription_id': result.subscription_id,
                    'wallet_id': result.wallet_id,
                    'plan_id': result.plan_id,
                    'status': result.status,
                    'start_time': result.start_time.isoformat() if result.start_time else None,
                    'end_time': result.end_time.isoformat() if result.end_time else None,
                    'message': result.message
                }
                
                # Commit the transaction
                db.commit()
                return {"action": "created", "subscription": subscription_data}

            elif subscription_type == "renew":
                result = db.execute(
                    text("SELECT * FROM renew_subscription(:wallet_id)"),
                    {"wallet_id": wallet_id}
                ).fetchone()

                if result is None:
                    raise Exception("Failed to renew subscription - no result returned")

                # Convert result to dictionary
                subscription_data = {
                    'subscription_id': result.subscription_id,
                    'wallet_id': result.wallet_id,
                    'plan_id': result.plan_id,
                    'status': result.status,
                    'end_time': result.end_time.isoformat() if result.end_time else None,
                    'message': result.message
                }
                
                # Commit the transaction
                db.commit()
                return {"action": "renewed", "subscription": subscription_data}

            elif subscription_type == "cancel":
                result = db.execute(
                    text("SELECT * FROM cancel_subscription(:wallet_id)"),
                    {"wallet_id": wallet_id}
                ).fetchone()

                if result is None:
                    raise Exception("Failed to cancel subscription - no result returned")

                # Convert result to dictionary (assuming similar structure)
                subscription_data = dict(result._mapping)
                
                # Commit the transaction
                db.commit()
                return {"action": "canceled", "subscription": subscription_data}

            else:
                raise ValueError("Invalid subscription_type. Must be 'new', 'renew', or 'cancel'")

        except Exception as e:
            logger.error(f"Subscription operation failed: {str(e)}")
            db.rollback()  # Rollback on error
            raise