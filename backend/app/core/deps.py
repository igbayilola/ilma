"""FastAPI dependency injection helpers."""
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/token"
)


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Decode JWT and return the current active user."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_repository.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias — ensures user is active (already checked above)."""
    return current_user


def require_role(*roles: UserRole):
    """Return a dependency that enforces the user has one of the given roles."""

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return _check


async def get_active_profile(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    x_profile_id: Optional[str] = Header(None, alias="X-Profile-Id"),
) -> Profile:
    """Resolve the active profile for the current request.

    - If X-Profile-Id header is present → load profile, verify ownership.
    - If no header + exactly 1 active profile → auto-select (standalone student).
    - If no header + 0 or 2+ active profiles → 400 error.
    """
    if x_profile_id:
        try:
            profile_uuid = UUID(x_profile_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="X-Profile-Id invalide.")

        result = await db.execute(
            select(Profile).where(
                Profile.id == profile_uuid,
                Profile.user_id == current_user.id,
                Profile.is_active.is_(True),
            )
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profil introuvable ou inactif.",
            )
        return profile

    # No header — auto-select if exactly one active profile
    result = await db.execute(
        select(Profile).where(
            Profile.user_id == current_user.id,
            Profile.is_active.is_(True),
        )
    )
    profiles = list(result.scalars().all())

    if len(profiles) == 1:
        return profiles[0]

    if len(profiles) == 0:
        raise HTTPException(
            status_code=400,
            detail="Aucun profil actif. Veuillez en créer un.",
        )

    raise HTTPException(
        status_code=400,
        detail="Plusieurs profils trouvés. Veuillez spécifier X-Profile-Id.",
    )
