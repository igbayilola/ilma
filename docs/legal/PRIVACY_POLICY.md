# Politique de Confidentialité — SITOU

**Dernière mise à jour : 2026-05-10**
**Version : 1.0**

> Source de vérité. Le contenu de la page `frontend/pages/legal/Privacy.tsx` doit refléter ce document.

---

## 1. Responsable du traitement

**SITOU** — Application éducative pour le cycle primaire au Bénin.

- **Adresse :** [À compléter — siège Bénin]
- **Email contact :** `contact@sitou.bj`
- **DPO (Délégué à la Protection des Données) :** `dpo@sitou.bj`

## 2. Cadre légal

Cette politique respecte :

- **Loi n°2017-20** du 20 avril 2018 portant Code du numérique en République du Bénin (Arts. 350 à 378)
- **Loi n°2019-43** du 29 novembre 2019 instituant l'APDP
- **Directive APDP n°2020-001** sur le consentement des mineurs

## 3. Données collectées

| Catégorie | Données | Finalité | Base légale |
|-----------|---------|----------|-------------|
| Authentification | email ou téléphone, mot de passe (hashé bcrypt) | Connexion sécurisée | Exécution du contrat |
| Profil parent | nom complet, langue préférée | Identification, communication | Exécution du contrat |
| Profil enfant | prénom, avatar, niveau scolaire | Personnalisation de l'apprentissage | Consentement parental |
| Données pédagogiques | scores, progression, exercices complétés, badges | Adaptation du parcours d'apprentissage | Consentement parental |
| Données techniques | adresse IP, user-agent | Sécurité (détection abus) | Intérêt légitime |
| Paiement | identifiant transaction, montant | Gestion abonnement | Exécution du contrat |

**Aucune donnée biométrique, aucune géolocalisation précise, aucune donnée sensible (santé, religion, opinions) n'est collectée.**

## 4. Finalités

1. Fournir un service d'apprentissage adapté aux élèves du cycle primaire au Bénin.
2. Permettre aux parents/tuteurs de suivre la progression de leurs enfants.
3. Permettre aux enseignants de suivre leur classe.
4. Améliorer la qualité du contenu pédagogique (analyses agrégées et anonymisées).
5. Assurer la sécurité du service (détection de fraude, abus).

## 5. Protection des mineurs

Sitou s'adresse à des enfants âgés de 6 à 15 ans. Conformément à la **Directive APDP n°2020-001** :

- Aucun profil enfant n'est créé sans le consentement explicite et vérifié du représentant légal.
- Le consentement est recueilli via case à cocher signée + confirmation OTP envoyée par SMS au numéro du parent.
- Le représentant légal peut à tout moment retirer son consentement et demander la suppression du profil de l'enfant.

## 6. Durées de conservation

| Donnée | Durée |
|--------|-------|
| Compte actif | Durée de vie du compte |
| Compte supprimé (demande utilisateur) | 30 jours (grace) puis suppression définitive |
| Données pédagogiques | Durée du compte + 1 an (étude longitudinale anonymisée) |
| Journaux de sécurité (IP, user-agent) | 90 jours |
| Données analytiques | 18 mois, anonymisées après 6 mois |
| Tickets support | 3 ans |
| Données de paiement (obligation comptable) | 10 ans (Code général des impôts) |

## 7. Vos droits (Arts. 355 à 360 du Code du numérique)

- **Droit d'accès :** obtenir une copie de toutes vos données.
- **Droit de rectification :** corriger des informations inexactes.
- **Droit à l'effacement :** demander la suppression complète de votre compte (`DELETE /me/purge`, confirmation OTP).
- **Droit d'opposition :** vous opposer à certains traitements (analytics, profilage).
- **Droit à la portabilité :** récupérer vos données en format JSON exportable.
- **Droit de retrait du consentement :** à tout moment, sans justification.

**Pour exercer ces droits :** contactez `dpo@sitou.bj` ou utilisez les fonctions « Supprimer mon compte » et « Exporter mes données » dans les paramètres.

## 8. Sécurité

- Mots de passe hashés (bcrypt, coût ≥ 12)
- Communications chiffrées (HTTPS / TLS 1.3 obligatoire)
- Données stockées dans des bases avec contrôle d'accès strict
- Sauvegardes chiffrées et hébergées dans un second site géographique
- Pas de tracking publicitaire, pas de tiers (Google Analytics, Facebook Pixel, etc.)
- Avatars générés localement (pas d'appel à des services externes type DiceBear)
- Erreurs techniques journalisées en interne uniquement (pas de Sentry tiers tant que non APDP-compatible)

## 9. Sous-traitants

| Sous-traitant | Finalité | Localisation | Garanties |
|---------------|----------|--------------|-----------|
| Twilio | Envoi SMS (OTP, alertes) | États-Unis | Clauses contractuelles types |
| KKiaPay / FedaPay | Paiement Mobile Money | Bénin | Conformité APDP locale |
| Backblaze B2 | Sauvegarde chiffrée hors-site | États-Unis | Chiffrement AES-256 côté Sitou |

Les transferts hors zone APDP sont limités au strict nécessaire et chiffrés. Les négociations sont en cours pour migrer vers des sous-traitants africains (Hubtel, Africa's Talking).

## 10. Réclamation

Si vous estimez vos droits non respectés, vous pouvez introduire une réclamation auprès de :

**APDP — Autorité de Protection des Données à caractère Personnel**
Cotonou, Bénin

## 11. Modifications de la politique

Toute modification substantielle sera notifiée par email/SMS aux utilisateurs concernés au moins 15 jours avant prise d'effet.
