# État du contenu pédagogique

> Dernière mise à jour : itération 40 (2026-05-17), audit data iter 37.

## Scope MVP

Sitou est positionné comme **compagnon-annuel pour le programme CM2 béninois**, avec une montée vers le **CEP**. Le scope MVP livré couvre **les mathématiques uniquement** côté pratique (questions). Les 3 autres matières du programme officiel sont présentes en **structure** (Subjects, Domains, Skills séquencés par trimestre/semaine) mais **sans contenu pratique** — c'est intentionnel.

## Volume actuel par matière

| Matière | Skills actifs | Skills avec questions | Questions totales |
|---|---|---|---|
| Mathématiques | 50 | **50** ✅ | 904 |
| Français | 77 | 0 | 0 |
| Éducation sociale | 57 | 0 | 0 |
| Éducation scientifique & technologique | 35 | 0 | 0 |
| **Total** | **219** | **50** | **904** |

> 169 skills actifs apparaissent dans la timeline `/app/student/programme` mais ne déclenchent pas d'exercice à ce jour. C'est **attendu** — l'objectif MVP est de prouver le modèle compagnon-annuel sur une matière complète avant d'élargir.

## Trimestres

| Trimestre | Semaines couvertes | Note |
|---|---|---|
| T1 | 14 semaines | Programme complet sur les 4 matières |
| T2 | 13 semaines | Programme complet sur les 4 matières |
| T3 | **2 semaines isolées** (W1 + W6) | T3 = révision CEP, intentionnellement allégé. Cf. note `<ProgramTimeline>` iter 38 |

Le `<ProgramTimeline>` (iter 38) rend explicitement une note « Période de révision CEP » quand l'élève est sur T3.W2-5,7+ pour ne pas laisser la timeline silencieuse.

## Leçons — l'app est en mode « exercises-only »

**Trace complète établie iter 41 (Q2 audit iter 37) :**

- FE `pages/student/SkillDetail.tsx` appelle `GET /subjects/skills/{skill_id}`.
- BE `endpoints/content.py:118` renvoie `{skill, lessons: skill.lessons, micro_skills}`.
- `Skill.lessons` est la relation `MicroLesson` (`models/content.py:117`).
- La table `micro_lessons` contient **1 seule entrée** en prod, sans `sections`.
- Le tree `content/` (Bénin CM2) contient `programme/`, `exercices/`, `epreuves/` — **aucun champ `content_html` ni `sections` côté lesson**. Les JSON sont du curriculum + des exercices, pas de leçons narratives.

Conséquence UX : pour 218/219 skills, `SkillDetail` reçoit `lessons: []`. Le composant gère le cas via `{hasLesson && ...}` (SkillDetail.tsx:123) → **la section « Leçon » n'est tout simplement pas rendue, silencieusement**. L'élève voit :
- Titre + description du skill.
- Sa progression (`score`, barre).
- Bouton « Commencer l'exercice » → ExercisePlayer.

Pas de texte pédagogique narratif (intro / règle / exemple) entre exercises. L'app fonctionne aujourd'hui comme un **drill engine + curriculum map**, pas comme un IXL complet.

**À décider** (ouvert post-iter 41) :
1. **Backfill `micro_lessons`** côté contenu (équipe MEMP, charge L, externe).
2. **Accepter** comme état MVP et l'expliciter dans la copy élève (ex. label « Pratique » plutôt que « Leçon » sur la page).
3. **Cleanup** : retirer le code mort du rendu leçon dans `SkillDetail` + `MicroLesson` si décision (2) confirmée.

Q2 est donc **fermé en investigation** mais ouvre une décision produit.

## Qualité des explications de questions

904/904 questions ont une `explanation` non vide, mais **855/904 font moins de 200 caractères** (moyenne 63). Ce sont des placeholders / hints courts, pas des worked-solutions complètes. Ce gap est connu depuis l'audit iter 24 (P1) et reste **bloqué côté contenu MEMP** — ce n'est pas du code.

## Pour les futures sessions

- **Ne pas reflagger** « 169/219 skills sans questions » comme un bug. C'est attendu MVP.
- **Re-vérifier** avant d'élargir le scope (français, etc.) : ce document est la source de vérité.
- **Audit data SQL** : voir entrée iter 37 dans `ROADMAP_90D.md` pour les queries utilisées.
