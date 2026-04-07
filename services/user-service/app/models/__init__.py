from app.models.base import Base
from app.models.user import User  # noqa: F401 — registers table for Alembic

__all__ = ["Base", "User"]
