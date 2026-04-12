"""Teacher endpoints: classroom management, assignments, reporting."""
import csv
import io
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, require_role
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.schemas.response import ok
from app.services.teacher_service import teacher_service

router = APIRouter(prefix="/teacher", tags=["Teacher"])

_teacher_or_admin = require_role(UserRole.TEACHER, UserRole.ADMIN)


# ── Schemas ───────────────────────────────────────────────────

class ClassroomCreate(BaseModel):
    name: str = Field(..., max_length=255)
    grade_level_id: Optional[UUID] = None


class JoinClassroom(BaseModel):
    invite_code: str = Field(..., max_length=8)


class AssignmentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    skill_id: Optional[UUID] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    question_count: int = Field(default=10, ge=1, le=100)


# ── Classrooms ────────────────────────────────────────────────

@router.get("/classrooms")
async def list_classrooms(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    items = await teacher_service.list_classrooms(db, current_user.id)
    return ok(data=items)


@router.post("/classrooms", status_code=201)
async def create_classroom(
    body: ClassroomCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    classroom = await teacher_service.create_classroom(
        db, current_user.id, body.name, body.grade_level_id,
    )
    await db.commit()
    return ok(data={
        "id": str(classroom.id),
        "name": classroom.name,
        "invite_code": classroom.invite_code,
    }, message="Classe créée avec succès.")


@router.get("/classrooms/{classroom_id}")
async def get_classroom(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    data = await teacher_service.get_classroom(db, classroom_id, current_user.id)
    return ok(data=data)


@router.delete("/classrooms/{classroom_id}")
async def deactivate_classroom(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    await teacher_service.deactivate_classroom(db, classroom_id, current_user.id)
    await db.commit()
    return ok(message="Classe désactivée.")


# ── Student join / remove ─────────────────────────────────────

@router.post("/classrooms/join")
async def join_classroom(
    body: JoinClassroom,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Student/parent joins a classroom via invite code."""
    data = await teacher_service.join_classroom(db, profile.id, body.invite_code)
    await db.commit()
    return ok(data=data, message="Inscription réussie.")


@router.delete("/classrooms/{classroom_id}/students/{profile_id}")
async def remove_student(
    classroom_id: UUID,
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    await teacher_service.remove_student(db, classroom_id, profile_id, current_user.id)
    await db.commit()
    return ok(message="Élève retiré de la classe.")


# ── Assignments ───────────────────────────────────────────────

@router.post("/classrooms/{classroom_id}/assignments", status_code=201)
async def create_assignment(
    classroom_id: UUID,
    body: AssignmentCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    assignment = await teacher_service.create_assignment(
        db,
        classroom_id,
        current_user.id,
        body.title,
        skill_id=body.skill_id,
        deadline=body.deadline,
        question_count=body.question_count,
        description=body.description,
    )
    await db.commit()
    return ok(data={
        "id": str(assignment.id),
        "title": assignment.title,
        "classroom_id": str(assignment.classroom_id),
    }, message="Devoir créé avec succès.")


@router.get("/classrooms/{classroom_id}/assignments")
async def list_assignments(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    items = await teacher_service.list_assignments(db, classroom_id)
    return ok(data=items)


@router.get("/assignments/{assignment_id}/results")
async def get_assignment_results(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    data = await teacher_service.get_assignment_results(db, assignment_id, current_user.id)
    return ok(data=data)


# ── Dashboard / Reporting ─────────────────────────────────────

@router.get("/classrooms/{classroom_id}/overview")
async def get_class_overview(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    data = await teacher_service.get_class_overview(db, classroom_id, current_user.id)
    return ok(data=data)


@router.get("/classrooms/{classroom_id}/report")
async def get_class_report(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    data = await teacher_service.generate_report_data(db, classroom_id, current_user.id)
    return ok(data=data)


@router.get("/classrooms/{classroom_id}/export/csv")
async def export_class_csv(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    """Export classroom report as CSV file."""
    data = await teacher_service.generate_report_data(db, classroom_id, current_user.id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nom", "Sessions", "Score moyen", "Meilleur score", "Temps (min)", "Bonnes réponses", "Total questions"])
    for s in data.get("students", []):
        writer.writerow([
            s["display_name"],
            s["sessions_count"],
            round(s["avg_score"], 1),
            round(s["best_score"], 1),
            round(s["total_time_seconds"] / 60, 1),
            s["total_correct"],
            s["total_questions"],
        ])
    output.seek(0)
    filename = f"classe_{data.get('classroom_name', classroom_id)}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/alerts")
async def get_alerts(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(_teacher_or_admin),
):
    alerts = await teacher_service.get_alerts(db, current_user.id)
    return ok(data=alerts)
