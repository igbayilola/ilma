"""Admin endpoints: user management, analytics, exports."""
import csv
import io
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import require_role
from app.core.exceptions import AppException, NotFoundException
from app.db.session import get_db_session
from app.models.notification import NotificationType
from app.models.profile import Profile
from app.models.subscription import PaymentStatus
from app.models.user import User, UserRole
from app.schemas.response import ok, paginated
from app.schemas.user import User as UserSchema
from app.services.admin_service import admin_service
from app.services.config_service import config_service
from app.services.notification_service import notification_service
from app.services.risk_service import (
    RiskLevel,
    compute_for_profile,
    compute_funnel,
    list_at_risk,
)

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

@router.get("/analytics/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Single endpoint aggregating KPIs + engagement for 2G-friendly dashboard."""
    kpis = await admin_service.get_kpis(db)
    engagement = await admin_service.get_engagement(db)
    return ok(data={"kpis": kpis, "engagement": engagement})


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


@router.get("/analytics/at-risk-funnel")
async def get_at_risk_funnel(
    period_days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Funnel : at-risk détecté → SMS parent envoyé → réactivation J+7.

    Période paramétrable (7–90 j, défaut 30). `detected_now` est un
    snapshot indépendant de la période ; les autres compteurs sont
    fenêtrés.
    """
    funnel = await compute_funnel(db, period_days=period_days)
    return ok(data={
        "period_days": funnel.period_days,
        "detected_now": funnel.detected_now,
        "sms_sent": funnel.sms_sent,
        "sms_with_reactivation": funnel.sms_with_reactivation,
        "reactivation_rate": round(funnel.reactivation_rate, 4),
    })


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


# ── At-risk students ───────────────────────────────────────
@router.get("/students/at-risk")
async def list_students_at_risk(
    min_level: RiskLevel = Query("medium", description="Seuil : 'medium' (défaut) ou 'high'"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Liste les profils actifs dont le risk_level est ≥ `min_level`.

    Même formule que le cron parent-inactivity (`risk_service.classify_risk`).
    Tri : risk_level décroissant puis days_inactive décroissant.
    """
    skip = (page - 1) * page_size
    rows, total = await list_at_risk(db, min_level=min_level, skip=skip, limit=page_size)
    items = [
        {
            "profile_id": str(r.profile_id),
            "display_name": r.display_name,
            "grade_level": r.grade_level,
            "parent_user_id": str(r.parent_user_id) if r.parent_user_id else None,
            "parent_phone": r.parent_phone,
            "last_completed_at": r.last_completed_at.isoformat() if r.last_completed_at else None,
            "days_inactive": r.signals.days_inactive,
            "avg_score": round(r.signals.avg_score, 1),
            "risk_level": r.signals.risk_level,
            "suggested_action": r.signals.action,
        }
        for r in rows
    ]
    return paginated(items=items, total=total, page=page, page_size=page_size)


@router.get("/students/at-risk/export.csv")
async def export_students_at_risk_csv(
    min_level: RiskLevel = Query("medium"),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Export CSV de la cohorte at-risk pour campagnes outreach (papier,
    appel téléphonique). Pas de pagination — l'admin veut tout d'un coup.
    Limite haute à 5000 pour éviter une réponse pathologique."""
    rows, _ = await list_at_risk(db, min_level=min_level, skip=0, limit=5000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "profile_id", "display_name", "grade_level",
        "risk_level", "days_inactive", "avg_score",
        "last_completed_at", "parent_phone", "suggested_action",
    ])
    for r in rows:
        writer.writerow([
            str(r.profile_id),
            r.display_name,
            r.grade_level or "",
            r.signals.risk_level,
            r.signals.days_inactive,
            round(r.signals.avg_score, 1),
            r.last_completed_at.isoformat() if r.last_completed_at else "",
            r.parent_phone or "",
            r.signals.action,
        ])
    filename = f"at_risk_{min_level}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/students/{profile_id}/send-inactivity-sms")
async def admin_send_inactivity_sms(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Déclenche un SMS d'inactivité manuel vers le parent du profil cible.

    Respecte le même throttling quotidien que le cron
    (`NOTIFICATION_MAX_PER_DAY`) — l'admin ne peut pas spammer un parent.
    Construit le message via la même logique de gravité (`classify_risk`),
    donc cohérent avec ce que ferait le cron à l'identique.
    """
    profile = (await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.is_active.is_(True))
    )).scalar_one_or_none()
    if not profile:
        raise NotFoundException("Profil", str(profile_id))

    parent = (await db.execute(
        select(User).where(User.id == profile.user_id, User.role == UserRole.PARENT)
    )).scalar_one_or_none()
    if not parent or not parent.phone:
        raise AppException(
            status_code=400, code="NO_PARENT_PHONE",
            message="Aucun téléphone parent disponible pour ce profil.",
        )

    signals = await compute_for_profile(db, profile)
    if signals.risk_level == "low":
        raise AppException(
            status_code=400, code="NOT_AT_RISK",
            message="Ce profil n'est pas classé à risque — aucun SMS envoyé.",
        )

    today_count = await notification_service.count_today(db, parent.id)
    if today_count >= settings.NOTIFICATION_MAX_PER_DAY:
        raise AppException(
            status_code=429, code="NOTIFICATION_THROTTLED",
            message="Limite quotidienne atteinte pour ce parent.",
        )

    child_name = profile.display_name or "Votre enfant"
    if signals.risk_level == "high":
        title = f"Alerte : {child_name} risque de décrocher"
        body = f"{child_name} n'a pas étudié depuis {signals.days_inactive} jours"
        if signals.avg_score < 40:
            body += f" et son score moyen est de {signals.avg_score:.0f}%"
        body += ". Encouragez-le à reprendre avec un exercice de 10 minutes."
    else:
        title = f"{child_name} n'a pas étudié depuis {signals.days_inactive} jours"
        body = f"Un petit rappel pourrait aider {child_name} à reprendre le rythme."

    await notification_service.create_multi_channel(
        db=db,
        user_id=parent.id,
        type=NotificationType.INACTIVITY,
        title=title,
        body=body,
        data={
            "subject_profile_id": str(profile.id),
            "risk_level": signals.risk_level,
            "trigger": "admin_manual",
        },
        phone=parent.phone,
    )
    await db.commit()
    return ok(
        data={"risk_level": signals.risk_level, "parent_phone": parent.phone},
        message="SMS envoyé au parent.",
    )


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
