from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import FeatureUsageRequest
from app.database import get_db
from app.services.feature_usage_service import FeatureUsageService
import traceback

router = APIRouter()


@router.post("/feature_usage")
def feature_usage(request: FeatureUsageRequest, db: Session = Depends(get_db)):
    try:
        FeatureUsageService.enqueue_feature_usage(db, request)
        return {"message": "Feature usage has been queued for processing"}
    except Exception as e:
        full_trace = traceback.format_exc()
        print("❌ FULL ERROR TRACE:\n", full_trace)
        raise HTTPException(status_code=500, detail=full_trace)
