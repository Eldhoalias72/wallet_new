from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Partner(Base):
    __tablename__ = "partner"

    partner_id = Column(Integer, primary_key=True, index=True)
    partner_name = Column(String)
    partner_email = Column(String)
    partner_ph_no = Column(Integer)
    partner_address = Column(String)
    is_active = Column(Boolean, default=True)
    commission_rate = Column(Float)
    commission_type = Column(String)
    onboarding_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    accounts = relationship("Account", back_populates="partner")
    transactions = relationship("PartnerTransaction", back_populates="partner")
    settlements = relationship("Settlement", back_populates="partner")


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    is_active = Column(Boolean, default=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    partner_id = Column(Integer, ForeignKey("partner.partner_id"))

    partner = relationship("Partner", back_populates="accounts")
    wallets = relationship("Wallet", back_populates="account")


class Wallet(Base):
    __tablename__ = "wallet"

    wallet_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    monthly_balance = Column(Float, default=0.0)
    fixed_balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    account = relationship("Account", back_populates="wallets")
    transactions = relationship("WalletTransaction", back_populates="wallet")
    subscriptions = relationship("Subscription", back_populates="wallet")


class WalletTransaction(Base):
    __tablename__ = "wallet_transaction"

    transaction_id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallet.wallet_id"))
    transaction_type = Column(String)
    amount = Column(Float)
    previous_balance = Column(Float)
    current_balance = Column(Float)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String)
    remark = Column(String)
    additional_info = Column(String)

    wallet = relationship("Wallet", back_populates="transactions")
    partner_transactions = relationship("PartnerTransaction", back_populates="wallet_transaction")


class Plan(Base):
    __tablename__ = "plan"

    plan_id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String)
    plan_amount = Column(Float)
    duration_in_days = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    price = Column(Float)

    features = relationship("PlanFeature", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscription"

    subscription_id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallet.wallet_id"))
    plan_id = Column(Integer, ForeignKey("plan.plan_id"))
    is_active = Column(Boolean, default=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_billed = Column(Boolean, default=False)
    subscription_type = Column(String)

    wallet = relationship("Wallet", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class PlanFeature(Base):
    __tablename__ = "plan_feature"

    feature_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plan.plan_id"))
    feature_name = Column(String)
    feature_description = Column(String)
    feature_catagory = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    plan = relationship("Plan", back_populates="features")


class PartnerTransaction(Base):
    __tablename__ = "partner_transaction"

    partner_transaction_id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partner.partner_id"))
    transaction_id = Column(Integer, ForeignKey("wallet_transaction.transaction_id"))
    is_active = Column(Boolean, default=True)
    commission_amount = Column(Float)
    transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    partner = relationship("Partner", back_populates="transactions")
    wallet_transaction = relationship("WalletTransaction", back_populates="partner_transactions")
    settlements = relationship("Settlement", back_populates="partner_transaction")


class Settlement(Base):
    __tablename__ = "settlement"

    settlement_id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partner.partner_id"))
    partner_transaction_id = Column(Integer, ForeignKey("partner_transaction.partner_transaction_id"))
    settlement_status = Column(String)
    settlement_date = Column(DateTime)
    settlement_amount = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    partner = relationship("Partner", back_populates="settlements")
    partner_transaction = relationship("PartnerTransaction", back_populates="settlements")

