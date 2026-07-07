"""Data access layer for Transaction entities."""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction, TransactionType


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction, attribute_names=["category"])
        return transaction

    async def get_by_id(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(Transaction.id == transaction_id, Transaction.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        type_filter: TransactionType | None = None,
        category_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None,
    ) -> tuple[list[Transaction], int]:
        query = select(Transaction).options(selectinload(Transaction.category)).where(
            Transaction.user_id == user_id
        )
        count_query = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)

        if type_filter:
            query = query.where(Transaction.type == type_filter)
            count_query = count_query.where(Transaction.type == type_filter)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
            count_query = count_query.where(Transaction.category_id == category_id)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
            count_query = count_query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
            count_query = count_query.where(Transaction.transaction_date <= end_date)
        if search:
            like = f"%{search}%"
            search_clause = or_(Transaction.description.ilike(like), Transaction.merchant.ilike(like))
            query = query.where(search_clause)
            count_query = count_query.where(search_clause)

        query = query.order_by(Transaction.transaction_date.desc()).offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        total_result = await self.db.execute(count_query)
        return list(result.scalars().all()), total_result.scalar_one()

    async def update(self, transaction: Transaction, data: dict) -> Transaction:
        for key, value in data.items():
            setattr(transaction, key, value)
        await self.db.commit()
        await self.db.refresh(transaction, attribute_names=["category"])
        return transaction

    async def delete(self, transaction: Transaction) -> None:
        await self.db.delete(transaction)
        await self.db.commit()

    async def bulk_delete(self, user_id: uuid.UUID, ids: list[uuid.UUID]) -> int:
        result = await self.db.execute(
            select(Transaction).where(Transaction.user_id == user_id, Transaction.id.in_(ids))
        )
        transactions = result.scalars().all()
        for t in transactions:
            await self.db.delete(t)
        await self.db.commit()
        return len(transactions)

    async def get_for_period(
        self, user_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
        )
        return list(result.scalars().all())

    async def bulk_create(self, transactions: list[Transaction]) -> None:
        self.db.add_all(transactions)
        await self.db.commit()

    async def get_all_for_user(self, user_id: uuid.UUID, limit: int = 500) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
