# ILMA — Plan de Mise en Oeuvre des Recommandations d'Audit

> Généré le 2026-03-11 — Basé sur le Rapport de Consultation Produit Senior
> Légende : [ ] À faire | [~] En cours | [x] Terminé | [-] Abandonné

---

## PHASE 1 : QUICK WINS (Mois 1-2 — Mars-Avril 2026)

### QW-1 : Hook de Rappel Quotidien sur le Dashboard (2j)
> Fichiers : `frontend/pages/Dashboard.tsx`, `frontend/store.ts`

- [x] QW-1.1 : Exposer le streak courant dans le store (authStore ou progressStore)
- [x] QW-1.2 : Calculer le temps restant avant minuit (countdown)
- [x] QW-1.3 : Remplacer la section "Reprendre" par le composant Streak avec avertissement visuel
- [x] QW-1.4 : Afficher variante "Commence une nouvelle série" si streak = 0
- [x] QW-1.5 : Tester les 3 états (streak actif, streak en danger, streak = 0)

### QW-2 : Célébration de Fin d'Exercice Enrichie (1j)
> Fichier : `frontend/pages/student/ExercisePlayer.tsx`

- [x] QW-2.1 : Récupérer le SmartScore avant/après depuis la réponse de `completeSession()`
- [x] QW-2.2 : Afficher le delta de progression (ex: "45 → 62 (+17)") avec barre de progression
- [x] QW-2.3 : Afficher le prochain objectif ("Encore X points pour maîtriser cette compétence")
- [x] QW-2.4 : Ajouter animation de progression (barre qui se remplit)

### QW-3 : Partage de Résultat via Web Share API (0.5j)
> Fichier : `frontend/pages/student/ExercisePlayer.tsx`

- [x] QW-3.1 : Ajouter bouton "Partager mon score" sur l'écran SUMMARY
- [x] QW-3.2 : Implémenter `navigator.share()` avec fallback (copier dans le presse-papier)
- [x] QW-3.3 : Texte de partage localisé français avec nom de la compétence et score
- [x] QW-3.4 : Tracker les événements de partage (telemetry)

---

### P0-1 : Notifications Automatiques Réelles (2-3 sem.)
> Impact : Rétention D7 +30-50%

#### Backend — Infrastructure notifications
- [x] P0-1.1 : Installer et configurer APScheduler (léger, intégré au process FastAPI) + lifespan
- [x] P0-1.2 : Créer le module `backend/app/tasks/` avec scheduler + notification_tasks
- [x] P0-1.3 : Implémenter le provider SMS réel (Twilio) avec fallback mock automatique
- [x] P0-1.4 : Implémenter le provider Push PWA réel (Web Push avec VAPID / pywebpush)
- [x] P0-1.5 : Ajouter la gestion des préférences de notification par utilisateur (opt-in/out, horaires)

