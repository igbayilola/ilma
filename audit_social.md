# Audit Social & Collaboration

## Résumé Exécutif

**Score Social : 4.5/10** — L'application privilégie l'apprentissage individuel avec quelques mécanismes compétitifs (classement global, défis 1v1) mais manque les dimensions communautaires essentielles à la culture béninoise : tutorat par les pairs, groupes d'étude locaux, communication parentale vocale, et gouvernance communautaire. L'approche est **transactionnelle** plutôt que **relationnelle**.

| Dimension | Existant | Adéquation Culturelle |
|-----------|----------|----------------------|
| Pair-learning | ❌ Absent | Critique — culture entraide |
| Groupes étude | ❌ Absent | Important — tontines éducation |
| Communication parents | ⚠️ SMS texte | Insuffisant — oralité dominante |
| Compétition | ✅ Leaderboard global | Risqué — démotivant faibles niveaux |
| Modération | ❌ Absente | Critique — sécurité jeunes |
| Enseignant facilitateur | ⚠️ Assignations | Limité — pas de défis groupe |

---

## État des Lieux Fonctionnalités

### Fonctionnalités Sociales Implémentées

```
┌─────────────────────────────────────────────────────────────┐
│  SOCIAL EXISTANT                                            │
├─────────────────────────────────────────────────────────────┤
│  ✅ Weekly Leaderboard (global, pseudonymisé)               │
│     • Top 20 + position perso                               │
│     • Historique 4 semaines                                 │
│                                                             │
│  ✅ Défis 1v1 (ami à ami)                                   │
│     • Création via partage lien                             │
│     • Durée 24h                                             │
│     • Score comparatif                                      │
│                                                             │
│  ✅ Salles de classe (teacher-centric)                      │
│     • Code invitation 8 caractères                          │
│     • Assignations par enseignant                           │
│     • Suivi progrès classe                                  │
│                                                             │
│  ❌ Absents :                                               │
│     • Chat / messagerie                                     │
│     • Groupes pairs (4-5 élèves)                            │
│     • Synchronisation proximité (offline)                   │
│     • Vocal parents                                         │
│     • Système modération                                    │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Technique

```python
# social.py - modèles existants
class WeeklyLeaderboard:
    profile_id, week_iso, xp_earned, pseudonym  # Global

class Challenge:
    challenger_id, challenged_id, skill_id, status  # 1v1 uniquement

# PAS DE :
# - StudyGroup (groupe d'étude)
# - PeerTutoring (tutorat)
# - VoiceMessage (vocal)
# - ModerationReport (signalement)
```

---

## Insuffisances Culturelles

### 🔴 IC-1 : Application purement individuelle, contradictoire avec pédagogie par entraide

**Problème :** Chaque élève progresse seul. Pas de mécanisme pour qu'un élève excellent CM2 aide un CE2 ou un CM1 en difficulté.

**Culture béninoise :**
- "L'école de la vie" = entraide inter-âges
- Grands frères/sœurs aident les plus jeunes
- Classes surchargées (60-90 élèves) nécessitent tutorat pair-à-pair

**Code manquant :**
```python
# PAS IMPLEMENTÉ
class PeerTutoring:
    tutor_id          # CM2 excellent
    tutee_id          # CE2/CM1
    skill_id          # Compétence cible
    status            # matched | active | completed
    sessions_count    # Nombre séances
    tutor_badge       # Badge "Grand Frère Numérique"
```

### 🔴 IC-2 : Pas de "cellules de révision" digitales

**Problème :** Pas de groupes d'étude localisés (quartier/village). Pas de synchronisation offline-to-offline.

**Besoin terrain :**
- 4-5 élèves du même quartier se réunissent après l'école
- Un a accès à l'app, les autres regardent
- Synchronisation des progrès quand l'un va en ville (connectivité)

**Technologie manquante :**
```javascript
// PAS IMPLEMENTÉ - Web Bluetooth / Web NFC
const studyGroup = {
  syncViaBluetooth: async () => {},  // P2P sans internet
  shareProgress: async () => {},      // Diffusion locale
  offlineCollaboration: true          // Sans réseau
};
```

### 🔴 IC-3 : Leaderboard global démotivant

**Problème :** Classement national/global où les meilleurs écrasent les autres. Pas de segmentation par école/quartier/niveau.

**Effet pervers :**
- Élève classé #15,847/20,000 → découragement
- Pas de visibilité sur les progrès relatifs (école locale)

**Actuel :**
```python
# leaderboard.py - requête actuelle
select * from weekly_leaderboard 
where week_iso = '2026-W11' 
order by xp_earned desc  # GLOBAL
limit 20
```

**Devrait être :**
```python
# Segmentation locale
where week_iso = '2026-W11' 
  AND school_id = ?          # Même école
  OR neighborhood_id = ?     # OU même quartier
