from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PartnerCreate(BaseModel):
    partner_name: str
    partner_email: EmailStr
    partner_ph_no: int
    partner_address: str
    is_active: bool = True

class AccountCreate(BaseModel):
    account_name: str
    is_active: bool = True
    balance: float
    partner_id: int

class WalletCreate(BaseModel):
    account_id: int
    monthly_balance: float
    fixed_balance: float
    token: int

class WalletTransactionCreate(BaseModel):
    wallet_id: int
    transaction_type: str
    amount: float
    previous_balance: float
    current_balance: float
    source: str
    remark: Optional[str]
    additional_info: Optional[str]

class SubscriptionCreate(BaseModel):
    wallet_id: int
    plan_id: int
    is_active: bool = False
    start_time: datetime
    end_time: datetime
    is_billed: bool = False

class PlanCreate(BaseModel):
    plan_name: str
    plan_amount: float
    duration_in_days: int
    is_active: bool = True
    token: float

class PlanFeatureCreate(BaseModel):
    plan_id: int
    feature_name: str
    feature_description: str
    feature_catagory: str
    is_active: bool = True


class PartnerTransactionCreate(BaseModel):
    parnter_id: int
    transaction_id: int
    commission_rate: float
    commission_type: str
    is_active: bool = True
    commission_amount: float
    transaction_date: datetime

class SettlementCreate(BaseModel):
    partner_id: int
    partner_transaction_id: int
    settlement_status: str
    settlement_date: datetime
    settlement_amount: float
