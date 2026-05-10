# Audit 7/7 : Gouvernance & Maintenance Opérationnelle

**Date** : 12 avril 2026  
**Auditeur** : Consultant Senior EdTech  
**Score global** : 5.5/10  

> Ce dernier audit évalue les processus organisationnels, la maintenance, la formation et la gouvernance de l'écosystème Sitou/ILMA pour assurer sa pérennité à grande échelle au Bénin.

---

## Résumé Exécutif

| Domaine | Score | Statut |
|---------|-------|--------|
| Workflow Éditorial | 7/10 | ✅ Fonctionnel |
| Mises à Jour OTA | 5/10 | ⚠️ À améliorer |
| Support Client | 2/10 | 🔴 Critique |
| Formation Enseignants | 1/10 | 🔴 Critique |
| Résilience Équipe (Bus Factor) | 4/10 | ⚠️ Risqué |
| Gouvernance Données | 4/10 | ⚠️ À documenter |

**Score global pondéré** : 5.5/10 — *Organisation fonctionnelle mais fragile à grande échelle*

---

## 1. Workflow Éditorial — Score : 7/10 ✅

### Forces

| Aspect | Implémentation | Qualité |
|--------|---------------|---------|
| **Kanban Board** | 4 colonnes (DRAFT → IN_REVIEW → PUBLISHED → ARCHIVED) | Intuitif |
| **Versioning** | Snapshots automatiques à chaque modification | Traçable |
| **Audit Trail** | `ContentTransition` avec notes de relecture | Transparent |
| **Types de questions** | 12 types supportés | Riche |
| **Import CSV/JSON** | Scripts d'import en masse | Efficace |

```python
# Workflow éditorial implémenté
transitions = {
    "DRAFT": ["IN_REVIEW"],
    "IN_REVIEW": ["PUBLISHED", "DRAFT"],  # Approbation ou retour
    "PUBLISHED": ["ARCHIVED"],
    "ARCHIVED": ["DRAFT"]  # Restauration possible
}
```

### Monitoring Qualité Automatisé

```python
# backend/app/tasks/content_tasks.py
LOW_SUCCESS_RATE = 0.20   # < 20% → trop difficile
HIGH_SUCCESS_RATE = 0.95  # > 95% → trop facile
MIN_ATTEMPTS = 20         # Seuil de fiabilité
```

**Alertes automatiques** envoyées aux admins si questions problématiques détectées.

### Faiblesses

| Problème | Impact | Priorité |
|----------|--------|----------|
| Pas de réviseur pédagogique dédié | Risque erreurs MEMP | Moyenne |
| Workflow manuel (pas de CI/CD contenu) | Lent à grande échelle | Moyenne |
| Pas de validation A/B des questions | Pas d'optimisation pédagogique | Faible |

---

## 2. Mises à Jour OTA (Over-The-Air) — Score : 5/10 ⚠️

### Implémentation Actuelle

```javascript
// frontend/components/pwa/UpdatePrompt.tsx
const PWAUpdatePrompt = () => {
  // Détection via Service Worker
  // Prompt utilisateur si nouvelle version dispo
  // skipWaiting() pour activation immédiate
}
```

