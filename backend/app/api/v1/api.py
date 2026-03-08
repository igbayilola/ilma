from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    admin_content,
    auth,
    badges,
    content,
    health,
    notifications,
    offline,
    profiles,
    progress,
    sessions,
    subscriptions,
)

api_router = APIRouter()

# Infrastructure
api_router.include_router(health.router)

# Auth
api_router.include_router(auth.router, prefix="/auth")

# Profiles (Netflix-style child profiles)
api_router.include_router(profiles.router)

# Content (public read)
api_router.include_router(content.router)

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

# Notifications
api_router.include_router(notifications.router)

# Admin
api_router.include_router(admin_content.router)
api_router.include_router(admin.router)
