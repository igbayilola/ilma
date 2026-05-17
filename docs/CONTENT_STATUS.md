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

## Leçons (`micro_lessons` table)

À date, la table `micro_lessons` ne contient **qu'une seule entrée** (sans `sections`). Les leçons consommées par les pages élèves (`SkillDetail`, `MicroLesson`) vivent probablement ailleurs — Q2 de la punch-list iter 37 reste **ouvert** : à investiguer (champ JSON sur le skill ? autre modèle ? statique côté contenu ?).

## Qualité des explications de questions

904/904 questions ont une `explanation` non vide, mais **855/904 font moins de 200 caractères** (moyenne 63). Ce sont des placeholders / hints courts, pas des worked-solutions complètes. Ce gap est connu depuis l'audit iter 24 (P1) et reste **bloqué côté contenu MEMP** — ce n'est pas du code.

## Pour les futures sessions

- **Ne pas reflagger** « 169/219 skills sans questions » comme un bug. C'est attendu MVP.
- **Re-vérifier** avant d'élargir le scope (français, etc.) : ce document est la source de vérité.
- **Audit data SQL** : voir entrée iter 37 dans `ROADMAP_90D.md` pour les queries utilisées.
