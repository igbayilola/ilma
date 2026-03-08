#!/usr/bin/env python3
"""Generate exercises for NUM-DEC-COMP-ORD (MS01-MS04) — exercises EX081-EX096."""
import json

def get_skill5_exercises():
    """NUM-DEC-COMP-ORD: Comparer et ordonner les decimaux"""
    return [
        {
            "micro_skill_external_id": "NUM-DEC-COMP-ORD::MS01",
            "exercises": [
                {
                    "exercise_id": "EX081",
                    "type": "short_answer",
                    "difficulty": "easy",
                    "text": "Compare avec <, > ou = : 0,6 ___ 0,8",
                    "accepted_answers": ["<"],
                    "correct_answer": "<",
                    "explanation": "0,6 = 6 dixiemes et 0,8 = 8 dixiemes. Comme 6 < 8, on a 0,6 < 0,8.",
                    "hint": "Compare les chiffres des dixiemes.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "comparaison", "dixiemes"],
                    "common_mistake_targeted": "Inverser le sens du signe < et >"
                },
                {
                    "exercise_id": "EX082",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Compare avec <, > ou = :\na) 3,45 ___ 3,54\nb) 12,80 ___ 12,8\nc) 0,099 ___ 0,1",
                    "blanks": ["<", "=", "<"],
                    "correct_answer": ["<", "=", "<"],
                    "explanation": "a) 3,45 < 3,54 (dixiemes : 4 < 5). b) 12,80 = 12,8 (le zero final ne change rien). c) 0,099 < 0,1 (0,099 < 0,100).",
                    "hint": "Aligne les decimales en ajoutant des zeros si necessaire.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "comparaison", "alignement"],
                    "common_mistake_targeted": "Croire que 0,099 > 0,1 car 99 > 1"
                },
                {
                    "exercise_id": "EX083",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "2,30 > 2,3",
                    "correct_answer": False,
                    "explanation": "2,30 = 2,3 car le zero final apres la virgule ne change pas la valeur. Donc 2,30 = 2,3, pas >.",
                    "hint": "Un zero a la fin de la partie decimale ne change pas la valeur du nombre.",
                    "points": 2,
                    "time_limit_seconds": 30,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "comparaison", "egalite", "zeros inutiles"],
                    "common_mistake_targeted": "Croire que plus de chiffres = plus grand"
                },
                {
                    "exercise_id": "EX084",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Lors d'une course a l'ecole de Natitingou, les temps des 3 finalistes sont : Koffi (12,8 s), Ayaba (12,08 s), Dossou (12,80 s).",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Compare les temps de Koffi et Dossou.",
                            "correct_answer": "12,8 = 12,80 (meme temps)"
                        },
                        {
                            "id": "b",
                            "text": "Qui a le temps le plus court (le vainqueur) ?",
                            "correct_answer": "Ayaba avec 12,08 s"
                        },
                        {
                            "id": "c",
                            "text": "Justifie en alignant les decimales.",
                            "correct_answer": "12,08 < 12,80 car au rang des dixiemes, 0 < 8."
                        }
                    ],
                    "correct_answer": {"a": "12,8 = 12,80", "b": "Ayaba", "c": "12,08 < 12,80 (dixiemes : 0 < 8)"},
                    "explanation": "12,8 = 12,80 (Koffi = Dossou). 12,08 < 12,80 car 0 dixieme < 8 dixiemes. Ayaba gagne avec 12,08 s.",
                    "hint": "Ecris tous les temps avec 2 chiffres apres la virgule pour comparer.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "comparaison", "probleme", "Benin", "Natitingou"],
                    "common_mistake_targeted": "Confondre 12,08 et 12,80"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-COMP-ORD::MS02",
            "exercises": [
                {
                    "exercise_id": "EX085",
                    "type": "ordering",
                    "difficulty": "easy",
                    "text": "Range dans l'ordre croissant : 0,5 ; 0,2 ; 0,9 ; 0,1",
                    "items": ["0,5", "0,2", "0,9", "0,1"],
                    "correct_answer": ["0,1", "0,2", "0,5", "0,9"],
                    "explanation": "0,1 < 0,2 < 0,5 < 0,9. On compare les dixiemes : 1 < 2 < 5 < 9.",
                    "hint": "Tous ces nombres ont la meme partie entiere (0). Compare les dixiemes.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "ordre croissant", "dixiemes"],
                    "common_mistake_targeted": "Ranger dans l'ordre decroissant au lieu de croissant"
                },
                {
                    "exercise_id": "EX086",
                    "type": "ordering",
                    "difficulty": "medium",
                    "text": "Range dans l'ordre croissant : 4,5 ; 4,05 ; 4,50 ; 4,055",
                    "items": ["4,5", "4,05", "4,50", "4,055"],
                    "correct_answer": ["4,05", "4,055", "4,5", "4,50"],
                    "explanation": "En alignant : 4,050 < 4,055 < 4,500 = 4,500. Donc : 4,05 < 4,055 < 4,5 = 4,50.",
                    "hint": "Aligne avec 3 chiffres apres la virgule : 4,500 ; 4,050 ; 4,500 ; 4,055.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "ordre croissant", "alignement"],
                    "common_mistake_targeted": "Croire que 4,50 > 4,5 ou que 4,05 > 4,5"
                },
                {
                    "exercise_id": "EX087",
                    "type": "mcq",
                    "difficulty": "hard",
                    "text": "Quel est l'ordre croissant correct pour : 0,38 ; 0,4 ; 0,308 ; 0,039 ?",
                    "choices": [
                        "0,039 < 0,308 < 0,38 < 0,4",
                        "0,039 < 0,308 < 0,4 < 0,38",
                        "0,308 < 0,039 < 0,38 < 0,4",
                        "0,039 < 0,38 < 0,308 < 0,4"
                    ],
                    "correct_answer": "0,039 < 0,308 < 0,38 < 0,4",
                    "explanation": "En alignant : 0,039 < 0,308 < 0,380 < 0,400. Comparaison des dixiemes d'abord, puis centiemes, puis milliemes.",
                    "hint": "Ecris tous les nombres avec 3 chiffres apres la virgule.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "ordre croissant", "alignement", "milliemes"],
                    "common_mistake_targeted": "Croire que 0,38 > 0,4 car 38 > 4"
                },
                {
                    "exercise_id": "EX088",
                    "type": "contextual_problem",
                    "difficulty": "medium",
                    "text": "Au controle de maths, 4 eleves de CM2 a Ouidah ont obtenu ces notes sur 10 : Afi (7,5), Brice (7,05), Carine (7,55), Deo (7,50).",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Range les notes dans l'ordre croissant.",
                            "correct_answer": "7,05 < 7,5 = 7,50 < 7,55"
                        },
                        {
                            "id": "b",
                            "text": "Qui a la meilleure note ?",
                            "correct_answer": "Carine"
                        }
                    ],
                    "correct_answer": {"a": "7,05 < 7,5 = 7,50 < 7,55", "b": "Carine"},
                    "explanation": "7,05 < 7,50 = 7,50 < 7,55. Brice a la note la plus basse (7,05) et Carine la meilleure (7,55). Afi et Deo ont la meme note.",
                    "hint": "Ecris toutes les notes avec 2 decimales pour comparer.",
                    "points": 2,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "ordre croissant", "probleme", "Benin", "Ouidah"],
                    "common_mistake_targeted": "Ne pas voir que 7,5 = 7,50"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-COMP-ORD::MS03",
            "exercises": [
                {
                    "exercise_id": "EX089",
                    "type": "ordering",
                    "difficulty": "easy",
                    "text": "Range dans l'ordre decroissant : 5,3 ; 5,7 ; 5,1 ; 5,9",
                    "items": ["5,3", "5,7", "5,1", "5,9"],
                    "correct_answer": ["5,9", "5,7", "5,3", "5,1"],
                    "explanation": "5,9 > 5,7 > 5,3 > 5,1. Meme partie entiere (5), on compare les dixiemes.",
                    "hint": "Decroissant = du plus grand au plus petit.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "ordre decroissant"],
                    "common_mistake_targeted": "Confondre croissant et decroissant"
                },
                {
                    "exercise_id": "EX090",
                    "type": "ordering",
                    "difficulty": "medium",
                    "text": "Range dans l'ordre decroissant : 15,6 ; 15,06 ; 15,60 ; 15,006",
                    "items": ["15,6", "15,06", "15,60", "15,006"],
                    "correct_answer": ["15,6", "15,60", "15,06", "15,006"],
                    "explanation": "15,600 = 15,600 > 15,060 > 15,006. 15,6 et 15,60 sont egaux (meme position).",
                    "hint": "Aligne avec 3 decimales : 15,600 ; 15,060 ; 15,600 ; 15,006.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "ordre decroissant", "alignement"],
                    "common_mistake_targeted": "Penser que 15,006 > 15,06 car 006 a plus de chiffres"
                },
                {
                    "exercise_id": "EX091",
                    "type": "fill_blank",
                    "difficulty": "hard",
                    "text": "Range dans l'ordre decroissant et ecris le resultat :\n1,1 ; 1,01 ; 1,001 ; 1,101 ; 1,011\nReponse : ___ > ___ > ___ > ___ > ___",
                    "blanks": ["1,101", "1,1", "1,011", "1,01", "1,001"],
                    "correct_answer": ["1,101", "1,1", "1,011", "1,01", "1,001"],
                    "explanation": "En alignant : 1,101 > 1,100 > 1,011 > 1,010 > 1,001.",
                    "hint": "Ecris chaque nombre avec 3 chiffres apres la virgule.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "ordre decroissant", "precision"],
                    "common_mistake_targeted": "Se tromper entre 1,1 et 1,101 (ne pas voir que 1,100 < 1,101)"
                },
                {
                    "exercise_id": "EX092",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Dans l'ordre decroissant : 2,9 > 2,89 > 2,899.",
                    "correct_answer": True,
                    "explanation": "2,900 > 2,890 > 2,899 ? Non ! 2,899 > 2,890. L'affirmation 2,9 > 2,89 > 2,899 : 2,900 > 2,890 > 2,899. En fait 2,899 > 2,890 est vrai. Recalculons : 2,900 > 2,899 > 2,890. Donc l'ordre donne (2,9 > 2,89 > 2,899) est faux car 2,899 > 2,89.",
                    "correct_answer": False,
                    "explanation": "L'ordre correct est 2,9 > 2,899 > 2,89 car 2,900 > 2,899 > 2,890. Dans l'enonce, 2,89 est place avant 2,899, ce qui est faux.",
                    "hint": "Aligne les decimales : 2,900 ; 2,890 ; 2,899. Compare.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "ordre decroissant", "vrai-faux", "piege"],
                    "common_mistake_targeted": "Ne pas aligner les decimales avant de comparer"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-DEC-COMP-ORD::MS04",
            "exercises": [
                {
                    "exercise_id": "EX093",
                    "type": "justification",
                    "difficulty": "easy",
                    "text": "Sans calculer, explique pourquoi 3,7 > 3,2.",
                    "scoring_rubric": "1 pt : reponse correcte. 1 pt : utilisation de la valeur de position.",
                    "correct_answer": "3,7 > 3,2 car les parties entieres sont egales (3 = 3) et aux dixiemes, 7 > 2.",
                    "explanation": "Meme partie entiere (3). On compare les dixiemes : 7 > 2. Donc 3,7 > 3,2.",
                    "hint": "Compare d'abord les parties entieres, puis les dixiemes.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Evaluer",
                    "ilma_level": "Decouverte",
                    "tags": ["decimaux", "comparaison", "justification", "raisonnement"],
                    "common_mistake_targeted": "Donner la reponse sans justifier par les rangs"
                },
                {
                    "exercise_id": "EX094",
                    "type": "justification",
                    "difficulty": "medium",
                    "text": "Moussa affirme que 0,19 > 0,2. Explique son erreur et donne la comparaison correcte.",
                    "scoring_rubric": "1 pt : identifier l'erreur. 1 pt : explication par valeur de position. 1 pt : correction (0,19 < 0,2).",
                    "correct_answer": "Moussa se trompe. 0,19 = 0,19 et 0,2 = 0,20. Aux dixiemes : 1 < 2, donc 0,19 < 0,2. Son erreur : il a compare 19 et 2 comme des entiers.",
                    "explanation": "En alignant : 0,19 et 0,20. Le chiffre des dixiemes : 1 < 2. Donc 0,19 < 0,20. L'erreur est de comparer 19 et 2 comme des nombres entiers.",
                    "hint": "Ecris 0,2 sous la forme 0,20 pour comparer.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Evaluer",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "comparaison", "justification", "erreur courante"],
                    "common_mistake_targeted": "Comparer les parties decimales comme des nombres entiers"
                },
                {
                    "exercise_id": "EX095",
                    "type": "mcq",
                    "difficulty": "hard",
                    "text": "Sans calculer, quel est le plus grand nombre parmi : 5,678 ; 5,687 ; 5,768 ; 5,786 ?",
                    "choices": ["5,678", "5,687", "5,768", "5,786"],
                    "correct_answer": "5,786",
                    "explanation": "Meme partie entiere (5). Dixiemes : 6, 6, 7, 7. Parmi ceux avec 7 dixiemes : 5,768 et 5,786. Centiemes : 6 < 8. Donc 5,786 est le plus grand.",
                    "hint": "Compare d'abord les dixiemes, puis les centiemes pour les ex aequo.",
                    "points": 3,
                    "time_limit_seconds": 60,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["decimaux", "comparaison", "raisonnement positionnel"],
                    "common_mistake_targeted": "Comparer les milliemes avant les dixiemes"
                },
                {
                    "exercise_id": "EX096",
                    "type": "error_correction",
                    "difficulty": "medium",
                    "text": "Un eleve a ecrit : 4,125 > 4,15 'car 125 > 15'. Corrige son raisonnement.",
                    "erroneous_content": "4,125 > 4,15 car 125 > 15",
                    "correct_answer": "4,125 < 4,15 car en alignant les decimales : 4,125 < 4,150. Aux centiemes : 2 < 5.",
                    "explanation": "L'erreur est de comparer 125 et 15 comme des entiers. Il faut aligner : 4,125 et 4,150. Les dixiemes sont egaux (1 = 1). Les centiemes : 2 < 5. Donc 4,125 < 4,150.",
                    "hint": "Aligne les nombres : 4,125 et 4,150. Compare rang par rang.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["decimaux", "comparaison", "correction", "erreur courante"],
                    "common_mistake_targeted": "Comparer les parties decimales comme des entiers (125 vs 15)"
                }
            ]
        }
    ]

if __name__ == "__main__":
    data = get_skill5_exercises()
    with open("/tmp/part5.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Part 5: {len(data)} micro-skills, {sum(len(ms['exercises']) for ms in data)} exercises")
