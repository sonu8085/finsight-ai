"""Data access layer for Budget entities."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.budget import Budget


class BudgetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, budget: Budget) -> Budget:
        self.db.add(budget)
        await self.db.commit()
        await self.db.refresh(budget, attribute_names=["category"])
        return budget

    async def get_by_id(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> Budget | None:
        result = await self.db.execute(
            select(Budget)
            .options(selectinload(Budget.category))
            .where(Budget.id == budget_id, Budget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_period(self, user_id: uuid.UUID, month: int, year: int) -> list[Budget]:
        result = await self.db.execute(
            select(Budget)
            .options(selectinload(Budget.category))
            .where(Budget.user_id == user_id, Budget.month == month, Budget.year == year)
        )
        return list(result.scalars().all())

    async def update(self, budget: Budget, data: dict) -> Budget:
        for key, value in data.items():
            setattr(budget, key, value)
        await self.db.commit()
        await self.db.refresh(budget, attribute_names=["category"])
        return budget

    async def delete(self, budget: Budget) -> None:
        await self.db.delete(budget)
        await self.db.commit()
