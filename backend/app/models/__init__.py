"""Import all models here so Alembic's autogenerate can discover them."""
from app.models.budget import Budget  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.user import User  # noqa: F401
