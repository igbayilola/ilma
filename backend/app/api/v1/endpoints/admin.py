"""Admin endpoints: user management, analytics, exports."""
import io
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_role
from app.db.session import get_db_session
from app.models.subscription import PaymentStatus
from app.models.user import User, UserRole
from app.schemas.response import ok, paginated
from app.schemas.user import User as UserSchema
from app.services.admin_service import admin_service
from app.services.config_service import config_service

router = APIRouter(prefix="/admin", tags=["Admin"])

_admin = require_role(UserRole.ADMIN)


# ── Users ──────────────────────────────────────────────────
@router.get("/users")
async def list_users(
    role: UserRole | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    skip = (page - 1) * page_size
    users, total = await admin_service.list_users(db, role=role, search=search, skip=skip, limit=page_size)
    return paginated(
        items=[UserSchema.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    user = await admin_service.suspend_user(db, user_id)
    await db.commit()
    return ok(data=UserSchema.model_validate(user), message="Utilisateur suspendu")


@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    user = await admin_service.reactivate_user(db, user_id)
    await db.commit()
    return ok(data=UserSchema.model_validate(user), message="Utilisateur réactivé")


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    await admin_service.reset_user_password(db, user_id, "Sitou2024!")
    await db.commit()
    return ok(message="Mot de passe réinitialisé (temporaire: Sitou2024!)")


# ── Payments ──────────────────────────────────────────────
@router.get("/payments")
async def list_payments(
    status: PaymentStatus | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    skip = (page - 1) * page_size
    items, total = await admin_service.list_payments(db, status=status, skip=skip, limit=page_size)
    return paginated(items=items, total=total, page=page, page_size=page_size)


# ── Analytics ──────────────────────────────────────────────
@router.get("/analytics/kpis")
async def get_kpis(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    kpis = await admin_service.get_kpis(db)
    return ok(data=kpis)


@router.get("/analytics/engagement")
async def get_engagement(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    data = await admin_service.get_engagement(db)
    return ok(data=data)


@router.get("/analytics/retention")
async def get_retention(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    data = await admin_service.get_retention(db)
    return ok(data=data)


@router.get("/analytics/conversion")
async def get_conversion(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    data = await admin_service.get_conversion(db)
    return ok(data=data)


@router.get("/analytics/virality")
async def get_virality(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    data = await admin_service.get_virality(db)
    return ok(data=data)


@router.get("/analytics/notifications")
async def get_notification_stats(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    stats = await admin_service.get_notification_stats(db)
    return ok(data=stats)


@router.get("/analytics/digest-stats")
async def get_digest_stats(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    stats = await admin_service.get_digest_stats(db)
    return ok(data=stats)


@router.get("/analytics/questions")
async def get_question_stats(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    stats = await admin_service.get_question_stats(db, limit=limit)
    return ok(data=stats)


# ── Exports ────────────────────────────────────────────────
@router.get("/export/users.csv")
async def export_users_csv(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    csv_content = await admin_service.export_users_csv(db)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"},
    )


@router.get("/export/report.pdf", summary="Export KPI report as PDF")
async def export_kpi_pdf(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    kpis = await admin_service.get_kpis(db)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8">
<style>
body {{ font-family: sans-serif; margin: 40px; color: #333; }}
h1 {{ color: #1E5AA8; border-bottom: 2px solid #1E5AA8; padding-bottom: 8px; }}
h2 {{ color: #555; margin-top: 24px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #1E5AA8; color: white; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.footer {{ margin-top: 40px; font-size: 0.85em; color: #999; }}
</style></head>
<body>
<h1>Sitou — Rapport d'activité</h1>
<p>Généré le {now}</p>

<h2>Indicateurs clés</h2>
<table>
<tr><th>Indicateur</th><th>Valeur</th></tr>
"""
    for key, value in (kpis if isinstance(kpis, dict) else {}).items():
        label = key.replace("_", " ").capitalize()
        html += f"<tr><td>{label}</td><td>{value}</td></tr>\n"

    html += """</table>
<div class="footer">Rapport généré automatiquement par Sitou Admin.</div>
</body></html>"""

    try:
        from weasyprint import HTML  # type: ignore[import-untyped]

        pdf_bytes = HTML(string=html).write_pdf()
    except ImportError:
        # Fallback: return HTML if weasyprint is not installed
        return StreamingResponse(
            iter([html.encode()]),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=ilma_report_{now[:10]}.html"},
        )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ilma_report_{now[:10]}.pdf"},
    )


# ── Dynamic Config ────────────────────────────────────────
@router.get("/config")
async def get_all_config(
    category: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    configs = await config_service.get_all(db, category=category)
    # Group by category
    grouped: dict[str, dict] = {}
    for key, info in configs.items():
        cat = info["category"]
        if cat not in grouped:
            grouped[cat] = {}
        grouped[cat][key] = info
    return ok(data=grouped)


@router.put("/config/bulk")
async def update_config_bulk(
    updates: dict[str, Any],
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    await config_service.set_bulk(db, updates)
    await db.commit()
    return ok(message="Configuration mise à jour")


@router.put("/config/{key}")
async def update_config(
    key: str,
    body: dict,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    value = body.get("value")
    if value is None:
        from app.core.exceptions import AppException
        raise AppException(status_code=400, code="MISSING_VALUE", message="Le champ 'value' est requis.")
    await config_service.set(db, key, value)
    await db.commit()
    return ok(message=f"Config '{key}' mise à jour")
