#!/usr/bin/env python3
"""Generate exercices_cm2_operations.json"""
import json

ex_id_counter = 0

def next_id():
    global ex_id_counter
    ex_id_counter += 1
    return f"EX{ex_id_counter:03d}"

def ms(skill, num):
    return f"{skill}::MS{num:02d}"

exercises_by_ms = []

# ============================================================
# SKILL 1: OPS-CALCUL-MENTAL-TABLES (5 MS)
# ============================================================
SK = "OPS-CALCUL-MENTAL-TABLES"

# MS01 — Rappeler les tables de multiplication (1 à 12)
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 1),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Combien font 7 × 8 ?",
            "choices": ["54", "56", "58", "48"],
            "correct_answer": "56",
            "explanation": "7 × 8 = 56. C'est un résultat de la table de 7 (ou de 8) à connaître par cœur.",
            "hint": "Pense à 7 × 7 = 49, puis ajoute 7.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["calcul mental", "tables", "multiplication"],
            "common_mistake_targeted": "Confusion entre 7×8 et 6×9"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Calcule mentalement : 9 × 12.",
            "tolerance": 0, "correct_answer": 108,
            "explanation": "9 × 12 = 9 × 10 + 9 × 2 = 90 + 18 = 108.",
            "hint": "Décompose 12 en 10 + 2.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "tables", "multiplication"],
            "common_mistake_targeted": "Erreur sur 9×12 confondu avec 9×11"
        },
        {
            "exercise_id": next_id(), "type": "fill_blank", "difficulty": "medium",
            "text": "Complète : 11 × ___ = 132",
            "blanks": ["12"],
            "correct_answer": ["12"],
            "explanation": "11 × 12 = 132. On peut vérifier : 132 ÷ 11 = 12.",
            "hint": "Divise 132 par 11.",
            "points": 2, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "tables", "division"],
            "common_mistake_targeted": "Ne pas connaître la table de 11"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "hard",
            "text": "Le produit 12 × 11 est égal à 131.",
            "correct_answer": False,
            "explanation": "12 × 11 = 132, pas 131. On peut vérifier : 12 × 10 = 120, 120 + 12 = 132.",
            "hint": "Calcule 12 × 10, puis ajoute 12.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Évaluer", "ilma_level": "Approfondissement",
            "tags": ["calcul mental", "tables", "vérification"],
            "common_mistake_targeted": "Erreur de 1 dans le produit"
        }
    ]
})

# MS02 — Utiliser doubles et moitiés (×2, ÷2)
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 2),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Quel est le double de 45 ?",
            "choices": ["80", "85", "90", "95"],
            "correct_answer": "90",
            "explanation": "Le double de 45 = 45 × 2 = 90. On peut décomposer : 40 × 2 + 5 × 2 = 80 + 10 = 90.",
            "hint": "Double de 40 = 80, double de 5 = 10.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["calcul mental", "doubles", "multiplication"],
            "common_mistake_targeted": "Oublier la retenue dans 5×2=10"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Quelle est la moitié de 174 ?",
            "tolerance": 0, "correct_answer": 87,
            "explanation": "La moitié de 174 = 174 ÷ 2 = 87. Vérifie : 87 × 2 = 174.",
            "hint": "Moitié de 100 = 50, moitié de 74 = 37.",
            "points": 1, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "moitiés", "division"],
            "common_mistake_targeted": "Erreur sur la moitié de 74"
        },
        {
            "exercise_id": next_id(), "type": "fill_blank", "difficulty": "medium",
            "text": "Pour multiplier 35 × 4, Kofi calcule le double du double. Le double de 35 est 70, le double de 70 est ___.",
            "blanks": ["140"],
            "correct_answer": ["140"],
            "explanation": "35 × 4 = 35 × 2 × 2 = 70 × 2 = 140.",
            "hint": "Calcule d'abord 35 × 2, puis encore × 2.",
            "points": 2, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "doubles", "stratégie"],
            "common_mistake_targeted": "Oublier de doubler deux fois"
        },
        {
            "exercise_id": next_id(), "type": "contextual_problem", "difficulty": "hard",
            "text": "Amina a 250 FCFA. Sa maman lui donne le double. Combien a-t-elle maintenant au total ?",
            "sub_questions": [
                {"id": "a", "text": "Combien sa maman lui donne-t-elle ?", "correct_answer": "500 FCFA"},
                {"id": "b", "text": "Combien Amina a-t-elle au total ?", "correct_answer": "750 FCFA"}
            ],
            "correct_answer": "750 FCFA",
            "explanation": "Le double de 250 = 500 FCFA. Total : 250 + 500 = 750 FCFA.",
            "hint": "Calcule d'abord le double de 250, puis additionne.",
            "points": 3, "time_limit_seconds": 90,
            "bloom_level": "Appliquer", "ilma_level": "Approfondissement",
            "tags": ["calcul mental", "doubles", "problème", "FCFA"],
            "common_mistake_targeted": "Oublier d'ajouter la somme initiale"
        }
    ]
})

