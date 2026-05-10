# Audit Intelligence & Analytics

## Résumé Exécutif

**Score Analytics : 5.5/10** — Le système collecte des données pédagogiques pertinentes (SmartScore, tentatives, streaks) avec une architecture de batching efficace pour le contexte offline. Cependant, il souffre d'un excès de "vanity metrics" (DAU, MAU) au détriment d'insights actionnables pour les enseignants peu formés. Pas de détection prédictive du décrochage, pas de visualisations adaptées à l'analphabétisme partiel des parents.

| Dimension | Évaluation | Problème clé |
|-----------|------------|--------------|
| Collecte efficiente | ✅ Bon | Batching 30s, sendBeacon, offline-first |
| Pertinence KPIs | ⚠️ Moyen | Trop de métriques volume, pas assez de mastering |
| Détection risque | ❌ Absent | Pas d'alerte élève en décrochage |
| Dashboards enseignants | ⚠️ Moyen | Complexe, desktop-centric |
| Accessibilité parents | ❌ Faible | Pas de support vocal/analphabètes |
| Agrégation | ✅ Bonne | Cohorts, rétention, SmartScore |

---

## État des Lieux Data

### Collecte Implémentée

```python
# AnalyticsEvent - modèle de données
class AnalyticsEvent:
    event_type: str  # exercise_start, exercise_step_completed, hint_requested, 
                     # exercise_completed, drop_off, content_viewed
    profile_id: UUID
    session_id: UUID
    data: JSONB      # Payload flexible
    client_ts: datetime
    server_ts: datetime
```

### Batching & Offline Strategy (✅ Points forts)

```typescript
// Frontend: analytics.ts
const FLUSH_INTERVAL_MS = 30_000;  // 30s batch
const MAX_BATCH = 50;              // Limite taille payload
navigator.sendBeacon();            // Survie au close de tab
```

**Évaluation :** Architecture adaptée au contexte béninois :
- Pas de tracking temps réel continu
- Events stockés localement en queue
- Retry automatique en cas d'échec réseau
- Payloads JSON compressés naturellement par batch

### Progress Tracking (SmartScore)

| Métrique | Stockée | Utilisée | Pertinence |
|----------|---------|----------|------------|
| SmartScore | ✅ | ✅ | Excellente (mastering) |
| Streak | ✅ | ✅ | Bonne (engagement) |
| Tentatives totales | ✅ | ✅ | Correcte |
| Temps passé | ❌ | ❌ | Non tracké (bien) |
| Drop-off point | ✅ | ⚠️ | Partiellement exploité |

---

## Insuffisances Analytiques

### 🔴 IC-1 : Pas de détection prédictive du décrochage (At-Risk Students)

**Problème :** Aucun algorithme ne détecte les élèves risquant d'abandonner. Pas de règles métier simples ni de ML léger.

**Signaux manqués :**
- Absence +3 jours consécutifs
- Baisse de SmartScore >20 points en 1 semaine
- Drop-off récurrent sur même type d'exercice
- Pas de connexion depuis date d'échéance objectif hebdomadaire

**Code concerné :**
```python
# progress_service.py - pas de méthode detect_at_risk()
# parent_dashboard.tsx - health summary basique (green/orange/red)
# sans explication des facteurs de risque
```

**Impact :** Les enseignants ne peuvent pas intervenir proactivement.

### 🔴 IC-2 : Dashboards trop complexes pour connexion 2G / écrans petits

**Problème :** Le dashboard admin (`AdminAnalyticsPage.tsx`) charge 8 endpoints simultanés :
- KPIs globaux
- Stats questions
- Digest stats
- Engagement (avec time series 30j)
- Retention cohorts
- Conversion funnel
- Viralité
- Notification stats

**Taille estimée des payloads :** 50-100KB par chargement → **10-20s sur 2G**

**Visualisations complexes :**
- Funnel bars animées
- Sparklines DAU 30 jours
- Tables cohortes rétention

**Impact :** Inutilisable par des directeurs d'école avec smartphone basique.

### 🔴 IC-3 : Pas d'adaptation à l'analphabétisme partiel des parents

**Problème :** Les dashboards parent utilisent exclusivement du texte et des graphiques chiffrés.

