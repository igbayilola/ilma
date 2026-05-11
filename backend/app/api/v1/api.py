from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    admin_content,
    analytics,
    auth,
    avatars,
    badges,
    content,
    diagnostic,
    exams,
    health,
    notifications,
    offline,
    profiles,
    progress,
    search,
    sessions,
    social,
    subscriptions,
    teacher,
)

api_router = APIRouter()

# Infrastructure
api_router.include_router(health.router)

# Auth
api_router.include_router(auth.router, prefix="/auth")

# Profiles (Netflix-style child profiles)
api_router.include_router(profiles.router)

# Avatars (local SVG generator — no external calls)
api_router.include_router(avatars.router)

# Content (public read)
api_router.include_router(content.router)

# Search
api_router.include_router(search.router)

# Sessions + exercises
api_router.include_router(sessions.router)

# Progress + stats
api_router.include_router(progress.router)

# Badges
api_router.include_router(badges.router)

# Offline sync
api_router.include_router(offline.router)

# Subscriptions + payments
api_router.include_router(subscriptions.router)

# Mock exams (Examens Blancs CEP)
api_router.include_router(exams.router)

# Diagnostic onboarding
api_router.include_router(diagnostic.router)

# Social (leaderboard + challenges)
api_router.include_router(social.router)

# Notifications
api_router.include_router(notifications.router)

# Analytics
api_router.include_router(analytics.router)

# Teacher (Espace Enseignant)
api_router.include_router(teacher.router)

# Admin
api_router.include_router(admin_content.router)
api_router.include_router(admin.router)
