"""Business logic for category management."""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    async def create(self, user_id: uuid.UUID, data: CategoryCreate) -> Category:
        category = Category(user_id=user_id, **data.model_dump())
        return await self.repo.create(category)

    async def list(self, user_id: uuid.UUID) -> list[Category]:
        return await self.repo.list_for_user(user_id)

    async def get(self, user_id: uuid.UUID, category_id: uuid.UUID) -> Category:
        category = await self.repo.get_by_id(user_id, category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

    async def update(self, user_id: uuid.UUID, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        category = await self.get(user_id, category_id)
        return await self.repo.update(category, data.model_dump(exclude_unset=True))

    async def delete(self, user_id: uuid.UUID, category_id: uuid.UUID) -> None:
        category = await self.get(user_id, category_id)
        if category.is_default:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a default category")
        await self.repo.delete(category)
