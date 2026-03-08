#!/usr/bin/env python3
"""Generate exercises for NUM-DROITE-NUM-ENTIERS (MS01-MS04) — exercises EX025-EX040."""
import json

def get_skill2_exercises():
    """NUM-DROITE-NUM-ENTIERS: Placer, encadrer, comparer, ordonner sur droite numerique"""
    return [
        {
            "micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS01",
            "exercises": [
                {
                    "exercise_id": "EX025",
                    "type": "tracing",
                    "difficulty": "easy",
                    "text": "Place le nombre 3 000 sur la droite numerique graduee de 0 a 10 000.",
                    "number_line": {
                        "min": 0,
                        "max": 10000,
                        "step": 1000,
                        "unit": "",
                        "label_min": "0",
                        "label_max": "10 000"
                    },
                    "correct_answer": {"3000": 0.3},
                    "explanation": "La droite va de 0 a 10 000 avec un pas de 1 000. Le nombre 3 000 se place a la 3e graduation.",
                    "hint": "Chaque graduation represente 1 000. Compte 3 graduations depuis 0.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "droite numerique", "placement"],
                    "common_mistake_targeted": "Ne pas respecter l'echelle de la droite"
                },
                {
                    "exercise_id": "EX026",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Sur une droite graduee de 0 a 1 000 000 avec un pas de 100 000, a quelle graduation se trouve 450 000 ?",
                    "choices": [
                        "Entre la 4e et la 5e graduation",
                        "A la 4e graduation",
                        "A la 5e graduation",
                        "Entre la 3e et la 4e graduation"
                    ],
                    "correct_answer": "Entre la 4e et la 5e graduation",
                    "explanation": "La 4e graduation = 400 000, la 5e = 500 000. 450 000 est exactement entre les deux.",
                    "hint": "Chaque graduation vaut 100 000. La 4e = 400 000, la 5e = 500 000.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "droite numerique", "reperage"],
                    "common_mistake_targeted": "Confondre le numero de la graduation avec la valeur"
                },
                {
                    "exercise_id": "EX027",
                    "type": "tracing",
                    "difficulty": "medium",
                    "text": "Place les nombres 25 000 000 et 75 000 000 sur la droite numerique.",
                    "number_line": {
                        "min": 0,
                        "max": 100000000,
                        "step": 10000000,
                        "unit": "",
                        "label_min": "0",
                        "label_max": "100 000 000"
                    },
                    "correct_answer": {"25000000": 0.25, "75000000": 0.75},
                    "explanation": "25 000 000 est au quart du segment (25/100) et 75 000 000 aux trois quarts (75/100).",
                    "hint": "25 millions = 1/4 de 100 millions, 75 millions = 3/4.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "droite numerique", "millions"],
                    "common_mistake_targeted": "Mal estimer la position proportionnelle"
                },
                {
                    "exercise_id": "EX028",
                    "type": "numeric_input",
                    "difficulty": "hard",
                    "text": "Sur une droite graduee de 200 000 a 300 000 avec un pas de 10 000, quel nombre se trouve a la 7e graduation apres 200 000 ?",
                    "tolerance": 0,
                    "correct_answer": 270000,
                    "explanation": "Chaque graduation ajoute 10 000. La 7e graduation apres 200 000 : 200 000 + 7 x 10 000 = 270 000.",
                    "hint": "Calcule 200 000 + 7 fois le pas de graduation.",
                    "points": 3,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "droite numerique", "calcul"],
                    "common_mistake_targeted": "Oublier de partir de 200 000 (et non de 0)"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS02",
            "exercises": [
                {
                    "exercise_id": "EX029",
                    "type": "fill_blank",
                    "difficulty": "easy",
                    "text": "Encadre 45 320 entre deux dizaines de mille consecutives : ___ < 45 320 < ___",
                    "blanks": ["40 000", "50 000"],
                    "correct_answer": ["40 000", "50 000"],
                    "explanation": "45 320 est entre 40 000 (4 dizaines de mille) et 50 000 (5 dizaines de mille).",
                    "hint": "Quel est le chiffre des dizaines de mille dans 45 320 ?",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "encadrement", "dizaines de mille"],
                    "common_mistake_targeted": "Encadrer par des milliers au lieu de dizaines de mille"
                },
                {
                    "exercise_id": "EX030",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quel est l'encadrement de 678 453 000 a la centaine de millions pres ?",
                    "choices": [
                        "600 000 000 < 678 453 000 < 700 000 000",
                        "670 000 000 < 678 453 000 < 680 000 000",
                        "678 000 000 < 678 453 000 < 679 000 000",
                        "500 000 000 < 678 453 000 < 800 000 000"
                    ],
                    "correct_answer": "600 000 000 < 678 453 000 < 700 000 000",
                    "explanation": "Le chiffre des centaines de millions est 6. Donc : 600 000 000 < 678 453 000 < 700 000 000.",
                    "hint": "A la centaine de millions pres, on garde le chiffre des centaines de millions.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "encadrement", "centaines de millions"],
                    "common_mistake_targeted": "Confondre encadrement a la centaine de millions et a la dizaine de millions"
                },
                {
                    "exercise_id": "EX031",
                    "type": "fill_blank",
                    "difficulty": "hard",
                    "text": "Encadre 99 999 entre deux centaines consecutives : ___ < 99 999 < ___",
                    "blanks": ["99 900", "100 000"],
                    "correct_answer": ["99 900", "100 000"],
                    "explanation": "99 999 est entre 99 900 (999 centaines) et 100 000 (1 000 centaines). On passe a la classe superieure.",
                    "hint": "Attention : la centaine superieure apres 99 900 est 100 000.",
                    "points": 3,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "encadrement", "passage de classe"],
                    "common_mistake_targeted": "Ne pas passer a la classe superieure (ecrire 99 900 < 99 999 < 99 1000)"
                },
                {
                    "exercise_id": "EX032",
                    "type": "contextual_problem",
                    "difficulty": "medium",
                    "text": "La ville de Porto-Novo compte 264 320 habitants. Le maire veut arrondir ce nombre a la dizaine de mille pres.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Encadre 264 320 entre deux dizaines de mille consecutives.",
                            "correct_answer": "260 000 < 264 320 < 270 000"
                        },
                        {
                            "id": "b",
                            "text": "De quel multiple de 10 000 ce nombre est-il le plus proche ?",
                            "correct_answer": "260 000"
                        }
                    ],
                    "correct_answer": {"a": "260 000 < 264 320 < 270 000", "b": "260 000"},
                    "explanation": "264 320 est entre 260 000 et 270 000. Il est plus proche de 260 000 (difference de 4 320) que de 270 000 (difference de 5 680).",
                    "hint": "Regarde le chiffre des unites de mille : 4 < 5, donc on arrondit a l'inferieur.",
                    "points": 2,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "encadrement", "arrondissement", "Benin", "Porto-Novo"],
                    "common_mistake_targeted": "Arrondir au superieur au lieu de l'inferieur quand le chiffre est < 5"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS03",
            "exercises": [
                {
                    "exercise_id": "EX033",
                    "type": "ordering",
                    "difficulty": "easy",
                    "text": "Range ces nombres dans l'ordre croissant : 12 500, 125 000, 1 250, 1 250 000",
                    "items": ["12 500", "125 000", "1 250", "1 250 000"],
                    "correct_answer": ["1 250", "12 500", "125 000", "1 250 000"],
                    "explanation": "1 250 < 12 500 < 125 000 < 1 250 000. On compare d'abord le nombre de chiffres.",
                    "hint": "Le nombre avec le moins de chiffres est le plus petit.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "ordre croissant", "comparaison"],
                    "common_mistake_targeted": "Se laisser tromper par les memes chiffres (1, 2, 5, 0)"
                },
                {
                    "exercise_id": "EX034",
                    "type": "ordering",
                    "difficulty": "medium",
                    "text": "Range ces nombres dans l'ordre decroissant : 8 500 000, 8 050 000, 8 005 000, 8 500 500",
                    "items": ["8 500 000", "8 050 000", "8 005 000", "8 500 500"],
                    "correct_answer": ["8 500 500", "8 500 000", "8 050 000", "8 005 000"],
                    "explanation": "Tous ont 7 chiffres. On compare chiffre par chiffre : 8 500 500 > 8 500 000 > 8 050 000 > 8 005 000.",
                    "hint": "Quand les nombres ont le meme nombre de chiffres, compare-les de gauche a droite.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "ordre decroissant", "comparaison"],
                    "common_mistake_targeted": "Confondre 8 050 000 et 8 500 000 a cause des zeros"
                },
                {
                    "exercise_id": "EX035",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Voici les populations de 5 villes du Benin : Cotonou (680 000), Abomey-Calavi (760 000), Porto-Novo (264 000), Parakou (255 000), Djougou (237 000).",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Range ces villes de la plus peuplee a la moins peuplee.",
                            "correct_answer": "Abomey-Calavi, Cotonou, Porto-Novo, Parakou, Djougou"
                        },
                        {
                            "id": "b",
                            "text": "Quelle est la difference de population entre la ville la plus peuplee et la moins peuplee ?",
                            "correct_answer": "523 000"
                        }
                    ],
                    "correct_answer": {"a": "Abomey-Calavi, Cotonou, Porto-Novo, Parakou, Djougou", "b": "523 000"},
                    "explanation": "760 000 > 680 000 > 264 000 > 255 000 > 237 000. Difference : 760 000 - 237 000 = 523 000.",
                    "hint": "Compare d'abord les centaines de mille.",
                    "points": 3,
                    "time_limit_seconds": 180,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "ordre decroissant", "probleme", "Benin", "populations"],
                    "common_mistake_targeted": "Se tromper dans l'ordre des villes de taille similaire"
                },
                {
                    "exercise_id": "EX036",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Si on range 305 200, 305 020 et 350 200 dans l'ordre croissant, on obtient : 305 020 < 305 200 < 350 200.",
                    "correct_answer": True,
                    "explanation": "305 020 < 305 200 (a la position des centaines, 0 < 2) et 305 200 < 350 200 (a la position des dizaines de mille, 0 < 5).",
                    "hint": "Compare chiffre par chiffre de gauche a droite.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "ordre croissant", "vrai-faux"],
                    "common_mistake_targeted": "Confondre 305 020 et 305 200 a cause de la position des zeros"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS04",
            "exercises": [
                {
                    "exercise_id": "EX037",
                    "type": "short_answer",
                    "difficulty": "easy",
                    "text": "Compare avec <, > ou = : 7 890 000 ___ 7 980 000",
                    "accepted_answers": ["<"],
                    "correct_answer": "<",
                    "explanation": "7 890 000 < 7 980 000 car a la position des dizaines de mille : 9 > 8 (on compare les centaines de mille d'abord : 8 < 9).",
                    "hint": "Les deux nombres commencent par 7. Compare le 2e chiffre.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "comparaison", "symboles"],
                    "common_mistake_targeted": "Comparer les derniers chiffres au lieu des premiers"
                },
                {
                    "exercise_id": "EX038",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Complete avec <, > ou = :\na) 450 300 ___ 450 030\nb) 1 000 000 ___ 999 999\nc) 302 000 ___ 302 000",
                    "blanks": [">", ">", "="],
                    "correct_answer": [">", ">", "="],
                    "explanation": "a) 450 300 > 450 030 (centaines : 3 > 0). b) 1 000 000 > 999 999 (7 chiffres > 6 chiffres). c) Meme nombre.",
                    "hint": "Compare le nombre de chiffres d'abord, puis chiffre par chiffre.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "comparaison", "symboles"],
                    "common_mistake_targeted": "Penser que 999 999 > 1 000 000 car les chiffres sont plus grands"
                },
                {
                    "exercise_id": "EX039",
                    "type": "justification",
                    "difficulty": "hard",
                    "text": "Femi dit que 999 888 > 1 000 000 parce que 999 888 a des chiffres plus grands. A-t-il raison ? Justifie.",
                    "scoring_rubric": "1 pt : reponse correcte (non). 1 pt : explication (nombre de chiffres). 1 pt : formulation claire.",
                    "correct_answer": "Non. 999 888 a 6 chiffres et 1 000 000 a 7 chiffres. Un nombre a 7 chiffres est toujours plus grand qu'un nombre a 6 chiffres, donc 999 888 < 1 000 000.",
                    "explanation": "On compare d'abord le nombre de chiffres. 1 000 000 (7 chiffres) > 999 888 (6 chiffres). La valeur des chiffres individuels n'est pas le critere principal.",
                    "hint": "Commence par compter le nombre de chiffres de chaque nombre.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Evaluer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "comparaison", "justification", "erreur courante"],
                    "common_mistake_targeted": "Comparer les chiffres individuellement au lieu du nombre total de chiffres"
                },
                {
                    "exercise_id": "EX040",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quel signe faut-il placer entre 72 036 000 et 72 306 000 ?",
                    "choices": ["<", ">", "=", "On ne peut pas comparer"],
                    "correct_answer": "<",
                    "explanation": "72 036 000 < 72 306 000. Les 2 premiers chiffres sont identiques (72). Ensuite, 0 (dizaines de mille du 1er) < 3 (dizaines de mille du 2e).",
                    "hint": "Compare chiffre par chiffre en partant de la gauche jusqu'a trouver une difference.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "comparaison", "zeros intercalaires"],
                    "common_mistake_targeted": "Se tromper a cause de la position des zeros"
                }
            ]
        }
    ]

if __name__ == "__main__":
    data = get_skill2_exercises()
    with open("/tmp/part2.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Part 2: {len(data)} micro-skills, {sum(len(ms['exercises']) for ms in data)} exercises")