order by xp_earned desc
```

### 🔴 IC-4 : Pas de support vocal pour parents

**Problème :** Dashboard parent 100% texte. Parents analphabètes ou semi-lettrés exclus.

**Communication actuelle :**
- SMS texte : "Votre enfant a obtenu 75% cette semaine"
- Notifications push écrites

**Besoin :**
- Messages vocaux WhatsApp
- Synthèse vocale dashboard (TTS)
- Notes vocales parents → enseignants

### 🔴 IC-5 : Absence totale de modération communautaire

**Problème :** Pas de système de signalement pour :
- Cyber-harcèlement (défis humiliants)
- Triche (partage réponses)
- Contenu inapproprié dans pseudonymes

**Risque :** Pseudonymes comme "StupidCaméléon" ou défi "Qui est le plus nul ?"

**Système manquant :**
```python
class ModerationReport:
    reporter_id
    reported_content_type  # pseudonym | challenge | ...
    reason                 # insult | cheating | inappropriate
    status                 # pending | reviewed | action_taken
    
class CommunityModerator:  # Délégués numériques
    profile_id
    classroom_id
    elected_at             # Élu par les pairs
```

### 🟡 IC-6 : Pas de valorisation de l'effort

**Problème :** SmartScore et XP basés uniquement sur résultats. Pas de badges "Persévérance", "Progression", "Aide aux autres".

**Culture béninoise :** "C'est l'effort qui compte" (adage local)

### 🟡 IC-7 : Enseignant transmetteur, pas facilitateur

**Problème :** L'enseignant assigne des exercices (top-down). Pas de création de "défis groupe" où la classe collabore.

**Exemple manquant :**
- "Défi Classe : 80% de réussite collective sur les fractions"
- Progression commune, pas individuelle

---

## Recommandations Culturellement Adaptées

### 1. Mode "Grand Frère Numérique" (Tutorat Pair-à-Pair)

```python
# peer_tutoring.py
class PeerTutoringService:
    async def match_tutor_tutee(self, db, school_id):
        """
        Algorithme simple (pas ML complexe) :
        - Top 20% CM2 sur compétence X → proposé comme tuteur
        - Bottom 30% CE2/CM1 sur même compétence → tuteur assigné
        """
        pass
    
    async def record_tutoring_session(self, db, tutor_id, tutee_id, skill_id):
        """
        Session enregistrée quand :
        - Tuteur explique via app (audio/screenshare)
        - Tutee progresse de 10+ points SmartScore
        """
        # Badge "Grand Frère" / "Grande Sœur" débloqué
        pass
```

**Interface :**
```
┌──────────────────────────────────────┐
│  DEVIENS GRAND FRÈRE NUMÉRIQUE       │
├──────────────────────────────────────┤
│                                      │
│  Tu excelles en Division (95%)      │
│                                      │
│  3 élèves de ton école ont besoin   │
│  d'aide sur cette compétence        │
│                                      │
│  [🎓 Proposer mon aide]              │
│                                      │
│  Récompense : Badge Or + 500 XP     │
└──────────────────────────────────────┘
```

### 2. Synchronisation Proximité (Web Bluetooth)

```javascript
// offlineStudyGroup.ts
class OfflineStudyGroup {
  async createGroup() {
    // Créer groupe Bluetooth local
    const device = await navigator.bluetooth.requestDevice({
      acceptAllDevices: true
    });
  }
  
  async syncProgressToPeers() {
    // Broadcast progrès aux pairs proches
    // Sans connexion internet
    for (const peer of this.peers) {
      await this.sendEncryptedProgress(peer);
    }
  }
}
```

**Cas d'usage :**
1. 4 élèves à la maison du voisin (pas de réseau)
2. Un fait l'exercice sur son téléphone
3. Les autres suivent, participent
4. Progrès synchronisés P2P via Bluetooth
5. Quand l'un va au marché (réseau), tout upload

### 3. Classements Locaux (École/Quartier)

```python
# leaderboard_local.py
async def get_local_leaderboard(
    db, 
    profile_id, 
    scope='school'  # 'school' | 'neighborhood' | 'classroom'
):
    """
    Classement contextualisé pour motivation positive
    """
    if scope == 'school':
        # Top 10 de l'école
        pass
    elif scope == 'neighborhood':
        # Top 10 du quartier (même code postal)
        pass
    elif scope == 'classroom':
        # Classement classe virtuelle
        pass
