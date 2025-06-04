from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import PlanCreate
from app.models.user import Plan
from app.database import get_db

router = APIRouter(prefix="/plan", tags=["Plan"])

@router.post("/")
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    new_plan = Plan(**plan.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return {"message": "Plan created", "id": new_plan.plan_id}