**Dashboard actuel parent :**
```
"Score moyen : 75%"
"Temps cette semaine : 120min"
"Objectif : 150min"
```

**Cas d'usage bloqué :** Parents analphabètes ou semi-lettrés ne comprennent pas les pourcentages.

**Solutions manquantes :**
- Text-to-Speech pour les résumés
- Icônes universelles (emoji succès/attention/danger)
- Synthèse vocale WhatsApp

### 🔴 IC-4 : Alertes SMS non contextualisées

**Problème :** Les notifications existantes (`notification_tasks.py`) sont génériques :
```
"Votre enfant a atteint son objectif !"
"Nouveau badge débloqué !"
```

**Manque :**
- Alertes "Votre enfant n'a pas étudié depuis 3 jours"
- Propositions rattrapage : "Redémarrer avec une révision de 10min ?"
- SMS professeur : "3 élèves de votre classe sont en décrochage"

### 🟡 IC-5 : Pas de "Courbe d'oubli" adaptée (Spaced Repetition)

**Problème :** Le SmartScore décroit avec le temps (`last_decay_at`) mais sans logique pédagogique explicite.

**Modèle actuel :** Simple decay linéaire ou absence de rappel
**Modèle recommandé :** Algorithme SM-2 simplifié (Anki-like) adapté

**Rappels manquants :**
- "Réviser la division - vous risquez d'oublier dans 2 jours"
- Notification push intelligente basée sur performance passée

### 🟡 IC-6 : Export pour registres scolaires papiers

**Problème :** Aucun export format "livret scolaire béninois" (compétences du Socle Commun).

**Besoin identifié :** Directeurs ont besoin de :
- Taux de complétion par compétence CEP
- Liste des élèves "à risque" avec actions concrètes
- Format imprimable A4 pour dossiers papier

---

## Solutions Recommandées

### Architecture Data (Frugale)

```
┌─────────────────────────────────────────────────────────────┐
│  SMARTPHONE ÉLÈVE (Offline-first)                           │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │ SQLite Local │    │ Analytics    │                       │
│  │ (IndexedDB)  │◄───┤ Queue (50)   │                       │
│  └──────────────┘    └──────────────┘                       │
│         │                    │                              │
│         └──────┬─────────────┘                              │
│                │ Sync (nightly/batch)                       │
└────────────────┼────────────────────────────────────────────┘
                 │ (2G-friendly, gzip)
┌────────────────▼────────────────────────────────────────────┐
│  BACKEND - Analyse & Alertes                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Risk Scoring │───►│ SMS Alerts   │   │ Aggregation  │  │
│  │ (règles)     │    │ (Twilio)     │    │ (daily)      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### KPIs Pertinents à Implémenter

| KPI | Calcul | Usage |
|-----|--------|-------|
| **Index de persévérance** | Jours actifs / Jours écoulés × 100 | Détection motivation |
| **Taux de mastering** | Compétences >80% / Total tentées | Réussite scolaire |
| **Temps de réponse moyen** | Secondes par question (par type) | Difficulté perçue |
| **Régularité** | Écart-type heures de connexion | Habitude structurée |
| **Risque de décrochage** | Règle : absence 3j OU baisse 20pts | Intervention SMS |

### Algorithme de Détection (Règles Simples)

```python
# risk_detection.py - approche frugale
async def detect_at_risk_students(db: AsyncSession) -> list[AtRiskStudent]:
    """
    Détection basée sur règles métier (pas de ML complexe)
    """
    risks = []
    
    # Règle 1 : Absence 72h
    students = await get_students_inactive_since(db, hours=72)
    for s in students:
        risks.append(AtRiskStudent(
            profile_id=s.id,
            risk_level='high',
            reason='absence_72h',
            action='sms_parent_reactivation'
        ))
    
    # Règle 2 : Baisse performance
    declining = await get_students_declining(db, 
        smart_score_drop=20, 
        window_days=7
    )
    for s in declining:
        risks.append(AtRiskStudent(
            profile_id=s.id,
            risk_level='medium',
            reason='performance_drop',
            action='sms_teacher_support'
        ))
    
    # Règle 3 : Drop-off récurrent
    dropouts = await get_students_recurrent_dropout(db, 
        min_dropouts=3,
        window_days=7
    )
    for s in dropouts:
        risks.append(AtRiskStudent(
            profile_id=s.id,
            risk_level='high',
            reason='recurrent_dropout',
            action='propose_easier_exercise'
        ))
    
    return risks
