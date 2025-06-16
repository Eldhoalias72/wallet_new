from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware



from fastapi.responses import FileResponse
import os


# Import all routers
from app.api import (
    partner,
    account,
    wallet,
    wallet_transaction,
    subscription,
    plan,
    payment,
    plan_feature,
    partner_transaction,
    settlement,
    feature_usage
)


app = FastAPI()

# Enable CORS (important for browser to make fetch requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (change in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Serve static files (e.g., JS, CSS, HTML)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ✅ Route to directly serve checkout.html from root path "/"
@app.get("/")
def serve_checkout():
    return FileResponse(os.path.join("app", "static", "checkout.html"))


# Register API routers
app.include_router(partner.router)
app.include_router(account.router)
app.include_router(wallet.router)
app.include_router(wallet_transaction.router)
app.include_router(subscription.router)
app.include_router(plan.router)
app.include_router(plan_feature.router)
app.include_router(partner_transaction.router)
app.include_router(settlement.router)
app.include_router(payment.router)
app.include_router(feature_usage.router)