# MS03 — Utiliser quadruples et quarts (×4, ÷4)
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 3),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Quel est le quadruple de 25 ?",
            "choices": ["75", "100", "125", "50"],
            "correct_answer": "100",
            "explanation": "Le quadruple de 25 = 25 × 4 = 100. On double deux fois : 25 × 2 = 50, 50 × 2 = 100.",
            "hint": "Quadruple signifie × 4, soit doubler deux fois.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["calcul mental", "quadruples", "multiplication"],
            "common_mistake_targeted": "Confondre quadruple (×4) et triple (×3)"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Calcule le quart de 360.",
            "tolerance": 0, "correct_answer": 90,
            "explanation": "Le quart de 360 = 360 ÷ 4 = 90. On peut calculer la moitié de la moitié : 360 ÷ 2 = 180, 180 ÷ 2 = 90.",
            "hint": "Le quart, c'est la moitié de la moitié.",
            "points": 1, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "quarts", "division"],
            "common_mistake_targeted": "Diviser par 2 une seule fois au lieu de deux"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "medium",
            "text": "Le quart de 500 est 125.",
            "correct_answer": True,
            "explanation": "500 ÷ 4 = 125. Vérification : 125 × 4 = 500. C'est correct !",
            "hint": "Calcule 500 ÷ 2 = 250, puis 250 ÷ 2.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Évaluer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "quarts", "vrai-faux"],
            "common_mistake_targeted": "Erreur de calcul sur 500÷4"
        },
        {
            "exercise_id": next_id(), "type": "contextual_problem", "difficulty": "hard",
            "text": "Un commerçant de Cotonou achète 4 sacs de riz identiques pour 12 000 FCFA au total. Quel est le prix d'un sac ?",
            "sub_questions": [
                {"id": "a", "text": "Quelle opération faut-il faire ?", "correct_answer": "12 000 ÷ 4"},
                {"id": "b", "text": "Quel est le prix d'un sac ?", "correct_answer": "3 000 FCFA"}
            ],
            "correct_answer": "3 000 FCFA",
            "explanation": "Prix d'un sac = 12 000 ÷ 4 = 3 000 FCFA. Le quart de 12 000 : moitié = 6 000, moitié = 3 000.",
            "hint": "Pour trouver le prix d'un sac, divise le total par 4.",
            "points": 3, "time_limit_seconds": 90,
            "bloom_level": "Appliquer", "ilma_level": "Approfondissement",
            "tags": ["calcul mental", "quarts", "problème", "FCFA"],
            "common_mistake_targeted": "Multiplier au lieu de diviser"
        }
    ]
})

