"""Business logic for financial goals."""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import GoalCreate, GoalOut, GoalUpdate


def _to_goal_out(goal: Goal) -> GoalOut:
    progress = (float(goal.current_amount) / float(goal.target_amount) * 100) if goal.target_amount else 0.0
    return GoalOut(
        id=goal.id,
        name=goal.name,
        target_amount=float(goal.target_amount),
        current_amount=float(goal.current_amount),
        target_date=goal.target_date,
        icon=goal.icon,
        progress_pct=round(min(progress, 100.0), 2),
    )


class GoalService:
    def __init__(self, db: AsyncSession):
        self.repo = GoalRepository(db)

    async def create(self, user_id: uuid.UUID, data: GoalCreate) -> GoalOut:
        goal = Goal(user_id=user_id, **data.model_dump())
        goal = await self.repo.create(goal)
        return _to_goal_out(goal)

    async def list(self, user_id: uuid.UUID) -> list[GoalOut]:
        goals = await self.repo.list_for_user(user_id)
        return [_to_goal_out(g) for g in goals]

    async def _get_or_404(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
        goal = await self.repo.get_by_id(user_id, goal_id)
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        return goal

    async def update(self, user_id: uuid.UUID, goal_id: uuid.UUID, data: GoalUpdate) -> GoalOut:
        goal = await self._get_or_404(user_id, goal_id)
        goal = await self.repo.update(goal, data.model_dump(exclude_unset=True))
        return _to_goal_out(goal)

    async def delete(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        goal = await self._get_or_404(user_id, goal_id)
        await self.repo.delete(goal)
