"""Business logic for registration, login, and token refresh."""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.category import Category
from app.models.transaction import TransactionType
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import AccessTokenOut, TokenPair, UserCreate, UserLogin

DEFAULT_CATEGORIES = [
    ("Salary", TransactionType.INCOME, "briefcase", "#22c55e"),
    ("Freelance", TransactionType.INCOME, "laptop", "#10b981"),
    ("Investments", TransactionType.INCOME, "trending-up", "#06b6d4"),
    ("Food & Dining", TransactionType.EXPENSE, "utensils", "#f97316"),
    ("Groceries", TransactionType.EXPENSE, "shopping-cart", "#84cc16"),
    ("Transport", TransactionType.EXPENSE, "car", "#3b82f6"),
    ("Rent", TransactionType.EXPENSE, "home", "#8b5cf6"),
    ("Utilities", TransactionType.EXPENSE, "zap", "#eab308"),
    ("Entertainment", TransactionType.EXPENSE, "film", "#ec4899"),
    ("Shopping", TransactionType.EXPENSE, "shopping-bag", "#f43f5e"),
    ("Healthcare", TransactionType.EXPENSE, "heart-pulse", "#14b8a6"),
    ("Subscriptions", TransactionType.EXPENSE, "repeat", "#a855f7"),
    ("Other", TransactionType.EXPENSE, "more-horizontal", "#64748b"),
]


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.category_repo = CategoryRepository(db)

    async def register(self, data: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        user = await self.user_repo.create(user)

        # Seed default categories for the new user
        default_cats = [
            Category(user_id=user.id, name=name, type=t, icon=icon, color=color, is_default=True)
            for name, t, icon, color in DEFAULT_CATEGORIES
        ]
        await self.category_repo.bulk_create(default_cats)

        return user

    async def login(self, data: UserLogin) -> TokenPair:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> AccessTokenOut:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        stored = await self.user_repo.get_refresh_token(refresh_token)
        if not stored or not self.user_repo.is_refresh_token_valid(stored):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

        access_token = create_access_token(subject=str(stored.user_id))
        return AccessTokenOut(access_token=access_token)

    async def logout(self, refresh_token: str) -> None:
        await self.user_repo.revoke_refresh_token(refresh_token)

    async def _issue_tokens(self, user: User) -> TokenPair:
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.user_repo.store_refresh_token(user.id, refresh_token, expires_at)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
