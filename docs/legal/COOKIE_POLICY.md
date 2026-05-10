# Politique Cookies — SITOU

**Dernière mise à jour : 2026-05-10**

## Cookies utilisés

SITOU utilise **uniquement des cookies strictement nécessaires** au fonctionnement du service. Aucun cookie publicitaire, aucun traceur tiers (Google Analytics, Facebook Pixel, etc.).

| Cookie | Finalité | Durée | Type |
|--------|----------|-------|------|
| `sitou_access_token` | Authentification (JWT court) | 1h | Essentiel |
| `sitou_refresh_token` | Renouvellement de session | 30j | Essentiel |
| `sitou_active_profile` | Mémorisation profil enfant actif | Session | Essentiel |
| `sitou_locale` | Préférence langue | 1 an | Préférence |

## Stockage local (IndexedDB / localStorage)

L'application utilise IndexedDB et localStorage pour le mode hors-ligne :

- Cache des questions et micro-leçons téléchargées
- File d'événements à synchroniser
- Brouillons d'exercices en cours

Ces données restent **strictement sur l'appareil de l'utilisateur** et ne sont synchronisées qu'avec le serveur Sitou (jamais avec un tiers).

## Refus / Suppression

Les cookies essentiels ne peuvent être désactivés sans dégrader le service. L'utilisateur peut :

- Vider le stockage local depuis les paramètres du navigateur.
- Demander la suppression complète de son compte (`DELETE /me/purge`).
