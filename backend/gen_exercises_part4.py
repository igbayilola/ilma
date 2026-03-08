#!/usr/bin/env python3
"""Generate exercises for NUM-DEC-ECRIRE-REP (MS01-MS06) — exercises EX057-EX080."""
import json

def get_skill4_exercises():
    """NUM-DEC-ECRIRE-REP: Nombres decimaux: ecrire, representer, encadrer, arrondir"""
    return [
        {
            "micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS01",
            "exercises": [
                {
                    "exercise_id": "EX057",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Quelle est l'ecriture decimale de la fraction 7/10 ?",
                    "choices": ["0,7", "7,0", "0,07", "0,007"],
                    "correct_answer": "0,7",
                    "explanation": "7/10 = 7 dixiemes = 0,7. On divise 7 par 10.",
                    "hint": "Diviser par 10, c'est placer une virgule avant le chiffre.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "fraction decimale", "conversion"],
                    "common_mistake_targeted": "Confondre dixiemes et centiemes"
                },
                {
                    "exercise_id": "EX058",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Complete les egalites :\na) 35/100 = ___\nb) 0,125 = ___ /1000",
                    "blanks": ["0,35", "125"],
                    "correct_answer": ["0,35", "125"],
                    "explanation": "a) 35/100 = 35 centiemes = 0,35. b) 0,125 = 125 milliemes = 125/1000.",
                    "hint": "Le denominateur indique la position apres la virgule : 10 = 1 chiffre, 100 = 2 chiffres, 1000 = 3 chiffres.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "fraction decimale", "conversion"],
                    "common_mistake_targeted": "Se tromper dans le nombre de zeros du denominateur"
                },
                {
                    "exercise_id": "EX059",
                    "type": "matching",
                    "difficulty": "medium",
                    "text": "Associe chaque fraction a son ecriture decimale :",
                    "left_items": ["3/10", "45/100", "8/1000", "250/1000"],
                    "right_items": ["0,3", "0,45", "0,008", "0,250"],
                    "correct_answer": {
                        "3/10": "0,3",
                        "45/100": "0,45",
                        "8/1000": "0,008",
                        "250/1000": "0,250"
                    },
                    "explanation": "3/10 = 0,3 (1 chiffre apres la virgule). 45/100 = 0,45 (2 chiffres). 8/1000 = 0,008 (3 chiffres avec des zeros). 250/1000 = 0,250.",
                    "hint": "Le nombre de zeros du denominateur donne le nombre de chiffres apres la virgule.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "fraction decimale", "association"],
                    "common_mistake_targeted": "Oublier les zeros devant le numerateur pour 8/1000"
                },
                {
                    "exercise_id": "EX060",
                    "type": "numeric_input",
                    "difficulty": "hard",
                    "text": "Combien de milliemes y a-t-il dans 2,5 ? Autrement dit, 2,5 = ?/1000",
                    "tolerance": 0,
                    "correct_answer": 2500,
                    "explanation": "2,5 = 2,500 = 2500/1000. Il y a 2 500 milliemes dans 2,5.",
                    "hint": "Ecris 2,5 avec 3 chiffres apres la virgule : 2,500.",
                    "points": 3,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "milliemes", "conversion"],
                    "common_mistake_targeted": "Repondre 25 au lieu de 2500 (confondre dixiemes et milliemes)"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS02",
            "exercises": [
                {
                    "exercise_id": "EX061",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Dans le nombre 14,375, quel est le chiffre des centiemes ?",
                    "choices": ["3", "7", "5", "4"],
                    "correct_answer": "7",
                    "explanation": "14,375 : apres la virgule, 3 est aux dixiemes, 7 est aux centiemes, 5 est aux milliemes.",
                    "hint": "Apres la virgule : 1er chiffre = dixiemes, 2e chiffre = centiemes, 3e chiffre = milliemes.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "valeur de position", "centiemes"],
                    "common_mistake_targeted": "Confondre dixiemes et centiemes"
                },
                {
                    "exercise_id": "EX062",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Dans le nombre 206,049 :\n- Le chiffre des dixiemes est : ___\n- Le chiffre des milliemes est : ___\n- Le chiffre des dizaines est : ___",
                    "blanks": ["0", "9", "0"],
                    "correct_answer": ["0", "9", "0"],
                    "explanation": "206,049 : dizaines = 0 (dans 206), dixiemes = 0 (apres la virgule), centiemes = 4, milliemes = 9.",
                    "hint": "Separe la partie entiere (206) de la partie decimale (049).",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "valeur de position", "zeros"],
                    "common_mistake_targeted": "Confondre les rangs de la partie entiere et de la partie decimale"
                },
                {
                    "exercise_id": "EX063",
                    "type": "true_false",
                    "difficulty": "hard",
                    "text": "Dans le nombre 5,806, le chiffre 0 represente 0 centieme.",
                    "correct_answer": True,
                    "explanation": "5,806 : 8 dixiemes, 0 centieme, 6 milliemes. Le 0 est bien a la position des centiemes et represente 0 centieme.",
                    "hint": "Identifie la position du 0 apres la virgule : 1er, 2e ou 3e chiffre ?",
                    "points": 3,
                    "time_limit_seconds": 45,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "valeur de position", "zero intercalaire"],
                    "common_mistake_targeted": "Penser que le zero n'a pas de position"
                },
                {
                    "exercise_id": "EX064",
                    "type": "contextual_problem",
                    "difficulty": "medium",
                    "text": "La taille de Yemi est 1,45 m. Celle d'Adjoa est 1,54 m.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Quel est le chiffre des dixiemes dans la taille de Yemi ?",
                            "correct_answer": "4"
                        },
                        {
                            "id": "b",
                            "text": "Quel est le chiffre des centiemes dans la taille d'Adjoa ?",
                            "correct_answer": "4"
                        },
                        {
                            "id": "c",
                            "text": "Les deux chiffres '4' ont-ils la meme valeur ? Explique.",
                            "correct_answer": "Non. Chez Yemi, le 4 vaut 4 dixiemes (0,4 m). Chez Adjoa, le 4 vaut 4 centiemes (0,04 m)."
                        }
                    ],
                    "correct_answer": {"a": "4", "b": "4", "c": "Non, valeurs differentes"},
                    "explanation": "Dans 1,45 : le 4 est aux dixiemes (= 0,4). Dans 1,54 : le 4 est aux centiemes (= 0,04). Meme chiffre, positions differentes, valeurs differentes.",
                    "hint": "Le meme chiffre peut avoir des valeurs differentes selon sa position.",
                    "points": 2,
                    "time_limit_seconds": 120,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "valeur de position", "probleme", "Benin"],
                    "common_mistake_targeted": "Croire que le meme chiffre a toujours la meme valeur"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS03",
            "exercises": [
                {
                    "exercise_id": "EX065",
                    "type": "tracing",
                    "difficulty": "easy",
                    "text": "Place le nombre 0,5 sur la droite numerique graduee de 0 a 1.",
                    "number_line": {
                        "min": 0,
                        "max": 1,
                        "step": 0.1,
                        "unit": "",
                        "label_min": "0",
                        "label_max": "1"
                    },
                    "correct_answer": {"0.5": 0.5},
                    "explanation": "0,5 = 5 dixiemes, donc il se place exactement au milieu du segment [0 ; 1].",
                    "hint": "0,5 = la moitie de 1.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "droite numerique", "placement"],
                    "common_mistake_targeted": "Placer 0,5 trop pres de 0 ou de 1"
                },
                {
                    "exercise_id": "EX066",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Sur une droite graduee de 3 a 4 divisee en 10 parts egales, ou se place 3,7 ?",
                    "choices": [
                        "A la 7e graduation apres 3",
                        "A la 3e graduation apres 3",
                        "A la 7e graduation apres 0",
                        "Au milieu entre 3 et 4"
                    ],
                    "correct_answer": "A la 7e graduation apres 3",
                    "explanation": "La droite va de 3 a 4 avec 10 parts egales (pas de 0,1). 3,7 = 3 + 0,7, donc 7 graduations apres 3.",
                    "hint": "Chaque graduation vaut 0,1. Combien de fois 0,1 dans 0,7 ?",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "droite numerique", "reperage"],
                    "common_mistake_targeted": "Compter depuis 0 au lieu de depuis 3"
                },
                {
                    "exercise_id": "EX067",
                    "type": "tracing",
                    "difficulty": "hard",
                    "text": "Place les nombres 1,25 et 1,75 sur la droite numerique graduee de 1 a 2.",
                    "number_line": {
                        "min": 1,
                        "max": 2,
                        "step": 0.1,
                        "unit": "",
                        "label_min": "1",
                        "label_max": "2"
                    },
                    "correct_answer": {"1.25": 0.25, "1.75": 0.75},
                    "explanation": "1,25 est au 1er quart entre 1 et 2 (entre la 2e et 3e graduation). 1,75 est aux 3/4 (entre la 7e et 8e graduation).",
                    "hint": "1,25 est entre 1,2 et 1,3. 1,75 est entre 1,7 et 1,8.",
                    "points": 3,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "droite numerique", "precision"],
                    "common_mistake_targeted": "Placer 1,25 a la graduation 1,2 ou 1,3 au lieu d'entre les deux"
                },
                {
                    "exercise_id": "EX068",
                    "type": "numeric_input",
                    "difficulty": "medium",
                    "text": "Sur une droite graduee de 0 a 1 divisee en 100 parts egales, a quelle graduation se trouve 0,43 ?",
                    "tolerance": 0,
                    "correct_answer": 43,
                    "explanation": "Chaque graduation vaut 0,01 (1 centieme). 0,43 = 43 centiemes = 43e graduation.",
                    "hint": "0,43 = 43/100, donc c'est la graduation numero...",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "droite numerique", "centiemes"],
                    "common_mistake_targeted": "Confondre avec la 4e graduation (ne voir que le dixieme)"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS04",
            "exercises": [
                {
                    "exercise_id": "EX069",
                    "type": "fill_blank",
                    "difficulty": "easy",
                    "text": "Decompose 3,45 :\nPartie entiere : ___\nPartie decimale : ___\n3,45 = 3 + ___ dixiemes + ___ centiemes",
                    "blanks": ["3", "0,45", "4", "5"],
                    "correct_answer": ["3", "0,45", "4", "5"],
                    "explanation": "3,45 a une partie entiere de 3 et une partie decimale de 0,45. On decompose : 3 + 4 dixiemes + 5 centiemes.",
                    "hint": "La virgule separe la partie entiere de la partie decimale.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "decomposition", "partie entiere", "partie decimale"],
                    "common_mistake_targeted": "Dire que la partie decimale est 45 au lieu de 0,45"
                },
                {
                    "exercise_id": "EX070",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quelle est la decomposition correcte de 12,608 ?",
                    "choices": [
                        "12 + 6/10 + 0/100 + 8/1000",
                        "12 + 6/10 + 8/100",
                        "1 + 2 + 6/10 + 0/100 + 8/1000",
                        "12 + 60/100 + 8/100"
                    ],
                    "correct_answer": "12 + 6/10 + 0/100 + 8/1000",
                    "explanation": "12,608 = 12 (partie entiere) + 6 dixiemes + 0 centieme + 8 milliemes = 12 + 6/10 + 0/100 + 8/1000.",
                    "hint": "Apres la virgule : 6 (dixiemes), 0 (centiemes), 8 (milliemes).",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "decomposition", "rangs"],
                    "common_mistake_targeted": "Oublier le rang des centiemes quand il vaut 0"
                },
                {
                    "exercise_id": "EX071",
                    "type": "guided_steps",
                    "difficulty": "hard",
                    "text": "Decompose le nombre 405,203 selon les rangs decimaux.",
                    "steps": [
                        {
                            "instruction": "Quelle est la partie entiere ?",
                            "expected_answer": "405",
                            "hint": "C'est ce qui est avant la virgule."
                        },
                        {
                            "instruction": "Quelle est la partie decimale ?",
                            "expected_answer": "0,203",
                            "hint": "C'est ce qui est apres la virgule."
                        },
                        {
                            "instruction": "Decompose : 405,203 = 400 + ___ + ___ + 2/10 + 0/100 + 3/1000",
                            "expected_answer": "5 et 0 (ou 400 + 5 + 0)",
                            "hint": "400 + 5 + 0 pour la partie entiere."
                        },
                        {
                            "instruction": "Ecris la decomposition complete.",
                            "expected_answer": "4 x 100 + 5 x 1 + 2 x 0,1 + 3 x 0,001",
                            "hint": "Chaque chiffre non nul multiplie par sa valeur de position."
                        }
                    ],
                    "correct_answer": "4 x 100 + 5 x 1 + 2 x 0,1 + 3 x 0,001",
                    "explanation": "405,203 = 400 + 5 + 0,2 + 0,003 = 4 x 100 + 5 x 1 + 2 x 0,1 + 3 x 0,001.",
                    "hint": "N'oublie pas les zeros intercalaires (0 dizaines, 0 centiemes).",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "decomposition", "etapes guidees"],
                    "common_mistake_targeted": "Inclure les rangs nuls dans la decomposition multiplicative"
                },
                {
                    "exercise_id": "EX072",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Le nombre 7,50 a la meme valeur que 7,5.",
                    "correct_answer": True,
                    "explanation": "7,50 = 7 + 5 dixiemes + 0 centieme = 7,5. Ajouter un zero a droite de la partie decimale ne change pas la valeur.",
                    "hint": "Que vaut le 0 des centiemes ?",
                    "points": 2,
                    "time_limit_seconds": 30,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "egalite", "zeros inutiles"],
                    "common_mistake_targeted": "Croire que 7,50 est different de 7,5"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS05",
            "exercises": [
                {
                    "exercise_id": "EX073",
                    "type": "fill_blank",
                    "difficulty": "easy",
                    "text": "Encadre 3,7 entre deux entiers consecutifs : ___ < 3,7 < ___",
                    "blanks": ["3", "4"],
                    "correct_answer": ["3", "4"],
                    "explanation": "3,7 est entre 3 et 4 car 3 < 3,7 < 4.",
                    "hint": "Quelle est la partie entiere de 3,7 ?",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "encadrement", "entiers"],
                    "common_mistake_targeted": "Ecrire 3 < 3,7 < 5 au lieu de 3 < 3,7 < 4"
                },
                {
                    "exercise_id": "EX074",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quel est l'encadrement de 8,64 au dixieme pres ?",
                    "choices": [
                        "8,6 < 8,64 < 8,7",
                        "8 < 8,64 < 9",
                        "8,64 < 8,64 < 8,65",
                        "8,60 < 8,64 < 8,70"
                    ],
                    "correct_answer": "8,6 < 8,64 < 8,7",
                    "explanation": "Au dixieme pres, on encadre par des nombres avec 1 chiffre apres la virgule : 8,6 et 8,7.",
                    "hint": "Au dixieme pres = entre deux nombres consecutifs ayant 1 chiffre apres la virgule.",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "encadrement", "dixiemes"],
                    "common_mistake_targeted": "Confondre encadrement au dixieme et au centieme"
                },
                {
                    "exercise_id": "EX075",
                    "type": "fill_blank",
                    "difficulty": "hard",
                    "text": "Encadre 5,999 au centieme pres : ___ < 5,999 < ___",
                    "blanks": ["5,99", "6,00"],
                    "correct_answer": ["5,99", "6,00"],
                    "explanation": "5,999 est entre 5,99 et 6,00 au centieme pres. On passe a l'entier suivant.",
                    "hint": "Quel est le centieme juste au-dessus de 5,99 ?",
                    "points": 3,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "encadrement", "centiemes", "passage entier"],
                    "common_mistake_targeted": "Ecrire 5,100 au lieu de 6,00 comme borne superieure"
                },
                {
                    "exercise_id": "EX076",
                    "type": "justification",
                    "difficulty": "medium",
                    "text": "Aissatou dit que 4,35 est plus proche de 4 que de 5. A-t-elle raison ? Justifie.",
                    "scoring_rubric": "1 pt : reponse correcte (oui). 1 pt : calcul des distances (0,35 et 0,65). 1 pt : conclusion argumentee.",
                    "correct_answer": "Oui. La distance de 4,35 a 4 est 0,35, et la distance de 4,35 a 5 est 0,65. Comme 0,35 < 0,65, 4,35 est plus proche de 4.",
                    "explanation": "4,35 - 4 = 0,35. 5 - 4,35 = 0,65. 0,35 < 0,65, donc 4,35 est plus proche de 4.",
                    "hint": "Calcule la distance entre 4,35 et chacun des deux entiers.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Evaluer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "encadrement", "justification", "distance"],
                    "common_mistake_targeted": "Conclure sans calculer les deux distances"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS06",
            "exercises": [
                {
                    "exercise_id": "EX077",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Quel est l'arrondi de 3,7 a l'unite ?",
                    "choices": ["3", "4", "3,5", "3,70"],
                    "correct_answer": "4",
                    "explanation": "3,7 : le chiffre des dixiemes est 7 (>= 5), donc on arrondit a l'unite superieure : 4.",
                    "hint": "Si le chiffre apres la virgule est 5 ou plus, on arrondit vers le haut.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "arrondi", "unite"],
                    "common_mistake_targeted": "Arrondir vers le bas quand le chiffre est >= 5"
                },
                {
                    "exercise_id": "EX078",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Arrondis les nombres suivants au dixieme :\na) 6,47 ≈ ___\nb) 12,851 ≈ ___\nc) 0,349 ≈ ___",
                    "blanks": ["6,5", "12,9", "0,3"],
                    "correct_answer": ["6,5", "12,9", "0,3"],
                    "explanation": "a) 6,47 : centieme = 7 >= 5, donc 6,5. b) 12,851 : centieme = 5 >= 5, donc 12,9. c) 0,349 : centieme = 4 < 5, donc 0,3.",
                    "hint": "Pour arrondir au dixieme, regarde le chiffre des centiemes.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "arrondi", "dixieme"],
                    "common_mistake_targeted": "Regarder le mauvais chiffre pour decider de l'arrondi"
                },
                {
                    "exercise_id": "EX079",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Au marche de Bohicon, Maman Sika achete 3,475 kg de riz. La balance n'affiche que 2 chiffres apres la virgule.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Quel poids la balance affiche-t-elle (arrondi au centieme) ?",
                            "correct_answer": "3,48"
                        },
                        {
                            "id": "b",
                            "text": "Explique pourquoi la balance arrondit a 3,48 et non a 3,47.",
                            "correct_answer": "Le chiffre des milliemes est 5, donc on arrondit le centieme au superieur : 7 devient 8."
                        }
                    ],
                    "correct_answer": {"a": "3,48", "b": "Le millieme 5 >= 5, donc on arrondit au centieme superieur"},
                    "explanation": "3,475 arrondi au centieme : le chiffre des milliemes est 5 (>= 5), on arrondit 7 centiemes a 8 centiemes. Resultat : 3,48 kg.",
                    "hint": "Pour arrondir au centieme, regarde le chiffre des milliemes.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "arrondi", "centieme", "probleme", "Benin", "Bohicon"],
                    "common_mistake_targeted": "Arrondir au dixieme au lieu du centieme"
                },
                {
                    "exercise_id": "EX080",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "L'arrondi de 9,95 a l'unite est 10.",
                    "correct_answer": True,
                    "explanation": "9,95 : le chiffre des dixiemes est 9 (>= 5), donc on arrondit a 10. On passe bien a la dizaine suivante.",
                    "hint": "9 arrondi au-dessus donne 10.",
                    "points": 2,
                    "time_limit_seconds": 30,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "arrondi", "unite", "passage dizaine"],
                    "common_mistake_targeted": "Penser que l'arrondi de 9,95 est 9 ou rester bloque sur 9"
                }
            ]
        }
    ]

if __name__ == "__main__":
    data = get_skill4_exercises()
    with open("/tmp/part4.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Part 4: {len(data)} micro-skills, {sum(len(ms['exercises']) for ms in data)} exercises")
