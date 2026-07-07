"""Pydantic schemas for transactions."""
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import PaymentMethod, TransactionType
from app.schemas.category import CategoryOut


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)
    notes: str | None = None
    category_id: uuid.UUID | None = None
    payment_method: PaymentMethod = PaymentMethod.OTHER
    merchant: str | None = None
    tags: str | None = None
    transaction_date: date


class TransactionUpdate(BaseModel):
    type: TransactionType | None = None
    amount: float | None = Field(default=None, gt=0)
    description: str | None = None
    notes: str | None = None
    category_id: uuid.UUID | None = None
    payment_method: PaymentMethod | None = None
    merchant: str | None = None
    tags: str | None = None
    transaction_date: date | None = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: TransactionType
    amount: float
    description: str
    notes: str | None
    payment_method: PaymentMethod
    merchant: str | None
    tags: str | None
    transaction_date: date
    is_recurring: bool
    category: CategoryOut | None = None


class TransactionListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TransactionOut]


class BulkDeleteRequest(BaseModel):
    ids: list[uuid.UUID]
