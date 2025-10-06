from __future__ import annotations

from fastapi import FastAPI
from src.budgetbuddy.api.routers.transaction import router as transactions_router

app = FastAPI(title="BudgetBuddy API")

# Routers
app.include_router(transactions_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
