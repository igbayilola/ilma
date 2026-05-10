# Audit Expérience Apprentissage - CM2 Bénin

## Résumé Exécutif

**Verdict global :** L'application présente une architecture solide avec une gestion offline robuste (SQLite via IndexedDB) et une bonne adaptation au contexte béninois (programmes MEMP, micro-séquences pédagogiques). Cependant, plusieurs failles UX critiques impactent l'autonomie des élèves et la résilience aux interruptions. **Score : 5.5/10**

---

## État des Lieux

### 1. Adaptation aux petits écrans et navigation one-thumb

| Aspect | Évaluation | Observations |
|--------|------------|--------------|
| Touch targets | ⚠️ Partiel | Boutons valider (48-56px) OK, mais flèches ordering (44px) trop petites pour enfants 10 ans |
| Navigation mobile | ✅ Bonne | Bottom nav 72px sticky, 4 items max, icônes + labels |
| Lecture | ⚠️ Partiel | Questions 20-24px OK, mais textes explicatifs parfois denses sur mobile |
| Fatigue visuelle | ❌ Insuffisant | Pas de mode "focus lecture" ni réduction animations pour faible luminosité |

### 2. Gestion des interruptions

| Scénario | Implémentation | Évaluation |
|----------|----------------|------------|
| Appel entrant | Draft auto-save localStorage (2h max) | ✅ Bon |
| Batterie faible (<15%) | Aucune alerte spécifique | ❌ Absent |
| Coupure réseau | SyncContext + queue IndexedDB | ✅ Très bon |
| Retour après fermeture | Reprise via draft + écran intro | ✅ Bon |
| Crash navigateur | Perte possible des 60s dernières réponses | ⚠️ Moyen |

### 3. Clarté des consignes (autonomie)

| Critère | Statut | Problème identifié |
|---------|--------|-------------------|
| Lecture audio TTS | ✅ Implémenté | Bouton "Écouter" sur chaque question |
| Indices progressifs | ✅ 3 niveaux | Bouton "Indice" visible mais petit |
| Visualisation consignes | ⚠️ Moyen | Pas d'icônes explicatifs (ex: 🔍 pour rechercher) |
| Langage | ⚠️ Hétérogène | "micro-skill", "SmartScore", termes abstraits |
| Support langues locales | ❌ Absent | Uniquement français, pas de Fon/Yoruba |

### 4. Feedback immédiat et encourageant

| Type | Implémentation | Efficacité |
|------|----------------|------------|
| Visuel | Couleurs vert/rouge + confettis | ✅ Fort impact |
| Textuel | Messages variables (4 corrects, 3 incorrects) | ⚠️ Limité, pas personnalisé |
| Sonore | Aucun | ❌ Critique pour culture orale forte |
| Haptique | Aucun | ⚠️ Standard pour mobile mais absent |
| Récompense | XP + SmartScore + Badges | ✅ Bon système |
| Encouragement erreurs | "C'est en forgeant..." | ⚠️ Standardisé, pas adaptatif |

### 5. Chunking pédagogique

| Aspect | Implémentation | Évaluation |
|--------|----------------|------------|
| Durée exercices | Non limitée | ❌ Pas de timer par question |
| Micro-leçons | DurationMinutes dans DB | ✅ Bon concept |
| Progression visuelle | Barre + dots numérotés | ✅ Clair |
| Pause suggérée | Aucune | ❌ Pas de break après 5min |
| Examens blancs | 60min simulé CEP | ✅ Réaliste |

### 6. Progression différenciée

| Fonctionnalité | Implémentation | Efficacité |
|----------------|----------------|------------|
| SmartScore adaptatif | Backend (0-100) | ✅ Bon indicateur |
| Prérequis | Check + affichage avant exercice | ✅ Très utile |
| Difficulté questions | difficulty_index (1-10) en DB | ⚠️ Pas visible par l'élève |
| Suggestion parcours | Aucune | ❌ Pas de recommandation IA |
| Niveau CM2 fixe | Pas de détection niveau réel | ❌ Hétérogénéité non gérée |

### 7. Alignement MEMP

| Matière | Couverture | Observations |
|---------|------------|--------------|
| Mathématiques | ✅ Complète | Numération, opérations, géométrie, mesures, données |
| Français | ✅ Complète | Grammaire, conjugaison, orthographe, CEP annales |
| Éducation Sociale | ✅ Complète | Programme Bénin intégré |
| Éducation Scientifique | ⚠️ Partielle | Exercices présents mais moins denses |
| Micro-compétences | ✅ Oui | external_id MEMP (ex: NUM-ENTIERS-0-1B) |

---

## Insuffisances Critiques Identifiées

### 🔴 IC-1 : Absence de feedback sonore (Impact Pédagogique Majeur)
**Problème :** Culture orale béninoise sous-exploitée. Les élèves n'ont pas de renforcement vocal ("Bravo !", explications audio).
**Conséquence :** Engagement réduit, difficultés compréhension pour les élèves à faible littératie.

