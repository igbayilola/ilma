"""Auth endpoints: register, login, refresh, logout, OTP, password change/reset."""
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.exceptions import AppException
from app.core.security import create_access_token, create_refresh_token
from app.db.session import get_db_session
from app.models.user import User as UserModel
from app.repositories.user_repository import user_repository
from app.schemas.auth import (
    LoginRequest,
    OTPSendRequest,
    OTPVerifyRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    RefreshRequest,
)
from app.schemas.response import ok
from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.services.audit_service import audit_service
from app.services.auth_service import auth_service
from app.services.otp_service import otp_service

router = APIRouter(tags=["Auth"])

EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


def _build_auth_response(user: UserModel, access_token: str, refresh_token: str) -> dict:
    """Build a combined auth response with user + tokens + profiles."""
    profiles = []
    if hasattr(user, "profiles") and user.profiles:
        for p in user.profiles:
            if p.is_active:
                profiles.append({
                    "id": str(p.id),
                    "display_name": p.display_name,
                    "avatar_url": p.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={p.id}",
                    "grade_level_id": str(p.grade_level_id) if p.grade_level_id else None,
                    "is_active": p.is_active,
                    "has_pin": p.pin_hash is not None,
                    "subscription_tier": "free",
                    "weekly_goal_minutes": p.weekly_goal_minutes,
                })
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": EXPIRES_IN,
        "user": User.model_validate(user).model_dump(),
        "profiles": profiles,
    }


# ── Registration ───────────────────────────────────────────
@router.post("/register", status_code=201)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    user = await auth_service.register_user(db, user_in)
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    await audit_service.log(db, "register", user_id=user.id, ip_address=request.client.host)
    await db.commit()
    # Refresh user to load newly-created profiles relationship
    await db.refresh(user, attribute_names=["profiles"])
    return ok(
        data=_build_auth_response(user, access_token, refresh_token),
        message="Inscription réussie",
    )


# ── Login (JSON body) ─────────────────────────────────────
@router.post("/login")
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    # Support 'identifier' field from frontend (email or phone)
    email = body.email or body.identifier
    if not email:
        raise AppException(status_code=400, code="MISSING_FIELD", message="Email ou téléphone requis.")
    result = await auth_service.login(db, email=email, password=body.password)
    await audit_service.log(
        db, "login_success", user_id=result["user"].id, ip_address=request.client.host
    )
    await db.commit()
    return ok(
        data=_build_auth_response(
            result["user"], result["access_token"], result["refresh_token"]
        )
    )


# ── Login (OAuth2 form — for Swagger UI) ──────────────────
@router.post("/login/token", include_in_schema=False)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    result = await auth_service.login(db, email=form_data.username, password=form_data.password)
    await db.commit()
    return Token(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


# ── Refresh ────────────────────────────────────────────────
@router.post("/refresh")
async def refresh_token_endpoint(
    body: RefreshRequest = RefreshRequest(),
    db: AsyncSession = Depends(get_db_session),
):
    """Accept refresh_token in body, decode it, issue new tokens."""
    if not body.refresh_token:
        raise AppException(status_code=400, code="MISSING_TOKEN", message="Refresh token requis.")

    try:
        payload = jwt.decode(
            body.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise AppException(status_code=401, code="INVALID_TOKEN", message="Token invalide.")
    except JWTError:
        raise AppException(status_code=401, code="INVALID_TOKEN", message="Token expiré ou invalide.")

    user = await user_repository.get(db, id=user_id)
    if not user or not user.is_active:
        raise AppException(status_code=401, code="INVALID_TOKEN", message="Utilisateur introuvable.")

    access = create_access_token(subject=user.id)
    refresh = create_refresh_token(subject=user.id)
    return ok(data=_build_auth_response(user, access, refresh))


# ── Logout (client-side — no server revocation for MVP) ───
@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    await audit_service.log(db, "logout", user_id=current_user.id, ip_address=request.client.host)
    await db.commit()
    return ok(message="Déconnexion réussie")


# ── Current user ───────────────────────────────────────────
@router.get("/me")
async def read_users_me(
    current_user: UserModel = Depends(get_current_user),
):
    return ok(data=User.model_validate(current_user))


# ── OTP ────────────────────────────────────────────────────
@router.post("/otp/send")
async def otp_send(
    body: OTPSendRequest,
    db: AsyncSession = Depends(get_db_session),
):
    result = await otp_service.send_otp(db, phone=body.phone)
    await db.commit()
    return ok(data=result, message="Code OTP envoyé")


@router.post("/otp/verify")
async def otp_verify(
    body: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db_session),
):
    await otp_service.verify_otp(db, phone=body.phone, code=body.code)
    await db.commit()
    return ok(message="Code OTP vérifié avec succès")


# ── Password ───────────────────────────────────────────────
@router.post("/password/change")
async def password_change(
    body: PasswordChangeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
):
    await auth_service.change_password(
        db, current_user, body.current_password, body.new_password
    )
    await audit_service.log(db, "password_change", user_id=current_user.id, ip_address=request.client.host)
    await db.commit()
    return ok(message="Mot de passe modifié avec succès")


@router.post("/password/reset")
async def password_reset(
    body: PasswordResetRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """Reset password — caller must have verified OTP beforehand."""
    await auth_service.reset_password(db, email=body.email, new_password=body.new_password)
    await audit_service.log(db, "password_reset", ip_address=request.client.host, details={"email": body.email})
    await db.commit()
    return ok(message="Mot de passe réinitialisé avec succès")
