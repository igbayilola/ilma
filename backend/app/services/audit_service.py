"""Audit logging service."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditService:
    async def log(
        self,
        db: AsyncSession,
        action: str,
        user_id=None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> None:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        db.add(entry)
        await db.flush()


audit_service = AuditService()
