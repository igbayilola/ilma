# Règles de Génération d'Exercices — ILMA CM2 Mathématiques Bénin

**Version** : 2.0.0  
**Date** : 2026-02-27  
**Scope** : 7 domaines, 50 skills, 224 micro-compétences  

---

## SECTION A — RÈGLES DE COUVERTURE OBLIGATOIRE

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R1** | **1 exercice = 1 micro-skill cible** | Chaque exercice mappe exactement 1 `micro_skill_id`. Jamais un skill parent générique. | Tag `micro_skill_id` obligatoire dans les métadonnées JSON de l'exercice |
| **R2** | **Quotas adaptatifs par difficulté** | Minimum d'exercices par micro-skill selon `difficulty_index` :<br>• diff ≤ 4 : **12** exercices (3 par niveau ILMA)<br>• diff 5-6 : **16** exercices (4 par niveau ILMA)<br>• diff 7-8 : **20** exercices (5 par niveau ILMA)<br>• diff ≥ 9 : **24** exercices (6 par niveau ILMA) | Dashboard de couverture avec alerte si < seuil. Total estimé : ~3 600 exercices |
| **R3** | **Séquence ILMA complète** | Pour chaque micro-skill, respecter les 4 niveaux :<br>1. **Découverte** — guidé, indices visuels, QCM<br>2. **Entraînement** — semi-guidé, autonomie partielle<br>3. **Maîtrise** — autonome, contextes variés<br>4. **Expert** — complexe, transfert, pièges | Vérifier que chaque niveau ILMA a ≥ quota/4 exercices |
| **R4** | **Couverture des types d'exercices** | Pour chaque micro-skill, utiliser **tous les types** listés dans `recommended_exercise_types`, avec ≥ 2 exercices par type par niveau ILMA | Matrice type × niveau ILMA sans case vide |
| **R5** | **Multiplicateur CEP** | Pour les skills avec `cep_frequency ≥ 70`, appliquer un **multiplicateur ×2** sur les quotas R2. Ces exercices supplémentaires sont au format examen. | Compteur CEP par skill, alerte si < quota×2 |

---

## SECTION B — RÈGLES DE PROGRESSION PÉDAGOGIQUE

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R6** | **Respect strict des prérequis** | Un exercice de niveau ILMA "Maîtrise" d'un micro-skill ne peut être proposé que si l'élève a atteint "Entraînement" validé sur **tous** ses `prerequisites_micro_skill_ids` + `external_prerequisites`. | Système de blocage avec message : "Tu dois d'abord maîtriser [nom du prérequis]" |
| **R7** | **Difficulté croissante intra-session** | Dans un parcours, ordonner les exercices d'un même micro-skill par difficulté croissante. Jamais aléatoire. Séquence type :<br>Ex 1-2 : Découverte (rappel)<br>Ex 3-5 : Entraînement<br>Ex 6-7 : Maîtrise (si ≥ 70%)<br>Ex 8+ : Expert (si ≥ 85%) | Algorithme de séquençage forcé avec seuils de passage |
| **R8** | **Seuils de maîtrise** | Bloquer le passage au niveau suivant tant que `mastery_threshold` non atteint. Par défaut :<br>• Découverte → Entraînement : 60% sur 4 ex<br>• Entraînement → Maîtrise : 80% sur 6 ex<br>• Maîtrise → Expert : 90% sur 5 ex<br>• Expert validé : 85% sur 4 ex | Vérification glissante sur les N derniers exercices |
| **R9** | **Régression automatique** | Si l'élève chute sous 50% sur 4 exercices consécutifs à un niveau, redescendre au niveau inférieur avec de **nouveaux exercices** (pas les mêmes). Si échec en Découverte, proposer les prérequis. | Log de régression, alerte enseignant si 2+ régressions |
| **R10** | **Expert = optionnel pour maîtrise** | Le niveau Expert n'est **pas requis** pour valider la maîtrise d'un micro-skill. "Maîtrise" validée = micro-skill acquis. Expert = enrichissement et défi. | Distinction claire dans le statut : "Maîtrisé" vs "Expert" |
| **R11** | **Parcours parallèles autorisés** | Un élève peut travailler sur **2 skills simultanément** si leurs prérequis sont satisfaits. Maximum 3 skills en parallèle pour éviter la dispersion. | Compteur de skills actifs, blocage au-delà de 3 |

---

