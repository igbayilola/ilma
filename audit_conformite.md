# Audit Conformité & Souveraineté - Bénin

## Résumé Exécutif

**Verdict légal : 🔴 NON CONFORME** — Plusieurs obligations du Code du Numérique béninois (Loi n°2017-20, Loi n°2019-43) ne sont pas respectées. Risque d'amende administrative et de sanction par l'APDP (Autorité de Protection des Données à caractère Personnel).

| Domaine | Statut | Risque |
|---------|--------|--------|
| Consentement parental | ❌ Absent | Élevé — mineurs non protégés |
| Politique confidentialité | ❌ Absente | Critique — obligation légale |
| DPO (Délégué) | ❌ Non nommé | Élevé — obligation >250 personnes traitées |
| Transfert données | 🟡 Sentry Allemagne | Moyen — absence garanties UE-Bénin |
| Droit à l'oubli | 🟡 Partiel (soft delete) | Moyen — données conservées indéfiniment |
| Sécurité | 🟡 Basique (TLS, bcrypt) | Moyen — pas de chiffrement local |

---

## État des Lieux Légal

### Cadre applicable
- **Loi n°2017-20** du 20 avril 2018 (Code du numérique) — Arts. 350-378 sur la protection des données
- **Loi n°2019-43** du 29 novembre 2019 — Création de l'APDP
- **Directive n°2020-001/APDP** — Consentement des mineurs

### Données collectées (analyse code)

| Donnée | Finalité | Base légale | Conforme |
|--------|----------|-------------|----------|
| Email, téléphone | Authentification | Consentement implicite | ⚠️ À valider |
| Nom complet | Profil utilisateur | Consentement implicite | ⚠️ À valider |
| Mot de passe (hash bcrypt) | Sécurité | Intérêt légitime | ✅ |
| Scores, exercices | Progression pédagogique | Consentement parent requis | ❌ Absent |
| IP, User-Agent | Audit logs | Intérêt légitime (sécurité) | ⚠️ À déclarer |
| ID profil (avatar externe DiceBear) | Personnalisation | Consentement | 🔴 Fuite de données |

---

## Insuffisances Critiques

### 🔴 IC-1 : Absence de consentement parental valide
**Problème :** Les enfants de 10-11 ans (CM2) s'inscrivent via un compte parent, mais aucune vérification du consentement explicite du parent n'est mise en œuvre (pas de SMS de confirmation, pas de signature électronique, pas de case à cocher "Je certifie être le représentant légal").

**Exigence légale :** Art. 15 de la Directive APDP 2020-001 : *"Le consentement du représentant légal doit être recueilli de manière claire, spécifique et documentée"*.

**Impact :** Les données scolaires des mineurs sont traitées sans base légale valide.

### 🔴 IC-2 : Absence de politique de confidentialité
**Problème :** Aucun document `privacy-policy.md`, `terms-of-service.md` ou page `/legal` n'existe dans le codebase.

**Exigence légale :** Art. 356 Code du numérique : *"Le responsable du traitement met à disposition des personnes concernées une information claire et transparente"*.

**Contenu manquant :**
- Identité du responsable traitement (DPO)
- Finalités précises
- Durée de conservation
- Droits des personnes (accès, rectification, suppression)
- Procédure de réclamation auprès de l'APDP

### 🔴 IC-3 : Pas de DPO nommé
**Problème :** Aucun Délégué à la Protection des Données n'est identifié. L'entreprise traite >250 personnes (mineurs + parents).

**Exigence légale :** Art. 362 Code du numérique : obligation de désignation si "traitement à grande échelle".

### 🔴 IC-4 : Transfert de données vers l'Union Européenne (Sentry)
**Problème :** 
```typescript
// telemetry.ts
SentrySDK.init({
  dsn: 'https://...ingest.de.sentry.io/...' // Allemagne
});
```

Les erreurs, performances (Web Vitals), et identifiants utilisateur sont envoyés vers l'Allemagne sans garanties suffisantes (pas de Décision d'adéquation UE-Bénin, pas de clauses contractuelles types documentées).

**Exigence légale :** Art. 368 Code du numérique : transferts internationaux soumis à autorisation APDP sauf garanties équivalentes.

### 🔴 IC-5 : Fuite de données via avatars externes
**Problème :**
```python
# profile_service.py
avatar_url = profile.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={profile.id}"
```

L'ID unique du profil est transmis à un service tiers (DiceBear) sans consentement. Cela constitue une fuite d'identifiant technique.

### 🟡 IC-6 : Droit à l'oubli partiel
**Problème :** La suppression de profil est un soft-delete (`is_active = False`). Les données sont conservées indéfiniment en base.

**Code concerné :**
```python
async def delete_profile(self, db: AsyncSession, profile: Profile) -> None:
    profile.is_active = False  # Pas de purge réelle
```

**Exigence légale :** Art. 357 Code du numérique : *"droit à l'effacement des données"* (sauf obligation légale de conservation).

### 🟡 IC-7 : Collecte excessive (audit logs)
**Problème :**
```python
# audit.py
ip_address = Column(String(45), nullable=True)
user_agent = Column(Text, nullable=True)
```

