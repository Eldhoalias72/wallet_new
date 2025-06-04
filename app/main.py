from fastapi import FastAPI

from app.api import (
    partner,
    account,
    wallet,
    wallet_transaction,
    subscription,
    plan,
    plan_feature,
    partner_transaction,
    settlement
)

app = FastAPI()

# Include routers
app.include_router(partner.router)
app.include_router(account.router)
app.include_router(wallet.router)
app.include_router(wallet_transaction.router)
app.include_router(subscription.router)
app.include_router(plan.router)
app.include_router(plan_feature.router)
app.include_router(partner_transaction.router)
app.include_router(settlement.router)
