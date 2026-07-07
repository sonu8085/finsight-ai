"""Pydantic schemas for budgets."""
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.budget import BudgetPeriod
from app.schemas.category import CategoryOut


class BudgetCreate(BaseModel):
    category_id: uuid.UUID | None = None
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    amount_limit: float = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetUpdate(BaseModel):
    amount_limit: float | None = Field(default=None, gt=0)


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    period: BudgetPeriod
    amount_limit: float
    month: int
    year: int
    category: CategoryOut | None = None


class BudgetProgressOut(BudgetOut):
    spent: float
    remaining: float
    utilization_pct: float
