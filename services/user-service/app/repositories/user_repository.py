import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for User persistence operations.

    Args:
        session: Active async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            email: The user's email address.

        Returns:
            The matching User, or ``None`` if not found.
        """
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Fetch a user by primary key.

        Args:
            user_id: User primary key.

        Returns:
            The matching User, or ``None`` if not found.
        """
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str, name: str) -> User:
        """Persist a new user and return the created instance.

        Args:
            email: Unique email address.
            password_hash: Bcrypt-hashed password.
            name: Display name.

        Returns:
            The newly created User instance.
        """
        user = User(email=email, password_hash=password_hash, name=name)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def update(
        self,
        user_id: uuid.UUID,
        name: str | None = None,
        password_hash: str | None = None,
    ) -> User | None:
        """Update a user's name and/or password hash.

        Args:
            user_id: User primary key.
            name: New display name, or ``None`` to leave unchanged.
            password_hash: New bcrypt hash, or ``None`` to leave unchanged.

        Returns:
            The updated User instance, or ``None`` if the user was not found.
        """
        user = await self._session.get(User, user_id)
        if not user:
            return None
        if name is not None:
            user.name = name
        if password_hash is not None:
            user.password_hash = password_hash
        await self._session.commit()
        await self._session.refresh(user)
        return user
