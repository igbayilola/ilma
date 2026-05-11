# Runbook — Notification APDP / RGPD en cas de violation de données

> **Objectif** : encadrer la réponse à une violation de données personnelles
> conformément à la **Loi 2017-20 (Bénin)** et au **RGPD** lorsque des utilisateurs
> de l'UE sont concernés. Notification à l'**APDP (Autorité de Protection des
> Données Personnelles)** sous **72 h** après prise de conscience.
>
> Ce runbook complète la section 3 « Violation de Données » de
> [`INCIDENT_RESPONSE.md`](./INCIDENT_RESPONSE.md). Utilise-le dès qu'un incident
> implique des **données personnelles** (élèves, parents, paiements, identifiants).

## Périmètre — qu'est-ce qu'une violation ?

Une violation = atteinte à la confidentialité, intégrité ou disponibilité de
données personnelles. Cas typiques sur Sitou :

- Fuite de la table `users` (emails, hashed_passwords, téléphones)
- Accès non autorisé à des profils élèves (mineurs → **risque élevé** systématique)
- Compromission d'un compte admin éditorial
- Perte/vol d'un backup non chiffré
- Bug applicatif exposant des données d'un compte à un autre (IDOR)
- Compromission d'un fournisseur tiers (KKiaPay, FedaPay, Sentry) si données partagées

## Horloge — T0 = prise de conscience