## SECTION C — RÈGLES DE DIVERSITÉ ET ROBUSTESSE

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R12** | **Diversité contextuelle** | Minimum **3 contextes différents** par micro-skill, tirés de `local_context_examples` ou générés. Ne jamais réutiliser le même contexte dans 2 exercices consécutifs. | Tag `context_id` par exercice, compteur de diversité |
| **R13** | **Pièges d'erreurs intégrés** | **30%** des exercices doivent inclure une erreur typique de `common_mistakes` comme distracteur (QCM) ou comme erreur à détecter (Correction d'erreur). | Tag `error_trap: true/false` dans les métadonnées |
| **R14** | **Non-répétition** | Un élève ne voit jamais le même exercice 2 fois dans la même session. Le pool doit permettre **3 sessions sans doublon** au même niveau ILMA. | Hash d'exercice, historique par élève |
| **R15** | **Alternance des types** | Jamais plus de **2 exercices consécutifs** du même type dans une session. | Algorithme d'alternance dans le séquenceur |

---

## SECTION D — MODULATION DE LA DIFFICULTÉ

Pour un même micro-skill, les 4 niveaux ILMA modulent la difficulté autour du `difficulty_index` nominal via ces leviers :

| Levier | Découverte (diff − 1) | Entraînement (nominal) | Maîtrise (diff + 1) | Expert (diff + 2) |
|---|---|---|---|---|
| **Nombres** | Petits, ronds (10, 100) | Moyens, courants | Grands ou décimaux | Non ronds, cas limites |
| **Étapes** | 1 opération | 1-2 opérations | 2-3 opérations | Multi-étapes + transfert |
| **Contexte** | Énoncé court, direct | Standard | Long, infos parasites | Infos contradictoires |
| **Guidage** | Étapes pré-découpées | Indices partiels | Aucun guidage | Aucun + piège |
| **Unités** | Une seule unité | Unité donnée | Conversion nécessaire | Unités mixtes |
| **Réponse** | QCM 3-4 choix | QCM ou numérique | Numérique ouvert | Rédaction complète |
| **Feedback** | Immédiat chaque étape | Après chaque exercice | En fin de série | Uniquement résultat final |
| **Temps** | Illimité | Illimité ou large | Chronomètre souple | Chronomètre serré |

---

## SECTION E — HINTS ADAPTATIFS

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R16** | **Nombre max = `adaptive_hints`** | Chaque micro-skill a un champ `adaptive_hints` (2-4). Ne jamais dépasser ce nombre. Au-delà, forcer retour au prérequis. | Compteur d'aides par exercice |
| **R17** | **Gradation obligatoire** | Les hints suivent une progression stricte. Jamais donner la solution directement avant d'avoir épuisé les étapes intermédiaires. | Revue de chaque hint |

**Gradation type :**

| Hint | Nature | Exemple (conversion 350 cm → m) |
|---|---|---|
| 1 | Rappel conceptuel | "Rappelle-toi : combien de cm dans 1 m ?" |
| 2 | Orientation méthodologique | "Place le nombre dans le tableau de conversion." |
| 3 | Étape partielle | "350 cm : 3 dans les m, 5 dans les dm, 0 dans les cm..." |
| 4 | Solution expliquée (dernier recours) | "350 cm = 3,50 m car on divise par 100." |

**Scoring avec hints :**

| Réponse | Score |
|---|---|
| Correcte sans hint | 100% |
| Correcte après hint 1 | 80% |
| Correcte après hint 2 | 60% |
| Correcte après hint 3 | 40% |
| Correcte après hint 4 | 20% |
| Incorrecte après tous les hints | 0% → exercice plus facile |

---

## SECTION F — RÉTENTION ESPACÉE

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R18** | **Révision espacée** | Une micro-compétence "Maîtrisée" est revérifiée selon le calendrier ci-dessous. Si échec, elle repasse en statut "Entraînement". | Scheduler automatique, log de rétention |

| Délai | Exercices | Niveau |
|---|---|---|
| J+1 | 3 flash | Entraînement |
| J+3 | 3 exercices | Entraînement |
| J+7 | 2 exercices | Maîtrise |
| J+14 | 2 exercices | Maîtrise |
| J+30 | 1 exercice | Expert |

---

## SECTION G — MODIFIERS PÉDAGOGIQUES

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R19** | **Application systématique** | Les `recommended_modifiers` du micro-skill sont appliqués automatiquement au niveau ILMA approprié. | Checklist de conformité |

**Règles d'activation :**

| Modifier | Activation | Interdiction |
|---|---|---|
| `timed` | Entraînement (après 60% réussite), Maîtrise, Expert | Découverte ; élève en régression |
| `flash` | Calcul mental, tables, formules connues | Problèmes contextualisés, construction |
| `binary` | Vrai/Faux rapide, comparaison | Réponses numériques complexes |
| `justification_required` | Maîtrise et Expert, Bloom ≥ Analyser | Découverte, Bloom Connaître/Comprendre |

**Temps par type (modifier `timed`) :**

