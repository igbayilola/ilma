"""Mock exam (Examen Blanc) service for CEP preparation."""
import random
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException, NotFoundException
from app.models.content import Domain, Question, Skill, Subject, DifficultyLevel, MicroLesson
from app.models.mock_exam import ExamItem, ExamSession, ExamSubQuestion, MockExam
from app.models.profile import Profile
from app.models.subscription import PlanTier
from app.services.subscription_service import subscription_service


class ExamService:
    async def generate_exam(
        self,
        db: AsyncSession,
        grade_level_id: UUID,
        subject_id: UUID,
        title: str = "Examen Blanc",
        total_questions: int = 30,
        duration_minutes: int = 60,
        is_free: bool = False,
        is_national: bool = False,
        national_date=None,
    ) -> MockExam:
        """Create a MockExam with balanced question distribution."""
        # Count available questions per difficulty for this subject
        result = await db.execute(
            select(Question.difficulty, func.count(Question.id))
            .join(Skill, Question.skill_id == Skill.id)
            .join(Domain, Skill.domain_id == Domain.id)
            .where(
                Domain.subject_id == subject_id,
                Question.is_active.is_(True),
            )
            .group_by(Question.difficulty)
        )
        counts = {row[0]: row[1] for row in result.all()}

        # Build distribution based on available questions
        total_available = sum(counts.values())
        if total_available == 0:
            raise AppException(
                status_code=400,
                code="NO_QUESTIONS",
                message="Aucune question disponible pour cette matière.",
            )

        # Default distribution: 33% easy, 50% medium, 17% hard
        distribution = {}
        easy_target = int(total_questions * 0.33)
        hard_target = int(total_questions * 0.17)
        medium_target = total_questions - easy_target - hard_target

        easy_count = counts.get(DifficultyLevel.EASY, 0)
        medium_count = counts.get(DifficultyLevel.MEDIUM, 0)
        hard_count = counts.get(DifficultyLevel.HARD, 0)

        distribution["easy"] = min(easy_target, easy_count)
        distribution["hard"] = min(hard_target, hard_count)
        distribution["medium"] = min(medium_target, medium_count)

        # Fill remaining slots from other difficulties
        assigned = sum(distribution.values())
        if assigned < total_questions:
            remaining = total_questions - assigned
            for diff_key, diff_count in [("medium", medium_count), ("easy", easy_count), ("hard", hard_count)]:
                can_add = diff_count - distribution[diff_key]
                add = min(can_add, remaining)
                distribution[diff_key] += add
                remaining -= add
                if remaining <= 0:
                    break

        actual_total = sum(distribution.values())

        exam = MockExam(
            grade_level_id=grade_level_id,
            subject_id=subject_id,
            title=title,
            duration_minutes=duration_minutes,
            total_questions=actual_total,
            question_distribution=distribution,
            is_free=is_free,
            is_national=is_national,
            national_date=national_date,
            is_active=True,
            exam_type="qcm",
        )
        db.add(exam)
        await db.flush()
        return exam

    async def check_free_exam_available(
        self, db: AsyncSession, profile_id: UUID, subject_id: UUID
    ) -> bool:
        """Check if user already used their free exam for this subject."""
        result = await db.execute(
            select(func.count(ExamSession.id))
            .join(MockExam, ExamSession.mock_exam_id == MockExam.id)
            .where(
                ExamSession.profile_id == profile_id,
                MockExam.subject_id == subject_id,
                MockExam.is_free.is_(True),
            )
        )
        count = result.scalar() or 0
        return count == 0

    async def start_exam(
        self, db: AsyncSession, profile: Profile, mock_exam_id: UUID
    ) -> dict:
        """Create an ExamSession, check paywall, select questions."""
        # Load the mock exam
        result = await db.execute(
            select(MockExam).where(MockExam.id == mock_exam_id, MockExam.is_active.is_(True))
        )
        exam = result.scalar_one_or_none()
        if not exam:
            raise NotFoundException("MockExam", str(mock_exam_id))

        # Paywall check
        if not exam.is_free:
            tier = await subscription_service.get_active_tier(db, profile)
            if tier != PlanTier.PREMIUM:
                raise AppException(
                    status_code=403,
                    code="PREMIUM_REQUIRED",
                    message="Cet examen nécessite un abonnement Premium. Le premier examen par matière est gratuit !",
                )
        else:
            # Check if free exam already used for this subject
            free_available = await self.check_free_exam_available(db, profile.id, exam.subject_id)
            if not free_available:
                tier = await subscription_service.get_active_tier(db, profile)
                if tier != PlanTier.PREMIUM:
                    raise AppException(
                        status_code=403,
                        code="FREE_EXAM_USED",
                        message="Tu as déjà utilisé ton examen blanc gratuit pour cette matière. Passe en Premium pour continuer !",
                    )

        # CEP-type exam: load items and sub-questions
        if exam.exam_type == "cep":
            return await self._start_cep_exam(db, exam, profile)

        # QCM-type exam: select random questions
        questions = await self._select_questions(db, exam)

        # Create session
        now = datetime.now(timezone.utc)
        session = ExamSession(
            profile_id=profile.id,
            mock_exam_id=mock_exam_id,
            started_at=now,
            total_questions=len(questions),
            answers=[],
            status="in_progress",
        )
        db.add(session)
        await db.flush()

        # Build question list for response
        question_list = [
            {
                "question_id": str(q.id),
                "text": q.text,
                "question_type": q.question_type.value,
                "difficulty": q.difficulty.value,
                "choices": q.choices,
                "media_url": q.media_url,
                "time_limit_seconds": q.time_limit_seconds,
                "points": q.points,
            }
            for q in questions
        ]

        return {
            "session_id": str(session.id),
            "mock_exam_id": str(exam.id),
            "title": exam.title,
            "duration_minutes": exam.duration_minutes,
            "total_questions": len(questions),
            "started_at": session.started_at.isoformat(),
            "exam_type": "qcm",
            "questions": question_list,
        }

    async def _start_cep_exam(self, db: AsyncSession, exam: MockExam, profile: Profile) -> dict:
        """Start a CEP-format exam with items and sub-questions."""
        # Load items with sub-questions
        items_result = await db.execute(
            select(ExamItem)
            .where(ExamItem.mock_exam_id == exam.id)
            .options(selectinload(ExamItem.sub_questions))
            .order_by(ExamItem.order)
        )
        items = list(items_result.scalars().all())

        # Count total sub-questions
        total_sub_questions = sum(len(item.sub_questions) for item in items)

        now = datetime.now(timezone.utc)
        session = ExamSession(
            profile_id=profile.id,
            mock_exam_id=exam.id,
            started_at=now,
            total_questions=total_sub_questions,
            answers=[],
            status="in_progress",
        )
        db.add(session)
        await db.flush()

        # Build items list for response
        items_list = []
        for item in items:
            sub_questions = []
            for sq in sorted(item.sub_questions, key=lambda x: x.order):
                sub_questions.append({
                    "id": str(sq.id),
                    "sub_label": sq.sub_label,
                    "text": sq.text,
                    "question_type": sq.question_type,
                    "choices": sq.choices,
                    "depends_on_previous": sq.depends_on_previous,
                    "hint": sq.hint,
                    "points": sq.points,
                })
            items_list.append({
                "item_number": item.item_number,
                "domain": item.domain,
                "context_text": item.context_text,
                "points": item.points,
                "sub_questions": sub_questions,
            })

        return {
            "session_id": str(session.id),
            "mock_exam_id": str(exam.id),
            "title": exam.title,
            "duration_minutes": exam.duration_minutes,
            "total_questions": total_sub_questions,
            "started_at": session.started_at.isoformat(),
            "exam_type": "cep",
            "context_text": exam.context_text,
            "items": items_list,
        }

    async def _select_questions(self, db: AsyncSession, exam: MockExam) -> list[Question]:
        """Select questions for an exam based on the distribution."""
        distribution = exam.question_distribution or {"easy": 10, "medium": 15, "hard": 5}
        difficulty_map = {
            "easy": DifficultyLevel.EASY,
            "medium": DifficultyLevel.MEDIUM,
            "hard": DifficultyLevel.HARD,
        }

        selected: list[Question] = []

        for diff_key, count in distribution.items():
            if count <= 0:
                continue
            diff_enum = difficulty_map.get(diff_key)
            if not diff_enum:
                continue

            result = await db.execute(
                select(Question)
                .join(Skill, Question.skill_id == Skill.id)
                .join(Domain, Skill.domain_id == Domain.id)
                .where(
                    Domain.subject_id == exam.subject_id,
                    Question.difficulty == diff_enum,
                    Question.is_active.is_(True),
                )
            )
            candidates = list(result.scalars().all())
            if candidates:
                picked = random.sample(candidates, min(count, len(candidates)))
                selected.extend(picked)

        random.shuffle(selected)
        return selected

    async def submit_answer(
        self,
        db: AsyncSession,
        exam_session_id: UUID,
        profile_id: UUID,
        question_id: UUID | None = None,
        answer: object = None,
        time_seconds: int | None = None,
        # CEP-format fields
        item_number: int | None = None,
        sub_label: str | None = None,
    ) -> dict:
        """Record an answer in the JSONB array."""
        result = await db.execute(
            select(ExamSession).where(ExamSession.id == exam_session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundException("ExamSession", str(exam_session_id))
        if session.profile_id != profile_id:
            raise AppException(status_code=403, code="FORBIDDEN", message="Accès refusé à cette session.")
        if session.status != "in_progress":
            raise AppException(status_code=400, code="EXAM_ENDED", message="Cet examen est terminé.")

        existing_answers = session.answers or []

        # CEP-format answer
        if item_number is not None and sub_label is not None:
            return await self._submit_cep_answer(
                db, session, existing_answers, item_number, sub_label, answer, time_seconds
            )

        # QCM-format answer (legacy)
        if question_id is None:
            raise AppException(status_code=400, code="MISSING_FIELD", message="question_id est requis.")

        # Check if question already answered
        for a in existing_answers:
            if a.get("question_id") == str(question_id):
                return a  # Idempotent

        # Get the question and check answer
        q_result = await db.execute(select(Question).where(Question.id == question_id))
        question = q_result.scalar_one_or_none()
        if not question:
            raise NotFoundException("Question", str(question_id))

        is_correct = self._check_answer(question, answer)

        answer_entry = {
            "question_id": str(question_id),
            "answer": answer,
            "correct": is_correct,
            "time_seconds": time_seconds,
        }

        # Append to answers JSONB
        updated_answers = list(existing_answers)
        updated_answers.append(answer_entry)
        session.answers = updated_answers

        await db.flush()
        return answer_entry

    async def _submit_cep_answer(
        self,
        db: AsyncSession,
        session: ExamSession,
        existing_answers: list,
        item_number: int,
        sub_label: str,
        answer: object,
        time_seconds: int | None,
    ) -> dict:
        """Submit an answer for a CEP-format sub-question."""
        # Check if already answered (idempotent)
        for a in existing_answers:
            if a.get("item_number") == item_number and a.get("sub_label") == sub_label:
                return a

        # Find the sub-question
        exam = session.mock_exam
        if not exam:
            raise AppException(status_code=400, code="EXAM_NOT_FOUND", message="Examen introuvable.")

        sq_result = await db.execute(
            select(ExamSubQuestion)
            .join(ExamItem, ExamSubQuestion.exam_item_id == ExamItem.id)
            .where(
                ExamItem.mock_exam_id == exam.id,
                ExamItem.item_number == item_number,
                ExamSubQuestion.sub_label == sub_label,
            )
        )
        sub_question = sq_result.scalar_one_or_none()
        if not sub_question:
            raise NotFoundException("ExamSubQuestion", f"Item {item_number}, {sub_label}")

        # Check answer
        is_correct = self._check_cep_answer(sub_question, answer)
        points_earned = sub_question.points if is_correct else 0.0

        answer_entry = {
            "item_number": item_number,
            "sub_label": sub_label,
            "sub_question_id": str(sub_question.id),
            "answer": answer,
            "correct": is_correct,
            "points_earned": points_earned,
            "time_seconds": time_seconds,
        }

        updated_answers = list(existing_answers)
        updated_answers.append(answer_entry)
        session.answers = updated_answers

        await db.flush()
        return answer_entry

    async def complete_exam(
        self, db: AsyncSession, exam_session_id: UUID, profile_id: UUID
    ) -> dict:
        """Calculate score, predicted CEP score, update status."""
        result = await db.execute(
            select(ExamSession).where(ExamSession.id == exam_session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundException("ExamSession", str(exam_session_id))
        if session.profile_id != profile_id:
            raise AppException(status_code=403, code="FORBIDDEN", message="Accès refusé à cette session.")

        if session.status == "completed":
            return self._session_to_dict(session)  # Idempotent

        now = datetime.now(timezone.utc)
        answers = session.answers or []

        # Check if this is a CEP exam
        exam = session.mock_exam
        is_cep = exam and exam.exam_type == "cep"

        if is_cep:
            # CEP scoring: sum of points_earned, score out of 20
            total_points = sum(a.get("points_earned", 0) for a in answers)
            total_correct = sum(1 for a in answers if a.get("correct"))
            score = round(total_points, 1)  # This IS the /20 score
            predicted_cep = score
        else:
            # QCM scoring: percentage-based
            total_correct = sum(1 for a in answers if a.get("correct"))
            total_questions = session.total_questions
            score = round(total_correct / total_questions * 100, 1) if total_questions > 0 else 0.0
            predicted_cep = round(score / 100 * 20, 1)

        started = session.started_at
        if started and started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        time_spent = int((now - started).total_seconds()) if started else None

        session.completed_at = now
        session.time_spent_seconds = time_spent
        session.score = score
        session.total_correct = total_correct
        session.predicted_cep_score = predicted_cep
        session.status = "completed"

        await db.flush()
        return self._session_to_dict(session)

    async def get_exam_history(
        self, db: AsyncSession, profile_id: UUID
    ) -> list[dict]:
        """Return past exam sessions with scores."""
        result = await db.execute(
            select(ExamSession)
            .where(ExamSession.profile_id == profile_id)
            .order_by(ExamSession.created_at.desc())
        )
        sessions = result.scalars().all()
        return [self._session_to_dict(s) for s in sessions]

    async def get_exam_correction(
        self, db: AsyncSession, exam_session_id: UUID, profile_id: UUID
    ) -> dict:
        """Return detailed correction with links to relevant micro-lessons."""
        result = await db.execute(
            select(ExamSession).where(ExamSession.id == exam_session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundException("ExamSession", str(exam_session_id))
        if session.profile_id != profile_id:
            raise AppException(status_code=403, code="FORBIDDEN", message="Accès refusé à cette session.")

        exam = session.mock_exam
        is_cep = exam and exam.exam_type == "cep"

        if is_cep:
            return await self._get_cep_correction(db, session, exam)

        # QCM correction (legacy)
        answers = session.answers or []
        corrections = []

        for ans in answers:
            q_id = ans.get("question_id")
            if not q_id:
                continue

            q_result = await db.execute(select(Question).where(Question.id == q_id))
            question = q_result.scalar_one_or_none()
            if not question:
                continue

            # Find related micro-lesson
            lesson_info = None
            lesson_result = await db.execute(
                select(MicroLesson).where(
                    MicroLesson.skill_id == question.skill_id,
                    MicroLesson.is_active.is_(True),
                ).limit(1)
            )
            lesson = lesson_result.scalar_one_or_none()
            if lesson:
                lesson_info = {
                    "lesson_id": str(lesson.id),
                    "title": lesson.title,
                    "summary": lesson.summary,
                }

            corrections.append({
                "question_id": str(question.id),
                "text": question.text,
                "question_type": question.question_type.value,
                "difficulty": question.difficulty.value,
                "student_answer": ans.get("answer"),
                "correct_answer": question.correct_answer,
                "is_correct": ans.get("correct", False),
                "explanation": question.explanation,
                "time_seconds": ans.get("time_seconds"),
                "related_lesson": lesson_info,
            })

        return {
            **self._session_to_dict(session),
            "exam_type": "qcm",
            "corrections": corrections,
        }

    async def _get_cep_correction(self, db: AsyncSession, session: ExamSession, exam: MockExam) -> dict:
        """Return detailed correction for a CEP-format exam."""
        # Load items with sub-questions
        items_result = await db.execute(
            select(ExamItem)
            .where(ExamItem.mock_exam_id == exam.id)
            .options(selectinload(ExamItem.sub_questions))
            .order_by(ExamItem.order)
        )
        items = list(items_result.scalars().all())

        answers = session.answers or []
        # Build lookup: (item_number, sub_label) -> answer
        answer_lookup = {}
        for a in answers:
            key = (a.get("item_number"), a.get("sub_label"))
            answer_lookup[key] = a

        items_correction = []
        for item in items:
            sub_corrections = []
            for sq in sorted(item.sub_questions, key=lambda x: x.order):
                ans = answer_lookup.get((item.item_number, sq.sub_label), {})
                sub_corrections.append({
                    "sub_question_id": str(sq.id),
                    "sub_label": sq.sub_label,
                    "text": sq.text,
                    "question_type": sq.question_type,
                    "choices": sq.choices,
                    "student_answer": ans.get("answer"),
                    "correct_answer": sq.correct_answer,
                    "is_correct": ans.get("correct", False),
                    "points_earned": ans.get("points_earned", 0),
                    "points_possible": sq.points,
                    "explanation": sq.explanation,
                    "hint": sq.hint,
                    "depends_on_previous": sq.depends_on_previous,
                    "time_seconds": ans.get("time_seconds"),
                })
            items_correction.append({
                "item_number": item.item_number,
                "domain": item.domain,
                "context_text": item.context_text,
                "points": item.points,
                "sub_questions": sub_corrections,
            })

        return {
            **self._session_to_dict(session),
            "exam_type": "cep",
            "context_text": exam.context_text,
            "items": items_correction,
        }

    async def list_exams(
        self, db: AsyncSession, grade_level_id: UUID | None = None
    ) -> list[dict]:
        """List available mock exams, optionally filtered by grade."""
        query = select(MockExam).where(MockExam.is_active.is_(True))
        if grade_level_id:
            query = query.where(MockExam.grade_level_id == grade_level_id)
        query = query.order_by(MockExam.created_at.desc())

        result = await db.execute(query)
        exams = result.scalars().all()
        return [
            {
                "id": str(e.id),
                "title": e.title,
                "grade_level_id": str(e.grade_level_id),
                "subject_id": str(e.subject_id),
                "duration_minutes": e.duration_minutes,
                "total_questions": e.total_questions,
                "question_distribution": e.question_distribution,
                "is_free": e.is_free,
                "is_national": e.is_national,
                "national_date": e.national_date.isoformat() if e.national_date else None,
                "exam_type": e.exam_type or "qcm",
            }
            for e in exams
        ]

    def _check_answer(self, question: Question, answer: object) -> bool:
        correct = question.correct_answer
        if isinstance(correct, str) and isinstance(answer, str):
            return correct.strip().lower() == answer.strip().lower()
        return correct == answer

    def _check_cep_answer(self, sub_question: ExamSubQuestion, answer: object) -> bool:
        """Check answer for a CEP sub-question (more lenient matching)."""
        correct = sub_question.correct_answer
        if not isinstance(answer, str) or not isinstance(correct, str):
            return str(answer).strip() == str(correct).strip()

        answer_clean = answer.strip().lower().replace(" ", "").replace("\u00a0", "")
        correct_clean = correct.strip().lower().replace(" ", "").replace("\u00a0", "")

        # Exact match
        if answer_clean == correct_clean:
            return True

        # For numeric answers, compare as numbers
        try:
            return float(answer_clean.replace(",", ".")) == float(correct_clean.replace(",", "."))
        except (ValueError, TypeError):
            pass

        return False

    def _session_to_dict(self, session: ExamSession) -> dict:
        exam = session.mock_exam
        return {
            "session_id": str(session.id),
            "mock_exam_id": str(session.mock_exam_id),
            "profile_id": str(session.profile_id),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "time_spent_seconds": session.time_spent_seconds,
            "score": session.score,
            "total_correct": session.total_correct,
            "total_questions": session.total_questions,
            "predicted_cep_score": session.predicted_cep_score,
            "status": session.status,
            "exam_title": exam.title if exam else None,
            "mock_exam_title": exam.title if exam else None,
            "exam_type": exam.exam_type if exam else "qcm",
        }


exam_service = ExamService()
