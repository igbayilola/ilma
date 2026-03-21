"""Import all models so Alembic can discover them."""
from app.models.user import User, UserRole  # noqa
from app.models.profile import Profile  # noqa
from app.models.parent_student import ParentStudent  # noqa
from app.models.content import GradeLevel, Subject, Domain, Skill, MicroSkill, Question, QuestionComment, MicroLesson, ContentVersion  # noqa
from app.models.content import ContentStatus, DifficultyLevel, QuestionType  # noqa
from app.models.session import ExerciseSession, Attempt, SessionMode, SessionStatus  # noqa
from app.models.progress import Progress, MicroSkillProgress  # noqa
from app.models.badge import Badge, StudentBadge, BadgeCategory  # noqa
from app.models.subscription import Plan, Subscription, Payment  # noqa
from app.models.subscription import PlanTier, SubscriptionStatus, PaymentStatus, PaymentProvider  # noqa
from app.models.notification import Notification, NotificationType, NotificationChannel  # noqa
from app.models.offline import ContentPack  # noqa
from app.models.audit import AuditLog  # noqa
from app.models.otp import OTPCode  # noqa
from app.models.app_config import AppConfig, ValueType  # noqa
from app.models.social import WeeklyLeaderboard, Challenge, ChallengeStatus  # noqa
from app.models.content_audit import ContentTransition  # noqa
