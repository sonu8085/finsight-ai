"""Data access layer for Goal entities."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal


class GoalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, goal: Goal) -> Goal:
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def get_by_id(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal | None:
        result = await self.db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Goal]:
        result = await self.db.execute(
            select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, goal: Goal, data: dict) -> Goal:
        for key, value in data.items():
            setattr(goal, key, value)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def delete(self, goal: Goal) -> None:
        await self.db.delete(goal)
        await self.db.commit()
