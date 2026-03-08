"""OTP generation, validation, and sending (mock + Twilio provider)."""
import random
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, RateLimitException
from app.models.otp import OTPCode

# Benin phone prefixes: MTN (96,97,66,67), Moov (95,94,64,65,69), etc.
BENIN_PHONE_RE = re.compile(r"^\+229(9[4-7]|6[4-9])\d{6}$")

OTP_VALIDITY_MINUTES = 5
OTP_MAX_ATTEMPTS = 3
OTP_RESEND_COOLDOWN_SECONDS = 60


def validate_benin_phone(phone: str) -> bool:
    return bool(BENIN_PHONE_RE.match(phone))


def generate_otp_code() -> str:
    return f"{random.randint(0, 999999):06d}"


class SMSProvider:
    """Base SMS provider interface."""

    async def send(self, phone: str, message: str) -> None:
        raise NotImplementedError


class MockSMSProvider(SMSProvider):
    async def send(self, phone: str, message: str) -> None:
        print(f"[SMS MOCK] To {phone}: {message}")


class TwilioSMSProvider(SMSProvider):
    def __init__(self) -> None:
        from twilio.rest import Client  # type: ignore[import-untyped]

        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_FROM_NUMBER

    async def send(self, phone: str, message: str) -> None:
        # Twilio's client is sync; run in thread to avoid blocking
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(body=message, from_=self.from_number, to=phone),
        )


def _get_sms_provider() -> SMSProvider:
    if settings.SMS_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID:
        return TwilioSMSProvider()
    return MockSMSProvider()


class OTPService:
    def __init__(self) -> None:
        self._sms = _get_sms_provider()

    async def send_otp(self, db: AsyncSession, phone: str, user_id=None) -> dict:
        if not validate_benin_phone(phone):
            raise AppException(
                status_code=400,
                code="INVALID_PHONE",
                message="Numéro de téléphone invalide. Format attendu: +229XXXXXXXX",
            )

        # Rate limit: check cooldown
        recent = await db.execute(
            select(OTPCode)
            .where(OTPCode.phone == phone, OTPCode.is_used.is_(False))
            .order_by(OTPCode.created_at.desc())
            .limit(1)
        )
        last_otp = recent.scalar_one_or_none()
        if last_otp:
            elapsed = (datetime.now(timezone.utc) - last_otp.created_at.replace(tzinfo=timezone.utc)).total_seconds()
            if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
                raise RateLimitException(
                    message=f"Veuillez attendre {int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)}s avant de renvoyer un code."
                )

        code = generate_otp_code()
        otp = OTPCode(
            phone=phone,
            code=code,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_VALIDITY_MINUTES),
        )
        db.add(otp)
        await db.flush()

        await self._sms.send(phone, f"Votre code ILMA : {code}")

        return {"phone": phone, "expires_in": OTP_VALIDITY_MINUTES * 60}

    async def verify_otp(self, db: AsyncSession, phone: str, code: str) -> bool:
        result = await db.execute(
            select(OTPCode)
            .where(
                OTPCode.phone == phone,
                OTPCode.is_used.is_(False),
            )
            .order_by(OTPCode.created_at.desc())
            .limit(1)
        )
        otp = result.scalar_one_or_none()

        if not otp:
            raise AppException(status_code=400, code="OTP_NOT_FOUND", message="Aucun code OTP actif pour ce numéro.")

        now = datetime.now(timezone.utc)
        if otp.expires_at.replace(tzinfo=timezone.utc) < now:
            raise AppException(status_code=400, code="OTP_EXPIRED", message="Le code OTP a expiré.")

        if otp.attempts >= otp.max_attempts:
            raise AppException(status_code=400, code="OTP_MAX_ATTEMPTS", message="Nombre maximal de tentatives atteint.")

        if otp.code != code:
            otp.attempts += 1
            await db.flush()
            remaining = otp.max_attempts - otp.attempts
            raise AppException(
                status_code=400,
                code="OTP_INVALID",
                message=f"Code incorrect. {remaining} tentative(s) restante(s).",
            )

        # Success
        otp.is_used = True
        await db.flush()
        return True


otp_service = OTPService()
