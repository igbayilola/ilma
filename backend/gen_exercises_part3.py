#!/usr/bin/env python3
"""Generate exercises for NUM-DIVISIBILITE-2-3-5 (MS01-MS04) — exercises EX041-EX056."""
import json

def get_skill3_exercises():
    """NUM-DIVISIBILITE-2-3-5: Criteres de divisibilite"""
    return [
        {
            "micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS01",
            "exercises": [
                {
                    "exercise_id": "EX041",
                    "type": "true_false",
                    "difficulty": "easy",
                    "text": "Le nombre 4 738 est divisible par 2.",
                    "correct_answer": True,
                    "explanation": "Un nombre est divisible par 2 si son dernier chiffre est pair (0, 2, 4, 6 ou 8). Le dernier chiffre de 4 738 est 8 (pair), donc il est divisible par 2.",
                    "hint": "Regarde uniquement le dernier chiffre du nombre.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["divisibilite", "critere par 2", "pair"],
                    "common_mistake_targeted": "Regarder le premier chiffre au lieu du dernier"
                },
                {
                    "exercise_id": "EX042",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Parmi ces nombres, lesquels sont divisibles par 2 ? 3 456, 7 891, 12 340, 55 553",
                    "choices": [
                        "3 456 et 12 340",
                        "3 456, 7 891 et 12 340",
                        "Tous les quatre",
                        "3 456 seulement"
                    ],
                    "correct_answer": "3 456 et 12 340",
                    "explanation": "3 456 (dernier chiffre 6 : pair) et 12 340 (dernier chiffre 0 : pair) sont divisibles par 2. 7 891 (1 : impair) et 55 553 (3 : impair) ne le sont pas.",
                    "hint": "Verifie si le dernier chiffre de chaque nombre est pair.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "critere par 2", "selection"],
                    "common_mistake_targeted": "Oublier que 0 est un chiffre pair"
                },
                {
                    "exercise_id": "EX043",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Trouve le plus petit chiffre qui rend 23 45_ divisible par 2 : ___",
                    "blanks": ["0"],
                    "correct_answer": ["0"],
                    "explanation": "Pour que 23 45_ soit divisible par 2, le dernier chiffre doit etre pair : 0, 2, 4, 6 ou 8. Le plus petit est 0.",
                    "hint": "Quel est le plus petit chiffre pair ?",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "critere par 2", "completement"],
                    "common_mistake_targeted": "Oublier que 0 est un chiffre pair et repondre 2"
                },
                {
                    "exercise_id": "EX044",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Au marche Dantokpa a Cotonou, une marchande a 1 347 oranges. Elle veut les repartir en paquets de 2.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Peut-elle faire des paquets de 2 sans qu'il en reste ?",
                            "correct_answer": "Non"
                        },
                        {
                            "id": "b",
                            "text": "Justifie ta reponse en utilisant le critere de divisibilite par 2.",
                            "correct_answer": "1 347 se termine par 7 qui est impair, donc 1 347 n'est pas divisible par 2."
                        },
                        {
                            "id": "c",
                            "text": "Combien d'oranges restera-t-il ?",
                            "correct_answer": "1"
                        }
                    ],
                    "correct_answer": {"a": "Non", "b": "Le dernier chiffre 7 est impair", "c": "1"},
                    "explanation": "1 347 se termine par 7 (impair), donc n'est pas divisible par 2. 1 347 = 2 x 673 + 1. Il restera 1 orange.",
                    "hint": "Regarde le dernier chiffre de 1 347.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["divisibilite", "critere par 2", "probleme", "Benin", "marche Dantokpa"],
                    "common_mistake_targeted": "Ne pas faire le lien entre divisibilite et reste de la division"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS02",
            "exercises": [
                {
                    "exercise_id": "EX045",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Quel critere permet de savoir si un nombre est divisible par 5 ?",
                    "choices": [
                        "Son dernier chiffre est 0 ou 5",
                        "Son dernier chiffre est pair",
                        "La somme de ses chiffres est divisible par 5",
                        "Son premier chiffre est 5"
                    ],
                    "correct_answer": "Son dernier chiffre est 0 ou 5",
                    "explanation": "Un nombre est divisible par 5 si et seulement si son dernier chiffre est 0 ou 5.",
                    "hint": "Pense aux nombres 5, 10, 15, 20, 25... Que remarques-tu sur leur dernier chiffre ?",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["divisibilite", "critere par 5", "regle"],
                    "common_mistake_targeted": "Confondre avec le critere de divisibilite par 3"
                },
                {
                    "exercise_id": "EX046",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Parmi les nombres suivants, ecris ceux qui sont divisibles par 5 : 230, 452, 1 005, 3 333, 78 900.\nReponse : ___",
                    "blanks": ["230, 1 005, 78 900"],
                    "correct_answer": ["230, 1 005, 78 900"],
                    "explanation": "230 (termine par 0), 1 005 (termine par 5), 78 900 (termine par 0) sont divisibles par 5. 452 (termine par 2) et 3 333 (termine par 3) ne le sont pas.",
                    "hint": "Regarde le dernier chiffre de chaque nombre : est-ce 0 ou 5 ?",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "critere par 5", "tri"],
                    "common_mistake_targeted": "Oublier les nombres terminant par 5 (ne garder que ceux en 0)"
                },
                {
                    "exercise_id": "EX047",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Le nombre 10 035 est divisible a la fois par 2 et par 5.",
                    "correct_answer": False,
                    "explanation": "10 035 se termine par 5, donc il est divisible par 5. Mais 5 est impair, donc 10 035 n'est pas divisible par 2. Il n'est pas divisible par les deux a la fois.",
                    "hint": "Pour etre divisible par 2 ET par 5, le nombre doit se terminer par quel chiffre ?",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "critere par 5", "critere par 2", "double critere"],
                    "common_mistake_targeted": "Ne verifier qu'un seul critere au lieu des deux"
                },
                {
                    "exercise_id": "EX048",
                    "type": "numeric_input",
                    "difficulty": "hard",
                    "text": "On distribue 2 375 FCFA en pieces de 5 FCFA. Combien de pieces obtient-on ?",
                    "tolerance": 0,
                    "correct_answer": 475,
                    "explanation": "2 375 se termine par 5, donc est divisible par 5. 2 375 / 5 = 475 pieces.",
                    "hint": "Divise 2 375 par 5.",
                    "points": 3,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["divisibilite", "critere par 5", "division", "FCFA"],
                    "common_mistake_targeted": "Erreur de calcul dans la division par 5"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS03",
            "exercises": [
                {
                    "exercise_id": "EX049",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Pour savoir si 123 est divisible par 3, que faut-il faire ?",
                    "choices": [
                        "Calculer la somme des chiffres : 1 + 2 + 3 = 6",
                        "Regarder le dernier chiffre : 3",
                        "Diviser 123 par 3 directement",
                        "Regarder si le nombre est pair"
                    ],
                    "correct_answer": "Calculer la somme des chiffres : 1 + 2 + 3 = 6",
                    "explanation": "Le critere de divisibilite par 3 : on additionne tous les chiffres du nombre. Si la somme est divisible par 3, le nombre l'est aussi. 1 + 2 + 3 = 6, et 6 est divisible par 3, donc 123 est divisible par 3.",
                    "hint": "Additionne tous les chiffres du nombre.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["divisibilite", "critere par 3", "somme des chiffres"],
                    "common_mistake_targeted": "Confondre le critere par 3 avec celui par 2 ou par 5"
                },
                {
                    "exercise_id": "EX050",
                    "type": "guided_steps",
                    "difficulty": "medium",
                    "text": "Verifie si 4 521 est divisible par 3.",
                    "steps": [
                        {
                            "instruction": "Calcule la somme des chiffres de 4 521.",
                            "expected_answer": "4 + 5 + 2 + 1 = 12",
                            "hint": "Additionne 4, 5, 2 et 1."
                        },
                        {
                            "instruction": "La somme 12 est-elle divisible par 3 ?",
                            "expected_answer": "Oui, car 12 = 3 x 4",
                            "hint": "12 / 3 = ?"
                        },
                        {
                            "instruction": "Conclus : 4 521 est-il divisible par 3 ?",
                            "expected_answer": "Oui",
                            "hint": "Si la somme des chiffres est divisible par 3, le nombre aussi."
                        }
                    ],
                    "correct_answer": "Oui, 4 521 est divisible par 3",
                    "explanation": "Somme des chiffres : 4 + 5 + 2 + 1 = 12. 12 est divisible par 3 (12 = 3 x 4), donc 4 521 est divisible par 3.",
                    "hint": "Additionne les chiffres, puis verifie si le resultat est un multiple de 3.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "critere par 3", "etapes guidees"],
                    "common_mistake_targeted": "Faire une erreur dans l'addition des chiffres"
                },
                {
                    "exercise_id": "EX051",
                    "type": "true_false",
                    "difficulty": "hard",
                    "text": "Le nombre 8 888 est divisible par 3.",
                    "correct_answer": False,
                    "explanation": "Somme des chiffres : 8 + 8 + 8 + 8 = 32. 32 n'est pas divisible par 3 (32 = 3 x 10 + 2). Donc 8 888 n'est pas divisible par 3.",
                    "hint": "Calcule 8 + 8 + 8 + 8, puis verifie si le resultat est un multiple de 3.",
                    "points": 3,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["divisibilite", "critere par 3", "vrai-faux"],
                    "common_mistake_targeted": "Croire que si un nombre n'a que des chiffres divisibles par 2, il est aussi divisible par 3"
                },
                {
                    "exercise_id": "EX052",
                    "type": "contextual_problem",
                    "difficulty": "medium",
                    "text": "Un instituteur de Parakou a 234 cahiers. Il veut les distribuer equitablement a 3 groupes d'eleves.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "234 est-il divisible par 3 ? Justifie avec le critere.",
                            "correct_answer": "Oui, car 2 + 3 + 4 = 9 et 9 est divisible par 3."
                        },
                        {
                            "id": "b",
                            "text": "Combien de cahiers recevra chaque groupe ?",
                            "correct_answer": "78"
                        }
                    ],
                    "correct_answer": {"a": "Oui, 2 + 3 + 4 = 9 divisible par 3", "b": "78"},
                    "explanation": "Somme des chiffres : 2 + 3 + 4 = 9. 9 est divisible par 3, donc 234 l'est aussi. 234 / 3 = 78 cahiers par groupe.",
                    "hint": "Additionne les chiffres de 234, puis divise 234 par 3.",
                    "points": 2,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "critere par 3", "probleme", "Benin", "Parakou"],
                    "common_mistake_targeted": "Oublier de justifier avec le critere de divisibilite"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS04",
            "exercises": [
                {
                    "exercise_id": "EX053",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Pour simplifier la fraction 6/10, par quel nombre peut-on diviser le numerateur et le denominateur ?",
                    "choices": ["Par 2", "Par 3", "Par 5", "Par 7"],
                    "correct_answer": "Par 2",
                    "explanation": "6 et 10 sont tous les deux pairs (divisibles par 2). 6/2 = 3 et 10/2 = 5. Donc 6/10 = 3/5.",
                    "hint": "Cherche un nombre qui divise a la fois 6 et 10.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["divisibilite", "simplification", "fractions"],
                    "common_mistake_targeted": "Ne pas identifier le diviseur commun"
                },
                {
                    "exercise_id": "EX054",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Simplifie la fraction 15/45 en utilisant le critere de divisibilite.\n15/45 = ___ / ___",
                    "blanks": ["1", "3"],
                    "correct_answer": ["1", "3"],
                    "explanation": "15 et 45 sont divisibles par 5 : 15/5 = 3, 45/5 = 9. Puis 3/9 : 3 et 9 sont divisibles par 3 : 3/3 = 1, 9/3 = 3. Donc 15/45 = 1/3.",
                    "hint": "15 et 45 se terminent par 5, ils sont donc divisibles par 5. Simplifie une premiere fois.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "simplification", "fractions", "etapes"],
                    "common_mistake_targeted": "Ne simplifier qu'une seule fois au lieu d'aller jusqu'a la fraction irreductible"
                },
                {
                    "exercise_id": "EX055",
                    "type": "matching",
                    "difficulty": "hard",
                    "text": "Associe chaque fraction a sa forme simplifiee :",
                    "left_items": ["12/18", "20/30", "9/15"],
                    "right_items": ["2/3", "3/5", "2/3"],
                    "correct_answer": {
                        "12/18": "2/3",
                        "20/30": "2/3",
                        "9/15": "3/5"
                    },
                    "explanation": "12/18 : divisibles par 6 -> 2/3. 20/30 : divisibles par 10 -> 2/3. 9/15 : divisibles par 3 -> 3/5.",
                    "hint": "Utilise les criteres de divisibilite pour trouver les diviseurs communs.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["divisibilite", "simplification", "fractions", "association"],
                    "common_mistake_targeted": "Confondre les fractions equivalentes"
                },
                {
                    "exercise_id": "EX056",
                    "type": "guided_steps",
                    "difficulty": "medium",
                    "text": "Simplifie la fraction 30/75 en utilisant les criteres de divisibilite.",
                    "steps": [
                        {
                            "instruction": "30 et 75 sont-ils divisibles par 5 ? Justifie.",
                            "expected_answer": "Oui, car 30 se termine par 0 et 75 se termine par 5.",
                            "hint": "Quel est le dernier chiffre de chaque nombre ?"
                        },
                        {
                            "instruction": "Divise le numerateur et le denominateur par 5.",
                            "expected_answer": "30/5 = 6, 75/5 = 15, donc 30/75 = 6/15",
                            "hint": "30 / 5 = ? et 75 / 5 = ?"
                        },
                        {
                            "instruction": "6 et 15 sont-ils divisibles par 3 ? Simplifie si oui.",
                            "expected_answer": "Oui : 6 + 15 -> 6/3 = 2, 15/3 = 5. Donc 6/15 = 2/5.",
                            "hint": "Somme des chiffres de 6 = 6 (divisible par 3). Somme des chiffres de 15 = 6 (divisible par 3)."
                        }
                    ],
                    "correct_answer": "2/5",
                    "explanation": "30/75 -> divisibles par 5 -> 6/15 -> divisibles par 3 -> 2/5. La fraction simplifiee est 2/5.",
                    "hint": "Cherche d'abord si les deux nombres sont divisibles par 5, puis par 3.",
                    "points": 2,
                    "time_limit_seconds": 150,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["divisibilite", "simplification", "fractions", "etapes guidees"],
                    "common_mistake_targeted": "S'arreter apres la premiere simplification"
                }
            ]
        }
    ]

if __name__ == "__main__":
    data = get_skill3_exercises()
    with open("/tmp/part3.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Part 3: {len(data)} micro-skills, {sum(len(ms['exercises']) for ms in data)} exercises")
