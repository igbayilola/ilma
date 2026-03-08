#!/usr/bin/env python3
"""Generate exercises for NUM-FRAC-REP (MS01-MS06) — exercises EX097-EX120."""
import json

def get_skill6_exercises():
    """NUM-FRAC-REP: Representer et interpreter des fractions"""
    return [
        {
            "micro_skill_external_id": "NUM-FRAC-REP::MS01",
            "exercises": [
                {
                    "exercise_id": "EX097",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Une galette est partagee en 8 parts egales. Kodjo en mange 3. Quelle fraction de la galette a-t-il mangee ?",
                    "choices": ["3/8", "8/3", "3/5", "5/8"],
                    "correct_answer": "3/8",
                    "explanation": "La galette est divisee en 8 parts egales. Kodjo en mange 3. Il a mange 3 parts sur 8, soit 3/8.",
                    "hint": "Le denominateur est le nombre total de parts, le numerateur est le nombre de parts prises.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["fractions", "partage", "comprehension"],
                    "common_mistake_targeted": "Inverser numerateur et denominateur"
                },
                {
                    "exercise_id": "EX098",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Si on coupe un gateau en 6 parts egales et qu'on en prend 6, on a pris la totalite du gateau, soit 6/6 = 1.",
                    "correct_answer": True,
                    "explanation": "6 parts sur 6 = 6/6 = 1 gateau entier. Quand le numerateur egale le denominateur, la fraction vaut 1.",
                    "hint": "Que se passe-t-il quand on prend toutes les parts ?",
                    "points": 2,
                    "time_limit_seconds": 30,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "partage", "unite"],
                    "common_mistake_targeted": "Ne pas reconnaitre que n/n = 1"
                },
                {
                    "exercise_id": "EX099",
                    "type": "contextual_problem",
                    "difficulty": "medium",
                    "text": "Au marche de Ganhi a Cotonou, une marchande coupe un ananas en 5 parts egales. Elle en vend 2 parts le matin et 1 part l'apres-midi.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Quelle fraction de l'ananas a-t-elle vendue au total ?",
                            "correct_answer": "3/5"
                        },
                        {
                            "id": "b",
                            "text": "Quelle fraction de l'ananas lui reste-t-il ?",
                            "correct_answer": "2/5"
                        }
                    ],
                    "correct_answer": {"a": "3/5", "b": "2/5"},
                    "explanation": "Elle a vendu 2 + 1 = 3 parts sur 5, soit 3/5. Il reste 5 - 3 = 2 parts, soit 2/5.",
                    "hint": "Additionne les parts vendues, puis soustrait du total.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "partage", "probleme", "Benin", "Cotonou"],
                    "common_mistake_targeted": "Oublier d'additionner les parts vendues"
                },
                {
                    "exercise_id": "EX100",
                    "type": "error_correction",
                    "difficulty": "hard",
                    "text": "Un eleve ecrit : 'J'ai partage un terrain en 3 morceaux. Le premier fait 1/3, le deuxieme 1/3, le troisieme 1/4. Tout est distribue.' Corrige l'erreur.",
                    "erroneous_content": "1/3 + 1/3 + 1/4 = 1 (tout le terrain)",
                    "correct_answer": "1/3 + 1/3 + 1/4 = 4/12 + 4/12 + 3/12 = 11/12, ce qui n'est pas egal a 1. Les parts ne sont pas egales et le total ne fait pas le terrain entier.",
                    "explanation": "Pour que le partage soit complet : 1/3 + 1/3 + 1/4 = 4/12 + 4/12 + 3/12 = 11/12 ≠ 1. Il manque 1/12 du terrain. De plus, les parts ne sont pas egales.",
                    "hint": "Mets les fractions au meme denominateur et verifie si la somme fait 1.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["fractions", "partage", "correction", "somme"],
                    "common_mistake_targeted": "Croire que toute repartition en fractions donne forcement 1"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-FRAC-REP::MS02",
            "exercises": [
                {
                    "exercise_id": "EX101",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Que signifie la fraction 15/3 ?",
                    "choices": [
                        "15 divise par 3",
                        "3 divise par 15",
                        "15 multiplie par 3",
                        "15 moins 3"
                    ],
                    "correct_answer": "15 divise par 3",
                    "explanation": "La fraction a/b signifie a divise par b. Donc 15/3 = 15 divise par 3 = 5.",
                    "hint": "La barre de fraction signifie 'divise par'.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["fractions", "quotient", "division"],
                    "common_mistake_targeted": "Confondre le sens du numerateur et du denominateur dans une division"
                },
                {
                    "exercise_id": "EX102",
                    "type": "numeric_input",
                    "difficulty": "medium",
                    "text": "Calcule la valeur de la fraction 20/4.",
                    "tolerance": 0,
                    "correct_answer": 5,
                    "explanation": "20/4 = 20 ÷ 4 = 5. La fraction est un quotient exact.",
                    "hint": "Divise 20 par 4.",
                    "points": 2,
                    "time_limit_seconds": 30,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "quotient", "calcul"],
                    "common_mistake_targeted": "Repondre 80 (multiplication au lieu de division)"
                },
                {
                    "exercise_id": "EX103",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "On partage equitablement 7 mangues entre 4 enfants. Chaque enfant recoit ___ mangues, soit la fraction ___.",
                    "blanks": ["1,75", "7/4"],
                    "correct_answer": ["1,75", "7/4"],
                    "explanation": "7 ÷ 4 = 1,75. Chaque enfant recoit 7/4 de mangue = 1 mangue entiere et 3/4 de mangue.",
                    "hint": "Divise 7 par 4. Le quotient peut etre un nombre decimal.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "quotient", "partage equitable"],
                    "common_mistake_targeted": "Repondre 1 reste 3 sans exprimer en fraction"
                },
                {
                    "exercise_id": "EX104",
                    "type": "justification",
                    "difficulty": "hard",
                    "text": "Akpene dit que 3/7 et 6/14 representent le meme partage. A-t-elle raison ? Justifie en utilisant le sens de quotient.",
                    "scoring_rubric": "1 pt : reponse correcte (oui). 1 pt : 3 ÷ 7 = 6 ÷ 14. 1 pt : explication (fraction equivalente par multiplication par 2).",
                    "correct_answer": "Oui. 3/7 = 3 ÷ 7 et 6/14 = 6 ÷ 14. Or 6 = 3 x 2 et 14 = 7 x 2, donc 6/14 = (3 x 2)/(7 x 2) = 3/7. Les deux quotients sont egaux.",
                    "explanation": "3/7 et 6/14 sont des fractions equivalentes : on a multiplie numerateur et denominateur par 2. Le quotient est le meme : environ 0,4286.",
                    "hint": "Simplifie 6/14 en divisant le numerateur et le denominateur par 2.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Evaluer",
                    "ilma_level": "Approfondissement",
                    "tags": ["fractions", "quotient", "equivalence", "justification"],
                    "common_mistake_targeted": "Ne pas reconnaitre les fractions equivalentes"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-FRAC-REP::MS03",
            "exercises": [
                {
                    "exercise_id": "EX105",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Dans une classe de CM2, il y a 15 filles et 10 garcons. Quelle fraction des eleves sont des filles ?",
                    "choices": ["15/25", "10/25", "15/10", "10/15"],
                    "correct_answer": "15/25",
                    "explanation": "Total d'eleves : 15 + 10 = 25. Fraction de filles : 15/25 (15 filles sur 25 eleves).",
                    "hint": "Calcule d'abord le nombre total d'eleves.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["fractions", "rapport", "proportion"],
                    "common_mistake_targeted": "Utiliser le nombre de garcons comme denominateur (15/10)"
                },
                {
                    "exercise_id": "EX106",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Un sac contient 20 billes : 8 rouges, 5 bleues et 7 vertes. La fraction de billes bleues est : ___. Simplifie-la : ___.",
                    "blanks": ["5/20", "1/4"],
                    "correct_answer": ["5/20", "1/4"],
                    "explanation": "5 billes bleues sur 20 = 5/20. En simplifiant par 5 : 5/20 = 1/4.",
                    "hint": "Fraction = nombre de billes bleues / nombre total de billes.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "rapport", "simplification"],
                    "common_mistake_targeted": "Oublier de simplifier la fraction"
                },
                {
                    "exercise_id": "EX107",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "A l'ecole primaire de Savalou, il y a 120 eleves en CM2. 40 eleves viennent a pied, 60 en zem (moto-taxi) et 20 en voiture.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Quelle fraction des eleves vient en zem ? Simplifie.",
                            "correct_answer": "60/120 = 1/2"
                        },
                        {
                            "id": "b",
                            "text": "Quelle fraction des eleves ne vient PAS a pied ? Simplifie.",
                            "correct_answer": "80/120 = 2/3"
                        }
                    ],
                    "correct_answer": {"a": "1/2", "b": "2/3"},
                    "explanation": "a) 60/120 = 1/2 (la moitie). b) Ne viennent pas a pied : 60 + 20 = 80 eleves. 80/120 = 2/3.",
                    "hint": "Pour b), calcule d'abord combien n'arrivent pas a pied.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["fractions", "rapport", "probleme", "Benin", "Savalou", "zem"],
                    "common_mistake_targeted": "Calculer la fraction de ceux qui viennent a pied au lieu de ceux qui n'y viennent pas"
                },
                {
                    "exercise_id": "EX108",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Si 3 eleves sur 12 portent des lunettes, alors la fraction d'eleves sans lunettes est 3/12.",
                    "correct_answer": False,
                    "explanation": "3/12 est la fraction d'eleves AVEC lunettes. La fraction SANS lunettes est 12 - 3 = 9 eleves, soit 9/12 = 3/4.",
                    "hint": "Lis bien la question : on demande la fraction SANS lunettes.",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "rapport", "complementaire", "vrai-faux"],
                    "common_mistake_targeted": "Confondre la fraction d'un groupe avec celle du groupe complementaire"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-FRAC-REP::MS04",
            "exercises": [
                {
                    "exercise_id": "EX109",
                    "type": "matching",
                    "difficulty": "easy",
                    "text": "Associe chaque fraction usuelle a sa valeur decimale :",
                    "left_items": ["1/2", "1/4", "3/4", "1/10"],
                    "right_items": ["0,5", "0,25", "0,75", "0,1"],
                    "correct_answer": {
                        "1/2": "0,5",
                        "1/4": "0,25",
                        "3/4": "0,75",
                        "1/10": "0,1"
                    },
                    "explanation": "1/2 = 0,5 (la moitie). 1/4 = 0,25 (le quart). 3/4 = 0,75 (trois quarts). 1/10 = 0,1 (un dixieme).",
                    "hint": "1/2 = 5/10 = 0,5. 1/4 = 25/100 = 0,25.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["fractions", "fractions usuelles", "conversion"],
                    "common_mistake_targeted": "Ne pas connaitre les equivalences des fractions courantes"
                },
                {
                    "exercise_id": "EX110",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Complete :\na) La moitie de 50 = 1/2 x 50 = ___\nb) Le quart de 100 = 1/4 x 100 = ___\nc) Les trois quarts de 80 = 3/4 x 80 = ___",
                    "blanks": ["25", "25", "60"],
                    "correct_answer": ["25", "25", "60"],
                    "explanation": "a) 1/2 x 50 = 50 ÷ 2 = 25. b) 1/4 x 100 = 100 ÷ 4 = 25. c) 3/4 x 80 = (80 ÷ 4) x 3 = 20 x 3 = 60.",
                    "hint": "Pour calculer a/b d'un nombre, divise par b puis multiplie par a.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "fractions usuelles", "calcul"],
                    "common_mistake_targeted": "Pour 3/4, diviser par 3 au lieu de diviser par 4 puis multiplier par 3"
                },
                {
                    "exercise_id": "EX111",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Papa Comlan a 2 000 FCFA. Il donne 1/4 a Afi et 1/2 a Brice.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Combien Afi recoit-elle ?",
                            "correct_answer": "500 FCFA"
                        },
                        {
                            "id": "b",
                            "text": "Combien Brice recoit-il ?",
                            "correct_answer": "1 000 FCFA"
                        },
                        {
                            "id": "c",
                            "text": "Quelle fraction reste a Papa Comlan ?",
                            "correct_answer": "1/4"
                        }
                    ],
                    "correct_answer": {"a": "500 FCFA", "b": "1 000 FCFA", "c": "1/4"},
                    "explanation": "Afi : 1/4 x 2 000 = 500. Brice : 1/2 x 2 000 = 1 000. Reste : 2 000 - 500 - 1 000 = 500 = 1/4 de 2 000.",
                    "hint": "Calcule chaque fraction de 2 000, puis soustrait du total.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["fractions", "fractions usuelles", "probleme", "Benin", "FCFA"],
                    "common_mistake_targeted": "Oublier de calculer le reste"
                },
                {
                    "exercise_id": "EX112",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quel est le quart de 360 ?",
                    "choices": ["90", "120", "180", "72"],
                    "correct_answer": "90",
                    "explanation": "Le quart = 1/4. 360 ÷ 4 = 90.",
                    "hint": "Le quart, c'est diviser par 4.",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "fractions usuelles", "quart"],
                    "common_mistake_targeted": "Confondre quart (÷4) et tiers (÷3)"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-FRAC-REP::MS05",
            "exercises": [
                {
                    "exercise_id": "EX113",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Un disque est partage en 4 parts egales. 3 parts sont coloriees. Quelle fraction est representee ?",
                    "choices": ["3/4", "1/4", "4/3", "3/3"],
                    "correct_answer": "3/4",
                    "explanation": "3 parts coloriees sur 4 parts egales = 3/4.",
                    "hint": "Compte les parts coloriees (numerateur) et le total de parts (denominateur).",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["fractions", "representation visuelle", "disque"],
                    "common_mistake_targeted": "Compter les parts non coloriees comme numerateur"
                },
                {
                    "exercise_id": "EX114",
                    "type": "tracing",
                    "difficulty": "medium",
                    "text": "Place la fraction 3/5 sur la droite numerique graduee de 0 a 1.",
                    "number_line": {
                        "min": 0,
                        "max": 1,
                        "step": 0.2,
                        "unit": "",
                        "label_min": "0",
                        "label_max": "1"
                    },
                    "correct_answer": {"0.6": 0.6},
                    "explanation": "3/5 = 0,6. Sur une droite de 0 a 1 divisee en 5 parts egales, 3/5 se place a la 3e graduation (chaque pas = 1/5 = 0,2).",
                    "hint": "La droite est divisee en 5 parts. 3/5 = 3e part.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "droite numerique", "representation"],
                    "common_mistake_targeted": "Placer 3/5 a la 3e graduation sur une droite en 10 parts"
                },
                {
                    "exercise_id": "EX115",
                    "type": "matching",
                    "difficulty": "hard",
                    "text": "Associe chaque fraction a la description de sa representation sur une barre :",
                    "left_items": ["2/6", "4/6", "5/6"],
                    "right_items": [
                        "Un tiers de la barre coloriee",
                        "Deux tiers de la barre coloriee",
                        "Presque toute la barre coloriee"
                    ],
                    "correct_answer": {
                        "2/6": "Un tiers de la barre coloriee",
                        "4/6": "Deux tiers de la barre coloriee",
                        "5/6": "Presque toute la barre coloriee"
                    },
                    "explanation": "2/6 = 1/3 (un tiers). 4/6 = 2/3 (deux tiers). 5/6 est tres proche de 1 (presque toute la barre).",
                    "hint": "Simplifie 2/6 et 4/6 pour reconnaitre des fractions connues.",
                    "points": 3,
                    "time_limit_seconds": 90,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["fractions", "representation visuelle", "barre", "simplification"],
                    "common_mistake_targeted": "Ne pas simplifier pour reconnaitre la fraction"
                },
                {
                    "exercise_id": "EX116",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Sur une droite graduee de 0 a 2, la fraction 1/2 se place a la graduation 1.",
                    "correct_answer": False,
                    "explanation": "1/2 = 0,5. Sur une droite de 0 a 2, la graduation 1 correspond a la moitie du segment, mais 1/2 vaut 0,5, pas 1. 1/2 se place entre 0 et 1.",
                    "hint": "1/2 = 0,5. Ou se trouve 0,5 sur une droite de 0 a 2 ?",
                    "points": 2,
                    "time_limit_seconds": 45,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "droite numerique", "vrai-faux", "piege"],
                    "common_mistake_targeted": "Confondre la moitie du segment avec la valeur 1/2"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-FRAC-REP::MS06",
            "exercises": [
                {
                    "exercise_id": "EX117",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "La fraction 5/3 est :",
                    "choices": [
                        "Superieure a 1",
                        "Egale a 1",
                        "Inferieure a 1",
                        "On ne peut pas savoir"
                    ],
                    "correct_answer": "Superieure a 1",
                    "explanation": "5/3 : le numerateur (5) est plus grand que le denominateur (3). Donc 5/3 > 1. En effet, 5/3 = 1 + 2/3.",
                    "hint": "Compare le numerateur et le denominateur. Si numerateur > denominateur, la fraction est > 1.",
                    "points": 1,
                    "time_limit_seconds": 30,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["fractions", "fraction superieure a 1", "comparaison"],
                    "common_mistake_targeted": "Penser que toutes les fractions sont inferieures a 1"
                },
                {
                    "exercise_id": "EX118",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Transforme 7/4 en nombre mixte : ___ entier(s) et ___/4",
                    "blanks": ["1", "3"],
                    "correct_answer": ["1", "3"],
                    "explanation": "7 ÷ 4 = 1 reste 3. Donc 7/4 = 1 entier et 3/4. On ecrit aussi 1 3/4.",
                    "hint": "Divise 7 par 4. Le quotient est la partie entiere, le reste donne la fraction.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "nombre mixte", "conversion"],
                    "common_mistake_targeted": "Confondre quotient et reste dans la division"
                },
                {
                    "exercise_id": "EX119",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Pour la fete de Tabaski, Maman Adjara prepare 11/4 de kilogramme de viande.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Convertis 11/4 en nombre mixte.",
                            "correct_answer": "2 entiers et 3/4"
                        },
                        {
                            "id": "b",
                            "text": "Convertis 11/4 en nombre decimal.",
                            "correct_answer": "2,75"
                        },
                        {
                            "id": "c",
                            "text": "A-t-elle plus ou moins de 3 kg de viande ?",
                            "correct_answer": "Moins, car 2,75 < 3"
                        }
                    ],
                    "correct_answer": {"a": "2 3/4", "b": "2,75", "c": "Moins de 3 kg"},
                    "explanation": "11 ÷ 4 = 2 reste 3. Donc 11/4 = 2 3/4 = 2,75 kg. C'est moins de 3 kg.",
                    "hint": "Divise 11 par 4 pour trouver le quotient et le reste.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["fractions", "nombre mixte", "decimal", "probleme", "Benin", "Tabaski"],
                    "common_mistake_targeted": "Se tromper dans la conversion fraction -> decimal"
                },
                {
                    "exercise_id": "EX120",
                    "type": "guided_steps",
                    "difficulty": "medium",
                    "text": "Transforme la fraction 13/5 en nombre mixte puis en decimal.",
                    "steps": [
                        {
                            "instruction": "Effectue la division euclidienne : 13 ÷ 5 = ? reste ?",
                            "expected_answer": "13 ÷ 5 = 2 reste 3",
                            "hint": "5 x 2 = 10, et 13 - 10 = 3."
                        },
                        {
                            "instruction": "Ecris le nombre mixte correspondant.",
                            "expected_answer": "2 3/5",
                            "hint": "Quotient = partie entiere, reste = numerateur."
                        },
                        {
                            "instruction": "Convertis 3/5 en decimal.",
                            "expected_answer": "0,6",
                            "hint": "3/5 = 6/10 = 0,6."
                        },
                        {
                            "instruction": "Ecris 13/5 sous forme decimale.",
                            "expected_answer": "2,6",
                            "hint": "Partie entiere + partie decimale = 2 + 0,6."
                        }
                    ],
                    "correct_answer": "2,6",
                    "explanation": "13 ÷ 5 = 2 reste 3. Nombre mixte : 2 3/5. En decimal : 3/5 = 0,6, donc 13/5 = 2,6.",
                    "hint": "Divise d'abord, puis convertis le reste en fraction decimale.",
                    "points": 2,
                    "time_limit_seconds": 150,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["fractions", "nombre mixte", "decimal", "etapes guidees"],
                    "common_mistake_targeted": "Ne pas savoir convertir le reste en decimal"
                }
            ]
        }
    ]

if __name__ == "__main__":
    data = get_skill6_exercises()
    with open("/tmp/part6.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Part 6: {len(data)} micro-skills, {sum(len(ms['exercises']) for ms in data)} exercises")