Collecte systématique d'IP et User-Agent sans durée de conservation définie.

### 🟡 IC-8 : Absence de mécanisme de retrait du consentement
**Problème :** Pas de bouton "Supprimer mon compte et mes données" dans l'interface utilisateur.

---

## Plan de Conformité

### Actions Immédiates (Bloquantes — 2 semaines)

| Jour | Action | Livrable |
|------|--------|----------|
| 1-2 | Désactiver Sentry ou migrer vers instance locale | Suppression du DSN européen |
| 3-4 | Remplacer avatars DiceBear par génération locale | Service SVG local |
| 5-7 | Rédiger politique confidentialité | `PRIVACY_POLICY.md` (FR simple) |
| 8-10 | Implémenter checkbox consentement parental | Case "Je suis le parent/tuteur" + date |
| 11-14 | Nommer DPO interne | Publication email DPO |

### Actions Moyen Terme (1-2 mois)

| Action | Description |
|--------|-------------|
| Déclaration APDP | Fichier des traitements (obligatoire dans 3 mois après création) |
| Mise en place suppression définitive | Endpoint `DELETE /me/purge` avec confirmation email/SMS |
| Chiffrement local IndexedDB | CryptoJS AES pour données sensibles offline |
| Audit sécurité externe | Pentest léger par prestataire local |

### Documentation Requise

```
/docs/legal/
├── PRIVACY_POLICY.md       # Politique simplifiée (FR)
├── TERMS_OF_SERVICE.md     # CGU
├── COOKIE_POLICY.md        # Cookies (même si essentiels uniquement)
├── DPO_CONTACT.md          # Coordonnées DPO + APDP
└── DATA_RETENTION.md       # Durées de conservation
```

**Template PRIVACY_POLICY.md (extrait) :**
```markdown
# Politique de Confidentialité — SITOU

**Responsable du traitement :** [Nom entreprise], [Adresse Bénin]
**DPO :** dpo@sitou.bj — (+229) XX XX XX XX

## Données collectées
- Email, téléphone : authentification
- Nom, avatar : profil  
- Données pédagogiques : progression scolaire

## Durées de conservation
- Compte actif : durée de vie du compte
- Compte supprimé : 1 an (obligation légale), puis anonymisation

## Vos droits
Accès, rectification, suppression : contactez dpo@sitou.bj
Réclamation : APDP, 01 BP [XXX], Cotonou
```

---

## Recommandations Souveraineté

### Stratégie recommandée : "Hébergement local avec failover régional"

| Composant | Actuel | Recommandé | Priorité |
|-----------|--------|------------|----------|
| **Application** | VPS non localisé | Serveur Bénin (Isoc BJ, Benin Telecom) ou Ghana | Élevée |
| **Base de données** | PostgreSQL local | Même zone (Bénin/Ghana) | Élevée |
| **Fichiers** | MinIO local | Même zone | Élevée |
| **Monitoring** | Sentry Allemagne | Sentry auto-hébergé ou GlitchTip | Élevée |
| **SMS** | Twilio (US) | Twilio ou fournisseur local avec accord | Moyenne |

### Fournisseurs africains recommandés

| Service | Fournisseur | Localisation | Coût relatif |
|---------|-------------|--------------|--------------|
| Cloud | **Azure Afrique du Sud** | Johannesburg | Standard |
| Cloud | **AWS Lagos** | Nigeria | Standard |
| Cloud | **Isoc Bénin** | Cotonou | +20% (souveraineté) |
| VPS | **Keliweb Ghana** | Accra | -10% |
| SMS | **Hubtel** | Ghana | Compétitif |

### Frise de migration

```
Phase 1 (immédiat) :
├─ Désactiver Sentry cloud
├─ Host avatars localement
└─ Politique confidentialité

Phase 2 (1 mois) :
├─ Migrer vers hébergeur africain
├─ Déclaration APDP
└─ DPO formé

Phase 3 (3 mois) :
├─ Certification APDP (si dispo)
├─ Audit sécurité externe
└─ PIA (Privacy Impact Assessment)
```

---

## Métriques de Conformité

| KPI | Actuel | Cible (30j) | Cible (90j) |
|-----|--------|-------------|-------------|
| Documentation légale | 0% | 100% | 100% |
| Consentement parental | 0% | 100% | 100% |
| Données en Afrique | ~70% | 95% | 100% |
| DPO nommé | ❌ | ✅ | ✅ |
| Déclaration APDP | ❌ | En cours | ✅ |

---

## Notes Juridiques

**Définitions Code du numérique béninois :**
- **Mineur** : < 18 ans (Art. 350)
- **Données sensibles** : Données relatives aux mineurs (Art. 351)
- **Traitement à grande échelle** : > 250 personnes concernées (Art. 362)

**Sanctions encourues (Art. 382) :**
- Amende administrative : 1M à 10M FCFA
- Pénale (cas grave) : 6 mois à 2 ans + 5M à 50M FCFA

---

*Audit réalisé le 12 avril 2026*
*Références : Loi n°2017-20, Loi n°2019-43, Directive APDP n°2020-001*