### 🔴 IC-2 : Pas de gestion batterie faible / mode économie
**Problème :** 1-2GB RAM + écrans 5-6 pouces = batterie qui fond vite. Aucune détection ni adaptation.
**Conséquence :** Interruptions forcées, perte de progression, frustration.

### 🔴 IC-3 : Langage technique non adapté à 10-11 ans
**Problème :** Termes comme "micro-skill", "SmartScore", "prérequis" affichés sans explication.
**Conséquence :** Besoin d'assistance adulte, autonomie réduite.

### 🔴 IC-4 : Pas de pause intelligente ni limite de temps
**Problème :** Exercices peuvent durer >10min sans break. Pas de timer pédagogique.
**Conséquence :** Dérive attentionnelle, fatigue cognitive en classe surchargée.

### 🟡 IC-5 : Aucune personnalisation au niveau réel de l'élève
**Problème :** Progression linéaire CM2, pas de diagnostic entrée. Élèves faibles bloquent vite.
**Conséquence :** Découragement, abandon des élèves en difficulté.

---

## Recommandations d'Actions

### Pour IC-1 (Feedback sonore) - Solution Frugale
```
Approche : Synthèse vocale locale + fichiers audio légers
- TTS navigateur (speechSynthesis) pour consignes et feedback courts
- Pré-enregistrer 20-30 phrases encouragements en français (MP3 64kbps)
- Option "Mode Audio" qui lit automatiquement questions ET réponses
- Coût : Négligeable (API native) + 2-3h enregistrement
- Alternative locale : Partenariat radio scolaire Bénin pour voix familière
```

### Pour IC-2 (Batterie) - Solution Frugale
```
Approche : Détection API + adaptation interface
- Battery Status API (si dispo) ou dégradation performance
- En dessous de 20% : désactiver animations, confettis, images HD
- En dessous de 10% : alerte "Sauvegarde rapide" + proposition pause
- Mode "École" : luminosité réduite, pas d'animations par défaut
- Coût : Développement uniquement
```

### Pour IC-3 (Langage) - Solution Frugale
```
Approche : Glossary embarqué + tooltips
- Remplacer "SmartScore" par "Ton niveau : X/100"
- "micro-skill" → "petite compétence à maîtriser"
- Tooltips (?) sur termes techniques avec explication 10 mots max
- Avatar tuteur (simple SVG animé) qui explique la 1ère fois
- Coût : Textes + traduction i18n existante
```

### Pour IC-4 (Chunking) - Solution Frugale
```
Approche : Timer pédagogique optionnel + breaks gamifiés
- Timer visible (sable visuel 3min) pour chaque question
- Après 5min d'usage : mascotte "Tu mérites une pause !"
- Mini-jeu 20s (respiration, stretch virtuel) optionnel
- Examens : garder timer CEP (60min) mais alertes 30/15/5min
- Coût : Timer existe déjà pour examens, à réutiliser
```

### Pour IC-5 (Différenciation) - Solution Frugale
```
Approche : Diagnostic rapide (5 questions) + 3 niveaux auto-assignés
- À l'inscription : mini-test 5min (numération, lecture compréhension)
- Résultat → suggestion "Niveau Renforcement / CM2 / Excellence"
- SmartScore s'adapte : seuils 60/70/80% selon niveau assigné
- Badge spécial "Explorateur" pour élèves qui essaient niveau supérieur
- Coût : 15 questions préparées × 3 niveaux = 45 questions
```

---

## Plan de Remédiation Priorisé

| Priorité | Action | Impact | Délai | Complexité |
|----------|--------|--------|-------|------------|
| **HAUTE** | Ajouter TTS + feedback vocal de base | Élevé | 1 semaine | Basse |
| **HAUTE** | Mode économie batterie + alerte 20% | Élevé | 3 jours | Basse |
| **HAUTE** | Simplifier labels (SmartScore → Niveau) | Élevé | 2 jours | Très basse |
| **MOYENNE** | Timer 3min/question + pause mascotte | Élevé | 1 semaine | Moyenne |
| **MOYENNE** | Diagnostic entrée 5 questions | Élevé | 2 semaines | Moyenne |
| **MOYENNE** | Tooltips glossaire | Moyen | 3 jours | Basse |
| **BASSE** | Haptic feedback (vibration) | Faible | 2 jours | Très basse |
| **BASSE** | Support Fon/Yoruba (UI uniquement) | Moyen | 3 semaines | Moyenne |

---

## Notes Méthodologiques

**Review heuristique effectuée sur :**
- Parcours inscription → 1ère leçon → exercice → retour interruption
- Test sur dimensions écran 360×640 (Android Go baseline)
- Analyse code : React + PWA + IndexedDB + SyncContext

**Contraintes respectées :**
- Solutions privilégiant Web APIs natives (pas de librairies lourdes)
- Pas de dépendance cloud pour features offline-first
- Coûts opérationnels négligeables

---

*Audit réalisé le 12 avril 2026*
*Méthodologie : Review heuristique mobile-first, Android Go compatible*
