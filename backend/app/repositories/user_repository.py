"""User repository with password hashing on create."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        statement = select(self._model).where(self._model.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> Optional[User]:
        statement = select(self._model).where(self._model.phone == phone)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        from app.core.security import get_password_hash

        db_obj = self._model(
            email=obj_in.email,
            phone=obj_in.phone,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role,
            grade_level_id=obj_in.grade_level_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


user_repository = UserRepository(User)
