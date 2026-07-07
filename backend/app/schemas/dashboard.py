"""Pydantic schemas for dashboard/analytics responses."""
from pydantic import BaseModel


class CategoryBreakdownItem(BaseModel):
    category_name: str
    category_color: str
    total: float
    percentage: float


class MonthlyTrendItem(BaseModel):
    month: str  # e.g. "2026-06"
    income: float
    expense: float
    net: float


class DashboardSummary(BaseModel):
    total_balance: float
    monthly_income: float
    monthly_expense: float
    net_savings: float
    savings_rate_pct: float
    category_breakdown: list[CategoryBreakdownItem]
    monthly_trends: list[MonthlyTrendItem]
    recent_transactions_count: int
