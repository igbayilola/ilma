#!/usr/bin/env python3
"""Generate exercises for NUM-ENTIERS-0-1B (MS01-MS06) — exercises EX001-EX024."""
import json

def get_skill1_exercises():
    """NUM-ENTIERS-0-1B: Lire, ecrire, decomposer les entiers 0-1 milliard"""
    return [
        {
            "micro_skill_external_id": "NUM-ENTIERS-0-1B::MS01",
            "exercises": [
                {
                    "exercise_id": "EX001",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Dans le nombre 45 678 321, quel est le chiffre des dizaines de mille ?",
                    "choices": ["4", "5", "7", "6"],
                    "correct_answer": "7",
                    "explanation": "Dans 45 678 321, en partant de la droite : 1 (unites), 2 (dizaines), 3 (centaines), 8 (unites de mille), 7 (dizaines de mille). Le chiffre des dizaines de mille est donc 7.",
                    "hint": "Compte les positions en partant de la droite : unites, dizaines, centaines, unites de mille, dizaines de mille.",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "classes", "rangs", "dizaines de mille"],
                    "common_mistake_targeted": "Confondre le rang des dizaines de mille avec celui des centaines de mille"
                },
                {
                    "exercise_id": "EX002",
                    "type": "matching",
                    "difficulty": "medium",
                    "text": "Associe chaque chiffre souligné du nombre 836 472 159 à son rang :",
                    "left_items": ["8", "4", "1"],
                    "right_items": ["Centaines de millions", "Centaines de mille", "Centaines"],
                    "correct_answer": {
                        "8": "Centaines de millions",
                        "4": "Centaines de mille",
                        "1": "Centaines"
                    },
                    "explanation": "836 472 159 : le 8 est aux centaines de millions, le 4 est aux centaines de mille (472), le 1 est aux centaines (159).",
                    "hint": "Separe le nombre en classes de 3 chiffres depuis la droite : 836 | 472 | 159.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "classes", "rangs", "association"],
                    "common_mistake_targeted": "Confondre les rangs entre classes differentes"
                },
                {
                    "exercise_id": "EX003",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Complete le tableau de numeration pour le nombre 507 030 200 :\nClasse des millions : ___ centaines, ___ dizaines, ___ unites\nClasse des mille : ___ centaines, ___ dizaines, ___ unites\nClasse des unites : ___ centaines, ___ dizaines, ___ unites",
                    "blanks": ["5", "0", "7", "0", "3", "0", "2", "0", "0"],
                    "correct_answer": ["5", "0", "7", "0", "3", "0", "2", "0", "0"],
                    "explanation": "507 030 200 se decompose : millions (5, 0, 7), milliers (0, 3, 0), unites (2, 0, 0).",
                    "hint": "Separe le nombre en groupes de 3 chiffres : 507 | 030 | 200.",
                    "points": 2,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "tableau", "classes", "rangs"],
                    "common_mistake_targeted": "Oublier les zeros intercalaires dans le tableau"
                },
                {
                    "exercise_id": "EX004",
                    "type": "numeric_input",
                    "difficulty": "hard",
                    "text": "Dans le nombre 1 000 000 000, combien y a-t-il de classes (groupes de 3 chiffres) au total ?",
                    "tolerance": 0,
                    "correct_answer": 4,
                    "explanation": "1 000 000 000 = 1 | 000 | 000 | 000. Il y a 4 classes : milliards, millions, milliers, unites.",
                    "hint": "Separe le nombre en groupes de 3 chiffres depuis la droite.",
                    "points": 3,
                    "time_limit_seconds": 60,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "classes", "milliard"],
                    "common_mistake_targeted": "Oublier que le chiffre 1 seul forme une classe (milliards)"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-ENTIERS-0-1B::MS02",
            "exercises": [
                {
                    "exercise_id": "EX005",
                    "type": "numeric_input",
                    "difficulty": "easy",
                    "text": "Ecris en chiffres le nombre : trois millions cinq cent mille.",
                    "tolerance": 0,
                    "correct_answer": 3500000,
                    "explanation": "Trois millions = 3 000 000, cinq cent mille = 500 000. Total : 3 500 000.",
                    "hint": "Ecris d'abord les millions, puis ajoute les milliers.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "ecriture en chiffres", "millions"],
                    "common_mistake_targeted": "Oublier des zeros entre les classes"
                },
                {
                    "exercise_id": "EX006",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Le nombre qui est compose de 4 centaines de millions, 2 dizaines de millions, 0 unites de millions, 8 centaines de mille et 5 unites s'ecrit : ___",
                    "blanks": ["420 800 005"],
                    "correct_answer": ["420 800 005"],
                    "explanation": "4 centaines de millions = 400 000 000, 2 dizaines de millions = 20 000 000, 8 centaines de mille = 800 000, 5 unites = 5. Total : 420 800 005.",
                    "hint": "Additionne : 400 000 000 + 20 000 000 + 800 000 + 5.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "ecriture en chiffres", "decomposition"],
                    "common_mistake_targeted": "Ne pas mettre de zero aux rangs vides"
                },
                {
                    "exercise_id": "EX007",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quel nombre correspond a la decomposition : 6 x 100 000 000 + 5 x 10 000 + 3 x 100 ?",
                    "choices": ["600 050 300", "650 300", "600 500 300", "60 050 300"],
                    "correct_answer": "600 050 300",
                    "explanation": "6 x 100 000 000 = 600 000 000, 5 x 10 000 = 50 000, 3 x 100 = 300. Total : 600 050 300.",
                    "hint": "Calcule chaque terme separement puis additionne.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "decomposition", "recomposition"],
                    "common_mistake_targeted": "Oublier les zeros intercalaires entre les termes non nuls"
                },
                {
                    "exercise_id": "EX008",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Le directeur d'une banque a Cotonou annonce que les depots totaux s'elevent a : sept cent quatre-vingt-trois millions deux cent six mille cinquante francs CFA.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Ecris ce nombre en chiffres.",
                            "correct_answer": "783 206 050"
                        },
                        {
                            "id": "b",
                            "text": "Quel est le chiffre des dizaines de mille ?",
                            "correct_answer": "0"
                        }
                    ],
                    "correct_answer": {"a": "783 206 050", "b": "0"},
                    "explanation": "783 millions = 783 000 000, 206 mille = 206 000, 50 unites = 50. Total : 783 206 050. Le chiffre des dizaines de mille est 0.",
                    "hint": "Decompose l'enonce en classes : millions, milliers, unites.",
                    "points": 3,
                    "time_limit_seconds": 150,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "ecriture en chiffres", "probleme", "Benin", "FCFA"],
                    "common_mistake_targeted": "Ecrire 783 260 050 au lieu de 783 206 050 (inverser 06 en 60)"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-ENTIERS-0-1B::MS03",
            "exercises": [
                {
                    "exercise_id": "EX009",
                    "type": "mcq",
                    "difficulty": "easy",
                    "text": "Comment ecrit-on 2 450 000 en lettres ?",
                    "choices": [
                        "Deux millions quatre cent cinquante mille",
                        "Vingt-quatre millions cinquante mille",
                        "Deux millions quarante-cinq mille",
                        "Deux cent quarante-cinq mille"
                    ],
                    "correct_answer": "Deux millions quatre cent cinquante mille",
                    "explanation": "2 450 000 = 2 millions + 450 mille. En lettres : deux millions quatre cent cinquante mille.",
                    "hint": "Separe en classes : 2 (millions) et 450 (milliers).",
                    "points": 1,
                    "time_limit_seconds": 45,
                    "bloom_level": "Connaitre",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "ecriture en lettres", "millions"],
                    "common_mistake_targeted": "Confondre les classes millions et milliers"
                },
                {
                    "exercise_id": "EX010",
                    "type": "short_answer",
                    "difficulty": "medium",
                    "text": "Ecris en lettres le nombre 80 005 020.",
                    "accepted_answers": [
                        "quatre-vingts millions cinq mille vingt",
                        "quatre-vingt millions cinq mille vingt"
                    ],
                    "correct_answer": "quatre-vingts millions cinq mille vingt",
                    "explanation": "80 005 020 = 80 millions + 5 mille + 20. En lettres : quatre-vingts millions cinq mille vingt.",
                    "hint": "Attention aux zeros intercalaires : pas de centaines de mille ni de centaines.",
                    "points": 2,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "ecriture en lettres", "zeros intercalaires"],
                    "common_mistake_targeted": "Ecrire les zeros intercalaires en lettres ou oublier 'mille'"
                },
                {
                    "exercise_id": "EX011",
                    "type": "error_correction",
                    "difficulty": "medium",
                    "text": "Un eleve a ecrit : 305 070 en lettres donne 'trois cent cinq mille soixante-dix'. Corrige si necessaire.",
                    "erroneous_content": "trois cent cinq mille soixante-dix",
                    "correct_answer": "trois cent cinq mille soixante-dix",
                    "explanation": "305 070 = 305 mille + 70. L'ecriture 'trois cent cinq mille soixante-dix' est correcte. Il n'y a pas d'erreur.",
                    "hint": "Verifie chaque classe : 305 (milliers) et 070 (unites).",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "correction", "ecriture en lettres"],
                    "common_mistake_targeted": "Corriger a tort une ecriture deja correcte (piege)"
                },
                {
                    "exercise_id": "EX012",
                    "type": "short_answer",
                    "difficulty": "hard",
                    "text": "Ecris en lettres le nombre 900 000 100.",
                    "accepted_answers": [
                        "neuf cents millions cent",
                        "neuf cent millions cent"
                    ],
                    "correct_answer": "neuf cents millions cent",
                    "explanation": "900 000 100 = 900 millions + 100. En lettres : neuf cents millions cent. Attention : pas de milliers.",
                    "hint": "Il n'y a rien dans la classe des milliers (000).",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "ecriture en lettres", "zeros intercalaires"],
                    "common_mistake_targeted": "Ajouter 'mille' alors que la classe des milliers est vide"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-ENTIERS-0-1B::MS04",
            "exercises": [
                {
                    "exercise_id": "EX013",
                    "type": "fill_blank",
                    "difficulty": "easy",
                    "text": "Decompose 7 320 000 sous forme additive : 7 000 000 + ___ + ___",
                    "blanks": ["300 000", "20 000"],
                    "correct_answer": ["300 000", "20 000"],
                    "explanation": "7 320 000 = 7 000 000 + 300 000 + 20 000.",
                    "hint": "Separe chaque chiffre non nul multiplie par sa valeur de position.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "decomposition additive"],
                    "common_mistake_targeted": "Confondre decomposition additive et multiplicative"
                },
                {
                    "exercise_id": "EX014",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quelle est la decomposition correcte de 405 060 000 ?",
                    "choices": [
                        "400 000 000 + 5 000 000 + 60 000",
                        "400 000 000 + 50 000 000 + 6 000",
                        "4 000 000 + 50 000 + 60 000",
                        "400 000 000 + 5 000 000 + 600 000"
                    ],
                    "correct_answer": "400 000 000 + 5 000 000 + 60 000",
                    "explanation": "405 060 000 : le 4 vaut 400 000 000 (centaines de millions), le 5 vaut 5 000 000 (unites de millions), le 6 vaut 60 000 (dizaines de mille).",
                    "hint": "Identifie la valeur de chaque chiffre non nul.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Comprendre",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "decomposition additive", "zeros intercalaires"],
                    "common_mistake_targeted": "Se tromper de rang a cause des zeros intercalaires"
                },
                {
                    "exercise_id": "EX015",
                    "type": "matching",
                    "difficulty": "hard",
                    "text": "Associe chaque nombre a sa decomposition multiplicative :",
                    "left_items": [
                        "53 200 000",
                        "5 320 000",
                        "532 000"
                    ],
                    "right_items": [
                        "5 x 100 000 + 3 x 10 000 + 2 x 1 000",
                        "5 x 10 000 000 + 3 x 1 000 000 + 2 x 100 000",
                        "5 x 1 000 000 + 3 x 100 000 + 2 x 10 000"
                    ],
                    "correct_answer": {
                        "53 200 000": "5 x 10 000 000 + 3 x 1 000 000 + 2 x 100 000",
                        "5 320 000": "5 x 1 000 000 + 3 x 100 000 + 2 x 10 000",
                        "532 000": "5 x 100 000 + 3 x 10 000 + 2 x 1 000"
                    },
                    "explanation": "Les chiffres 5, 3, 2 sont les memes mais leurs rangs changent selon le nombre de zeros.",
                    "hint": "Compare le nombre de chiffres de chaque nombre pour trouver les rangs.",
                    "points": 3,
                    "time_limit_seconds": 120,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "decomposition multiplicative", "association"],
                    "common_mistake_targeted": "Confondre les rangs quand les memes chiffres apparaissent"
                },
                {
                    "exercise_id": "EX016",
                    "type": "guided_steps",
                    "difficulty": "hard",
                    "text": "Decompose le nombre 802 004 070 dans un tableau de numeration.",
                    "steps": [
                        {
                            "instruction": "Combien y a-t-il de centaines de millions ?",
                            "expected_answer": "8",
                            "hint": "C'est le premier chiffre du nombre."
                        },
                        {
                            "instruction": "Combien y a-t-il d'unites de millions ?",
                            "expected_answer": "2",
                            "hint": "Regarde le 3e chiffre : 802 xxx xxx."
                        },
                        {
                            "instruction": "Combien y a-t-il d'unites de mille ?",
                            "expected_answer": "4",
                            "hint": "Classe des mille : 004, donc 4 unites de mille."
                        },
                        {
                            "instruction": "Ecris la decomposition additive complete.",
                            "expected_answer": "800 000 000 + 2 000 000 + 4 000 + 70",
                            "hint": "Additionne les valeurs de chaque chiffre non nul."
                        }
                    ],
                    "correct_answer": "800 000 000 + 2 000 000 + 4 000 + 70",
                    "explanation": "802 004 070 = 8 x 100 000 000 + 2 x 1 000 000 + 4 x 1 000 + 7 x 10 = 800 000 000 + 2 000 000 + 4 000 + 70.",
                    "hint": "Identifie chaque chiffre non nul et sa position.",
                    "points": 3,
                    "time_limit_seconds": 180,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "tableau de numeration", "decomposition", "etapes guidees"],
                    "common_mistake_targeted": "Oublier un chiffre non nul dans la decomposition"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-ENTIERS-0-1B::MS05",
            "exercises": [
                {
                    "exercise_id": "EX017",
                    "type": "numeric_input",
                    "difficulty": "easy",
                    "text": "Recompose le nombre : 3 centaines de millions + 5 dizaines de mille + 2 unites = ?",
                    "tolerance": 0,
                    "correct_answer": 300050002,
                    "explanation": "3 centaines de millions = 300 000 000, 5 dizaines de mille = 50 000, 2 unites = 2. Total : 300 050 002.",
                    "hint": "Ecris chaque valeur puis additionne.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "recomposition", "rangs"],
                    "common_mistake_targeted": "Oublier les zeros entre les classes"
                },
                {
                    "exercise_id": "EX018",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Quel nombre obtient-on en recomposant : 7 x 1 000 000 + 25 x 1 000 + 8 x 10 ?",
                    "choices": ["7 025 080", "7 250 080", "7 025 800", "70 025 080"],
                    "correct_answer": "7 025 080",
                    "explanation": "7 x 1 000 000 = 7 000 000, 25 x 1 000 = 25 000, 8 x 10 = 80. Total : 7 025 080.",
                    "hint": "Attention : 25 milliers = 25 000, pas 250 000.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "recomposition", "decomposition multiplicative"],
                    "common_mistake_targeted": "Mal placer le 25 dans la classe des mille"
                },
                {
                    "exercise_id": "EX019",
                    "type": "fill_blank",
                    "difficulty": "medium",
                    "text": "Recompose : 40 millions + 600 mille + 9 = ___",
                    "blanks": ["40 600 009"],
                    "correct_answer": ["40 600 009"],
                    "explanation": "40 000 000 + 600 000 + 9 = 40 600 009.",
                    "hint": "Ecris 40 millions, puis place les 600 mille et les 9 unites.",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "recomposition"],
                    "common_mistake_targeted": "Ecrire 40 600 900 au lieu de 40 600 009"
                },
                {
                    "exercise_id": "EX020",
                    "type": "contextual_problem",
                    "difficulty": "hard",
                    "text": "Le budget du ministere de l'Education au Benin se decompose ainsi : 2 centaines de milliards + 5 dizaines de milliards + 3 milliards + 8 centaines de millions de FCFA.",
                    "sub_questions": [
                        {
                            "id": "a",
                            "text": "Ecris ce budget en chiffres.",
                            "correct_answer": "253 800 000 000"
                        },
                        {
                            "id": "b",
                            "text": "Combien de chiffres comporte ce nombre ?",
                            "correct_answer": "12"
                        }
                    ],
                    "correct_answer": {"a": "253 800 000 000", "b": "12"},
                    "explanation": "200 000 000 000 + 50 000 000 000 + 3 000 000 000 + 800 000 000 = 253 800 000 000 (12 chiffres).",
                    "hint": "Ecris chaque terme puis additionne.",
                    "points": 3,
                    "time_limit_seconds": 180,
                    "bloom_level": "Appliquer",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "recomposition", "probleme", "Benin", "FCFA"],
                    "common_mistake_targeted": "Se tromper dans le nombre de zeros des milliards"
                }
            ]
        },
        {
            "micro_skill_external_id": "NUM-ENTIERS-0-1B::MS06",
            "exercises": [
                {
                    "exercise_id": "EX021",
                    "type": "error_correction",
                    "difficulty": "easy",
                    "text": "Un eleve a ecrit le nombre 'cinq millions trois mille' ainsi : 5 300 000. Trouve et corrige l'erreur.",
                    "erroneous_content": "5 300 000",
                    "correct_answer": "5 003 000",
                    "explanation": "Cinq millions = 5 000 000, trois mille = 3 000. Le nombre correct est 5 003 000, pas 5 300 000. L'eleve a oublie les zeros entre les millions et les milliers.",
                    "hint": "Cinq millions trois mille : il n'y a rien aux centaines de mille ni aux dizaines de mille.",
                    "points": 1,
                    "time_limit_seconds": 60,
                    "bloom_level": "Analyser",
                    "ilma_level": "Decouverte",
                    "tags": ["numeration", "correction", "zeros intercalaires"],
                    "common_mistake_targeted": "Placer les chiffres sans respecter les zeros des rangs vides"
                },
                {
                    "exercise_id": "EX022",
                    "type": "mcq",
                    "difficulty": "medium",
                    "text": "Parmi ces ecritures, laquelle contient une erreur de zeros ?",
                    "choices": [
                        "Deux millions quarante = 2 000 040",
                        "Trois millions six cents = 3 000 600",
                        "Sept millions cinq mille = 7 500 000",
                        "Neuf millions dix = 9 000 010"
                    ],
                    "correct_answer": "Sept millions cinq mille = 7 500 000",
                    "explanation": "Sept millions cinq mille = 7 005 000, pas 7 500 000. L'erreur : 500 000 represente cinq cent mille, pas cinq mille.",
                    "hint": "Verifie chaque nombre en le decomposant classe par classe.",
                    "points": 2,
                    "time_limit_seconds": 90,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "detection erreur", "zeros"],
                    "common_mistake_targeted": "Confondre cinq mille (5 000) et cinq cent mille (500 000)"
                },
                {
                    "exercise_id": "EX023",
                    "type": "true_false",
                    "difficulty": "medium",
                    "text": "Le nombre 'six cent trois millions quarante mille' s'ecrit 603 040 000.",
                    "correct_answer": True,
                    "explanation": "603 millions = 603 000 000, quarante mille = 40 000. Total : 603 040 000. C'est correct.",
                    "hint": "Decompose : 603 (millions) + 040 (milliers) + 000 (unites).",
                    "points": 2,
                    "time_limit_seconds": 60,
                    "bloom_level": "Analyser",
                    "ilma_level": "Entrainement",
                    "tags": ["numeration", "verification", "zeros"],
                    "common_mistake_targeted": "Douter d'une ecriture correcte contenant des zeros intercalaires"
                },
                {
                    "exercise_id": "EX024",
                    "type": "error_correction",
                    "difficulty": "hard",
                    "text": "Kofi a ecrit : 'Huit cent millions cinquante' = 800 000 500. Detecte et corrige l'erreur.",
                    "erroneous_content": "800 000 500",
                    "correct_answer": "800 000 050",
                    "explanation": "Huit cent millions = 800 000 000, cinquante = 50. Le nombre correct est 800 000 050. Kofi a ecrit 500 (cinq cents) au lieu de 50 (cinquante).",
                    "hint": "Cinquante = 50, pas 500. Verifie la classe des unites.",
                    "points": 3,
                    "time_limit_seconds": 90,
                    "bloom_level": "Analyser",
                    "ilma_level": "Approfondissement",
                    "tags": ["numeration", "correction", "zeros", "confusion"],
                    "common_mistake_targeted": "Confondre cinquante (50) et cinq cents (500)"
                }
            ]
        }
    ]

if __name__ == "__main__":
    data = get_skill1_exercises()
    with open("/tmp/part1.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Part 1: {len(data)} micro-skills, {sum(len(ms['exercises']) for ms in data)} exercises")