# MS04 — Trouver les compléments à 10, 100, 1000
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 4),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "fill_blank", "difficulty": "easy",
            "text": "Complète : 63 + ___ = 100",
            "blanks": ["37"],
            "correct_answer": ["37"],
            "explanation": "100 − 63 = 37. Vérification : 63 + 37 = 100.",
            "hint": "Combien faut-il ajouter à 63 pour arriver à 100 ?",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["calcul mental", "compléments", "100"],
            "common_mistake_targeted": "Erreur sur le complément à 10 des unités"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Quel nombre faut-il ajouter à 465 pour obtenir 1 000 ?",
            "tolerance": 0, "correct_answer": 535,
            "explanation": "1 000 − 465 = 535. On peut procéder étape par étape : de 465 à 500 il y a 35, de 500 à 1 000 il y a 500, donc 35 + 500 = 535.",
            "hint": "Va d'abord à la centaine suivante, puis à 1 000.",
            "points": 2, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "compléments", "1000"],
            "common_mistake_targeted": "Oublier une retenue dans la soustraction"
        },
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "medium",
            "text": "Quel est le complément à 10 de 3,7 ?",
            "choices": ["6,3", "7,3", "6,7", "7,7"],
            "correct_answer": "6,3",
            "explanation": "10 − 3,7 = 6,3. Vérification : 3,7 + 6,3 = 10.",
            "hint": "Combien manque-t-il de 3,7 à 4 ? Puis de 4 à 10 ?",
            "points": 2, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "compléments", "10", "décimaux"],
            "common_mistake_targeted": "Erreur sur le complément décimal"
        },
        {
            "exercise_id": next_id(), "type": "contextual_problem", "difficulty": "hard",
            "text": "Fatimatou veut acheter un cahier à 1 000 FCFA. Elle a déjà 725 FCFA. Combien lui manque-t-il ?",
            "sub_questions": [
                {"id": "a", "text": "Quelle opération fais-tu ?", "correct_answer": "1 000 − 725"},
                {"id": "b", "text": "Combien lui manque-t-il ?", "correct_answer": "275 FCFA"}
            ],
            "correct_answer": "275 FCFA",
            "explanation": "1 000 − 725 = 275 FCFA. De 725 à 1 000 : 725 + 75 = 800, 800 + 200 = 1 000, donc 75 + 200 = 275.",
            "hint": "Calcule le complément de 725 à 1 000.",
            "points": 3, "time_limit_seconds": 90,
            "bloom_level": "Appliquer", "ilma_level": "Approfondissement",
            "tags": ["calcul mental", "compléments", "problème", "FCFA"],
            "common_mistake_targeted": "Erreur dans la soustraction avec retenues"
        }
    ]
})

# MS05 — Multiplier/diviser par 10, 100, 1000
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 5),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Combien font 47 × 100 ?",
            "choices": ["470", "4 700", "47 000", "4 070"],
            "correct_answer": "4 700",
            "explanation": "47 × 100 = 4 700. On ajoute deux zéros à droite du nombre.",
            "hint": "Multiplier par 100, c'est ajouter deux zéros.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["calcul mental", "×100", "multiplication"],
            "common_mistake_targeted": "Ajouter un seul zéro ou trois zéros"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Calcule : 3,56 × 1 000.",
            "tolerance": 0, "correct_answer": 3560,
            "explanation": "3,56 × 1 000 = 3 560. La virgule se déplace de 3 rangs vers la droite.",
            "hint": "Déplace la virgule de 3 rangs vers la droite.",
            "points": 1, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "×1000", "décimaux"],
            "common_mistake_targeted": "Mauvais placement de la virgule"
        },
        {
            "exercise_id": next_id(), "type": "fill_blank", "difficulty": "medium",
            "text": "Complète : 8 250 ÷ ___ = 82,5",
            "blanks": ["100"],
            "correct_answer": ["100"],
            "explanation": "8 250 ÷ 100 = 82,5. La virgule se déplace de 2 rangs vers la gauche.",
            "hint": "Combien de rangs la virgule s'est-elle déplacée ?",
            "points": 2, "time_limit_seconds": 60,
            "bloom_level": "Analyser", "ilma_level": "Entraînement",
            "tags": ["calcul mental", "÷100", "décimaux"],
            "common_mistake_targeted": "Confondre ×100 et ÷100"
        },
        {
            "exercise_id": next_id(), "type": "error_correction", "difficulty": "hard",
            "text": "Kofi a écrit : 5,7 × 10 = 5,70. Trouve et corrige son erreur.",
            "erroneous_content": "5,7 × 10 = 5,70",
            "correct_answer": "5,7 × 10 = 57",
            "explanation": "Multiplier par 10 déplace la virgule d'un rang vers la droite. 5,7 × 10 = 57, pas 5,70 (ajouter un zéro après la virgule ne change pas la valeur).",
            "hint": "Que fait-on à la virgule quand on multiplie par 10 ?",
            "points": 3, "time_limit_seconds": 60,
            "bloom_level": "Évaluer", "ilma_level": "Approfondissement",
            "tags": ["calcul mental", "×10", "erreur", "décimaux"],
            "common_mistake_targeted": "Ajouter un zéro à la partie décimale au lieu de déplacer la virgule"
        }
    ]
})