```

### Dashboard Ultra-Léger Enseignant

```
┌─────────────────────────────────────────┐
│  CLASSE 5A - Vue d'ensemble             │
├─────────────────────────────────────────┤
│                                         │
│  🟢 En forme (12)   🔴 Alerte (3)       │
│  [▓▓▓▓▓▓▓▓▓▓]       [▓▓▓░░░░░░░]      │
│                                         │
│  🟡 Attention (5)                        │
│  [▓▓▓▓▓░░░░░]                           │
│                                         │
├─────────────────────────────────────────┤
│  ACTIONS SUGGÉRÉES :                    │
│  • Contacter Kofi (absent 4j)           │
│  • Aider Amina (division)               │
│  • Féliciter groupe vert                │
│                                         │
│  [📱 Envoyer SMS aux absents]           │
│  [📄 Export trimestriel]                │
└─────────────────────────────────────────┘
```

**Caractéristiques :**
- Chargement : 3 appels API max (<10KB)
- Visualisation : Emoji + barres ASCII
- Actions : Boutons contextuels one-tap
- Pas de graphiques complexes

### Dashboard Parent Vocal/Visuel

```typescript
// ParentVoiceSummary.tsx
const generateVoiceSummary = (health: ChildHealthDTO): string => {
    // Génération texte simple pour TTS
    if (health.status === 'green') {
        return "Bonjour ! Votre enfant {name} va bien. " +
               "Il a travaillé {minutes} minutes cette semaine. " +
               "Continuez comme ça !";
    }
    if (health.status === 'orange') {
        return "Attention : {name} n'a pas beaucoup travaillé " +
               "cette semaine. Essayez de l'encourager.";
    }
    return "Alerte : {name} risque de prendre du retard. " +
           "Contactez son enseignant ou proposez-lui de réviser.";
};

// Lecture audio via Web Speech API
const speakSummary = () => {
    const text = generateVoiceSummary(healthData);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    speechSynthesis.speak(utterance);
};
```

---

## Implémentation Data (Stack Frugale)

### Phase 1 : Détection Risque + SMS (3 semaines)

| Semaine | Tâche | Stack |
|---------|-------|-------|
| 1 | Algorithme règles basiques | Python + SQLAlchemy |
| 2 | SMS alerts automatiques | Twilio + APScheduler |
| 3 | Dashboard enseignant léger | React + recharts-lite |

### Phase 2 : Accessibilité Parents (3 semaines)

| Semaine | Tâche | Stack |
|---------|-------|-------|
| 4 | Résumés vocaux TTS | Web Speech API |
| 5 | Icônes universelles | Emoji + SVG simples |
| 6 | Export livret scolaire | jsPDF + CSV |

### Outils Recommandés

| Fonction | Solution | Coût |
|----------|----------|------|
| Analytics events | SQLite + batch upload | Gratuit |
| SMS | Twilio Africa's Talking | ~10 FCFA/SMS |
| TTS | Web Speech API (navigateur) | Gratuit |
| Graphiques SVG | D3-lite / custom SVG | Gratuit |
| Export PDF | jsPDF | Gratuit |

---

## Métriques de Succès

| KPI Actuel | KPI Cible (6 mois) |
|------------|-------------------|
| Élèves "at risk" détectés | 0 → 85% |
| Temps chargement dashboard | 15s → 3s (2G) |
| Parents utilisant TTS | 0 → 40% |
| Enseignants utilisant alertes | N/A → 60% |
| Taux de réactivation (SMS) | N/A → 25% |

---

## Recommandations Immédiates

1. **Cette semaine :** Implémenter règle simple "absence 3j → SMS parent"
2. **Cette semaine :** Ajouter bouton "🔊 Lire mon résumé" sur dashboard parent
3. **Ce mois :** Créer dashboard enseignant simplifié (3 métriques max)
4. **Ce mois :** Export CSV basique des élèves à risque pour directeurs

---

*Audit réalisé le 12 avril 2026*
*Méthodologie : Analyse codebase + benchmarks analytics contexte ressources limitées*
