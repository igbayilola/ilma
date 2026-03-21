---
name: Architecture decisions March 2026
description: Key technical decisions made for monitoring, analytics, sync, versioning, and feature prioritization
type: project
---

Decisions validated on 2026-03-18:

1. **Monitoring**: Sentry free + UptimeRobot free + in-database counters (no Grafana/Datadog yet)
   **Why:** Budget-constrained startup, free tiers sufficient until 1000+ DAU
   **How to apply:** Notification delivery tracked via status field on Notification model. Admin dashboard at /admin/analytics/notifications

2. **Sync cross-device (SEC.1)**: Guard at logout — warn if syncQueue has pending events, force sync if online, confirm if offline
   **Why:** Server already has all data; only risk is losing offline queue. Cheapest solution covering 95% of cases
   **How to apply:** Implemented in Shell.tsx logout buttons (sidebar + mobile drawer)

3. **Content versioning (SEC.2)**: Lightweight — `version` int field + `content_versions` table with JSON snapshots
   **Why:** Full git-like versioning is overkill for educational content. Snapshots + rollback is sufficient
   **How to apply:** Auto-snapshot on question/lesson update. Rollback endpoint restores from snapshot. UI in Editorial "Historique" tab

4. **Analytics (ANALYTICS.1-5)**: Endpoints maison, no external tracking service
   **Why:** All data already in DB (sessions, users, subscriptions, challenges). Zero external dependency
   **How to apply:** 4 admin endpoints: /engagement, /retention, /conversion, /virality. Frontend Analytics.tsx enhanced

5. **Next features priority**: P1-TWA (2 sem) → P2-2 Examens blancs CEP (3-4 sem) → EXPANSION-CM1 → P2-1 Espace enseignant (rentrée sept 2026)
   **Why:** TWA = quick Play Store presence. Examens blancs = killer monetization feature + CEP seasonality (June). Enseignant = B2B revenue for back-to-school

6. **Registration design**: Register always creates PARENT accounts (no STUDENT self-registration). Profiles are created separately
   **Why:** Architecture shifted to parent-first model where parents manage student profiles