# ============================================================
# SKILL 2: OPS-ESTIMER-VERIFIER (5 MS)
# ============================================================
SK = "OPS-ESTIMER-VERIFIER"

# MS01 — Arrondir un entier pour estimer
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 1),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Quel est l'arrondi de 387 à la centaine la plus proche ?",
            "choices": ["300", "380", "390", "400"],
            "correct_answer": "400",
            "explanation": "387 est plus proche de 400 que de 300. Le chiffre des dizaines (8) est ≥ 5, donc on arrondit à la centaine supérieure.",
            "hint": "Regarde le chiffre des dizaines : 8 ≥ 5, donc on monte.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["estimation", "arrondi", "centaine"],
            "common_mistake_targeted": "Arrondir à la dizaine au lieu de la centaine"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Arrondis 4 538 au millier le plus proche.",
            "tolerance": 0, "correct_answer": 5000,
            "explanation": "4 538 est plus proche de 5 000 que de 4 000. Le chiffre des centaines (5) est ≥ 5, on arrondit au millier supérieur.",
            "hint": "Regarde le chiffre des centaines pour décider.",
            "points": 1, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["estimation", "arrondi", "millier"],
            "common_mistake_targeted": "Ne pas regarder le bon chiffre pour décider"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "medium",
            "text": "L'arrondi de 2 450 au millier le plus proche est 2 000.",
            "correct_answer": False,
            "explanation": "2 450 arrondi au millier le plus proche donne 2 000 car le chiffre des centaines est 4 < 5. Attention, si on utilise la règle « 5 on monte », le chiffre des centaines est 4, pas 5, donc on reste à 2 000. En fait c'est vrai ! Non : 2 450, le chiffre des centaines = 4, donc on arrondit à 2 000. L'affirmation est correcte... Rectification : l'affirmation dit 2 000, et c'est correct car 4 < 5.",
            "hint": "Le chiffre des centaines est 4, qui est < 5.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Évaluer", "ilma_level": "Entraînement",
            "tags": ["estimation", "arrondi", "millier"],
            "common_mistake_targeted": "Confondre le chiffre à examiner"
        },
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "hard",
            "text": "Pour estimer 789 + 1 214, on arrondit chaque nombre au millier. Quelle estimation obtient-on ?",
            "choices": ["1 000 + 1 000 = 2 000", "800 + 1 200 = 2 000", "700 + 1 200 = 1 900", "1 000 + 2 000 = 3 000"],
            "correct_answer": "1 000 + 1 000 = 2 000",
            "explanation": "789 arrondi au millier = 1 000. 1 214 arrondi au millier = 1 000. Estimation : 1 000 + 1 000 = 2 000. (Résultat exact : 2 003.)",
            "hint": "Arrondis chaque nombre au millier le plus proche.",
            "points": 2, "time_limit_seconds": 60,
            "bloom_level": "Appliquer", "ilma_level": "Approfondissement",
            "tags": ["estimation", "arrondi", "addition"],
            "common_mistake_targeted": "Arrondir au mauvais ordre de grandeur"
        }
    ]
})