| Type | Entraînement | Maîtrise | Expert |
|---|---|---|---|
| QCM / VF | 30 sec | 20 sec | 15 sec |
| Réponse numérique | 60 sec | 45 sec | 30 sec |
| Compléter | 90 sec | 60 sec | 45 sec |
| Problème contextualisé | 3 min | 2 min 30 | 2 min |
| Construction / Tracer | 5 min | 4 min | 3 min |
| Correction d'erreur | 2 min | 1 min 30 | 1 min |

**Marge de temps globale (R13bis)** : durée totale du parcours ≤ somme des `estimated_time_minutes` × **1.2**.

---

## SECTION H — CONTEXTE LOCAL BÉNINOIS

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R20** | **Contextualisation 60%** | ≥ 60% des exercices de type "Problème contextualisé" utilisent des contextes locaux béninois. | Compteur de contextes, audit trimestriel |

**Catégories de contextes :**

| Catégorie | Exemples |
|---|---|
| Monnaie | F CFA, prix au marché de Dantokpa |
| Aliments | Riz, maïs, manioc, igname, gari, arachides |
| Commerce | Marché, vendeuse, sacs de 25/50 kg |
| Transport | Zem (moto-taxi), taxi-brousse, Cotonou-Parakou |
| Agriculture | Champ de manioc, récolte, hectares, saison des pluies |
| École | Cahiers, craies, tableau, effectif classe, CEP |
| Artisanat | Pagnes, tissus au mètre, couture |
| Infrastructure | Puits (cercle), carrefour (angles), plan de quartier |
| Famille | Budget familial, partage entre enfants |

**Prénoms** : Adjovi, Koffi, Afi, Dossou, Akouavi, Sèna, Kokou, Ablavi, Yao, Fifamè (alterner garçons/filles).

**Valeurs réalistes :**

| Grandeur | Fourchette |
|---|---|
| Riz (kg) | 400-600 F CFA |
| Cahier | 150-300 F CFA |
| Course zem | 200-500 F CFA |
| Salaire mensuel | 50 000-150 000 F CFA |
| Surface champ | 0,5-10 ha |
| Cotonou-Porto-Novo | ~35 km |
| Effectif classe | 40-60 élèves |

---

## SECTION I — BLOOM ALIGNMENT

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R21** | **Cohérence Bloom-exercice** | Chaque exercice cible le `bloom_taxonomy_level` de son micro-skill. Un QCM ne peut être "Évaluer" que si les choix exigent un jugement critique. | Matrice Bloom ↔ consigne, revue systématique |

**Mapping Bloom → types naturels :**

| Bloom | Types naturels | Verbes d'action dans la consigne |
|---|---|---|
| Connaître (14 MS) | QCM, VF, FC, Compléter | Nommer, définir, lister, rappeler |
| Comprendre (25 MS) | QCM, RC, GD, Classement | Expliquer, reformuler, interpréter |
| Appliquer (124 MS) | RN, Compléter, Construction, Tracer, EG | Calculer, convertir, tracer, appliquer |
| Analyser (36 MS) | CE, Classement, PB, RC | Décomposer, comparer, identifier |
| Évaluer (23 MS) | CE, Justification, PB | Juger, vérifier, critiquer, justifier |
| Créer (2 MS) | Construction, PB, Tracer | Concevoir, produire, planifier |

---

## SECTION J — ACCESSIBILITÉ

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R22** | **Tags respectés** | Chaque `accessibility_tag` du micro-skill impose des adaptations obligatoires sur **100% des exercices** de ce MS (pas un sous-ensemble). | Pipeline de vérification automatique |

| Tag | Adaptations obligatoires |
|---|---|
| `Dyscalculie-support` | Police ≥ 16pt, espacement large, nombres alignés, pas de surcharge |
| `Dyslexie-friendly` | Phrases < 15 mots, police Arial/OpenDyslexic, pas de justification de texte |
| `Audio-support` | Énoncé TTS-compatible, pas d'info uniquement visuelle |
| `visual_fraction_models` | Toujours accompagner les fractions d'un visuel (barre, disque) |
| `grid_overlay` | Quadrillage fourni pour les constructions |
| `zoomable_protractor` | Rapporteur interactif zoomable |
| `high_contrast_lines` | Lignes ≥ 2px, couleurs contrastées, jamais de gris clair |
| `step_by_step_mode` | Exercice décomposé en sous-étapes cliquables |
| `low_text_mode` | Minimum de texte, maximum de visuels/icônes |
| `clock_visual_aids` | Horloge visuelle interactive pour les exercices de temps |
| `calendar_visual_aids` | Calendrier visuel interactif |
| `formula_card` | Carte de formules accessible en permanence |
| `unit_table_scaffold` | Tableau de conversion pré-rempli partiellement |
| `unit_ladder_visual` | Échelle visuelle des unités (escalier) |
| `worked_examples` | Exemple résolu affiché avant l'exercice |
| `table_scaffold` | Structure de tableau fournie, l'élève complète |
| `checklist_mode` | Liste de vérification interactive |
| `highlight_keywords` | Mots-clés surlignés dans l'énoncé |
| `side_by_side_view` | Vue comparée (sa réponse vs corrigé) |
| `color_coded_categories` | Catégories d'erreurs codées par couleur |
| `high_contrast_axes` | Axes de graphique en contraste élevé |

