from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import AccountCreate
from app.models.user import Account
from app.database import get_db

router = APIRouter(prefix="/account", tags=["Account"])

@router.post("/")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    new_account = Account(**account.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {"message": "Account created", "id": new_account.id}