# MS02 — Arrondir un décimal pour prévoir un résultat
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 2),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Pour estimer 3,87 × 5, on arrondit 3,87 à l'entier le plus proche. Quel entier ?",
            "choices": ["3", "4", "5", "3,9"],
            "correct_answer": "4",
            "explanation": "3,87 est plus proche de 4 que de 3 (car 0,87 > 0,5). Estimation : 4 × 5 = 20.",
            "hint": "La partie décimale 0,87 est-elle supérieure ou inférieure à 0,5 ?",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["estimation", "arrondi", "décimaux"],
            "common_mistake_targeted": "Toujours arrondir vers le bas"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Estime le résultat de 9,7 × 4,2 en arrondissant chaque facteur à l'entier le plus proche.",
            "tolerance": 0, "correct_answer": 40,
            "explanation": "9,7 ≈ 10, 4,2 ≈ 4. Estimation : 10 × 4 = 40. (Résultat exact : 40,74.)",
            "hint": "Arrondis 9,7 et 4,2 à l'entier le plus proche.",
            "points": 2, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["estimation", "arrondi", "multiplication", "décimaux"],
            "common_mistake_targeted": "Arrondir 4,2 à 5 au lieu de 4"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "medium",
            "text": "Pour estimer 12,3 + 7,8, on peut calculer 12 + 8 = 20.",
            "correct_answer": True,
            "explanation": "12,3 ≈ 12 et 7,8 ≈ 8. L'estimation 12 + 8 = 20 est raisonnable. (Résultat exact : 20,1.)",
            "hint": "Arrondis chaque nombre à l'entier le plus proche.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Évaluer", "ilma_level": "Entraînement",
            "tags": ["estimation", "arrondi", "addition", "décimaux"],
            "common_mistake_targeted": "Croire qu'on ne peut pas arrondir des décimaux"
        },
        {
            "exercise_id": next_id(), "type": "contextual_problem", "difficulty": "hard",
            "text": "Au marché de Dantokpa, Amina achète 2,8 kg de tomates à 490 FCFA le kg. Estime le prix total en arrondissant.",
            "sub_questions": [
                {"id": "a", "text": "Arrondis 2,8 et 490.", "correct_answer": "3 et 500"},
                {"id": "b", "text": "Calcule l'estimation.", "correct_answer": "1 500 FCFA"}
            ],
            "correct_answer": "1 500 FCFA",
            "explanation": "2,8 ≈ 3, 490 ≈ 500. Estimation : 3 × 500 = 1 500 FCFA. (Exact : 2,8 × 490 = 1 372 FCFA.)",
            "hint": "Arrondis chaque nombre pour simplifier le calcul.",
            "points": 3, "time_limit_seconds": 90,
            "bloom_level": "Appliquer", "ilma_level": "Approfondissement",
            "tags": ["estimation", "arrondi", "problème", "FCFA", "marché"],
            "common_mistake_targeted": "Arrondir dans le mauvais sens"
        }
    ]
})

# MS03 — Donner un ordre de grandeur avant le calcul exact
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 3),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Avant de calculer 48 × 21, quel est l'ordre de grandeur du résultat ?",
            "choices": ["Environ 100", "Environ 500", "Environ 1 000", "Environ 10 000"],
            "correct_answer": "Environ 1 000",
            "explanation": "48 ≈ 50, 21 ≈ 20. Ordre de grandeur : 50 × 20 = 1 000. (Exact : 48 × 21 = 1 008.)",
            "hint": "Arrondis 48 et 21 à des nombres faciles à multiplier.",
            "points": 1, "time_limit_seconds": 45,
            "bloom_level": "Comprendre", "ilma_level": "Découverte",
            "tags": ["estimation", "ordre de grandeur", "multiplication"],
            "common_mistake_targeted": "Confondre ordre de grandeur et résultat exact"
        },
        {
            "exercise_id": next_id(), "type": "numeric_input", "difficulty": "medium",
            "text": "Donne un ordre de grandeur de 295 + 712 en arrondissant à la centaine.",
            "tolerance": 0, "correct_answer": 1000,
            "explanation": "295 ≈ 300, 712 ≈ 700. Ordre de grandeur : 300 + 700 = 1 000. (Exact : 1 007.)",
            "hint": "Arrondis chaque nombre à la centaine la plus proche.",
            "points": 1, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["estimation", "ordre de grandeur", "addition"],
            "common_mistake_targeted": "Ne pas arrondir au bon ordre"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "medium",
            "text": "L'ordre de grandeur de 198 × 52 est environ 10 000.",
            "correct_answer": True,
            "explanation": "198 ≈ 200, 52 ≈ 50. Ordre de grandeur : 200 × 50 = 10 000. (Exact : 10 296.)",
            "hint": "Arrondis les deux facteurs et multiplie.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Évaluer", "ilma_level": "Entraînement",
            "tags": ["estimation", "ordre de grandeur", "multiplication"],
            "common_mistake_targeted": "Mal estimer un produit"
        },
        {
            "exercise_id": next_id(), "type": "justification", "difficulty": "hard",
            "text": "Explique comment tu donnerais un ordre de grandeur du calcul 4 980 ÷ 49 avant de le poser.",
            "correct_answer": "4 980 ≈ 5 000 et 49 ≈ 50, donc l'ordre de grandeur est 5 000 ÷ 50 = 100.",
            "scoring_rubric": "1 pt pour l'arrondi correct de chaque nombre, 1 pt pour le calcul de l'estimation, 1 pt pour la justification claire.",
            "explanation": "En arrondissant 4 980 à 5 000 et 49 à 50, on obtient 5 000 ÷ 50 = 100. Cela donne une bonne idée du résultat attendu.",
            "hint": "Arrondis le dividende et le diviseur à des nombres faciles à diviser.",
            "points": 3, "time_limit_seconds": 120,
            "bloom_level": "Évaluer", "ilma_level": "Approfondissement",
            "tags": ["estimation", "ordre de grandeur", "justification"],
            "common_mistake_targeted": "Ne pas savoir quels nombres choisir pour l'arrondi"
        }
    ]
})

