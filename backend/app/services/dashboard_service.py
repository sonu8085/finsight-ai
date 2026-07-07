"""Business logic for dashboard summary and analytics aggregation."""
import calendar
import uuid
from collections import defaultdict
from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.dashboard import CategoryBreakdownItem, DashboardSummary, MonthlyTrendItem


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.repo = TransactionRepository(db)

    async def get_summary(self, user_id: uuid.UUID, months_back: int = 6) -> DashboardSummary:
        today = date.today()
        range_start = (today.replace(day=1) - relativedelta(months=months_back - 1))
        all_transactions = await self.repo.get_for_period(user_id, range_start, today)

        # Current month figures
        month_start = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        month_end = today.replace(day=last_day)

        this_month = [t for t in all_transactions if month_start <= t.transaction_date <= month_end]
        monthly_income = sum(float(t.amount) for t in this_month if t.type == TransactionType.INCOME)
        monthly_expense = sum(float(t.amount) for t in this_month if t.type == TransactionType.EXPENSE)
        net_savings = monthly_income - monthly_expense
        savings_rate = (net_savings / monthly_income * 100) if monthly_income > 0 else 0.0

        total_income = sum(float(t.amount) for t in all_transactions if t.type == TransactionType.INCOME)
        total_expense = sum(float(t.amount) for t in all_transactions if t.type == TransactionType.EXPENSE)
        total_balance = total_income - total_expense

        # Category breakdown for current month expenses
        cat_totals: dict[str, float] = defaultdict(float)
        cat_colors: dict[str, str] = {}
        for t in this_month:
            if t.type != TransactionType.EXPENSE:
                continue
            name = t.category.name if t.category else "Uncategorized"
            cat_totals[name] += float(t.amount)
            cat_colors[name] = t.category.color if t.category else "#94a3b8"

        breakdown = [
            CategoryBreakdownItem(
                category_name=name,
                category_color=cat_colors[name],
                total=round(total, 2),
                percentage=round((total / monthly_expense * 100) if monthly_expense > 0 else 0, 2),
            )
            for name, total in sorted(cat_totals.items(), key=lambda x: -x[1])
        ]

        # Monthly trends
        trend_map: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
        for t in all_transactions:
            key = t.transaction_date.strftime("%Y-%m")
            if t.type == TransactionType.INCOME:
                trend_map[key]["income"] += float(t.amount)
            else:
                trend_map[key]["expense"] += float(t.amount)

        trends = []
        for i in range(months_back):
            month_date = range_start + relativedelta(months=i)
            key = month_date.strftime("%Y-%m")
            data = trend_map.get(key, {"income": 0.0, "expense": 0.0})
            trends.append(
                MonthlyTrendItem(
                    month=key,
                    income=round(data["income"], 2),
                    expense=round(data["expense"], 2),
                    net=round(data["income"] - data["expense"], 2),
                )
            )

        return DashboardSummary(
            total_balance=round(total_balance, 2),
            monthly_income=round(monthly_income, 2),
            monthly_expense=round(monthly_expense, 2),
            net_savings=round(net_savings, 2),
            savings_rate_pct=round(savings_rate, 2),
            category_breakdown=breakdown,
            monthly_trends=trends,
            recent_transactions_count=len(this_month),
        )
