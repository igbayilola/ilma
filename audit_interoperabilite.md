# Audit Interopérabilité Écosystème Bénin

## Résumé Exécutif

**Score d'interopérabilité : 5/10** — L'application dispose d'une architecture modulaire favorable aux intégrations (providers de paiement, SMS, push notifications) mais manque des connecteurs essentiels pour l'écosystème béninois : pas de Mobile Money natif (MTN MoMo API), pas d'export pour directeurs d'école, pas de support langues locales (Fon/Yoruba).

**Verdict :** Application isolée pouvant fonctionner seule, mais **peu intégrée au tissu éducatif local** (WhatsApp comme canal informel, Mobile Money omniprésent, gestion administrative papier/Excel).

---

## État des Lieux Intégrations

### Intégrations Existantes

| Domaine | Technologie | Statut | Commentaire |
|---------|-------------|--------|-------------|
| **Paiement** | KKiaPay + FedaPay | ✅ | Agrégateurs supportant Mobile Money indirectement |
| **Auth** | OTP SMS (Twilio) | ✅ | Préfixes MTN/Moov validés (+229 96/97/95/94...) |
| **Notifications** | SMS + Push Web + In-app | ✅ | Multi-canal avec fallback |
| **i18n** | React i18n (fr/en) | ⚠️ | Infrastructure prête mais langues locales absentes |
| **Enseignant** | Salles de classe + codes inv. | ✅ | Code alphanumérique 8 caractères |

### Architecture Modulaire (Points Forts)

```python
# Pattern Provider flexible - facilement extensible
class PaymentProviderBase:
    async def create_transaction(self, amount, description, callback_url): ...

class KKiaPayProvider(PaymentProviderBase): ...
class FedaPayProvider(PaymentProviderBase): ...
# → MTNMoMoProvider et MoovMoneyProvider faciles à ajouter
```

---

## Gaps d'Intégration Critiques

### 🔴 IC-1 : Pas d'intégration Mobile Money directe (MTN MoMo API / Moov Money)

**Problème :** Les paiements passent par des agrégateurs (KKiaPay/FedaPay) qui ajoutent une couche et des frais. Pas de micro-paiements (par jour/semaine) adaptés au pouvoir d'achat local.

**Impact business :**
- Commission agrégateur : 3-5% vs 1-2% en direct
- Pas de paiement USSD (feature phones)
- Pas de "pass journalier" à 100 FCFA

**Code actuel :**
```python
# subscription_service.py - forfaits classiques uniquement
class Plan:
    duration_days: int  # 30, 90, 365 - pas de "1 jour"
    price_xof: int      # 2500, 6000, 20000
```

### 🔴 IC-2 : Pas d'export de données pour directeurs d'école

**Problème :** Aucun endpoint `/export/csv` ou génération PDF pour les registres scolaires. Les directeurs utilisent Excel ou papier.

**Besoin identifié :** Export trimestriel des résultats par classe (nom, prénom, matière, score moyen) pour import dans les systèmes existants.

### 🔴 IC-3 : Pas de support WhatsApp Business API

**Problème :** Les notifications SMS coûtent ~10-20 FCFA/unité. WhatsApp est gratuit (ou quasi) et déjà utilisé par 90% des parents via les "groupes classe" informels.

**Architecture actuelle :**
```python
class NotificationChannel:
    IN_APP = "in_app"
    SMS = "sms"      # Twilio - payant
    PUSH = "push"    # Web push - limité
    # WHATSAPP absent
```

### 🔴 IC-4 : i18n bloqué sur français uniquement

**Problème :** L'infrastructure i18n existe (`i18n/index.ts`) mais seules les traductions FR/EN sont présentes. Pas de Fon, Yoruba, Bariba.

**Fichier concerné :**
```typescript
// i18n/index.ts
type Locale = 'fr' | 'en';  // Pas de 'fon', 'yo', 'bba'
```

**Impact :** 40%+ des parents au Bénin ont le français comme langue seconde.

### 🟡 IC-5 : Pas d'API ouverte pour partenariats MEMP/ONG

**Problème :** L'API est interne uniquement. Pas de documentation publique, pas de clés API pour partenaires.

**Cas d'usage bloqués :**
- Plan International voulant synchroniser les progrès
- Projet "École Numérique" du MEMP pour tableau de bord national
- UNICEF pour statistiques agrégées (anonymisées)

### 🟡 IC-6 : Pas de USSD fallback

**Problème :** Les feature phones (40% du parc au Bénin) ne peuvent pas utiliser l'app web. Pas de service USSD (*123# style) pour consulter les scores ou payer.

### 🟡 IC-7 : Pas d'intégration avec groupes WhatsApp existants

**Problème :** Les enseignants créent déjà des groupes WhatsApp classe. L'app ne propose pas de "Partager sur WhatsApp" pour les résultats hebdomadaires.

---

## Roadmap d'Intégration

### Phase 1 : Mobile Money Natif (6 semaines)

| Semaine | Action | Livrable |
|---------|--------|----------|
| 1-2 | Intégration MTN MoMo API | `MTNMoMoProvider` avec sandbox |
| 3 | Intégration Moov Money API | `MoovMoneyProvider` |
| 4 | Micro-paiements | Plans "1 jour" (100 FCFA), "1 semaine" (500 FCFA) |
| 5 | USSD Push | Déclenchement paiement depuis USSD |
| 6 | Tests end-to-end | Transactions réelles en sandbox |

