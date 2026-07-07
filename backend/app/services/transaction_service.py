"""Business logic for transaction CRUD, filtering, and pagination."""
from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionListOut, TransactionUpdate


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.repo = TransactionRepository(db)

    async def create(self, user_id: uuid.UUID, data: TransactionCreate) -> Transaction:
        transaction = Transaction(user_id=user_id, **data.model_dump())
        return await self.repo.create(transaction)

    async def get(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction:
        transaction = await self.repo.get_by_id(user_id, transaction_id)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return transaction

    async def list(
        self,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
        type_filter: TransactionType | None,
        category_id: uuid.UUID | None,
        start_date: date | None,
        end_date: date | None,
        search: str | None,
    ) -> TransactionListOut:
        items, total = await self.repo.list(
            user_id, page, page_size, type_filter, category_id, start_date, end_date, search
        )
        return TransactionListOut(total=total, page=page, page_size=page_size, items=items)

    async def update(self, user_id: uuid.UUID, transaction_id: uuid.UUID, data: TransactionUpdate) -> Transaction:
        transaction = await self.get(user_id, transaction_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(transaction, update_data)

    async def delete(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> None:
        transaction = await self.get(user_id, transaction_id)
        await self.repo.delete(transaction)

    async def bulk_delete(self, user_id: uuid.UUID, ids: list[uuid.UUID]) -> int:
        return await self.repo.bulk_delete(user_id, ids)
