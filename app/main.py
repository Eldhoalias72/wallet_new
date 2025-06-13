from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    partner,
    account,
    wallet,
    wallet_transaction,
    subscription,
    plan,
    plan_feature,
    partner_transaction,
    settlement,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use specific domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)