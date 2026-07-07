"""Business logic for budgets, including spend-vs-limit progress calculation."""
import calendar
import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.transaction import TransactionType
from app.repositories.budget_repository import BudgetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.budget import BudgetCreate, BudgetProgressOut, BudgetUpdate


class BudgetService:
    def __init__(self, db: AsyncSession):
        self.repo = BudgetRepository(db)
        self.transaction_repo = TransactionRepository(db)

    async def create(self, user_id: uuid.UUID, data: BudgetCreate) -> Budget:
        budget = Budget(user_id=user_id, **data.model_dump())
        return await self.repo.create(budget)

    async def get(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> Budget:
        budget = await self.repo.get_by_id(user_id, budget_id)
        if not budget:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
        return budget

    async def update(self, user_id: uuid.UUID, budget_id: uuid.UUID, data: BudgetUpdate) -> Budget:
        budget = await self.get(user_id, budget_id)
        return await self.repo.update(budget, data.model_dump(exclude_unset=True))

    async def delete(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> None:
        budget = await self.get(user_id, budget_id)
        await self.repo.delete(budget)

    async def list_with_progress(self, user_id: uuid.UUID, month: int, year: int) -> list[BudgetProgressOut]:
        budgets = await self.repo.list_for_period(user_id, month, year)

        last_day = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        transactions = await self.transaction_repo.get_for_period(user_id, start_date, end_date)
        expenses = [t for t in transactions if t.type == TransactionType.EXPENSE]

        result = []
        for budget in budgets:
            if budget.category_id:
                spent = sum(float(t.amount) for t in expenses if t.category_id == budget.category_id)
            else:
                spent = sum(float(t.amount) for t in expenses)

            limit = float(budget.amount_limit)
            remaining = limit - spent
            utilization = (spent / limit * 100) if limit > 0 else 0.0

            result.append(
                BudgetProgressOut(
                    id=budget.id,
                    period=budget.period,
                    amount_limit=limit,
                    month=budget.month,
                    year=budget.year,
                    category=budget.category,
                    spent=round(spent, 2),
                    remaining=round(remaining, 2),
                    utilization_pct=round(utilization, 2),
                )
            )
        return result