**Coût estimé :**
- MTN MoMo API : Gratuit (sandbox), 1-2% par transaction (prod)
- Développement : 1 dev backend × 6 semaines

### Phase 2 : Export & Partage (4 semaines)

| Semaine | Action | Livrable |
|---------|--------|----------|
| 1 | Export CSV | `/teacher/classrooms/{id}/export/csv` |
| 2 | Génération PDF | Rapport PDF léger (jsPDF) des résultats |
| 3 | Share WhatsApp | `share/whatsapp?text=...` avec template |
| 4 | Notifications WhatsApp Business | Intégration WhatsApp Business API |

### Phase 3 : Multilinguisme & API Ouverte (6 semaines)

| Semaine | Action | Livrable |
|---------|--------|----------|
| 1-2 | Traductions Fon | `fon.json` avec traducteur natif |
| 3 | Traductions Yoruba | `yo.json` |
| 4 | Documentation API | Swagger public + clés API partenaires |
| 5 | Webhooks partenaires | `/webhooks/partners/{org}` (Plan, UNICEF) |
| 6 | Agrégation anonymisée | Endpoints statistiques pour MEMP |

---

## Standards à Implémenter

### Mobile Money APIs

| Fournisseur | Documentation | Difficulté |
|-------------|---------------|------------|
| **MTN MoMo API** | `https://momodeveloper.mtn.com` | Moyenne (OAuth2) |
| **Moov Money (Flooz)** | API propriétaire | Moyenne |
| **KKiaPay** (actuel) | `https://docs.kkiapay.me` | Facile (REST) |

**Exemple MTN MoMo API :**
```python
class MTNMoMoProvider(PaymentProviderBase):
    """MTN Mobile Money API v1"""
    BASE_URL = "https://sandbox.momodeveloper.mtn.com"
    
    async def create_transaction(self, amount, description, callback_url):
        # 1. Récupérer token OAuth2
        # 2. POST /collection/v1_0/requesttopay
        # 3. Polling ou webhook pour confirmation
        pass
```

### SMS Providers Afrique

| Provider | Couverture Bénin | Coût SMS |
|----------|------------------|----------|
| **Twilio** (actuel) | Bonne | ~15 FCFA |
| **Africa's Talking** | Excellente | ~8 FCFA |
| **Hubtel** (Ghana) | Régionale | ~10 FCFA |

**Recommandation :** Migrer vers Africa's Talking pour coût réduit de 50%.

### WhatsApp Business API

| Solution | Coût | Complexité |
|----------|------|------------|
| **Meta Business API** | Gratuit (1er niveau) | Élevée (vérification entreprise) |
| **Twilio WhatsApp** | Pay-per-message | Moyenne |
| **Clickatell** | Moyen | Facile |

**Solution frugale :** Lien `https://wa.me/?text=` (partage one-way gratuit) en Phase 2, puis API officielle en Phase 3.

### i18n Langues Locales

```typescript
// Extension i18n/index.ts
type Locale = 'fr' | 'en' | 'fon' | 'yo' | 'bba';

// Priorité traduction (par nombre de locuteurs) :
// 1. Fon (~4M locuteurs au Bénin)
// 2. Yoruba (~1M au Bénin, plus au Nigeria/Ghana)
// 3. Bariba (~1M)
```

---

## Opportunités Partenariats

| Organisation | Opportunité | Intégration technique |
|--------------|-------------|----------------------|
| **MEMP Bénin** | Tableau de bord national | API agrégée anonymisée |
| **Orange/MTN** | Zero-rating (data gratuite) | Packaging APK opérateur |
| **Plan International** | Suivi filles vulnérables | Webhook événements + alertes |
| **UNICEF** | Statistiques éducation | Export CSV mensuel |
| **Biasharys/ISOC BJ** | Hébergement local | Déploiement serveur Cotonou |
| **Fondation Mastercard** | Paiement scolaire | Intégration QR code Mobile Money |

---

## Métriques de Réussite

| KPI | Actuel | Cible 6 mois |
|-----|--------|--------------|
| Canaux paiement | 2 (KKiaPay, FedaPay) | 4 (+MTN MoMo, Moov direct) |
| Langues supportées | 2 (fr, en) | 4 (+Fon, Yoruba) |
| Formats export | 0 | 2 (CSV, PDF) |
| Canaux notification | 3 (in-app, SMS, push) | 4 (+WhatsApp) |
| Partenaires API intégrés | 0 | 2+ |
| Taux utilisation Mobile Money | ~60% | 85% |

---

## Recommandations Immédiates (Low-cost)

1. **Cette semaine :** Ajouter bouton "Partager sur WhatsApp" dans parent dashboard
2. **Cette semaine :** Créer fichier `fon.json` avec 20 phrases essentielles (authentification)
3. **Ce mois :** S'inscrire aux sandbox MTN MoMo API et Moov Money
4. **Ce mois :** Implémenter export CSV basique pour salles de classe

---

*Audit réalisé le 12 avril 2026*
*Références : MTN MoMo API docs, FedaPay docs, WhatsApp Business API guidelines*
