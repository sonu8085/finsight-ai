"""Aggregates all v1 routers into a single router included by main.py."""
from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.categories import router as categories_router
from app.api.v1.csv_import import router as csv_import_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.goals import router as goals_router
from app.api.v1.transactions import router as transactions_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(transactions_router)
api_router.include_router(categories_router)
api_router.include_router(budgets_router)
api_router.include_router(goals_router)
api_router.include_router(dashboard_router)
api_router.include_router(csv_import_router)
api_router.include_router(ai_router)