| Échéance | Action | Owner |
|---|---|---|
| **T0 + 1 h** | Déclarer l'incident, ouvrir le canal de crise (Slack `#incident`, war room) | Tech Lead |
| **T0 + 4 h** | Contenir : isoler, révoquer tokens, snapshot logs | Tech Lead + DPO |
| **T0 + 24 h** | Évaluation initiale documentée (nature, volume, populations) | DPO |
| **T0 + 48 h** | Décision : risque élevé pour les personnes ? Si oui → préparer notif utilisateurs | DPO + Direction |
| **T0 + 72 h** | **Notification APDP** envoyée (obligatoire, même si l'évaluation est partielle) | DPO |
| **T0 + 72 h** | Notification utilisateurs concernés si risque élevé | DPO + Comms |
| **T0 + 30 j** | Post-mortem publié, mesures correctives validées | Tech Lead |

⚠️ **Si l'évaluation n'est pas finalisée à T+72 h** : envoyer quand même la notif
APDP avec les éléments disponibles + indiquer « complément à suivre sous X jours ».
Mieux notifier incomplet que tard.

## Étapes opérationnelles

### 1. Contenir (T0 → T0 + 4 h)

```bash
# Isoler le service compromis (couper accès externe)
docker compose stop api  # ou bloquer via Nginx upstream

# Snapshot des logs (audit + applicatif)
docker exec sitou-db pg_dump -U sitou_user -d sitou_db -t audit_logs > /var/incidents/audit_$(date +%Y%m%d_%H%M%S).sql
docker compose logs api > /var/incidents/api_$(date +%Y%m%d_%H%M%S).log
docker compose logs nginx > /var/incidents/nginx_$(date +%Y%m%d_%H%M%S).log

# Geler l'état de la DB
docker exec sitou-db pg_dump -U sitou_user -d sitou_db | gzip > /var/incidents/db_snapshot_$(date +%Y%m%d_%H%M%S).sql.gz

# Révoquer tokens : rotation SECRET_KEY → invalide tous les JWT
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
# → mettre à jour .env, restart api
```

### 2. Évaluer (T0 + 4 h → T0 + 24 h)

Documenter dans `/var/incidents/<id>/evaluation.md` :

- **Nature** : confidentialité / intégrité / disponibilité
- **Origine** : externe (attaque) / interne (erreur humaine, bug)
- **Catégories** : identifiants, contacts, données scolaires, paiements,
  données de santé (état de stress mineurs ?)
- **Volume** : nombre d'utilisateurs, lignes exposées
- **Populations** : élèves (mineurs ↑ risque), parents, enseignants, admin
- **Risque** : faible / modéré / **élevé** (mineurs + données scolaires = élevé par défaut)
- **Conséquences** : usurpation, discrimination, perte financière, harcèlement
- **Mesures de protection en place avant l'incident** : chiffrement at rest,
  hashed_password, RBAC, audit logs, etc.

### 3. Notifier l'APDP (avant T0 + 72 h)

**Canal** : voir [https://apdp.bj](https://apdp.bj) section « notifier une violation »
ou email à `notification@apdp.bj` (vérifier l'adresse à jour avant l'incident).

**Template à compléter** (français) :

```
Objet : Notification de violation de données — Sitou (Article 392 Loi 2017-20)

Madame, Monsieur,

Conformément à la Loi 2017-20 portant code du numérique en République du Bénin
(article 392) et au RGPD (article 33), nous vous notifions une violation de
données personnelles affectant la plateforme éducative Sitou.

1. Identification du responsable du traitement
   - Entité : [Raison sociale]
   - Adresse : [Adresse]
   - DPO : [Nom], [email DPO], [téléphone]

2. Description de la violation
   - Date de prise de conscience : [JJ/MM/AAAA HH:MM TZ]
   - Date présumée du début : [JJ/MM/AAAA] (ou « inconnue »)
   - Nature : [confidentialité / intégrité / disponibilité]
   - Origine probable : [externe / interne / inconnue]

3. Catégories et volume
   - Catégories de données : [identifiants, contacts, données scolaires, …]
   - Nombre estimé de personnes concernées : [N]
   - Catégories de personnes : [élèves mineurs / parents / enseignants / admin]

4. Conséquences probables
   - [Décrire : risque d'usurpation, exposition de données scolaires, …]

5. Mesures déjà mises en œuvre
   - [Isolement, révocation tokens, rotation secrets, audit, …]

6. Mesures correctives prévues
   - [Patch, durcissement, audit externe, …]

7. Notification des personnes concernées
   - [Prévue le …] / [Non requise car risque faible, justification : …]

Pièces jointes :
- Chronologie détaillée de l'incident
- Extrait d'audit logs
- Analyse d'impact

Cordialement,
[Nom], DPO Sitou
```

### 4. Notifier les utilisateurs (si risque élevé)

**Critère de risque élevé** : mineurs concernés ET (identifiants + contacts) OU
(données scolaires) OU paiements. Sur Sitou, **toute violation impliquant des
élèves est par défaut un risque élevé**.

**Canaux** :
- SMS parents (numéro vérifié dans `users.phone`)
- Email parent + élève (si email vérifié)
- Bannière in-app au prochain login
- Communiqué public si > 10 % de la base concernée

**Template SMS parent** (160 car max, FR-FR, ton calme) :

```
Sitou: une partie de vos donnees a ete exposee ([type]) le [date].
Aucune action requise/[action requise]. Details: sitou.app/breach/[id].
Questions: dpo@sitou.bj
```

**Template email parent** (placer dans `app/templates/email/breach_notification.html`) :

```
Sujet : Information importante concernant la sécurité de votre compte Sitou

Bonjour [Prénom parent],

Le [date], nous avons détecté un incident de sécurité affectant votre compte
Sitou (et celui de votre/vos enfant(s) [prénoms]).

Ce qui s'est passé :
[Description en langage simple, 2-3 phrases]

Données concernées :
- [Liste claire]

Données NON concernées (rassurer) :
- Mots de passe (stockés chiffrés, non lisibles)
- Paiements (gérés par notre prestataire et non exposés)
- [...]

Ce que vous devez faire :
1. [Action immédiate, si applicable — changer mot de passe, vérifier compte]
2. Activer la double authentification : [lien]
3. Rester vigilant face aux tentatives d'hameçonnage usurpant Sitou

Ce que nous faisons :
- [Mesures techniques + organisationnelles déjà en place]
- Audit externe en cours par [cabinet]
- Notification de l'APDP effectuée le [date]

Nous présentons nos excuses pour cet incident et restons à votre disposition :
- DPO : dpo@sitou.bj
- Support : aide@sitou.bj
- Téléphone : +229 XX XX XX XX (lun-ven 8h-18h)

L'équipe Sitou
```

### 5. Tracer (log d'incident)

Créer `/var/incidents/<id>/index.md` :

```markdown
# Incident #YYYY-NNN

| Champ | Valeur |
|---|---|
| ID | YYYY-NNN |
| Statut | DETECTED / CONTAINED / NOTIFIED / RESOLVED |
| Sévérité | P0 / P1 / P2 |
| T0 (prise de conscience) | YYYY-MM-DD HH:MM TZ |
| T_containment | … |
| T_apdp_notified | … |
| T_users_notified | … |
| T_resolved | … |
| Personnes concernées | N (dont M mineurs) |
| Données | [liste] |
| Cause racine | [analyse 5 pourquoi] |
| Owner | [Nom] |
| Commit du fix | [SHA] |
| Post-mortem | [lien] |

## Timeline détaillée
- T0+00:00 : …
- T0+00:15 : …

## Décisions clés
- …

## Actions correctives
- [ ] Patch déployé (PR #…)
- [ ] Test de régression ajouté
- [ ] Hardening (rate limiting, audit, …)
- [ ] Communication parents envoyée
- [ ] Notification APDP envoyée + accusé reçu
- [ ] Post-mortem publié
```

### 6. Post-mortem (T0 + 30 j max)

Format blameless. À publier dans `docs/postmortems/YYYY-NNN.md`. Doit
répondre à :

1. **Quoi** — chronologie factuelle
2. **Impact** — qui, combien, combien de temps, conséquences mesurées
3. **Cause racine** — 5 pourquoi, pas un nom de personne
4. **Détection** — comment on a su, combien de temps après le début
5. **Réponse** — ce qui a marché, ce qui n'a pas marché
6. **Action items** — chacun assigné + daté

## Données spécifiques mineurs (loi 2017-20 art. 408)

Les élèves de Sitou sont **mineurs** par défaut (CM2 ≈ 10-12 ans). Cela durcit
les obligations :

- **Consentement** : parental, vérifié à l'inscription (`Profile.parent_consent_at`)
- **Effacement** : sur demande parentale, sans condition (`User.scheduled_purge_at`)
- **Notification** : seuil de risque abaissé — toujours notifier les parents
  en cas de violation impliquant des données d'élève
- **Pas de profilage publicitaire** : aucun usage marketing de ces données

## Contacts d'urgence (à maintenir à jour)

| Rôle | Contact | Backup |
|---|---|---|
| Tech Lead (ouverture incident) | [à renseigner] | [à renseigner] |
| DPO Sitou | dpo@sitou.bj | +229 XX XX XX XX |
| APDP Bénin (notification) | notification@apdp.bj | https://apdp.bj |
| CERT-BJ (si attaque externe) | cert@bj.cert | +229 XX XX XX XX |
| Hébergeur | [contact OVH/Scaleway/Azure] | … |
| Avocat (si litige) | [cabinet] | … |

## Checklist post-incident

- [ ] Logs archivés et chiffrés (≥ 1 an de rétention)
- [ ] Mots de passe / tokens compromis rotated
- [ ] Patch déployé en production
- [ ] Test de non-régression ajouté
- [ ] APDP notifiée + accusé de réception archivé
- [ ] Utilisateurs notifiés (SMS + email) si risque élevé
- [ ] Post-mortem publié dans 30 j
- [ ] Runbook mis à jour avec les enseignements
- [ ] Action items trackés dans `ROADMAP_90D.md` ou Linear

## Références

- [Loi 2017-20 du Bénin — Code du numérique](https://apdp.bj/textes)
- [RGPD art. 33 — Notification à l'autorité de contrôle](https://www.cnil.fr/fr/reglement-europeen-protection-donnees)
- [`docs/legal/PRIVACY_POLICY.md`](../legal/PRIVACY_POLICY.md)
- [`docs/legal/DPO_CONTACT.md`](../legal/DPO_CONTACT.md)
- [`docs/runbooks/INCIDENT_RESPONSE.md`](./INCIDENT_RESPONSE.md) — section 3