#### Backend — Triggers automatiques (CRON jobs)
- [x] P0-1.6 : CRON 16h UTC : "Ton défi du jour t'attend !" (si pas joué aujourd'hui)
- [x] P0-1.7 : CRON 10h UTC J+2 inactivité : "Tu vas perdre ta série de X jours !"
- [x] P0-1.8 : Trigger immédiat : notification badge gagné (dans badge_service.award_badges)
- [x] P0-1.9 : CRON dimanche 17h UTC : digest parent SMS (résumé semaine de chaque enfant)
- [x] P0-1.10 : Throttling / rate-limiting pour éviter le spam (max 2 notifs/jour/user via count_today)

#### Frontend — Réception notifications
- [x] P0-1.11 : Implémenter l'inscription push (pushService.ts + bouton dans Settings)
- [x] P0-1.12 : Gérer la réception de notification en foreground (in-app toast via useForegroundNotifications hook)
- [x] P0-1.13 : Gérer le click sur notification (deeplink via sw.js notificationclick handler)
- [x] P0-1.14 : Page de paramètres notifications (toggles par type + push on/off dans Settings)

#### Validation
- [x] P0-1.15 : Tests unitaires des triggers CRON
- [ ] P0-1.16 : Test E2E : inscription push → réception notification → navigation
- [x] P0-1.17 : Monitoring : taux de livraison SMS, taux d'ouverture push

---

### P1-3 : Dashboard Parent "Santé Scolaire" (1-2 sem.)
> Impact : Rétention parents +35%, Conversion premium +20%

#### Backend
- [x] P1-3.1 : Endpoint `GET /api/v1/students/health-summary` retournant pour chaque enfant : score moyen, streak, temps semaine, delta vs semaine précédente, compétence en difficulté
- [x] P1-3.2 : Logique de calcul du statut santé (Vert ≥70% + actif / Orange 40-69% ou inactif 2-3j / Rouge <40% ou inactif 4j+)
- [x] P1-3.3 : Générer les conseils contextuels positifs ("Parler de : les fractions")

#### Frontend
- [x] P1-3.4 : Nouveau composant `ChildHealthCard` avec indicateur couleur (vert/orange/rouge)
- [x] P1-3.5 : Afficher streak, temps semaine avec delta, barre de progression
- [x] P1-3.6 : Afficher le conseil contextuel positif (tonalité encourageante, jamais négative)
- [x] P1-3.7 : Bouton "Voir le détail" → page existante du détail enfant
- [x] P1-3.8 : Bouton "Digest SMS" → déclencher l'envoi du résumé par SMS
- [x] P1-3.9 : Remplacer le dashboard parent actuel par la nouvelle vue "Santé Scolaire"

---

### P1-4 : Système de Badges Extensible — 30+ badges (1 sem.)
> Impact : Rétention D30 +15%

#### Backend
- [x] P1-4.1 : Créer un modèle `BadgeRule` en base (ou config JSON dans AppConfig) : `{id, code, category, name_fr, description_fr, icon, condition_type, condition_params}`
- [x] P1-4.2 : Migrer les 5 règles hardcodées vers le nouveau système
- [x] P1-4.3 : Ajouter les ~25 nouvelles règles de badges par catégorie :
  - [x] Régularité : série 7j, série 30j, série 100j, lève-tôt (avant 8h)
  - [x] Maîtrise : score 100%, 5/10 skills maîtrisés, domaine complet, matière complète, zéro erreur (10 q.)
  - [x] Exploration : toutes matières, premier examen blanc, 100 questions, brouillon 10x, micro-leçon 20x
  - [x] CEP : examen blanc 80%+, examen blanc 90%+, toutes matières CEP, prêt pour le CEP
  - [x] Social : premier défi envoyé, 5 défis gagnés, top 3 classement, série d'invitations
- [x] P1-4.4 : Moteur d'évaluation des règles déclenché à chaque `session.complete`
- [x] P1-4.5 : Tests unitaires du moteur de badges avec chaque type de condition

#### Frontend
- [x] P1-4.6 : Page "Mes badges" enrichie avec catégories et badges verrouillés visibles (silhouettes)
- [x] P1-4.7 : Animation de déblocage de badge (modal célébration)
- [x] P1-4.8 : Indicateur de progression vers le prochain badge ("3/7 jours pour Série 7j")

---

### P1-TWA : TWA Android — Présence Play Store Immédiate (2 sem.)
> Impact : Acquisition via Play Store

- [ ] P1-TWA.1 : Configurer le projet TWA (Bubblewrap ou PWABuilder)
- [ ] P1-TWA.2 : Générer les assets Play Store (icône, screenshots, description fr)
- [ ] P1-TWA.3 : Configurer Digital Asset Links (assetlinks.json sur le domaine)
- [ ] P1-TWA.4 : Build APK/AAB signé
- [ ] P1-TWA.5 : Soumettre sur Google Play Console (fiche store en français)
- [ ] P1-TWA.6 : Tester sur Android Go (device réel ou émulateur low-end)

---

## PHASE 2 : ENGAGEMENT (Mois 3-5 — Mai-Juillet 2026)

### P0-2 : Téléchargement Offline Granulaire par Compétence (4-5 sem.)
> Impact : Acquisition zones rurales +40% marché adressable

#### Backend
- [x] P0-2.1 : Endpoint `GET /api/v1/offline/packs/skills/{skill_id}` — pack micro par compétence (JSON)
- [x] P0-2.2 : Service `PackBuilder` : génère JSON (questions + leçons + micro-skills) avec hash d'intégrité MD5
- [x] P0-2.3 : Stockage des packs sur S3/Minio avec cache CDN edge
- [x] P0-2.4 : Endpoint `GET /api/v1/offline/packs/delta?since={timestamp}` — delta sync
- [x] P0-2.5 : Activer gzip sur toutes les réponses API (GZipMiddleware, min_size=500)
- [x] P0-2.6 : Endpoint `GET /api/v1/offline/packs/skills` pour lister les packs disponibles avec taille et version

#### Frontend — Service Worker
- [x] P0-2.7 : Nouveau `skillOfflineManager.ts` : packs par compétence via IndexedDB (store skillPacks + skillPackData)
- [x] P0-2.8 : `prefetchNextSkills()` : téléchargement automatique des N prochaines compétences
- [x] P0-2.9 : Prefetch intelligent : Network Information API (WiFi/4G only) avant prefetch
- [x] P0-2.10 : Delta sync : `checkForUpdates()` via `/offline/packs/delta?since=`
- [x] P0-2.11 : UI de gestion du stockage offline (voir/supprimer les skill packs, espace utilisé)
- [x] P0-2.12 : Indicateur de téléchargement par compétence (progression, retry)

#### Validation
- [x] P0-2.13 : Test E2E : téléchargement pack skill → mode avion → exercice complet → retour online → sync
- [ ] P0-2.14 : Test de performance : téléchargement sur connexion 2G simulée (< 30s pour un pack micro)
- [x] P0-2.15 : Test LRU cleanup : vérifier que l'espace est bien libéré quand le device est plein

---

### P0-3 : Social Léger — Classement Hebdo + Défis Amis (4-6 sem.)
> Impact : Rétention D30 +20%, Acquisition organique +15%

#### Backend — Classement
- [x] P0-3.1 : Table `weekly_leaderboard` (profile_id, week_iso, xp_earned, pseudonym)
- [x] P0-3.2 : Bibliothèque de pseudonymes auto-générés (adjectif + animal, ~600 combinaisons)
- [x] P0-3.3 : Le classement se renouvelle automatiquement par semaine ISO (pas de reset nécessaire)
- [x] P0-3.4 : Incrémenter `xp_earned` à chaque session complétée (à brancher dans session_service)
- [x] P0-3.5 : Endpoint `GET /api/v1/social/leaderboard/weekly` (top 20 + position du user)
- [x] P0-3.6 : Endpoint `GET /api/v1/social/leaderboard/weekly/history` (classements passés)

#### Backend — Défis
- [x] P0-3.7 : Table `challenges` (id, challenger_id, challenged_id, skill_id, status, scores, expires_at)
- [x] P0-3.8 : Endpoint `POST /api/v1/social/challenges` (créer un défi)
- [x] P0-3.9 : Endpoint `POST /api/v1/social/challenges/{id}/accept` (accepter un défi)
- [x] P0-3.10 : Endpoint `POST /api/v1/social/challenges/{id}/complete` (soumettre le score)
- [x] P0-3.11 : CRON : expirer les défis non-acceptés après 24h (hourly job)
- [x] P0-3.12 : Notification push au challengé quand un défi est reçu
- [x] P0-3.13 : Notification push au challenger quand le résultat est disponible

#### Frontend
- [x] P0-3.14 : Nouvel onglet "Classement" dans la bottom nav
- [x] P0-3.15 : Page classement hebdo (top 20 + position user mise en évidence)
- [x] P0-3.16 : Bouton "Défier un ami" → Web Share API avec lien deeplink
- [x] P0-3.17 : Page de défi (accepter, jouer, voir le résultat comparé)
- [x] P0-3.18 : Notification in-app pour les défis reçus
- [x] P0-3.19 : Historique des défis (tab "Défis" avec statuts)

#### Sécurité / Modération
- [x] P0-3.20 : Pseudonymes obligatoires (pas de vrais noms dans le classement)
- [x] P0-3.21 : Pas de profil public, pas de chat, classement positif uniquement (XP gagnés)
- [x] P0-3.22 : Rate-limiting sur la création de défis (max 5/jour)

---

### P1-5 : Mascotte Ilo Interactive (3-4 sem.)
> Impact : Engagement émotionnel, différenciation brand

#### Design / Illustration
- [ ] P1-5.1 : Créer les illustrations SVG d'Ilo (caméléon béninois) — 4 évolutions :
  - Niveaux 1-3 : Ilo bébé (petit, couleurs douces)
  - Niveaux 4-6 : Ilo enfant (plus grand, couleurs vives)
  - Niveaux 7-9 : Ilo ado (motifs complexes)
  - Niveaux 10-12 : Ilo champion (doré, cape, couronne)
- [ ] P1-5.2 : Créer les 8-10 poses par évolution (neutre, content, triste, danse, encourage, célèbre, dort, salue)
- [ ] P1-5.3 : Optimiser les SVG (< 200KB total compressé pour les ~40 illustrations)

#### Frontend — Composant Ilo
- [ ] P1-5.4 : Composant `<Ilo />` avec props : `mood`, `level`, `message`, `animated`
- [ ] P1-5.5 : Animations CSS simples (rebond, oscillation, apparition) — pas de Lottie
- [ ] P1-5.6 : Bulle de dialogue avec messages contextuels

#### Frontend — Intégrations
- [ ] P1-5.7 : Onboarding : Ilo guide l'élève ("Salut ! Je suis Ilo !")
- [ ] P1-5.8 : Dashboard : Ilo change de couleur selon le streak (vert → doré)
- [ ] P1-5.9 : Dashboard inactivité : Ilo triste ("Tu me manques...")
- [ ] P1-5.10 : Exercice bonne réponse : Ilo danse / applaudit
- [ ] P1-5.11 : Exercice erreur : Ilo encourage ("Pas grave, essaie encore !")
- [ ] P1-5.12 : Badge gagné : Ilo célèbre avec l'élève
- [ ] P1-5.13 : Personnalisation : accessoires à débloquer (chapeau, lunettes...) via badges/XP

---

### P1-2 : Workflow Éditorial Contenu (3-4 sem.)
> Impact : -50% temps création contenu, +30% qualité questions

#### Backend
- [x] P1-2.1 : Ajouter champ `status` (DRAFT / IN_REVIEW / PUBLISHED / ARCHIVED) sur les modèles Question et MicroLesson
- [x] P1-2.2 : Migration Alembic pour le nouveau champ (valeur par défaut PUBLISHED pour l'existant)
- [x] P1-2.3 : Filtrer les contenus : seuls les PUBLISHED sont servis aux élèves (content_service)
- [x] P1-2.4 : Endpoints de transition de statut : `POST /admin/content/questions/{id}/transition` + `/lessons/{id}/transition`
- [x] P1-2.5 : Champ `reviewer_notes` pour le feedback du validateur
- [x] P1-2.6 : Historique des transitions de statut (audit trail)
- [x] P1-2.7 : Alertes automatiques si taux réussite question < 20% ou > 95%

#### Frontend Admin
- [x] P1-2.8 : Vue Kanban des contenus (colonnes Draft / En relecture / Publié / Archivé)
- [x] P1-2.9 : Formulaire de création/édition de question avec sauvegarde en DRAFT
- [x] P1-2.10 : Bouton "Soumettre pour relecture" + "Approuver" / "Retourner avec feedback"
- [x] P1-2.11 : Preview "mode élève" : tester un exercice comme un élève avant publication
- [x] P1-2.12 : Commentaires inline sur chaque question
- [x] P1-2.13 : Stats post-publication (taux réussite, temps moyen) liées à l'éditeur

#### Validation
- [x] P1-2.14 : Import JSON robuste avec rollback partiel en cas d'erreur
- [x] P1-2.15 : Tests du workflow complet : DRAFT → IN_REVIEW → feedback → DRAFT → PUBLISHED

---

### P1-DIGEST : Digest SMS Hebdomadaire Parents (1 sem.)
> Dépend de P0-1 (infrastructure notifications)

- [x] P1-DIGEST.1 : Template SMS résumé hebdomadaire par enfant (score, streak, temps, conseil)
- [x] P1-DIGEST.2 : CRON dimanche 17h UTC : générer et envoyer les digests (notification_tasks)
- [x] P1-DIGEST.3 : Opt-in/opt-out pour le digest SMS dans les paramètres parent
- [x] P1-DIGEST.4 : Tracking : taux d'envoi, taux de réponse (si applicable)

---

## PHASE 3 : SCALE (Mois 6-9 — Août-Novembre 2026)

### P1-RN : App Android Native React Native / Expo (8-12 sem.)
> Impact : Acquisition +60%, Rétention +25%

#### Setup
- [ ] P1-RN.1 : Initialiser le projet Expo (managed workflow)
- [ ] P1-RN.2 : Configurer Expo EAS Build pour CI/CD
- [ ] P1-RN.3 : Extraire la couche logique partagée (services, stores, types) en package commun

#### Fonctionnalités core
- [ ] P1-RN.4 : Écrans d'authentification (OTP, sélection profil)
- [ ] P1-RN.5 : Dashboard élève
- [ ] P1-RN.6 : Exercice player (tous les types de questions)
- [ ] P1-RN.7 : Dashboard parent
- [ ] P1-RN.8 : Navigation bottom tabs + stack
- [ ] P1-RN.9 : Classement et défis

#### Natif
- [ ] P1-RN.10 : `expo-notifications` pour push fiables
- [ ] P1-RN.11 : `expo-sqlite` pour offline (remplace IndexedDB)
- [ ] P1-RN.12 : Sync offline avec le même protocole que la PWA
- [ ] P1-RN.13 : Deep links (défi ami, notification → page)

#### Publication
- [ ] P1-RN.14 : Fiche Google Play Store (screenshots, description, catégorie Éducation)
- [ ] P1-RN.15 : Tests sur Android Go (device réel low-end, 1-2Go RAM)
- [ ] P1-RN.16 : Beta testing avec 50 utilisateurs pilotes avant lancement public

---

### P2-2 : Examens Blancs CEP Simulés (3-4 sem.)
> Impact : Conversion premium +30%

#### Backend
- [ ] P2-2.1 : Modèle `MockExam` (id, grade, subject, duration_minutes, question_ids, is_free)
- [ ] P2-2.2 : Service de génération d'examen blanc (mix de questions couvrant tout le programme)
- [ ] P2-2.3 : Endpoint `POST /api/v1/exams/start` → crée une session examen avec timer
- [ ] P2-2.4 : Score prédictif : algorithme "Avec ce niveau → X/20 au CEP"
- [ ] P2-2.5 : Historique des examens blancs par élève
- [ ] P2-2.6 : 1 examen blanc gratuit par matière, puis Premium uniquement
- [ ] P2-2.7 : "Examen blanc national" mensuel (même date pour tous)

#### Frontend
- [ ] P2-2.8 : Page "Examens blancs" avec liste des examens disponibles
- [ ] P2-2.9 : Mode examen : timer réaliste, pas de brouillon, pas d'aide
- [ ] P2-2.10 : Correction détaillée avec renvoi vers micro-leçons pertinentes
- [ ] P2-2.11 : Affichage du score prédictif CEP
- [ ] P2-2.12 : Historique avec courbe de progression visible
- [ ] P2-2.13 : Partage résultat avec parents (notification push)

---

### P2-1 : Espace Enseignant V1 (10-14 sem.)
> Impact : Revenus B2B, Acquisition organique

#### Backend
- [ ] P2-1.1 : Rôle TEACHER dans UserRole enum + RBAC
- [ ] P2-1.2 : Modèle `Classroom` (id, teacher_id, name, invite_code, grade)
- [ ] P2-1.3 : Modèle `TeacherStudent` (N:N, basé sur le pattern ParentStudent existant)
- [ ] P2-1.4 : Modèle `Assignment` (id, classroom_id, skill_id, deadline, created_by)
- [ ] P2-1.5 : Endpoints CRUD classes + élèves + devoirs assignés
- [ ] P2-1.6 : Endpoint résultats par exercice assigné (scores de la classe)
- [ ] P2-1.7 : Export PDF pour réunion parents
- [ ] P2-1.8 : Alertes enseignant : élèves en difficulté (score < 40%)

#### Frontend
- [ ] P2-1.9 : Dashboard enseignant (classes, scores moyens, alertes)
- [ ] P2-1.10 : Page création/gestion de classe (code d'invitation)
- [ ] P2-1.11 : Page assignation exercice ciblé (skill + deadline)
- [ ] P2-1.12 : Page résultats par exercice (vue classe)
- [ ] P2-1.13 : Export PDF (côté client ou via backend)

#### Monétisation B2B
- [ ] P2-1.14 : Plans école : Gratuit (1 classe, 30 élèves) / Basic (5 classes, 15K FCFA/mois) / Premium (illimité, 40K FCFA/mois)
- [ ] P2-1.15 : Page de souscription école avec facturation annuelle (-20%)

---

### P1-VIDEO : Vidéo Micro-Leçons (3-4 sem.)

- [ ] P1-VIDEO.1 : Support media enrichi dans les micro-leçons (vidéo, audio)
- [ ] P1-VIDEO.2 : Compression agressive des vidéos (format adapté 2G/3G : 240p, codec H.265)
- [ ] P1-VIDEO.3 : Streaming adaptatif (HLS avec segments courts)
- [ ] P1-VIDEO.4 : Téléchargement offline des vidéos (optionnel, avec avertissement taille)
- [ ] P1-VIDEO.5 : Player vidéo léger avec sous-titres
- [ ] P1-VIDEO.6 : Fallback texte/image si vidéo non disponible offline

---

### EXPANSION-CM1 : Extension au CM1

- [ ] EXP-CM1.1 : Ajouter le GradeLevel CM1 dans le curriculum
- [ ] EXP-CM1.2 : Créer la structure de contenu CM1 (domaines, compétences, micro-compétences)
- [ ] EXP-CM1.3 : Importer les premières questions CM1
- [ ] EXP-CM1.4 : Permettre la sélection multi-classe dans le profil élève

---

## PHASE 4 : EXPANSION (Mois 10-18 — Déc 2026 - Sept 2027)

### P2-MARKETPLACE : Marketplace Contenu Enseignants

- [ ] P2-MKT.1 : Interface de création de questions par les enseignants
- [ ] P2-MKT.2 : Système de modération / validation communautaire
- [ ] P2-MKT.3 : Attribution et crédits aux créateurs
- [ ] P2-MKT.4 : Stats d'utilisation des questions créées

### P2-3 : Récompenses Tangibles (Partenariats)

- [ ] P2-3.1 : Système de génération de coupon codes côté backend (au seuil atteint)
- [ ] P2-3.2 : API de vérification pour les partenaires
- [ ] P2-3.3 : Dashboard admin pour suivre les rédemptions
- [ ] P2-3.4 : Intégration partenaires : MTN/Moov (data), librairies, imprimeries, radio

### P2-iOS : App iOS (Expo)

- [ ] P2-iOS.1 : Build iOS via Expo EAS
- [ ] P2-iOS.2 : Adaptation UI (guidelines Apple HIG)
- [ ] P2-iOS.3 : Soumission App Store (fiche FR, catégorie Éducation)
- [ ] P2-iOS.4 : In-App Purchase Apple (en complément Mobile Money)

### EXPANSION-CI : Expansion Côte d'Ivoire

- [ ] EXP-CI.1 : Adaptation du curriculum (programmes ivoiriens)
- [ ] EXP-CI.2 : Adaptation paiement (opérateurs locaux : Orange Money CI, MTN CI)
- [ ] EXP-CI.3 : Contenu spécifique 6ème

### P2-TUTORAT : Tutorat en Ligne

- [ ] P2-TUT.1 : Mise en relation tuteur-élève
- [ ] P2-TUT.2 : Messagerie asynchrone
- [ ] P2-TUT.3 : Modèle de revenus par commission

---

## TÂCHES TRANSVERSES (à maintenir tout au long)

### Qualité & Performance
- [ ] QUAL.1 : Budget performance : LCP < 3s sur 3G, tests réguliers sur Android Go réel
- [x] QUAL.2 : Tests E2E offline obligatoires (non-régression à chaque release)
- [x] QUAL.3 : Monitoring taux de livraison notifications (SMS + push)
- [x] QUAL.4 : Monitoring taux de réussite par question (alertes si < 20% ou > 95%)

### Sécurité & Données
- [x] SEC.1 : Sync cross-device : permettre à un élève qui change de téléphone de retrouver ses données
- [x] SEC.2 : Versioning du contenu : historique des modifications, rollback possible
- [x] SEC.3 : Import robuste : validation JSON + rollback partiel en cas d'erreur

### Analytics & Métriques
- [x] ANALYTICS.1 : Tracker DAU/MAU ratio
- [x] ANALYTICS.2 : Tracker rétention D1, D7, D14, D30
- [x] ANALYTICS.3 : Tracker conversion Free → Paywall → Paiement → Complété
- [x] ANALYTICS.4 : Tracker K-factor viralité (invitations × taux conversion)
- [x] ANALYTICS.5 : Admin dashboard enrichi : report builder, drill-down, export planifié

---

## RÉSUMÉ PAR EFFORT

| Phase | Tâche | Priorité | Effort | Statut |
|-------|-------|----------|--------|--------|
| 1 | QW-1 Hook rappel quotidien | P0 | 2j | [x] |
| 1 | QW-2 Célébration fin exercice | P0 | 1j | [x] |
| 1 | QW-3 Web Share API | P0 | 0.5j | [x] |
| 1 | P0-1 Notifications automatiques | P0 | 2-3 sem | [~] |
| 1 | P1-3 Dashboard parent santé | P1 | 1-2 sem | [x] |
| 1 | P1-4 30+ badges extensibles | P1 | 1 sem | [x] |
| 1 | P1-TWA Android TWA | P1 | 2 sem | [ ] |
| 2 | P0-2 Offline granulaire | P0 | 4-5 sem | [x] |
| 2 | P0-3 Social classement + défis | P0 | 4-6 sem | [x] |
| 2 | P1-5 Mascotte Ilo | P1 | 3-4 sem | [ ] |
| 2 | P1-2 Workflow éditorial | P1 | 3-4 sem | [x] |
| 2 | P1-DIGEST SMS parents | P1 | 1 sem | [x] |
| 3 | P1-RN App Android native | P1 | 8-12 sem | [ ] |
| 3 | P2-2 Examens blancs CEP | P2 | 3-4 sem | [ ] |
| 3 | P2-1 Espace enseignant | P2 | 10-14 sem | [ ] |
| 3 | P1-VIDEO Vidéo micro-leçons | P1 | 3-4 sem | [ ] |
| 4 | P2-MKT Marketplace contenu | P2 | TBD | [ ] |
| 4 | P2-3 Récompenses tangibles | P2 | TBD | [ ] |
| 4 | P2-iOS App iOS | P2 | TBD | [ ] |
| 4 | EXP-CI Expansion Côte d'Ivoire | P2 | TBD | [ ] |
| 4 | P2-TUT Tutorat en ligne | P2 | TBD | [ ] |
