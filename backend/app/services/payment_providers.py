"""Payment provider adapters for KKiaPay and FedaPay."""
import hashlib
import hmac

import httpx

from app.core.config import settings


class PaymentProviderBase:
    """Base payment provider interface."""

    async def create_transaction(self, amount: int, description: str, callback_url: str) -> dict:
        raise NotImplementedError

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        raise NotImplementedError


class MockPaymentProvider(PaymentProviderBase):
    async def create_transaction(self, amount: int, description: str, callback_url: str) -> dict:
        import uuid

        return {
            "provider": "mock",
            "transaction_id": f"mock_{uuid.uuid4().hex[:12]}",
            "status": "completed",
            "amount": amount,
        }

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        return True


class StubPaymentProvider(PaymentProviderBase):
    """Stub for real providers when API keys are not configured. Returns pending status."""

    def __init__(self, name: str):
        self.name = name

    async def create_transaction(self, amount: int, description: str, callback_url: str) -> dict:
        import uuid

        return {
            "provider": self.name,
            "transaction_id": f"stub_{uuid.uuid4().hex[:12]}",
            "status": "pending",
            "amount": amount,
        }

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        return False


class KKiaPayProvider(PaymentProviderBase):
    BASE_URL = "https://api.kkiapay.me/api/v1"

    async def create_transaction(self, amount: int, description: str, callback_url: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/transactions/request",
                json={
                    "amount": amount,
                    "description": description,
                    "callback": callback_url,
                },
                headers={"X-API-Key": settings.KKIAPAY_PRIVATE_KEY},
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "provider": "kkiapay",
                "transaction_id": data.get("transactionId", ""),
                "status": "pending",
                "payment_url": data.get("payment_url", ""),
            }

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        if not settings.KKIAPAY_SECRET:
            return False
        expected = hmac.new(settings.KKIAPAY_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


class FedaPayProvider(PaymentProviderBase):
    BASE_URL = "https://api.fedapay.com/v1"

    @property
    def _base_url(self) -> str:
        if settings.FEDAPAY_ENVIRONMENT == "sandbox":
            return "https://sandbox-api.fedapay.com/v1"
        return self.BASE_URL

    async def create_transaction(self, amount: int, description: str, callback_url: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/transactions",
                json={
                    "description": description,
                    "amount": amount,
                    "currency": {"iso": "XOF"},
                    "callback_url": callback_url,
                },
                headers={
                    "Authorization": f"Bearer {settings.FEDAPAY_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            tx = data.get("v1/transaction", data)
            return {
                "provider": "fedapay",
                "transaction_id": str(tx.get("id", "")),
                "status": "pending",
                "payment_url": tx.get("payment_url", ""),
            }

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        if not settings.FEDAPAY_API_KEY:
            return False
        expected = hmac.new(settings.FEDAPAY_API_KEY.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


def get_payment_provider(provider: str) -> PaymentProviderBase:
    if provider == "kkiapay":
        if settings.KKIAPAY_PRIVATE_KEY:
            return KKiaPayProvider()
        return StubPaymentProvider("kkiapay")
    if provider == "fedapay":
        if settings.FEDAPAY_API_KEY:
            return FedaPayProvider()
        return StubPaymentProvider("fedapay")
    return MockPaymentProvider()
