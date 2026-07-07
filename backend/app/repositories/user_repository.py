"""Data access layer for User and RefreshToken entities."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def store_refresh_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None:
        self.db.add(RefreshToken(user_id=user_id, token=token, expires_at=expires_at))
        await self.db.commit()

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token == token))
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> None:
        await self.db.execute(
            update(RefreshToken).where(RefreshToken.token == token).values(revoked=True)
        )
        await self.db.commit()

    @staticmethod
    def is_refresh_token_valid(rt: RefreshToken) -> bool:
        expires_at = rt.expires_at
        if expires_at.tzinfo is None:
            # SQLite (used in tests) does not preserve tz info; Postgres does.
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return not rt.revoked and expires_at > datetime.now(timezone.utc)
