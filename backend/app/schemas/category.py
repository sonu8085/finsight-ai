"""Pydantic schemas for categories."""
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: TransactionType = TransactionType.EXPENSE
    icon: str = "tag"
    color: str = "#6366f1"


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    color: str | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: TransactionType
    icon: str
    color: str
    is_default: bool
