"""Authentication service: register, login, password change/reset."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ConflictException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate


class AuthService:
    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        if not user_in.email and not user_in.phone:
            raise AppException(status_code=400, code="MISSING_FIELD", message="Email ou téléphone requis.")
        if user_in.email:
            existing = await user_repository.get_by_email(db, email=user_in.email)
            if existing:
                raise ConflictException("Un compte avec cet email existe déjà.")
        if user_in.phone:
            existing = await user_repository.get_by_phone(db, phone=user_in.phone)
            if existing:
                raise ConflictException("Un compte avec ce numéro existe déjà.")
        user = await user_repository.create(db, obj_in=user_in)
        return user

    async def login(self, db: AsyncSession, *, email: str, password: str) -> dict:
        user = await user_repository.get_by_email(db, email=email)
        if not user:
            # Try phone lookup if email lookup failed
            user = await user_repository.get_by_phone(db, phone=email)
        if not user or not verify_password(password, user.hashed_password):
            raise AppException(
                status_code=401,
                code="INVALID_CREDENTIALS",
                message="Email ou mot de passe incorrect.",
            )
        if not user.is_active:
            raise AppException(
                status_code=403,
                code="ACCOUNT_DISABLED",
                message="Ce compte est désactivé.",
            )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise AppException(
                status_code=400,
                code="WRONG_PASSWORD",
                message="Le mot de passe actuel est incorrect.",
            )
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        await db.flush()

    async def reset_password(
        self,
        db: AsyncSession,
        email: str,
        new_password: str,
    ) -> None:
        """Reset password after OTP verification (caller must verify OTP first)."""
        user = await user_repository.get_by_email(db, email=email)
        if not user:
            raise AppException(status_code=404, code="USER_NOT_FOUND", message="Utilisateur introuvable.")
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        await db.flush()


auth_service = AuthService()