---

## SECTION K — FORMAT CEP

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R23** | **Format examen** | Les exercices "format CEP" reproduisent les conditions réelles. | Conformité avec les annales 2010-2025 |

**Caractéristiques d'un exercice format CEP :**

- Énoncé de 3-5 lignes avec contexte béninois
- Questions numérotées (a, b, c)
- Réponse rédigée attendue (phrase complète + unité)
- Barème indicatif (/2, /3, /4 points)
- Modifier `timed` activé
- Pas de hint (conditions d'examen)
- Feedback uniquement après soumission complète

---

## SECTION L — CONTRÔLE QUALITÉ ET ANTI-RÉGRESSION

| # | Règle | Implémentation | Validation |
|---|-------|---------------|------------|
| **R24** | **Anti-cycles** | Vérifier avant toute génération de parcours qu'aucun chemin ne crée de boucle de prérequis. | Algorithme DFS sur le graphe de prérequis |
| **R25** | **Distracteurs plausibles** | QCM : les mauvaises réponses sont construites à partir de `common_mistakes` :<br>• Distracteur 1 : erreur de calcul (retenue, virgule)<br>• Distracteur 2 : erreur de méthode (mauvaise opération)<br>• Distracteur 3 : erreur d'unité/ordre de grandeur<br>Jamais de distracteur absurde. | Revue systématique des distracteurs |
| **R26** | **Cross-domain prerequisites** | Les `external_prerequisites` cross-domain sont résolus via les `external_micro_skill_stubs`. Le moteur doit vérifier le statut de maîtrise du MS externe dans son domaine d'origine avant de débloquer. | Query cross-domain dans la base de progression élève |

---

## SECTION M — CHECKLIST DE VALIDATION AVANT PUBLICATION

```
□ R1  : Tous les exercices mappent 1 micro_skill_id ?
□ R2  : Quotas atteints par MS selon difficulty_index ?
□ R3  : 4 niveaux ILMA représentés pour chaque MS ?
□ R4  : Tous les recommended_exercise_types couverts ?
□ R5  : Multiplicateur ×2 appliqué pour CEP ≥ 70 ?
□ R6  : Prérequis vérifiés (internes + externes + cross-domain) ?
□ R7  : Difficulté croissante dans le séquençage ?
□ R12 : ≥ 3 contextes par MS ?
□ R13 : 30% des exercices avec error_trap ?
□ R14 : Pool suffisant pour 3 sessions sans doublon ?
□ R15 : Alternance des types (max 2 consécutifs identiques) ?
□ R21 : Bloom alignment vérifié ?
□ R22 : Accessibility tags respectés ?
□ R24 : Pas de cycles dans les prérequis ?
□ R25 : Distracteurs basés sur common_mistakes ?
```

---

## SECTION N — QUESTIONS DE DESIGN OUVERTES

Ces questions devront être tranchées lors de l'implémentation :

1. **Gestion des échecs répétés** : Si un élève régresse 2+ fois sur le même micro-skill, faut-il alerter l'enseignant ou proposer un parcours de remédiation automatique ?
2. **Exercices générés vs éditoriaux** : Quel ratio d'exercices générés automatiquement (par LLM) vs rédigés manuellement par des enseignants ? Quel processus de validation pour les exercices générés ?
3. **Localisation multi-pays** : Si le système est étendu au-delà du Bénin, les règles de contextualisation (section H) devront être paramétrables par pays.
4. **Offline-first** : Le pool d'exercices doit-il être téléchargeable pour utilisation hors connexion ? Si oui, quelle taille maximale par domaine ?
5. **Analytics enseignant** : Quels tableaux de bord exposer aux enseignants pour suivre la progression (par MS, par Bloom, par CEP) ?

---

## ANNEXE — Résumé quantitatif estimé

| Domaine | Skills | MS | Diff moy | Exercices estimés (R2+R5) |
|---|---|---|---|---|
| Numération | 6 | 30 | 3.3 | ~450 |
| Opérations | 11 | 55 | 5.9 | ~1 200 |
| Géométrie | 9 | 35 | 5.0 | ~650 |
| Grandeurs et Mesures | 12 | 55 | 5.2 | ~1 150 |
| Proportionnalité | 5 | 19 | 5.5 | ~450 |
| Organisation de données | 5 | 22 | 4.7 | ~380 |
| Préparation au CEP | 2 | 8 | 6.4 | ~220 |
| **TOTAL** | **50** | **224** | | **~4 500** |
