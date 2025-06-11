from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, IntegrityError
from app.schemas.user import SubscriptionCreate
from app.database import get_db
from app.services.subscription_service import SubscriptionService
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.post("/", response_model=Dict[str, Any])
def create_subscription(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing subscription: wallet_id={sub.wallet_id}, plan_id={sub.plan_id}, type={sub.subscription_type}")

        # Validate input
        if not sub.wallet_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="wallet_id is required"
            )
        
        if sub.subscription_type.lower() == "new" and not sub.plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="plan_id is required for new subscriptions"
            )

        result = SubscriptionService.handle_subscription(
            db=db,
            wallet_id=sub.wallet_id,
            plan_id=sub.plan_id,
            subscription_type=sub.subscription_type.lower()
        )

        logger.info(f"Subscription processed successfully: {result}")
        return {
            "success": True,
            "message": "Subscription processed successfully",
            "data": result
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except IntegrityError as ie:
        logger.error(f"Database integrity error: {str(ie)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database constraint violation - check if subscription already exists or invalid references"
        )

    except OperationalError as oe:
        logger.error(f"Database operational error: {str(oe)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )