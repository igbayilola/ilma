# Politique de Conservation des Données — SITOU

**Dernière mise à jour : 2026-05-10**
**Référence légale :** Art. 357 du Code du numérique béninois (durée de conservation proportionnée à la finalité)

---

## Principe général

Les données personnelles ne sont conservées que pendant la durée strictement nécessaire à la finalité du traitement. Au-delà, elles sont **anonymisées** ou **supprimées définitivement**.

## Tableau de rétention

### Données utilisateur

| Donnée | Durée de conservation | Action en fin de durée |
|--------|----------------------|------------------------|
| Compte actif (user, profile, settings) | Durée de vie du compte | — |
| Compte supprimé sur demande utilisateur | 30 jours (grace) | Suppression définitive |
| Compte inactif > 24 mois | 24 mois | Notification + suppression si pas de réactivation |

### Données pédagogiques

| Donnée | Durée | Action |
|--------|-------|--------|
| Sessions d'exercices, tentatives, scores | Durée du compte + 1 an | Anonymisation (user_id → NULL, hash conservé) |
| SmartScore historique | Durée du compte + 1 an | Anonymisation |
| Badges, XP | Durée du compte | Suppression à la suppression du compte |
| Brouillons / drafts | 2h (localStorage) | Effacement automatique |

### Données techniques

| Donnée | Durée | Action |
|--------|-------|--------|
| Logs d'accès (IP, user-agent) | 90 jours | Suppression automatique |
| Logs d'erreur (Sentry/GlitchTip) | 30 jours | Suppression automatique |
| Audit logs (admin actions, payments) | 5 ans | Conservation légale (comptabilité, fraude) |
| Backups DB | 7 jours (daily), 30 jours (weekly) | Rotation automatique |
| Backups off-site (Backblaze B2) | 90 jours | Rotation automatique |

### Données de communication

| Donnée | Durée | Action |
|--------|-------|--------|
| Notifications envoyées (SMS, push, in-app) | 90 jours | Suppression automatique |
| Tickets support | 3 ans | Suppression |
| OTP générés | 10 minutes | Expiration automatique |

### Données financières

| Donnée | Durée | Action |
|--------|-------|--------|
| Transactions Mobile Money | 10 ans | Conservation légale (Code général des impôts) |
| Factures | 10 ans | Conservation légale |
| Tokens de paiement | Aucune | Non stockés (gérés par KKiaPay/FedaPay) |

### Données analytiques

| Donnée | Durée | Action |
|--------|-------|--------|
| Événements analytics (raw) | 6 mois | Anonymisation (suppression user_id) |
| Agrégats (DAU, MAU, cohorts) | 18 mois | Suppression |
| Rapports business | 5 ans | Conservation interne |

## Procédure de suppression

### Suppression sur demande utilisateur

1. L'utilisateur déclenche `DELETE /me/purge` depuis les paramètres.
2. Confirmation OTP envoyée par SMS au numéro associé.
3. `users.purge_requested_at = now()`, `users.purge_scheduled_at = now() + 30 jours`.
4. Pendant 30 jours, l'utilisateur peut annuler en se reconnectant.
5. À J+30, cron `purge_tasks.py` exécute :
   - Suppression : `users`, `profiles`, `sessions`, `attempts`, `notifications`, `push_subscriptions`, `parental_consent`.
   - Anonymisation : `audit_logs.user_id = NULL` (hash conservé pour stats agrégées).
   - Anonymisation : `transactions.user_id = NULL` (montant et date conservés pour comptabilité).

### Suppression automatique périodique

| Fréquence | Cible | Cron |
|-----------|-------|------|
| Quotidienne (3h UTC) | Logs d'accès > 90j | `purge_tasks.purge_old_logs` |
| Hebdomadaire (dimanche 4h UTC) | Notifications > 90j | `purge_tasks.purge_old_notifications` |
| Mensuelle (1er du mois) | Comptes inactifs > 24 mois | `purge_tasks.notify_inactive_accounts` |

## Anonymisation

L'anonymisation consiste à :

- Remplacer `user_id` / `profile_id` par `NULL`.
- Conserver un hash SHA-256 (sel rotatif tous les 6 mois) pour permettre l'agrégation sans ré-identification.
- Supprimer toute donnée libre (commentaires, noms).

L'anonymisation est **irréversible**.
