from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import PlanFeatureCreate
from app.models.user import PlanFeature
from app.database import get_db

router = APIRouter(prefix="/plan_feature", tags=["PlanFeature"])

@router.post("/")
def create_feature(feature: PlanFeatureCreate, db: Session = Depends(get_db)):
    new_feature = PlanFeature(**feature.dict())
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    return {"message": "Feature added", "id": new_feature.feature_id}