**Fonctionnalités** :
- ✅ Détection automatique nouvelle version
- ✅ Installation différée en exercice (pas d'interruption)
- ✅ Message adapté au contexte (exercice vs navigation)

### Problèmes Identifiés

| Problème | Impact | Solution Recommandée |
|----------|--------|---------------------|
| **Téléchargement complet** (10-20MB) | Lourd sur 2G | Delta updates (diff) |
| **Pas de fallback offline** | Bloquant si échec | Mode dégradé |
| **Pas de release channels** | Tous utilisateurs en même temps | Staged rollout (5% → 50% → 100%) |
| **Pas de rollback** | Risque si bug critique | Version pinning |

### Recommandation : Système de Delta Updates

```javascript
// Version cible
interface DeltaUpdate {
  baseVersion: "2.1.0",
  targetVersion: "2.1.1",
  patches: [
    { file: "/assets/main.[hash].js", diff: "<binary-diff>" },
    { file: "/assets/styles.[hash].css", diff: "<binary-diff>" }
  ],
  size: "150KB",  // vs 15MB full
}
```

---

## 3. Support Client — Score : 2/10 🔴

### Constats

| Canal | Statut | Observation |
|-------|--------|-------------|
| **WhatsApp** | ❌ Non intégré | Canal dominant au Bénin |
| **SMS** | ⚠️ Unidirectionnel | Notifications seulement |
| **In-App Chat** | ❌ Absent | Pas de support temps réel |
| **Centre d'aide** | ❌ Absent | Pas de FAQ/Documentation |
| **Email** | ❌ Non configuré | - |

### Impact Utilisateur

> *"Parent analphabète avec problème de paiement → aucun canal accessible"*

### Solution Recommandée : Support Multicanal

```python
class SupportChannel(Enum):
    WHATSAPP = "whatsapp"      # Canal principal (MTN MoMo friendly)
    USSD = "*229*123#"         # Fallback texte
    VOICE = "+229-XX-XX-XX"    # Hotline pour cas complexes
    IN_APP = "chat"            # Chat async dans l'app
```

#### Chatbot WhatsApp Basique (MVP)

```
Menu WhatsApp:
1. Problème de paiement
2. Enfant bloqué sur exercice
3. Réinitialiser mot de passe
4. Parler à un humain (file d'attente)
0. Retour au menu
```

**Coût estimé** : ~200 000 FCFA/mois (Twilio WhatsApp API)

---

## 4. Formation Enseignants — Score : 1/10 🔴

### Constats

| Élément | Statut | Impact |
|---------|--------|--------|
| **Programme de formation** | ❌ Inexistant | Enseignants autodidactes |
| **Guide d'utilisation** | ❌ Absent | Usage sous-optimal |
| **Webinaires** | ❌ Jamais organisé | Pas de communauté |
| **Certification** | ❌ Non prévue | Pas de reconnaissance |
| **Tutorat pairs** | ❌ Non structuré | Silos par école |

### Contexte Bénin

- 60-90 élèves par classe en moyenne
- 1 professeur des écoles pour toutes les matières
- Faible accès à la formation continue
- Résistance au changement pédagogique

### Programme Recommandé : "Ambassadeurs Sitou"

```
Phase 1 (Mois 1-3) : Bootcamp en ligne
├── Module 1 : Navigation et fonctionnalités (2h)
├── Module 2 : Suivi de la progression (1h)
├── Module 3 : Analyse des résultats (2h)
└── Certification "Utilisateur Certifié Sitou"

Phase 2 (Mois 4-6) : Communauté
├── Groupes WhatsApp par région
├── Session mensuelle "Astuces du mois"
└── Programme "Parrainage" (enseignant → enseignant)

Phase 3 (Mois 7-12) : Leadership
├── Sélection "Ambassadeurs Sitou" (1/école)
├── Formation formateurs
└── Événements trimestriels de partage
```

**Budget indicatif** : 500 000 - 1 000 000 FCFA/an (certifications, événements)

---

## 5. Résilience Équipe (Bus Factor) — Score : 4/10 ⚠️

### Évaluation du Risque

| Composant | Expertise Requise | Bus Factor | Risque |
|-----------|-------------------|------------|--------|
| Backend FastAPI | Python, SQLAlchemy | 1-2 | 🔴 Élevé |
| Frontend React | TypeScript, Vite | 1-2 | 🔴 Élevé |
| DevOps/Déploiement | Docker, Linux | 1 | 🔴 Critique |
| Contenu Pédagogique | MEMP, Didactique | 1 | 🔴 Critique |
| Mobile/PWA | Service Workers | 1 | 🟡 Moyen |

### Documentation Existante

| Document | Couverture | Qualité |
|----------|------------|---------|
| `DEPLOY.md` | Déploiement VPS | ✅ Complète |
| `ROADMAP_AUDIT.md` | Plan d'action | ✅ À jour |
| `README_OBSERVABILITY.md` | Monitoring | ⚠️ Basique |
| Architecture Decision Records | ❌ Absent | - |
| Runbooks incidents | ❌ Absent | - |
| Documentation API | Auto-générée (OpenAPI) | ✅ OK |

### Plan de Continuité Recommandé

```yaml
# Documentation critique à produire
runbooks:
  - incident_response: "Procédure en cas de downtime"
  - database_recovery: "Restauration backup step-by-step"
  - security_breach: "Protocole violation de données"
  - vendor_dropout: "Si KKiaPay/FedaPay indisponible"

knowledge_transfer:
  - paire_programming: "2 développeurs sur chaque feature critique"
  - code_reviews: "Obligatoire, avec explications"
  - documentation: "Chaque PR = mise à jour docs"

external_support:
  - retainer_contract: "Accord avec agence technique de secours"
  - escrow_agreement: "Code source déposé chez notaire"
```

---

## 6. Gouvernance des Données — Score : 4/10 ⚠️

### Politiques Manquantes

| Politique | Statut | Obligation Légale |
|-----------|--------|-------------------|
| Politique de confidentialité | ❌ Absente | 🔴 OBLIGATOIRE (APDP) |
| Conditions d'utilisation | ❌ Absente | 🔴 OBLIGATOIRE |
| Charte d'utilisation (élèves) | ❌ Absente | 🟡 Recommandée |
| Politique de conservation | ❌ Absente | 🔴 OBLIGATOIRE |
| Procédure de suppression | ❌ Absente | 🔴 OBLIGATOIRE (droit à l'oubli) |
| Consentement parental | ❌ Absent | 🔴 OBLIGATOIRE (mineurs) |

### Rétention des Données Recommandée

```python
# Politique de conservation
data_retention = {
    # Données actives
    "user_sessions": "2 ans après dernière activité",
    "exercise_attempts": "Durée du compte + 1 an",
    "progression": "Durée du compte",
    
    # Données de communication
    "notifications": "90 jours",
    "support_tickets": "3 ans",
    
    # Données analytiques
    "analytics_events": "18 mois (anonymisées après 6 mois)",
    "performance_metrics": "2 ans",
    
    # Données supprimées
    "deleted_accounts": "30 jours (puis purge)",
    "failed_payments": "1 an",
}
```

### DPO (Data Protection Officer)

| Aspect | Statut | Action Requise |
|--------|--------|----------------|
| Nomination DPO | ❌ Non | Désigner un responsable |
| Registre des traitements | ❌ Non | Documenter les flux |
| DPIA (Privacy Impact) | ❌ Non | Évaluation risques |
| Délégué APDP | ❌ Non | Enregistrement obligatoire |

---

## 7. Infrastructure de Sauvegarde — Score : 6/10

### Implémentation Actuelle

```bash
# deploy/backup.sh
BACKUP_TYPE="${1:-daily}"  # daily | weekly
RETENTION_DAILY=7          # 7 jours
RETENTION_WEEKLY=30        # 30 jours

# PostgreSQL dump → gzip
# Rotation automatique
```

**Points forts** :
- ✅ Automatisation via cron
- ✅ Compression gzip
- ✅ Rotation configurable
- ✅ Intégration Docker

### Lacunes

| Problème | Impact | Solution |
|----------|--------|----------|
| **Pas de backup hors-site** | Pertes totale si incendie/inondation | S3 glacier, replica cloud |
| **Pas de test de restauration** | Backup corrompu = inutilisable | Restore test mensuel |
| **Single point of failure** | Docker exec dépend du container up | Health check + fallback |
| **Pas de backup fichiers** | Médias/illustrations non sauvegardés | MinIO backup sync |
| **Pas de monitoring backup** | Échec silencieux possible | Alertes échec backup |

### Architecture de Backup Recommandée

```
┌─────────────────┐
│  Production     │
│  (AlmaLinux VPS)│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐  ┌──▼────┐
│Daily  │  │Weekly │
│(local)│  │(local)│
└───┬───┘  └───┬───┘
    │          │
    └────┬─────┘
         │
    ┌────▼──────────┐
    │  Off-site     │
    │  (Backblaze   │
    │   B2 / S3)    │
    └───────────────┘
```

**Coût** : ~10 000 FCFA/mois pour 100GB (Backblaze B2)

---

## 8. Recommandations Synthétiques

### Phase 1 : Critical Fixes (Mois 1)

| Priorité | Action | Responsable | Budget |
|----------|--------|-------------|--------|
| P0 | Rédiger politique de confidentialité | Legal/DPO | 200K FCFA |
| P0 | Créer compte support WhatsApp Business | Ops | 50K FCFA |
| P0 | Documenter runbook incident | Tech Lead | Interne |
| P1 | Configurer backup hors-site | DevOps | 120K FCFA/an |

### Phase 2 : Amélioration (Mois 2-3)

| Priorité | Action | Impact |
|----------|--------|--------|
| P1 | Programmation formation enseignants | Adoption +40% |
| P1 | Système de tickets support | Satisfaction +50% |
| P2 | Delta updates OTA | Bande passante -80% |
| P2 | Documentation technique complète | Bus factor ↓ |

### Phase 3 : Maturité (Mois 4-6)

| Priorité | Action | Impact |
|----------|--------|--------|
| P2 | Programme "Ambassadeurs" | Viralité +30% |
| P2 | Automation tests de restauration | Fiabilité ↑ |
| P3 | Release channels (staged rollout) | Risque baisse |

---

## Conclusion

### Score Global : 5.5/10

**Verdict** : L'organisation dispose d'une base solide (workflow éditorial, backup) mais présente des fragilités majeures en support client, formation et gouvernance des données.

### Points Clés

1. **🔴 URGENT** : La conformité légale est insuffisante (pas de DPO, pas de politique confidentialité)
2. **🔴 CRITIQUE** : Aucun canal support accessible aux populations analphabètes
3. **⚠️ IMPORTANT** : Le bus factor élevé crée un risque de dépendance critique
4. **✅ POSITIF** : Le workflow éditorial est bien conçu et traçable

### Roadmap Gouvernance

```
Mois 1  →  Documentation légale + Support WhatsApp
Mois 2  →  Formation enseignants v1 + Runbooks
Mois 3  →  Backup off-site + Tests restore
Mois 4  →  Programme ambassadeurs + Delta updates
Mois 5  →  Audit sécurité externe + Certification
Mois 6  →  Revue gouvernance + Amélioration continue
```

---

*Fin de l'audit. Score moyen global des 7 audits : 4.8/10 — Prêt pour déploiement limité, Phase 1 de corrections requise avant scale national.*
