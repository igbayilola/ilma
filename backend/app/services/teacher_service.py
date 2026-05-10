"""Teacher service: classroom management, assignments, and reporting."""
import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ConflictException, ForbiddenException, NotFoundException
from app.models.classroom import Assignment, Classroom, ClassroomStudent
from app.models.session import ExerciseSession, SessionStatus


class TeacherService:
    # ── Classrooms ────────────────────────────────────────────

    async def create_classroom(
        self,
        db: AsyncSession,
        teacher_id: UUID,
        name: str,
        grade_level_id: UUID | None = None,
    ) -> Classroom:
        invite_code = secrets.token_urlsafe(6)[:8].upper()
        classroom = Classroom(
            teacher_id=teacher_id,
            name=name,
            invite_code=invite_code,
            grade_level_id=grade_level_id,
        )
        db.add(classroom)
        await db.flush()
        return classroom

    async def list_classrooms(
        self,
        db: AsyncSession,
        teacher_id: UUID,
    ) -> list[dict]:
        result = await db.execute(
            select(Classroom).where(
                Classroom.teacher_id == teacher_id,
                Classroom.is_active.is_(True),
            )
        )
        classrooms = list(result.scalars().all())

        items = []
        for c in classrooms:
            # Count students
            count_result = await db.execute(
                select(func.count(ClassroomStudent.id)).where(
                    ClassroomStudent.classroom_id == c.id,
                )
            )
            student_count = count_result.scalar() or 0

            items.append({
                "id": str(c.id),
                "name": c.name,
                "invite_code": c.invite_code,
                "grade_level_id": str(c.grade_level_id) if c.grade_level_id else None,
                "is_active": c.is_active,
                "max_students": c.max_students,
                "student_count": student_count,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            })
        return items

    async def get_classroom(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        teacher_id: UUID,
    ) -> dict:
        classroom = await self._get_owned_classroom(db, classroom_id, teacher_id)

        # Get students with their profiles
        result = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id == classroom_id,
            )
        )
        cs_links = list(result.scalars().all())

        students = []
        for cs in cs_links:
            profile = cs.profile
            students.append({
                "profile_id": str(cs.profile_id),
                "display_name": profile.display_name if profile else None,
                "avatar_url": profile.avatar_url if profile else None,
                "joined_at": cs.joined_at.isoformat() if cs.joined_at else None,
            })

        return {
            "id": str(classroom.id),
            "name": classroom.name,
            "invite_code": classroom.invite_code,
            "grade_level_id": str(classroom.grade_level_id) if classroom.grade_level_id else None,
            "is_active": classroom.is_active,
            "max_students": classroom.max_students,
            "students": students,
            "created_at": classroom.created_at.isoformat() if classroom.created_at else None,
        }

    async def deactivate_classroom(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        teacher_id: UUID,
    ) -> None:
        classroom = await self._get_owned_classroom(db, classroom_id, teacher_id)
        classroom.is_active = False
        db.add(classroom)
        await db.flush()

    # ── Student join / remove ─────────────────────────────────

    async def join_classroom(
        self,
        db: AsyncSession,
        profile_id: UUID,
        invite_code: str,
    ) -> dict:
        # Find classroom by invite code
        result = await db.execute(
            select(Classroom).where(
                Classroom.invite_code == invite_code.upper(),
                Classroom.is_active.is_(True),
            )
        )
        classroom = result.scalar_one_or_none()
        if not classroom:
            raise NotFoundException("Classroom", invite_code)

        # Check max students
        count_result = await db.execute(
            select(func.count(ClassroomStudent.id)).where(
                ClassroomStudent.classroom_id == classroom.id,
            )
        )
        current_count = count_result.scalar() or 0
        if current_count >= classroom.max_students:
            raise AppException(
                status_code=400,
                code="CLASSROOM_FULL",
                message="Cette classe est pleine.",
            )

        # Check if already joined
        existing = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id == classroom.id,
                ClassroomStudent.profile_id == profile_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Ce profil est déjà inscrit dans cette classe.")

        cs = ClassroomStudent(
            classroom_id=classroom.id,
            profile_id=profile_id,
        )
        db.add(cs)
        await db.flush()

        return {
            "classroom_id": str(classroom.id),
            "classroom_name": classroom.name,
            "profile_id": str(profile_id),
        }

    async def remove_student(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        profile_id: UUID,
        teacher_id: UUID,
    ) -> None:
        await self._get_owned_classroom(db, classroom_id, teacher_id)

        result = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id == classroom_id,
                ClassroomStudent.profile_id == profile_id,
            )
        )
        cs = result.scalar_one_or_none()
        if not cs:
            raise NotFoundException("ClassroomStudent")
        await db.delete(cs)
        await db.flush()

    # ── Assignments ───────────────────────────────────────────

    async def create_assignment(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        teacher_id: UUID,
        title: str,
        skill_id: UUID | None = None,
        deadline: datetime | None = None,
        question_count: int = 10,
        description: str | None = None,
    ) -> Assignment:
        await self._get_owned_classroom(db, classroom_id, teacher_id)

        assignment = Assignment(
            classroom_id=classroom_id,
            skill_id=skill_id,
            title=title,
            description=description,
            deadline=deadline,
            created_by=teacher_id,
            question_count=question_count,
        )
        db.add(assignment)
        await db.flush()
        return assignment

    async def list_assignments(
        self,
        db: AsyncSession,
        classroom_id: UUID,
    ) -> list[dict]:
        result = await db.execute(
            select(Assignment).where(
                Assignment.classroom_id == classroom_id,
                Assignment.is_active.is_(True),
            ).order_by(Assignment.created_at.desc())
        )
        assignments = list(result.scalars().all())

        items = []
        for a in assignments:
            items.append({
                "id": str(a.id),
                "title": a.title,
                "description": a.description,
                "skill_id": str(a.skill_id) if a.skill_id else None,
                "skill_name": a.skill.name if a.skill else None,
                "deadline": a.deadline.isoformat() if a.deadline else None,
                "question_count": a.question_count,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })
        return items

    async def get_assignment_results(
        self,
        db: AsyncSession,
        assignment_id: UUID,
        teacher_id: UUID,
    ) -> dict:
        # Get assignment and verify ownership
        result = await db.execute(
            select(Assignment).where(Assignment.id == assignment_id)
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise NotFoundException("Assignment", str(assignment_id))

        await self._get_owned_classroom(db, assignment.classroom_id, teacher_id)

        # Get all students in the classroom
        students_result = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id == assignment.classroom_id,
            )
        )
        cs_links = list(students_result.scalars().all())
        profile_ids = [cs.profile_id for cs in cs_links]

        if not profile_ids:
            return {
                "assignment_id": str(assignment_id),
                "title": assignment.title,
                "results": [],
            }

        # Get completed sessions for this skill by these profiles
        sessions_result = await db.execute(
            select(ExerciseSession).where(
                ExerciseSession.profile_id.in_(profile_ids),
                ExerciseSession.skill_id == assignment.skill_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        sessions = list(sessions_result.scalars().all())

        # Build per-student results
        profile_map = {cs.profile_id: cs.profile for cs in cs_links}
        student_sessions: dict[UUID, list] = {}
        for s in sessions:
            student_sessions.setdefault(s.profile_id, []).append(s)

        results = []
        for pid in profile_ids:
            profile = profile_map.get(pid)
            ss = student_sessions.get(pid, [])
            best_score = max((s.score for s in ss), default=None)
            avg_score = round(sum(s.score for s in ss) / len(ss), 1) if ss else None
            results.append({
                "profile_id": str(pid),
                "display_name": profile.display_name if profile else None,
                "sessions_count": len(ss),
                "best_score": best_score,
                "avg_score": avg_score,
            })

        return {
            "assignment_id": str(assignment_id),
            "title": assignment.title,
            "skill_id": str(assignment.skill_id) if assignment.skill_id else None,
            "results": results,
        }

    # ── Dashboard / Reporting ─────────────────────────────────

    async def get_class_overview(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        teacher_id: UUID,
    ) -> dict:
        classroom = await self._get_owned_classroom(db, classroom_id, teacher_id)

        # Get students
        students_result = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id == classroom_id,
            )
        )
        cs_links = list(students_result.scalars().all())
        profile_ids = [cs.profile_id for cs in cs_links]
        total_students = len(profile_ids)

        if not profile_ids:
            return {
                "classroom_id": str(classroom_id),
                "classroom_name": classroom.name,
                "total_students": 0,
                "active_students": 0,
                "avg_score": None,
                "students_in_difficulty": [],
            }

        # Get completed sessions for all students
        sessions_result = await db.execute(
            select(ExerciseSession).where(
                ExerciseSession.profile_id.in_(profile_ids),
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        sessions = list(sessions_result.scalars().all())

        # Compute per-student stats
        profile_map = {cs.profile_id: cs.profile for cs in cs_links}
        student_scores: dict[UUID, list[float]] = {}
        for s in sessions:
            student_scores.setdefault(s.profile_id, []).append(s.score)

        active_students = len(student_scores)
        all_scores = [score for scores in student_scores.values() for score in scores]
        avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else None

        # Students in difficulty: avg score < 40%
        students_in_difficulty = []
        for pid, scores in student_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 40.0:
                profile = profile_map.get(pid)
                students_in_difficulty.append({
                    "profile_id": str(pid),
                    "display_name": profile.display_name if profile else None,
                    "avg_score": round(avg, 1),
                    "sessions_count": len(scores),
                })

        return {
            "classroom_id": str(classroom_id),
            "classroom_name": classroom.name,
            "total_students": total_students,
            "active_students": active_students,
            "avg_score": avg_score,
            "students_in_difficulty": students_in_difficulty,
        }

    async def generate_report_data(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        teacher_id: UUID,
    ) -> dict:
        classroom = await self._get_owned_classroom(db, classroom_id, teacher_id)

        # Get students
        students_result = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id == classroom_id,
            )
        )
        cs_links = list(students_result.scalars().all())
        profile_ids = [cs.profile_id for cs in cs_links]

        if not profile_ids:
            return {
                "classroom_id": str(classroom_id),
                "classroom_name": classroom.name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "students": [],
            }

        # Get all completed sessions
        sessions_result = await db.execute(
            select(ExerciseSession).where(
                ExerciseSession.profile_id.in_(profile_ids),
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        sessions = list(sessions_result.scalars().all())

        profile_map = {cs.profile_id: cs.profile for cs in cs_links}
        student_sessions: dict[UUID, list] = {}
        for s in sessions:
            student_sessions.setdefault(s.profile_id, []).append(s)

        students_data = []
        for pid in profile_ids:
            profile = profile_map.get(pid)
            ss = student_sessions.get(pid, [])
            scores = [s.score for s in ss]
            total_time = sum(s.duration_seconds or 0 for s in ss)
            avg_score = round(sum(scores) / len(scores), 1) if scores else None

            students_data.append({
                "profile_id": str(pid),
                "display_name": profile.display_name if profile else None,
                "sessions_count": len(ss),
                "avg_score": avg_score,
                "best_score": max(scores) if scores else None,
                "total_time_seconds": total_time,
                "total_correct": sum(s.correct_answers for s in ss),
                "total_questions": sum(s.total_questions for s in ss),
            })

        return {
            "classroom_id": str(classroom_id),
            "classroom_name": classroom.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_students": len(profile_ids),
            "students": students_data,
        }

    async def get_alerts(
        self,
        db: AsyncSession,
        teacher_id: UUID,
    ) -> list[dict]:
        """Get students in difficulty (avg score < 40%) across all teacher's classrooms."""
        # Get all active classrooms for this teacher
        result = await db.execute(
            select(Classroom).where(
                Classroom.teacher_id == teacher_id,
                Classroom.is_active.is_(True),
            )
        )
        classrooms = list(result.scalars().all())

        if not classrooms:
            return []

        classroom_map = {c.id: c for c in classrooms}
        classroom_ids = list(classroom_map.keys())

        # Get all students across classrooms
        cs_result = await db.execute(
            select(ClassroomStudent).where(
                ClassroomStudent.classroom_id.in_(classroom_ids),
            )
        )
        cs_links = list(cs_result.scalars().all())

        if not cs_links:
            return []

        profile_ids = [cs.profile_id for cs in cs_links]

        # Get completed sessions
        sessions_result = await db.execute(
            select(ExerciseSession).where(
                ExerciseSession.profile_id.in_(profile_ids),
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        sessions = list(sessions_result.scalars().all())

        # Build per-student score map
        student_scores: dict[UUID, list[float]] = {}
        for s in sessions:
            student_scores.setdefault(s.profile_id, []).append(s.score)

        # Build classroom membership map (profile_id -> classroom_ids)
        profile_classrooms: dict[UUID, list[UUID]] = {}
        profile_map: dict[UUID, object] = {}
        for cs in cs_links:
            profile_classrooms.setdefault(cs.profile_id, []).append(cs.classroom_id)
            profile_map[cs.profile_id] = cs.profile

        alerts = []
        for pid, scores in student_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 40.0:
                profile = profile_map.get(pid)
                cids = profile_classrooms.get(pid, [])
                for cid in cids:
                    classroom = classroom_map.get(cid)
                    alerts.append({
                        "profile_id": str(pid),
                        "display_name": profile.display_name if profile else None,
                        "classroom_id": str(cid),
                        "classroom_name": classroom.name if classroom else None,
                        "avg_score": round(avg, 1),
                        "sessions_count": len(scores),
                    })

        # Sort by avg_score ascending (worst first)
        alerts.sort(key=lambda a: a["avg_score"])
        return alerts

    # ── Helpers ───────────────────────────────────────────────

    async def _get_owned_classroom(
        self,
        db: AsyncSession,
        classroom_id: UUID,
        teacher_id: UUID,
    ) -> Classroom:
        result = await db.execute(
            select(Classroom).where(Classroom.id == classroom_id)
        )
        classroom = result.scalar_one_or_none()
        if not classroom:
            raise NotFoundException("Classroom", str(classroom_id))
        if classroom.teacher_id != teacher_id:
            raise ForbiddenException("Vous n'êtes pas le propriétaire de cette classe.")
        return classroom


teacher_service = TeacherService()