```

**Interface onglets :**
```
┌───────────────────────────────────────────────┐
│  🏆 CLASSEMENT                                │
├──────────┬──────────┬──────────┬─────────────┤
│  Mon École │ Quartier │  Bénin   │  Historique │
│     ●      │          │          │             │
├──────────┴──────────┴──────────┴─────────────┤
│  #1  Kofi        🥇  1,250 XP                │
│  #2  Ami         🥈  1,180 XP   (Toi)        │
│  #3  Kossi       🥉  1,050 XP                │
│  ...                                          │
│  #8  Awa           890 XP      👏 Progrès +5 │
└───────────────────────────────────────────────┘
```

### 4. Interface Parentale Vocale

```typescript
// ParentVoiceDashboard.tsx
const sendVoiceSummaryToWhatsApp = async (parentPhone: string, childData) => {
  const summary = generateVoiceSummary(childData); // TTS
  
  // Générer lien WhatsApp avec résumé vocal
  const whatsappUrl = `https://wa.me/${parentPhone}?text=${encodeURIComponent(
    "🎓 Résumé hebdomadaire SITOU\n\n" +
    "[Audio] Votre enfant a progressé cette semaine. " +
    "Cliquez pour écouter le détail."
  )}`;
  
  // Ou utiliser WhatsApp Business API pour envoi direct
};
```

**Dashboard parent simplifié :**
```
┌─────────────────────────────────────────┐
│  👨‍👩‍👧 PROGRESSION DE KOFI                │
├─────────────────────────────────────────┤
│                                         │
│  [🔊 ÉCOUTER LE RÉSUMÉ]                 │
│                                         │
│  Cette semaine :                        │
│  ⭐⭐⭐☆☆  (3/5 étoiles)                 │
│                                         │
│  📚 Maths : Très bien                   │
│  📖 Français : Continue l'effort        │
│                                         │
│  [💬 ENVOYER UN MOT À L'ENSEIGNANT]     │
│     (note vocale)                       │
└─────────────────────────────────────────┘
```

### 5. Gouvernance Communautaire (Délégués Numériques)

```python
# community_moderation.py
class CommunityGovernance:
    async def elect_class_delegate(self, db, classroom_id):
        """
        Élection annuelle d'un "Délégué Numérique" par les pairs
        Responsabilités :
        - Modérer pseudonymes de la classe
        - Valider défis entre amis
        - Signaler comportements inappropriés
        """
        pass
    
    async def report_content(self, db, reporter_id, content_type, content_id, reason):
        """
        Signalement par communauté, review par :
        1. Délégué numérique (élève)
        2. Enseignant si non résolu
        3. Admin si grave
        """
        pass
```

### 6. Défis de Classe Collaboratifs

```python
# collaborative_challenges.py
class CollaborativeChallenge:
    """
    Toute la classe travaille vers un objectif commun
    """
    classroom_id: UUID
    skill_id: UUID
    target_collective_score: int  # Ex: 80% moyenne classe
    deadline: datetime
    reward: str  # "Badge Classe Unie" + 100 XP chacun
    
    async def calculate_collective_progress(self):
        # Moyenne des scores individuels
        pass
```

---

## Plan de Déploiement Social

### Phase 1 : Fondation Sociale (4 semaines)

| Semaine | Fonctionnalité | Stack |
|---------|----------------|-------|
| 1 | Badges "Aide aux autres" | Backend + frontend |
| 2 | Leaderboard école/quartier | SQL + filtres géo |
| 3 | Signalement contenu (basique) | DB + notifications |
| 4 | Dashboard parent TTS | Web Speech API |

### Phase 2 : Pair-Learning (6 semaines)

| Semaine | Fonctionnalité | Stack |
|---------|----------------|-------|
| 5-6 | Matching tuteur/tutoré | Algo règles simples |
| 7-8 | Interface tutorat (audio) | WebRTC ou audio notes |
| 9-10 | Badges "Grand Frère" | Gamification |

### Phase 3 : Collaboration Locale (6 semaines)

| Semaine | Fonctionnalité | Stack |
|---------|----------------|-------|
| 11-12 | Web Bluetooth P2P | Experimental API |
| 13-14 | Défis classe collaboratifs | Backend + frontend |
| 15-16 | Délégués numériques | Élection + permissions |

---

## Métriques de Succès

| KPI | Actuel | Cible 6 mois |
|-----|--------|--------------|
| Sessions tutorat P2P | 0 | 30% élèves aidés |
| Utilisation leaderboard local | N/A | 60% préfèrent local vs global |
| Parents utilisant vocal | 0 | 40% |
| Signalements résolus par délégués | N/A | 80% |
| Défis collaboratifs créés | 0 | 5/classe/trimestre |

---

## Actions Immédiates

1. **Cette semaine :** Ajouter filtre "Mon école" au leaderboard existant
2. **Cette semaine :** Badge "Premier aidant" quand élève explique à un autre
3. **Ce mois :** Formulaire signalement basique (3 options : insulte | triche | autre)
4. **Ce mois :** Bouton "Écouter mon résumé" sur dashboard parent

---

*Audit réalisé le 12 avril 2026*
*Méthodologie : Analyse codebase + benchmarks social learning contexte africain*