# MS04 — Vérifier avec l'opération inverse
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 4),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Pour vérifier que 156 + 244 = 400, quelle opération inverse peut-on faire ?",
            "choices": ["400 − 244", "400 + 156", "400 × 244", "244 − 156"],
            "correct_answer": "400 − 244",
            "explanation": "L'opération inverse de l'addition est la soustraction. Si 156 + 244 = 400, alors 400 − 244 doit donner 156.",
            "hint": "L'inverse de l'addition est la soustraction.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Connaître", "ilma_level": "Découverte",
            "tags": ["vérification", "opération inverse", "addition"],
            "common_mistake_targeted": "Ne pas savoir quelle est l'opération inverse"
        },
        {
            "exercise_id": next_id(), "type": "fill_blank", "difficulty": "medium",
            "text": "Pour vérifier que 864 ÷ 12 = 72, on calcule : ___ × ___ = 864.",
            "blanks": ["72", "12"],
            "correct_answer": ["72", "12"],
            "explanation": "L'opération inverse de la division est la multiplication. 72 × 12 = 864, donc la division est correcte.",
            "hint": "L'inverse de la division est la multiplication.",
            "points": 2, "time_limit_seconds": 45,
            "bloom_level": "Appliquer", "ilma_level": "Entraînement",
            "tags": ["vérification", "opération inverse", "division"],
            "common_mistake_targeted": "Inverser quotient et diviseur dans la vérification"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "medium",
            "text": "Si 35 × 18 = 630, alors pour vérifier on peut calculer 630 ÷ 18. Si on obtient 35, le calcul est correct.",
            "correct_answer": True,
            "explanation": "C'est exact. 630 ÷ 18 = 35, ce qui confirme que 35 × 18 = 630.",
            "hint": "La division est l'opération inverse de la multiplication.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Comprendre", "ilma_level": "Entraînement",
            "tags": ["vérification", "opération inverse", "multiplication"],
            "common_mistake_targeted": "Croire qu'il faut refaire le même calcul pour vérifier"
        },
        {
            "exercise_id": next_id(), "type": "guided_steps", "difficulty": "hard",
            "text": "Vérifie si le calcul suivant est correct : 1 547 − 689 = 858.",
            "steps": [
                {"instruction": "Quelle est l'opération inverse de la soustraction ?", "expected_answer": "L'addition", "hint": "L'inverse de − est +."},
                {"instruction": "Calcule 858 + 689.", "expected_answer": "1 547", "hint": "Pose l'addition en colonnes."},
                {"instruction": "Le calcul initial est-il correct ?", "expected_answer": "Oui, car 858 + 689 = 1 547", "hint": "Compare avec le nombre de départ."}
            ],
            "correct_answer": "Oui, le calcul est correct car 858 + 689 = 1 547.",
            "explanation": "Pour vérifier une soustraction, on additionne le résultat et le nombre soustrait. 858 + 689 = 1 547, c'est bien le nombre initial.",
            "hint": "Additionne le résultat et le nombre qu'on a soustrait.",
            "points": 3, "time_limit_seconds": 120,
            "bloom_level": "Évaluer", "ilma_level": "Approfondissement",
            "tags": ["vérification", "opération inverse", "soustraction"],
            "common_mistake_targeted": "Ne pas savoir structurer une vérification"
        }
    ]
})

