# SITOU — Plan 90 jours « Vers world-class »

> Généré le 2026-05-10 — Bundle issu de la synthèse des 7 audits (score moyen 4.8/10 → cible ≥ 7/10 à J+90).
> Hypothèses staffing : 2 BE, 2 FE, 1 PO/legal mi-temps, 1 contenu MEMP. Sprints 2 semaines.
> Démarrage W1 = lundi suivant la validation.

---

## Objectif stratégique

Sortir du diagnostic "non conforme APDP + apprentissage linéaire + canal support absent" pour atteindre les 4 marqueurs world-class qui manquent à Sitou face à IXL :

1. **Apprentissage adaptatif** (diagnostic + worked-solutions + détection à risque)
2. **Conformité légale** (APDP, DPO, consentement parental, droit à l'oubli)
3. **Premium-trigger pédagogique** (examens blancs CEP + score prédictif)
4. **Présence acquisition** (Play Store TWA + Mobile Money natif + Espace Enseignant V1-min)

Le reste (mascotte, RN, vidéo, Fon/Yoruba, pair-tutoring) reste **hors-périmètre 90j** — anticipé en track C.

---

## État au 2026-05-16 (S+1 / W1)

> Le plan original ci-dessous reste inchangé comme référence. Cette section reflète l'état réel après audit du 16 mai. Beaucoup d'items Sprint 1-4 étaient déjà livrés à la rédaction du plan (corrections P0/P1/P2 antérieures). Les itérations P3 1-10 ont fait du picking dans le roadmap + un pivot UX « compagnon-annuel » hors-périmètre.

### Sprint 1 — Débloquer le légal + fondations diag &nbsp;✅ **complet**
A1.1 Privacy/ToS · A1.2 consentement parental · A1.3 `DELETE /me/purge` · A1.4 Sentry gated (`SENTRY_ENABLED=true` requis sinon désactivé) · A1.5 avatars locaux · A1.6 modèles `DiagnosticAttempt` + `is_diagnostic` · A1.7 backups B2

### Sprint 2 — Diagnostic + worked solutions &nbsp;✅ ~95 %
A2.1 questions diag (via refonte CEP v2) · A2.2 endpoints (`diagnostic_service.py` + endpoint) · A2.3 onboarding 5 min (iter 7) · A2.4 Tiptap admin (iter 11, **commits du 16 mai** — stocké dans la colonne `explanation` existante, pas de migration `explanation_html` séparée) · A2.5 worked-solution + TTS (iter 6) · **❌ A2.6 backfill explications top-200** (contenu)

### Sprint 3 — Détection à risque + a11y parents &nbsp;⚠️ moitié
A3.1 règles risk_level low/medium/high (cron APScheduler 11:30 UTC, `tasks/notification_tasks.py:244 _send_parent_inactivity_alerts`) · A3.3 SMS contextualisés (partiel, pas d'A/B vs digest) · A3.4 TTS résumé parent (sur `pages/parent/Dashboard.tsx:82`) — **❌ A3.2 `GET /admin/students/at-risk` · ❌ A3.5 carte « Action suggérée » côté parent · ❌ A3.6 funnel at-risk → SMS → réactivation J+7**

### Sprint 4 — Examens CEP 1/2 &nbsp;✅ complet
A4.1 MockExam · A4.2 score prédictif (iter 6) · A4.3 contenu CEP (largement plus que 4 examens — annales 2008-2025 importées) · A4.4 timer 60min (`ExamPlayer.tsx` countdown + auto-soumission) · A4.5 paywall « 1 free per subject » (`api/v1/endpoints/exams.py:49`)

### Sprint 5 — Examens 2/2 + TWA Play Store &nbsp;⚠️ partiel
A5.1 correction détaillée (`ExamCorrection.tsx`) · A5.2 score CEP UI (iter 7) — **❌ A5.3 Bubblewrap · ❌ A5.4 assetlinks.json · ❌ A5.5 fiche Play Store · ❌ A5.6 onboarding install PWA**

### Sprint 6 — Mobile Money + Espace Enseignant &nbsp;⚠️ tiers
A6.3 plans micro 100/500 FCFA (iter 1) · A6.4 rôle TEACHER + modèles Classroom/Assignment · A6.5 dashboard prof (`pages/teacher/Dashboard.tsx`) — **❌ A6.1 MTN MoMo · ❌ A6.2 Moov Money · ❌ A6.6 code invitation 8 chars classe**

### Pivot non-roadmap — Compagnon-annuel (iter 8-10)
Non prévu au plan initial, motivé par la mémoire produit « UX quotidienne = leçon du jour, pas crammer CEP ». Livré :
- Refonte dashboard élève autour de la leçon du jour (iter 8 1/2 + 2/2)
- Champs `Skill.trimester` + `Skill.week_order` (cf. `backend/app/models/content.py:106-111`) — séquencement programme MEMP
- Éditeur admin trimestre/semaine + validation Pydantic (iter 9)
- Cleanup chaîne Alembic (iter 10)

**✅ Backfill `trimester`/`week_order`** : 219 skills CM2 actifs séquencés par heuristique (iter 19, `app/scripts/backfill_curriculum_sequencing.py` idempotent). T3 = domaines `preparation-cep-*`, T1+T2 = reste, ordre `(domain effectif, skill.order)`. Override d'ordre maths intégré (toutes les rows à `domain.order=1` en base). Le picker FE bascule désormais en mode calendrier.

**✅ Picker rattrapage** (iter 20) : la stratégie 1 du `pickCurrentLesson` (`CurrentLessonHero.tsx`) sert maintenant le plus ancien skill non-maîtrisé `(T,W) ≤ aujourd'hui` au lieu du plus proche de la semaine courante. Effet : un élève neuf en T2.W5 voit T1.W1 d'abord (compagnon-annuel), pas T2.W5. Drapeau `isCatchUp` exposé à la hero pour basculer le label « Cette semaine en CM2 » → « À rattraper ».

**✅ Cleanup `Domain.order` maths** (iter 21) : les 7 domaines maths CM2 avaient tous `order=1` en base (donnée historique) — l'override hardcodé du backfill iter 19 contournait. Script `app/scripts/cleanup_domain_order.py` idempotent réordonne (numération→1, opérations→2, …, preparation-au-cep→7), et l'override est retiré du backfill (devenu redondant). Bénéficie aussi à l'admin UI et à l'explorateur FE (fallback picker correct hors période scolaire).

### Trous résiduels par ROI

| Rang | Item | Sprint d'origine | Charge | Bloque |
|------|------|------------------|--------|--------|
| 1 | A3.2 + A3.5 + A3.6 boucle at-risk admin/parent/funnel | 3 | BE+FE 3j | Boucle pédagogique ouverte côté admin |
| 2 | A5.3-A5.6 TWA Play Store | 5 | DevOps 3-4j | KPI ≥ 500 installs J+90 |
| 3 | A6.1 + A6.2 MTN/Moov Money | 6 | BE ~5j | Monétisation locale |
| 4 | A6.6 code invitation classe | 6 | BE+FE 1-2j | Usage réel du dashboard prof |
| 5 | ~~Backfill curriculum trimestre/semaine~~ | pivot | ~~contenu~~ | ✅ iter 19 |
| 6 | A2.6 backfill explications top-200 | 2 | contenu | KPI ≥ 60 % worked-solution |

> **Itération 19 livrée** (16 mai) : item #5 — backfill curriculum (script + tests + impact FE picker calendar-aware).

---

## Track A — Engineering (sprints 2 semaines)

### Sprint 1 (W1-W2) — Débloquer le légal + fondations diagnostic
| # | Livrable | Owner | DoD |
|---|----------|-------|-----|
| A1.1 | `PRIVACY_POLICY.md`, `TERMS_OF_SERVICE.md`, page `/legal/privacy` enrichie + `/legal/terms` | Legal + FE | Liens dans footer + onboarding, FR simple |
| A1.2 | Checkbox consentement parental + confirm OTP SMS lors de la création profil enfant | BE + FE | Champ `parental_consent_at` en DB, blocage si absent |
| A1.3 | `DELETE /me/purge` avec confirmation OTP — hard delete + grace 30j | BE | Test E2E suppression complète, audit log conservé anonymisé |
| A1.4 | Sentry EU → GlitchTip self-host (ou désactiver si retard) | DevOps | Aucun DSN externe en prod |
| A1.5 | DiceBear → générateur SVG local `avatar_service.py` | BE + FE | 0 appel sortant pour avatar (vérifié via netstat staging) |
| A1.6 | Modèle `DiagnosticTest` + `DiagnosticAttempt` + tiers `RENFORCEMENT/CM2/EXCELLENCE` | BE | Migration Alembic appliquée |
| A1.7 | Backups off-site Backblaze B2 + test restore mensuel scripté | DevOps | Cron + alerte en cas d'échec, runbook restore |

### Sprint 2 (W3-W4) — Diagnostic d'entrée + worked solutions
| # | Livrable | Owner | DoD |
|---|----------|-------|-----|
| A2.1 | 45 questions diagnostic (15 × 3 tiers × Maths + 15 × 3 tiers × Français) | Contenu | PUBLISHED en DB, taggées `is_diagnostic=true` |
| A2.2 | Endpoint `POST /diagnostic/start` + `POST /diagnostic/submit` → tier assigné au profil | BE | Tests unit + intégration |
| A2.3 | Flow onboarding "Mini-test 5 min" avec mascotte (placeholder Ilo) | FE | Skip possible, relance J+1 si skip |
| A2.4 | Champ `explanation_html` sur `Question` + éditeur admin (Tiptap) | BE + FE | Migration + Kanban admin enrichi |
| A2.5 | Affichage worked-solution après mauvaise réponse | FE | A11y testé clavier + TTS |
| A2.6 | Backfill explications sur top-200 questions les plus tentées | Contenu | Reporting `% questions avec explication` |

### Sprint 3 (W5-W6) — Détection à risque + accessibilité parents
| # | Livrable | Owner | DoD |
|---|----------|-------|-----|
| A3.1 | `risk_detection.py` — règles : absence 72h / Δ-20 SmartScore 7j / 3 dropouts | BE | Cron quotidien 9h UTC via APScheduler |
| A3.2 | `GET /admin/students/at-risk` + dashboard admin + filtre par classe | BE + FE | Liste avec raison + action proposée |
| A3.3 | SMS contextualisés ("X n'a pas étudié depuis 3 jours, propose 10 min ?") | BE | Templates A/B vs digest générique |
| A3.4 | Bouton "🔊 Écouter mon résumé" (Web Speech API) sur dashboard parent | FE | FR-FR, lecture entière du health summary |
| A3.5 | Carte "Action suggérée" sur `ChildHealthCard` | FE | Lien deeplink vers exercice |
| A3.6 | Métrique funnel : at-risk détecté → SMS envoyé → réactivé J+7 | BE | Endpoint analytics + dashboard admin |

### Sprint 4 (W7-W8) — Examens blancs CEP + score prédictif (1/2)
| # | Livrable | Owner | DoD |
|---|----------|-------|-----|
| A4.1 | `MockExam` complet (modèle existe déjà, finir service génération) | BE | Migration + tests |
| A4.2 | Algorithme score prédictif CEP : régression sur SmartScore × couverture | BE | Calibré sur dataset annales 2008-2017 |
| A4.3 | 4 examens blancs (1 par matière, ~40 questions chacun) | Contenu | PUBLISHED, 1 gratuit par matière |
| A4.4 | UI mode examen — timer 60min, pas d'aide, pas de brouillon | FE | Tests E2E timer expire → soumission auto |
| A4.5 | Gating Premium : 1 examen gratuit puis paywall | BE + FE | Tracker conversion |

### Sprint 5 (W9-W10) — Examens blancs (2/2) + TWA Play Store
| # | Livrable | Owner | DoD |
|---|----------|-------|-----|
| A5.1 | Correction détaillée avec liens vers micro-leçons par compétence faible | FE | Renvoi automatique sur skills < 60% |
| A5.2 | Affichage "Avec ce niveau → X/20 au CEP" + tooltip explicatif | FE | UX testée avec 3 parents |
| A5.3 | Bubblewrap config + signing keystore + AAB | DevOps | APK testé Android Go |
| A5.4 | `assetlinks.json` Digital Asset Links sur le domaine | DevOps | Vérifié via Google tool |
| A5.5 | Fiche Play Store FR (icône, 8 screenshots, description) | PO + Design | Soumis pour review |
| A5.6 | Onboarding "Installer l'app" pour les non-TWA | FE | A/B install rate |

### Sprint 6 (W11-W12) — Mobile Money natif + Espace Enseignant V1-min
| # | Livrable | Owner | DoD |
|---|----------|-------|-----|
| A6.1 | `MTNMoMoProvider` (sandbox + prod) | BE | Transaction sandbox réussie |
| A6.2 | `MoovMoneyProvider` | BE | Transaction sandbox réussie |
| A6.3 | Plans micro : Pass jour 100 FCFA / Pass semaine 500 FCFA | BE + FE | Affichés en paywall |
| A6.4 | Rôle `TEACHER` + RBAC + modèles `Classroom` / `Assignment` (existent déjà, à activer/finir) | BE | Migration + permissions |
| A6.5 | Dashboard enseignant ultra-léger (3 KPIs + 🟢🟡🔴 par élève) | FE | < 10KB payload, charge en 3s sur 3G |
| A6.6 | Code invitation 8 caractères + flow rejoindre une classe | BE + FE | E2E élève → classe |

### Sprint 7 (W13) — Buffer + finition + lancement TWA
- Stabilisation bugs des 6 sprints
- TWA en staged rollout 5% → 50% → 100%
- Communication MEMP / Plan International (préparée en track B)

---

## Track B — Ops / Legal / Contenu (parallèle, continu)

| Période | Action | Owner |
|---------|--------|-------|
| W1-W2 | Nommer DPO interne + email `dpo@sitou.bj` | Direction |
| W2-W4 | Déclaration APDP (registre des traitements) | DPO |
| W2-W6 | WhatsApp Business API setup (Twilio) + chatbot menu 4 options | Ops |
| W3-W6 | 45 questions diagnostic rédigées + relues MEMP | Contenu |
| W5-W10 | 160 questions examens blancs (40 × 4 matières) | Contenu |
| W6-W8 | Backfill explications top-200 questions | Contenu |
| W4-W12 | Runbooks : incident, restore DB, breach, vendor-down | Tech Lead |
| W8-W12 | Pair-programming systématique sur features critiques (réduire bus factor) | Équipe |

---

## Track C — Hors-périmètre 90 jours

À ne **pas** tenter dans les 90 jours, mais à anticiper :

- App React Native (P1-RN, 8-12 sem) — démarre M4
- Mascotte Ilo design + animation (P1-5, 3-4 sem) — démarre M4
- Vidéo micro-leçons (P1-VIDEO) — démarre M5
- Multilinguisme Fon/Yoruba — démarre M4 (commencer par 20 phrases auth)
- Pair tutoring / Web Bluetooth — backlog M6+
- Marketplace contenu enseignants — M9+
- Expansion Côte d'Ivoire — M12+

---

## Critères de succès J+90

| KPI | Baseline | Cible J+90 |
|-----|----------|------------|
| Conformité APDP | ❌ | ✅ déclaré, DPO nommé, politique publiée |
| Élèves diagnostiqués à l'inscription | 0% | ≥ 70% |
| Questions avec worked-solution | < 5% | ≥ 60% (top 200 + nouvelles) |
| Élèves at-risk détectés → SMS envoyés | 0 | ≥ 85% |
| Taux de réactivation post-SMS at-risk J+7 | N/A | ≥ 25% |
| Examens blancs joués | 0 | ≥ 1 / élève actif |
| Conversion paywall via score prédictif CEP | N/A | mesurée, baseline établie |
| Présence Play Store TWA | ❌ | ✅ live, ≥ 500 installs |
| Plans Mobile Money natifs | 0 | 4 (MTN + Moov × jour/semaine) |
| Enseignants avec ≥ 1 classe active | 0 | ≥ 20 |
| Score moyen audits (re-run) | 4.8/10 | ≥ 7/10 |

---

## Risques & callouts

- **Sprint 4-5 dépend du contenu** — si les 160 questions d'examens blancs ne sont pas prêtes W7, le sprint glisse. Démarrer la rédaction W3.
- **Play Store review** prend 7-14 jours imprévisibles → soumettre fin W10, pas W12.
- **MTN MoMo sandbox → prod** demande validation entreprise (KYC). Démarrer la paperasse W1, pas W11.
- **Bus factor reste 1-2** à J+90 — pair-programming insuffisant. Mettre en parallèle escrow contractuel ou recrutement.
- **Espace Enseignant V1-min** est volontairement réduit — le vrai produit B2B (assignments, alertes profs, export PDF) est M4-M5.
- **GlitchTip self-host** ajoute charge ops. Si retard, désactiver Sentry temporairement plutôt que reporter A1.4.

---

## Annexe — Sprint 1 décomposé (fichiers à toucher)

> Démarrage immédiat. Tickets prêts à assigner. Tous les chemins sont relatifs à `/opt/sitou/`.

### A1.1 — Politique confidentialité + ToS (Legal + FE, 2j)

**Nouveaux fichiers**
- `docs/legal/PRIVACY_POLICY.md` — politique simple FR (cf. template `audit_conformite.md`)
- `docs/legal/TERMS_OF_SERVICE.md` — CGU FR
- `docs/legal/COOKIE_POLICY.md` — cookies essentiels uniquement
- `docs/legal/DPO_CONTACT.md` — coordonnées + APDP
- `docs/legal/DATA_RETENTION.md` — durées de conservation

**Fichiers à modifier**
- `frontend/pages/legal/Privacy.tsx` — remplacer placeholder par contenu de `PRIVACY_POLICY.md` (rendu via `react-markdown` déjà dans node_modules ?)
- `frontend/pages/legal/Terms.tsx` — créer (jumeau de Privacy.tsx)
- `frontend/App.tsx` — ajouter route `/legal/terms`
- `frontend/components/Footer.tsx` (ou équivalent) — liens "Confidentialité" / "CGU" / "DPO"

### A1.2 — Consentement parental (BE + FE, 3j)

**Migration Alembic** — `backend/app/db/migrations/versions/<new>_add_parental_consent.py`
```python
op.add_column('profiles', sa.Column('parental_consent_at', sa.DateTime(timezone=True), nullable=True))
op.add_column('profiles', sa.Column('parental_consent_otp_hash', sa.String(128), nullable=True))
op.add_column('users', sa.Column('is_legal_guardian', sa.Boolean, server_default='false', nullable=False))
```

**Backend**
- `backend/app/models/profile.py` — ajouter `parental_consent_at`, `parental_consent_otp_hash`
- `backend/app/models/user.py` — ajouter `is_legal_guardian`
- `backend/app/schemas/profile.py` (créer si absent) ou existant — exposer `requires_parental_consent`
- `backend/app/services/profile_service.py:create_profile` — exiger consentement validé pour profil mineur (< 18 ans), bloquer sinon avec `HTTPException(403)`
- `backend/app/api/v1/endpoints/profiles.py` — ajouter `POST /profiles/{id}/parental-consent/request` (envoie OTP) + `POST /profiles/{id}/parental-consent/verify`

**Frontend**
- `frontend/pages/auth/ProfileCreate.tsx` — ajouter checkbox "Je certifie être le représentant légal" + flow OTP
- `frontend/services/profileService.ts` — méthodes `requestParentalConsent`, `verifyParentalConsent`

### A1.3 — Right-to-erasure `DELETE /me/purge` (BE, 2j)

**Backend**
- `backend/app/services/profile_service.py` — nouvelle méthode `purge_user(user_id)` :
  1. Send OTP confirmation
  2. Mark `users.purge_requested_at = now()`, `users.purge_scheduled_at = now() + 30 days`
  3. Cron quotidien purge ce qui est dû
- `backend/app/api/v1/endpoints/profiles.py` (ou `auth.py`) — `POST /me/purge/request` + `POST /me/purge/confirm`
- `backend/app/tasks/notification_tasks.py` (ou nouveau `purge_tasks.py`) — cron daily purge
- Migration : `users.purge_requested_at`, `users.purge_scheduled_at`

**Test E2E**
- `backend/tests/test_purge.py` — flow request → OTP → confirm → +30j → purge complet (profile, sessions, attempts, badges)
- Conserver `audit_logs` anonymisés (NULL sur user_id, hash conservé pour stats)

### A1.4 — Désactiver Sentry EU (DevOps, 0.5j)

**Choix rapide :** désactiver d'abord, migrer GlitchTip en Sprint 2.

- `backend/app/main.py:22-30` — wrapper l'init `sentry_sdk.init(...)` derrière `if settings.SENTRY_DSN and settings.SENTRY_ENABLED:`
- `frontend/services/telemetry.ts:17-30` — idem côté frontend
- `.env.production` (backend + frontend) — vider `SENTRY_DSN` ou `SENTRY_ENABLED=false`

**Self-host GlitchTip (Sprint 2 si capacité)** — `docker-compose.yml` ajouter service `glitchtip` + `redis-glitchtip` + `postgres-glitchtip`. Coût RAM ~512Mo.

### A1.5 — Avatar local (BE + FE, 1j)

**Backend** — créer `backend/app/services/avatar_service.py`
```python
def generate_local_svg(seed: str, size: int = 128) -> str:
    """SVG déterministe à partir du seed, palette béninoise, < 2KB."""
    # 1. hash seed → couleurs (chevelure, peau, fond) parmi palettes prédéfinies
    # 2. compose <svg> minimaliste (cercle visage + 2 yeux + bouche)
    # 3. retourne string SVG
```

**Endpoint** — ajouter dans `backend/app/api/v1/endpoints/profiles.py` :
- `GET /avatars/{seed}.svg` → renvoie SVG avec `Cache-Control: public, max-age=31536000, immutable`

**Backend — remplacer DiceBear**
- `backend/app/api/v1/endpoints/auth.py:44` — `f"/api/v1/avatars/{str(p.id)[:8]}.svg"`
- `backend/app/services/profile_service.py:146` — idem

**Frontend — remplacer DiceBear**
- `frontend/pages/Dashboard.tsx:290`
- `frontend/pages/auth/ProfileCreate.tsx:33,117`
- `frontend/pages/subscription/Plans.tsx:146`
- `frontend/services/authService.ts:23,42`
- `frontend/services/profileService.ts:8`
- `frontend/services/parentService.ts:35`

Helper centralisé pour éviter les répétitions : créer `frontend/utils/avatar.ts` exportant `avatarUrl(seed: string): string` puis le réutiliser partout.

### A1.6 — Modèle DiagnosticTest (BE, 2j)

**Migration Alembic** — `backend/app/db/migrations/versions/<new>_add_diagnostic.py`
```python
op.create_table('diagnostic_attempts',
    sa.Column('id', UUID, primary_key=True),
    sa.Column('profile_id', UUID, sa.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False),
    sa.Column('subject', sa.String(32), nullable=False),  # 'maths' | 'francais'
    sa.Column('answers', JSONB, nullable=False),  # [{question_id, correct, time_ms}]
    sa.Column('assigned_tier', sa.String(16), nullable=False),  # 'RENFORCEMENT' | 'CM2' | 'EXCELLENCE'
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
)
op.add_column('profiles', sa.Column('difficulty_tier', sa.String(16), nullable=True))
op.add_column('questions', sa.Column('is_diagnostic', sa.Boolean, server_default='false', nullable=False, index=True))
```

**Modèles**
- `backend/app/models/progress.py` (ou nouveau `diagnostic.py`) — classe `DiagnosticAttempt`
- `backend/app/models/profile.py` — champ `difficulty_tier`
- `backend/app/models/content.py` — champ `is_diagnostic` sur `Question`

> **Sprint 2 prendra le relais** pour les endpoints + UI + 45 questions contenu.

### A1.7 — Backups off-site (DevOps, 1.5j)

**Fichiers à modifier**
- `deploy/backup.sh` — ajouter étape `b2 sync /var/backups/sitou b2://sitou-backups/$(hostname)/`
- `deploy/backup.sh` — ajouter alerte SMS DPO en cas d'échec (`twilio-cli` ou curl direct)
- Nouveau `deploy/restore_test.sh` — script mensuel : restore dump dans container `postgres-test`, lance `\dt` + `SELECT count(*) FROM users;`, compare aux baselines, alerte si écart > 5%
- Cron `/etc/cron.d/sitou-backup` — ajouter ligne mensuelle restore_test
- Nouveau `docs/runbooks/BACKUP_RESTORE.md` — procédure manuelle step-by-step

**Compte Backblaze B2** — créer + récupérer `B2_KEY_ID` / `B2_APP_KEY`, stocker en secret VPS.

---

### Sortie attendue de Sprint 1

À la fin W2, démo possible :
1. Création profil enfant → bloquée sans consentement parental
2. OTP envoyé au parent → consentement validé → profil créé
3. Avatar SVG local affiché (pas d'appel `dicebear.com`)
4. Pages `/legal/privacy`, `/legal/terms` accessibles depuis footer
5. `DELETE /me/purge` fonctionne, audit log conservé anonymisé
6. Backup B2 visible dans la console Backblaze
7. Schéma DB prêt pour Sprint 2 (DiagnosticAttempt, difficulty_tier)
8. Sentry désactivé en prod (vérifié via DevTools Network onglet)