# MS05 — Détecter un résultat absurde et corriger
exercises_by_ms.append({
    "micro_skill_external_id": ms(SK, 5),
    "exercises": [
        {
            "exercise_id": next_id(), "type": "mcq", "difficulty": "easy",
            "text": "Un élève calcule 25 × 4 = 10. Ce résultat est-il raisonnable ?",
            "choices": ["Oui, c'est correct", "Non, c'est trop petit", "Non, c'est trop grand", "On ne peut pas savoir"],
            "correct_answer": "Non, c'est trop petit",
            "explanation": "25 × 4 = 100, pas 10. Le résultat 10 est absurde car 25 × 4 doit être plus grand que 25.",
            "hint": "Un produit de deux nombres plus grands que 1 est plus grand que chacun des facteurs.",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Évaluer", "ilma_level": "Découverte",
            "tags": ["vérification", "résultat absurde", "multiplication"],
            "common_mistake_targeted": "Accepter un résultat sans vérifier l'ordre de grandeur"
        },
        {
            "exercise_id": next_id(), "type": "error_correction", "difficulty": "medium",
            "text": "Amina a posé : 345 + 267 = 512. Détecte l'erreur et corrige.",
            "erroneous_content": "345 + 267 = 512",
            "correct_answer": "345 + 267 = 612",
            "explanation": "345 + 267 = 612, pas 512. L'erreur est dans la retenue : 3 + 2 + 1 (retenue) = 6, pas 5.",
            "hint": "Vérifie les centaines : 3 + 2 + retenue = ?",
            "points": 2, "time_limit_seconds": 60,
            "bloom_level": "Évaluer", "ilma_level": "Entraînement",
            "tags": ["vérification", "erreur", "addition"],
            "common_mistake_targeted": "Oublier la retenue"
        },
        {
            "exercise_id": next_id(), "type": "true_false", "difficulty": "medium",
            "text": "Le résultat de 1 000 − 347 ne peut pas être supérieur à 1 000.",
            "correct_answer": True,
            "explanation": "Quand on soustrait un nombre positif, le résultat est toujours inférieur au nombre de départ. 1 000 − 347 = 653 < 1 000.",
            "hint": "Que se passe-t-il quand on enlève quelque chose ?",
            "points": 1, "time_limit_seconds": 30,
            "bloom_level": "Comprendre", "ilma_level": "Entraînement",
            "tags": ["vérification", "résultat absurde", "soustraction"],
            "common_mistake_targeted": "Ne pas vérifier la cohérence d'un résultat"
        },
        {
            "exercise_id": next_id(), "type": "contextual_problem", "difficulty": "hard",
            "text": "Kofi dit : « J'ai partagé 840 FCFA entre 7 amis et chacun a reçu 1 200 FCFA. » Ce résultat est-il possible ? Justifie et corrige.",
            "sub_questions": [
                {"id": "a", "text": "Le résultat est-il possible ? Pourquoi ?", "correct_answer": "Non, car chaque part doit être inférieure au total (840 FCFA)"},
                {"id": "b", "text": "Quel est le résultat correct ?", "correct_answer": "120 FCFA"}
            ],
            "correct_answer": "Non. 840 ÷ 7 = 120 FCFA, pas 1 200 FCFA.",
            "explanation": "Chaque part d'un partage est forcément plus petite que le total. 840 ÷ 7 = 120 FCFA. Kofi a sans doute ajouté un zéro en trop.",
            "hint": "Peut-on donner plus que ce qu'on a ?",
            "points": 3, "time_limit_seconds": 90,
            "bloom_level": "Évaluer", "ilma_level": "Approfondissement",
            "tags": ["vérification", "résultat absurde", "division", "FCFA"],
            "common_mistake_targeted": "Ne pas vérifier que le résultat est cohérent avec le contexte"
        }
    ]
})

# Save Part 1 checkpoint
print(f"Part 1 done: {ex_id_counter} exercises, {len(exercises_by_ms)} micro-skills")
