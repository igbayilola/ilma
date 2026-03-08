"""Generate real exercises for Numération domain (30 micro-skills)."""
import json, random
random.seed(42)

def B(eid, typ, diff, text, **kw):
    """Build exercise dict."""
    d = {"exercise_id": eid, "type": typ, "difficulty": diff, "text": text,
         "points": {"easy":1,"medium":2,"hard":3}[diff],
         "time_limit_seconds": {"easy":45,"medium":60,"hard":90}[diff]}
    d.update(kw)
    return d

def mcq(eid, diff, text, choices, ans, expl, hint="Réfléchis bien.", **kw):
    return B(eid,"mcq",diff,text,choices=choices,correct_answer=ans,explanation=expl,hint=hint,**kw)

def tf(eid, diff, text, ans, expl, hint="Réfléchis bien."):
    return B(eid,"true_false",diff,text,correct_answer=ans,explanation=expl,hint=hint)

def fb(eid, diff, text, ans, expl, hint="Complète.", blanks=None):
    d = B(eid,"fill_blank",diff,text,correct_answer=ans,explanation=expl,hint=hint)
    if blanks: d["blanks"] = blanks
    return d

def ni(eid, diff, text, ans, expl, hint="Calcule.", tol=0):
    d = B(eid,"numeric_input",diff,text,correct_answer=ans,explanation=expl,hint=hint)
    if tol: d["tolerance"] = tol
    return d

def sa(eid, diff, text, ans, expl, hint="Écris ta réponse.", accepted=None):
    d = B(eid,"short_answer",diff,text,correct_answer=ans,explanation=expl,hint=hint)
    if accepted: d["accepted_answers"] = accepted
    return d

def order(eid, diff, text, items, ans, expl, hint="Mets dans l'ordre."):
    return B(eid,"ordering",diff,text,items=items,correct_answer=ans,explanation=expl,hint=hint)

def ec(eid, diff, text, erroneous, ans, expl, hint="Trouve l'erreur."):
    return B(eid,"error_correction",diff,text,erroneous_content=erroneous,correct_answer=ans,explanation=expl,hint=hint)

def gs(eid, diff, text, steps, ans, expl, hint="Suis les étapes."):
    return B(eid,"guided_steps",diff,text,steps=steps,correct_answer=ans,explanation=expl,hint=hint)

def jus(eid, diff, text, ans, expl, hint="Justifie.", rubric=None):
    d = B(eid,"justification",diff,text,correct_answer=ans,explanation=expl,hint=hint)
    if rubric: d["scoring_rubric"] = rubric
    return d

def tr(eid, diff, text, nl, ans, expl, hint="Observe la droite."):
    return B(eid,"tracing",diff,text,number_line=nl,correct_answer=ans,explanation=expl,hint=hint)

def match(eid, diff, text, left, right, ans, expl, hint="Associe."):
    return B(eid,"matching",diff,text,left_items=left,right_items=right,correct_answer=ans,explanation=expl,hint=hint)

blocks = []

# ═══ NUM-ENTIERS-0-1B ═══
# MS01: Identifier classes et rangs
blocks.append({"micro_skill_external_id": "NUM-ENTIERS-0-1B::MS01", "exercises": [
    mcq("EX001","easy","Dans le nombre 4 572 836, quel est le chiffre des dizaines de mille ?",
        ["7","5","4","2"],"7","Le chiffre des dizaines de mille est 7 (4 5̲7̲2 836).","Repère la position : unités, dizaines, centaines, milliers, dizaines de mille."),
    mcq("EX002","medium","Quel est le rang du chiffre 3 dans 8 305 417 ?",
        ["Centaines de mille","Dizaines de mille","Millions","Milliers"],"Centaines de mille",
        "Dans 8 305 417, le 3 occupe le rang des centaines de mille.","Décompose par classes."),
    tf("EX003","easy","Dans 12 456 789, le chiffre 4 est dans la classe des milliers.",True,
        "12 456 789 : classe des millions (12), classe des milliers (456), classe des unités (789). Le 4 est bien dans la classe des milliers."),
    fb("EX004","medium","Dans 67 890 123, le chiffre des ___ de mille est 9.","dizaines",
        "67 890 123 → 890 est la classe des milliers : 8 centaines de mille, 9 dizaines de mille, 0 milliers.","Repère la classe des milliers."),
]})

# MS02: Écrire un nombre en chiffres
blocks.append({"micro_skill_external_id": "NUM-ENTIERS-0-1B::MS02", "exercises": [
    ni("EX001","easy","Écris en chiffres : « trois millions cinq cent mille ».",3500000,
        "Trois millions = 3 000 000, cinq cent mille = 500 000, soit 3 500 000.","Commence par les millions."),
    ni("EX002","medium","Écris en chiffres : « vingt-trois millions quarante mille six cents ».",23040600,
        "23 millions = 23 000 000, 40 mille = 40 000, 600 → 23 040 600.","Attention aux zéros intercalés."),
    fb("EX003","medium","(5 × 1 000 000) + (3 × 10 000) + (7 × 100) = ___","5 030 700",
        "5 000 000 + 30 000 + 700 = 5 030 700.","Calcule chaque terme puis additionne."),
    ni("EX004","hard","Écris en chiffres : « deux milliards cent sept millions cinquante mille ».",2107050000,
        "2 milliards = 2 000 000 000, 107 millions = 107 000 000, 50 mille = 50 000 → 2 107 050 000."),
]})

# MS03: Écrire un nombre en lettres
blocks.append({"micro_skill_external_id": "NUM-ENTIERS-0-1B::MS03", "exercises": [
    sa("EX001","easy","Écris en lettres : 4 500 000.","quatre millions cinq cent mille",
        "4 500 000 = quatre millions cinq cent mille.",accepted=["quatre millions cinq cent mille","quatre millions cinq cents mille"]),
    sa("EX002","medium","Écris en lettres : 30 020 100.","trente millions vingt mille cent",
        "30 020 100 : trente millions, vingt mille, cent.",accepted=["trente millions vingt mille cent"]),
    mcq("EX003","medium","Quelle est l'écriture en lettres de 7 008 030 ?",
        ["Sept millions huit mille trente","Sept milliards huit mille trente","Sept millions huit cent trente","Sept millions huit cents trente"],
        "Sept millions huit mille trente","7 008 030 = 7 millions + 8 mille + 30."),
    fb("EX004","hard","805 600 000 s'écrit en lettres : ___.","huit cent cinq millions six cent mille",
        "805 millions = huit cent cinq millions, 600 mille = six cent mille."),
]})

# MS04: Décomposer un nombre
blocks.append({"micro_skill_external_id": "NUM-ENTIERS-0-1B::MS04", "exercises": [
    fb("EX001","easy","Décompose 34 567 : (3 × ___) + (4 × 1 000) + (5 × 100) + (6 × 10) + 7.","10 000",
        "34 567 = 3 × 10 000 + 4 × 1 000 + 5 × 100 + 6 × 10 + 7."),
    sa("EX002","medium","Donne la décomposition additive de 5 030 700.","5 000 000 + 30 000 + 700",
        "5 030 700 = 5 000 000 + 30 000 + 700.",accepted=["5 000 000 + 30 000 + 700","5000000 + 30000 + 700"]),
    mcq("EX003","medium","Quelle décomposition est correcte pour 2 405 060 ?",
        ["2×1000000 + 4×100000 + 5×1000 + 6×10","2×1000000 + 4×10000 + 5×1000 + 6×10",
         "2×1000000 + 4×100000 + 5×100 + 60","2×1000000 + 40×10000 + 5×1000 + 60"],
        "2×1000000 + 4×100000 + 5×1000 + 6×10","2 405 060 : 2M + 400k + 5k + 60."),
    ec("EX004","hard","Un élève décompose 6 080 300 ainsi : 6×100000 + 8×10000 + 3×100.",
        "6×100000 + 8×10000 + 3×100","6×1000000 + 8×10000 + 3×100",
        "L'erreur : 6 millions ≠ 6×100 000. Il faut 6×1 000 000.","Vérifie la valeur de chaque rang."),
]})

# MS05: Recomposer un nombre
blocks.append({"micro_skill_external_id": "NUM-ENTIERS-0-1B::MS05", "exercises": [
    ni("EX001","easy","Recompose : 4 millions + 200 mille + 30 =",4200030,"4 000 000 + 200 000 + 30 = 4 200 030."),
    ni("EX002","medium","Recompose : 7×1 000 000 + 3×100 000 + 5×10 + 8 =",7300058,
        "7 000 000 + 300 000 + 50 + 8 = 7 300 058.","Calcule chaque produit."),
    fb("EX003","medium","2 centaines de mille + 45 milliers + 6 centaines = ___","245 600",
        "200 000 + 45 000 + 600 = 245 600."),
    ni("EX004","hard","Recompose : 50 dizaines de mille + 3 centaines de mille + 12 unités =",800012,
        "50 × 10 000 = 500 000, 3 × 100 000 = 300 000, 12 → 800 012.","Attention : 50 dizaines de mille = 500 000."),
]})

# MS06: Détecter erreurs de zéros
blocks.append({"micro_skill_external_id": "NUM-ENTIERS-0-1B::MS06", "exercises": [
    ec("EX001","medium","Un élève écrit « cinq millions trois mille » = 5 300 000.",
        "5 300 000","5 003 000","Cinq millions = 5 000 000, trois mille = 3 000 → 5 003 000, pas 5 300 000."),
    mcq("EX002","medium","Quelle écriture est correcte pour « deux millions quarante » ?",
        ["2 000 040","2 000 400","2 004 000","20 000 040"],"2 000 040",
        "Deux millions = 2 000 000, quarante = 40 → 2 000 040."),
    ec("EX003","hard","Erreur à corriger : 10 307 050 → « dix millions trente-sept mille cinquante ».",
        "dix millions trente-sept mille cinquante","dix millions trois cent sept mille cinquante",
        "307 mille = trois cent sept mille, pas trente-sept mille."),
    tf("EX004","medium","Le nombre « huit millions six cents » s'écrit 8 000 600.",True,
        "8 millions = 8 000 000, six cents = 600 → 8 000 600. C'est correct."),
]})

# ═══ NUM-DROITE-NUM-ENTIERS ═══
# MS01: Placer un entier sur une droite graduée
blocks.append({"micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS01", "exercises": [
    tr("EX001","easy","Place le nombre 350 sur cette droite graduée.",
        {"min":0,"max":500,"step":50,"target":350},350,"350 se trouve entre 300 et 400, à mi-chemin + 50."),
    tr("EX002","medium","Place le nombre 7 500 sur cette droite graduée.",
        {"min":0,"max":10000,"step":1000,"target":7500},7500,"7 500 se situe entre 7 000 et 8 000."),
    ni("EX003","medium","Sur une droite graduée de 0 à 100 000 (pas de 10 000), à quelle graduation se trouve le point situé à 3/4 du trajet entre 20 000 et 30 000 ?",
        27500,"3/4 de 10 000 = 7 500. Donc 20 000 + 7 500 = 27 500."),
    mcq("EX004","easy","Sur une droite graduée de 0 à 1 000 (pas de 100), entre quelles graduations se trouve 450 ?",
        ["400 et 500","300 et 400","500 et 600","450 et 550"],"400 et 500","450 est entre 400 et 500."),
]})

# MS02: Encadrer un entier
blocks.append({"micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS02", "exercises": [
    fb("EX001","easy","Encadre 3 456 entre deux milliers consécutifs : ___ < 3 456 < ___","3 000 < 3 456 < 4 000",
        "Le millier avant est 3 000, le millier après est 4 000.",blanks=["3 000","4 000"]),
    fb("EX002","medium","Encadre 78 432 à la dizaine de mille : ___ < 78 432 < ___","70 000 < 78 432 < 80 000",
        "La dizaine de mille inférieure est 70 000, la supérieure est 80 000.",blanks=["70 000","80 000"]),
    ni("EX003","medium","Quel est le nombre entier immédiatement après 99 999 ?",100000,
        "99 999 + 1 = 100 000."),
    mcq("EX004","hard","Encadre 5 678 345 au million près.",
        ["5 000 000 < 5 678 345 < 6 000 000","5 600 000 < 5 678 345 < 5 700 000",
         "5 678 000 < 5 678 345 < 5 679 000","5 000 000 < 5 678 345 < 5 500 000"],
        "5 000 000 < 5 678 345 < 6 000 000","Au million près : le million inférieur est 5M, le supérieur 6M."),
]})

# MS03: Ordonner une série d'entiers
blocks.append({"micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS03", "exercises": [
    order("EX001","easy","Range ces nombres dans l'ordre croissant.",
        ["45 321","12 890","67 450","34 100"],["12 890","34 100","45 321","67 450"],
        "12 890 < 34 100 < 45 321 < 67 450."),
    order("EX002","medium","Range ces nombres dans l'ordre décroissant.",
        ["1 234 567","1 324 567","1 234 657","1 243 567"],
        ["1 324 567","1 243 567","1 234 657","1 234 567"],
        "On compare les chiffres de gauche à droite."),
    order("EX003","medium","Range dans l'ordre croissant : 999 999, 1 000 001, 1 000 000, 999 000.",
        ["999 999","1 000 001","1 000 000","999 000"],
        ["999 000","999 999","1 000 000","1 000 001"],
        "999 000 < 999 999 < 1 000 000 < 1 000 001."),
    order("EX004","hard","Range dans l'ordre croissant ces nombres proches.",
        ["3 456 789","3 465 789","3 456 798","3 456 879"],
        ["3 456 789","3 456 798","3 456 879","3 465 789"],
        "On compare rang par rang en partant de la gauche."),
]})

# MS04: Comparer des entiers avec <, >, =
blocks.append({"micro_skill_external_id": "NUM-DROITE-NUM-ENTIERS::MS04", "exercises": [
    mcq("EX001","easy","Compare : 45 678 ___ 45 876.",["<",">","="],"<",
        "45 678 < 45 876 car au rang des centaines, 6 < 8."),
    fb("EX002","easy","Complete avec <, > ou = : 1 000 000 ___ 999 999.",">",
        "1 000 000 > 999 999 car 1 000 000 a 7 chiffres et 999 999 en a 6."),
    jus("EX003","medium","Compare 3 045 678 et 3 054 678. Justifie ta réponse.",
        "3 045 678 < 3 054 678","Les millions sont égaux (3). Aux dizaines de mille : 4 < 5, donc 3 045 678 < 3 054 678.",
        rubric="1pt: bon symbole, 1pt: justification par rang"),
    mcq("EX004","medium","Quel signe manque ? 7 890 123 ___ 7 890 132.",["<",">","="],"<",
        "Les 5 premiers chiffres sont identiques. Au rang des dizaines : 2 < 3."),
]})

# ═══ NUM-DIVISIBILITE-2-3-5 ═══
blocks.append({"micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS01", "exercises": [
    tf("EX001","easy","4 678 est divisible par 2.",True,"Le dernier chiffre est 8 (pair), donc divisible par 2."),
    mcq("EX002","easy","Lesquels sont divisibles par 2 ?",["3 456 et 7 890","3 457 et 7 891","3 456 et 7 891","3 457 et 7 890"],
        "3 456 et 7 890","Un nombre est divisible par 2 si son dernier chiffre est pair (0,2,4,6,8)."),
    tf("EX003","easy","Le nombre 10 345 est divisible par 2.",False,"Le dernier chiffre est 5 (impair), donc non divisible par 2."),
    mcq("EX004","medium","Parmi ces nombres, lequel n'est PAS divisible par 2 ?",["124","356","783","900"],"783",
        "783 se termine par 3 (impair)."),
]})

blocks.append({"micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS02", "exercises": [
    tf("EX001","easy","Le nombre 4 325 est divisible par 5.",True,"Le dernier chiffre est 5, donc divisible par 5."),
    mcq("EX002","easy","Lesquels sont divisibles par 5 ?",["230 et 1 005","231 et 1 006","233 et 1 007","234 et 1 008"],
        "230 et 1 005","Un nombre est divisible par 5 si son dernier chiffre est 0 ou 5."),
    tf("EX003","easy","45 672 est divisible par 5.",False,"Le dernier chiffre est 2, pas 0 ni 5."),
    mcq("EX004","medium","Quel nombre est divisible à la fois par 2 et par 5 ?",["135","240","345","127"],"240",
        "240 se termine par 0, donc divisible par 2 et par 5."),
]})

blocks.append({"micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS03", "exercises": [
    mcq("EX001","medium","Le nombre 5 412 est-il divisible par 3 ?",
        ["Oui, car 5+4+1+2=12 qui est divisible par 3","Non, car 5+4+1+2=12 qui n'est pas divisible par 3",
         "Oui, car il se termine par 2","Non, car il est pair"],
        "Oui, car 5+4+1+2=12 qui est divisible par 3","Somme des chiffres : 12. 12÷3=4, donc divisible par 3."),
    fb("EX002","medium","Pour vérifier si 7 236 est divisible par 3, je calcule 7+2+3+6 = ___. Conclusion : ___.","18, oui",
        "7+2+3+6 = 18. 18÷3 = 6, donc 7 236 est divisible par 3."),
    tf("EX003","medium","2 341 est divisible par 3.",False,"2+3+4+1 = 10. 10 n'est pas divisible par 3."),
    mcq("EX004","hard","Quel nombre est divisible par 3 mais PAS par 2 ?",["4 521","4 522","4 524","4 520"],"4 521",
        "4+5+2+1=12, divisible par 3. Se termine par 1, pas divisible par 2."),
]})

blocks.append({"micro_skill_external_id": "NUM-DIVISIBILITE-2-3-5::MS04", "exercises": [
    gs("EX001","hard","Simplifie la fraction 12/18 en utilisant la divisibilité.",
        [{"instruction":"Trouve un diviseur commun de 12 et 18","expected":"6"},
         {"instruction":"Divise numérateur et dénominateur par ce diviseur","expected":"12÷6=2, 18÷6=3"},
         {"instruction":"Écris la fraction simplifiée","expected":"2/3"}],
        "2/3","12 et 18 sont tous deux divisibles par 6: 12÷6=2, 18÷6=3."),
    mcq("EX002","hard","Quelle est la forme simplifiée de 15/25 ?",["3/5","5/5","1/5","15/25"],"3/5",
        "15 et 25 sont divisibles par 5 : 15÷5=3, 25÷5=5."),
    ec("EX003","hard","Un élève simplifie 24/36 et obtient 4/9.",
        "24/36 = 4/9","24/36 = 2/3","24÷12=2, 36÷12=3. La fraction simplifiée est 2/3, pas 4/9."),
    ni("EX004","medium","Simplifie 20/30. Quel est le numérateur de la fraction irréductible ?",2,
        "PGCD(20,30) = 10. 20÷10 = 2."),
]})

# ═══ NUM-DEC-ECRIRE-REP ═══
blocks.append({"micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS01", "exercises": [
    ni("EX001","easy","Convertis 7/10 en nombre décimal.",0.7,"7/10 = 0,7.",tol=0.01),
    fb("EX002","medium","45/100 = ___","0,45","45 centièmes = 0,45."),
    mcq("EX003","medium","Quelle fraction correspond à 0,125 ?",["125/1000","125/100","12/100","1/8"],
        "125/1000","0,125 = 125 millièmes = 125/1000."),
    ni("EX004","hard","Convertis 3/1000 en nombre décimal.",0.003,"3/1000 = 0,003.",tol=0.0001),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS02", "exercises": [
    mcq("EX001","easy","Dans 4,567, quel est le chiffre des centièmes ?",["6","5","7","4"],"6",
        "4,567 → 5 dixièmes, 6 centièmes, 7 millièmes."),
    fb("EX002","medium","Dans 12,345, le chiffre 3 représente 3 ___.","dixièmes",
        "12,345 : 3 est au rang des dixièmes."),
    mcq("EX003","medium","Quelle est la valeur du chiffre 8 dans 0,089 ?",
        ["8 centièmes","8 dixièmes","8 millièmes","8 unités"],"8 centièmes","0,089 → 0 dixième, 8 centièmes, 9 millièmes."),
    tf("EX004","hard","Dans 5,207, le chiffre 0 occupe le rang des centièmes.",True,
        "5,207 → 2 dixièmes, 0 centième, 7 millièmes."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS03", "exercises": [
    tr("EX001","medium","Place 3,5 sur cette droite graduée.",
        {"min":3,"max":4,"step":0.1,"target":3.5},3.5,"3,5 est exactement au milieu entre 3 et 4."),
    tr("EX002","medium","Place 0,75 sur cette droite graduée.",
        {"min":0,"max":1,"step":0.1,"target":0.75},0.75,"0,75 se situe entre 0,7 et 0,8."),
    ni("EX003","hard","Sur une droite de 0 à 1 graduée en dixièmes, quel décimal est situé entre 0,4 et 0,5, plus près de 0,5 ?",
        0.47,"Un décimal entre 0,4 et 0,5 plus proche de 0,5 peut être 0,47.",tol=0.04),
    mcq("EX004","medium","Sur une droite de 2 à 3 graduée en dixièmes, entre quelles graduations se trouve 2,34 ?",
        ["2,3 et 2,4","2,2 et 2,3","2,4 et 2,5","2,34 et 2,35"],"2,3 et 2,4",
        "2,34 est entre 2,3 et 2,4."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS04", "exercises": [
    fb("EX001","medium","Décompose 7,45 : partie entière = ___, partie décimale = ___","7 ; 0,45",
        "7,45 = 7 + 0,45. Partie entière : 7. Partie décimale : 0,45.",blanks=["7","0,45"]),
    sa("EX002","medium","Décompose 3,208 en rangs : 3 unités + ___ dixièmes + ___ centièmes + ___ millièmes.",
        "2 dixièmes + 0 centième + 8 millièmes","3,208 = 3 + 2/10 + 0/100 + 8/1000.",
        accepted=["2 + 0 + 8","2, 0, 8"]),
    ni("EX003","hard","Recompose : 4 unités + 13 centièmes = ?",4.13,
        "4 + 13/100 = 4 + 0,13 = 4,13.",tol=0.001),
    fb("EX004","medium","56,7 = 56 unités + ___ dixièmes.","7","56,7 = 56 + 7/10."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS05", "exercises": [
    fb("EX001","medium","Encadre 4,67 entre deux entiers : ___ < 4,67 < ___.","4 < 4,67 < 5",
        "La partie entière est 4, donc 4 < 4,67 < 5.",blanks=["4","5"]),
    fb("EX002","medium","Encadre 7,345 au dixième : ___ < 7,345 < ___.","7,3 < 7,345 < 7,4",
        "7,345 est entre 7,3 et 7,4.",blanks=["7,3","7,4"]),
    jus("EX003","hard","Encadre 0,678 au centième et justifie.",
        "0,67 < 0,678 < 0,68","Le centième inférieur est 0,67 et le centième supérieur est 0,68. 0,678 est entre les deux car son millième est 8.",
        rubric="1pt: encadrement correct, 1pt: justification"),
    mcq("EX004","medium","Quel encadrement au dixième est correct pour 3,456 ?",
        ["3,4 < 3,456 < 3,5","3,45 < 3,456 < 3,46","3 < 3,456 < 4","3,5 < 3,456 < 3,6"],
        "3,4 < 3,456 < 3,5","Au dixième : 3,4 < 3,456 < 3,5."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-ECRIRE-REP::MS06", "exercises": [
    ni("EX001","medium","Arrondis 4,567 à l'unité.",5,"4,567 → le dixième est 5 (≥5), on arrondit à 5.",tol=0),
    mcq("EX002","medium","Arrondis 7,342 au dixième.",["7,3","7,4","7,34","7"],"7,3",
        "7,342 → le centième est 4 (<5), on garde 7,3."),
    ni("EX003","hard","Arrondis 12,8975 au centième.",12.90,"Le millième est 7 (≥5), on arrondit : 12,90.",tol=0.001),
    ec("EX004","hard","Un élève arrondit 3,450 au dixième et obtient 3,4.",
        "3,4","3,5","Le centième est 5, on arrondit au dixième supérieur : 3,5."),
]})

# ═══ NUM-DEC-COMP-ORD ═══
blocks.append({"micro_skill_external_id": "NUM-DEC-COMP-ORD::MS01", "exercises": [
    mcq("EX001","easy","Compare : 4,56 ___ 4,65.",["<",">","="],"<",
        "4,56 < 4,65 car au rang des dixièmes, 5 < 6."),
    fb("EX002","medium","Complete : 7,80 ___ 7,8.","=","7,80 = 7,8 car le zéro final ne change pas la valeur."),
    mcq("EX003","medium","Quel signe manque ? 0,309 ___ 0,31.",["<",">","="],"<",
        "0,309 < 0,310 car 309 millièmes < 310 millièmes."),
    tf("EX004","easy","3,5 > 3,50.",False,"3,5 = 3,50, les zéros finaux ne changent rien."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-COMP-ORD::MS02", "exercises": [
    order("EX001","medium","Range dans l'ordre croissant.",
        ["3,45","3,405","3,5","3,045"],["3,045","3,405","3,45","3,5"],
        "On aligne les décimales : 3,045 < 3,405 < 3,450 < 3,500."),
    order("EX002","medium","Range dans l'ordre croissant.",
        ["0,7","0,67","0,076","0,706"],["0,076","0,67","0,7","0,706"],
        "0,076 < 0,670 < 0,700 < 0,706."),
    order("EX003","hard","Range dans l'ordre croissant.",
        ["12,099","12,1","12,009","12,91"],["12,009","12,099","12,1","12,91"],
        "12,009 < 12,099 < 12,100 < 12,910."),
    order("EX004","easy","Range dans l'ordre croissant.",
        ["5,6","5,2","5,9","5,1"],["5,1","5,2","5,6","5,9"],"On compare les dixièmes."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-COMP-ORD::MS03", "exercises": [
    order("EX001","medium","Range dans l'ordre décroissant.",
        ["2,45","2,54","2,405","2,5"],["2,54","2,5","2,45","2,405"],
        "2,540 > 2,500 > 2,450 > 2,405."),
    order("EX002","hard","Range dans l'ordre décroissant.",
        ["8,01","8,1","8,001","8,101"],["8,101","8,1","8,01","8,001"],
        "8,101 > 8,100 > 8,010 > 8,001."),
    order("EX003","medium","Range dans l'ordre décroissant.",
        ["0,5","0,55","0,505","0,055"],["0,55","0,505","0,5","0,055"],
        "0,550 > 0,505 > 0,500 > 0,055."),
    order("EX004","easy","Range dans l'ordre décroissant.",
        ["7,3","7,8","7,1","7,5"],["7,8","7,5","7,3","7,1"],"Compare les dixièmes."),
]})

blocks.append({"micro_skill_external_id": "NUM-DEC-COMP-ORD::MS04", "exercises": [
    jus("EX001","hard","Sans calculer, compare 6,789 et 6,8. Justifie.",
        "6,789 < 6,8","6,789 < 6,800. Au rang des dixièmes : 7 < 8, donc 6,789 < 6,8.",
        rubric="1pt: bon symbole, 1pt: justification par rang"),
    mcq("EX002","medium","Sans calcul, quel est le plus grand : 0,9 ou 0,89 ?",
        ["0,9","0,89","Ils sont égaux","On ne peut pas savoir"],"0,9",
        "0,90 > 0,89 car au dixième 9 > 8."),
    jus("EX003","hard","Compare 4,50 et 4,500. Justifie sans calcul.",
        "4,50 = 4,500","Les zéros ajoutés à droite de la partie décimale ne changent pas la valeur : 4,50 = 4,500.",
        rubric="1pt: égalité, 1pt: justification"),
    mcq("EX004","medium","Sans calcul, range du plus petit au plus grand : 1,5 / 1,05 / 1,50.",
        ["1,05 < 1,5 = 1,50","1,5 < 1,05 < 1,50","1,50 < 1,5 < 1,05","1,05 < 1,50 < 1,5"],
        "1,05 < 1,5 = 1,50","1,5 et 1,50 sont égaux. 1,05 < 1,50."),
]})

# ═══ NUM-FRAC-REP ═══
blocks.append({"micro_skill_external_id": "NUM-FRAC-REP::MS01", "exercises": [
    mcq("EX001","easy","Une pizza est partagée en 8 parts égales. Moussa en mange 3. Quelle fraction de la pizza a-t-il mangée ?",
        ["3/8","8/3","3/5","5/8"],"3/8","3 parts sur 8 au total = 3/8.","Combien de parts au total ? Combien mangées ?"),
    match("EX002","medium","Associe chaque situation à sa fraction.",
        ["2 parts sur 5","1 part sur 4","3 parts sur 3"],["2/5","1/4","3/3"],
        {"2 parts sur 5":"2/5","1 part sur 4":"1/4","3 parts sur 3":"3/3"},
        "Le numérateur = parts prises, le dénominateur = parts totales."),
    mcq("EX003","medium","Un terrain est divisé en 10 parcelles égales. 7 parcelles sont cultivées. Quelle fraction est cultivée ?",
        ["7/10","10/7","3/10","7/3"],"7/10","7 parcelles sur 10 = 7/10."),
    tf("EX004","easy","Si on coupe un gâteau en 6 parts égales et qu'on en prend 6, on a pris 6/6 = 1 gâteau entier.",True,
        "6/6 = 1 entier."),
]})

blocks.append({"micro_skill_external_id": "NUM-FRAC-REP::MS02", "exercises": [
    sa("EX001","medium","Que signifie la fraction 3/4 en termes de division ?","3 divisé par 4",
        "3/4 = 3 ÷ 4. Une fraction est un quotient.",accepted=["3 divisé par 4","3÷4","3 : 4"]),
    gs("EX002","hard","Calcule 7/4 sous forme décimale.",
        [{"instruction":"Effectue la division 7 ÷ 4","expected":"1,75"},
         {"instruction":"Vérifie : 1,75 × 4 = ?","expected":"7"}],
        "1,75","7 ÷ 4 = 1,75."),
    mcq("EX003","medium","Quelle division correspond à 5/8 ?",["5 ÷ 8","8 ÷ 5","5 × 8","8 − 5"],"5 ÷ 8",
        "5/8 signifie 5 divisé par 8."),
    ni("EX004","hard","Calcule le quotient décimal de 3/8.",0.375,"3 ÷ 8 = 0,375.",tol=0.001),
]})

blocks.append({"micro_skill_external_id": "NUM-FRAC-REP::MS03", "exercises": [
    mcq("EX001","hard","Dans une classe de 30 élèves, 18 sont des filles. Quelle fraction représente le rapport filles/total ?",
        ["18/30","30/18","18/12","12/18"],"18/30","18 filles sur 30 élèves = 18/30 (= 3/5 simplifiée)."),
    jus("EX002","hard","Sur 25 mangues, 5 sont pourries. Exprime le rapport mangues pourries / total et simplifie.",
        "5/25 = 1/5","5 sur 25 = 5/25. On simplifie par 5 : 1/5.",
        rubric="1pt: fraction correcte, 1pt: simplification"),
    mcq("EX003","hard","Akouavi a 12 billes et Kofi en a 8. Quel est le rapport billes de Kofi / billes d'Akouavi ?",
        ["8/12","12/8","8/20","12/20"],"8/12","Le rapport est 8/12 = 2/3."),
    tf("EX004","medium","Le rapport 6/10 signifie « 6 pour chaque groupe de 10 ».",True,
        "Un rapport a/b signifie a pour chaque b."),
]})

blocks.append({"micro_skill_external_id": "NUM-FRAC-REP::MS04", "exercises": [
    mcq("EX001","easy","Quelle fraction correspond à la moitié ?",["1/2","1/4","2/1","1/3"],"1/2",
        "La moitié = 1/2."),
    match("EX002","medium","Associe chaque fraction usuelle à sa valeur.",
        ["1/2","1/4","3/4","1/10"],["0,5","0,25","0,75","0,1"],
        {"1/2":"0,5","1/4":"0,25","3/4":"0,75","1/10":"0,1"},
        "1/2=0,5, 1/4=0,25, 3/4=0,75, 1/10=0,1."),
    fb("EX003","easy","La moitié de 1 = 1/2 = 0,___","5","1/2 = 0,5."),
    mcq("EX004","medium","Quelle fraction usuelle est égale à 0,25 ?",["1/4","1/2","3/4","1/5"],"1/4",
        "0,25 = 25/100 = 1/4."),
]})

blocks.append({"micro_skill_external_id": "NUM-FRAC-REP::MS05", "exercises": [
    mcq("EX001","easy","Sur un disque partagé en 4 parts égales, combien de parts colories-tu pour représenter 3/4 ?",
        ["3","4","1","2"],"3","3/4 = 3 parts sur 4."),
    tr("EX002","medium","Place 2/5 sur cette droite graduée (0 à 1, pas de 1/5).",
        {"min":0,"max":1,"step":0.2,"target":0.4},0.4,"2/5 = 0,4, soit 2 graduations de 1/5."),
    match("EX003","medium","Associe chaque fraction à sa représentation.",
        ["1/2","1/3","2/3"],["50% d'une barre","1 part sur 3","2 parts sur 3"],
        {"1/2":"50% d'une barre","1/3":"1 part sur 3","2/3":"2 parts sur 3"},
        "1/2 = moitié, 1/3 = un tiers, 2/3 = deux tiers."),
    mcq("EX004","easy","Quelle fraction est représentée si 5 cases sur 10 sont coloriées ?",
        ["5/10","10/5","5/5","1/5"],"5/10","5 cases coloriées sur 10 = 5/10 = 1/2."),
]})

blocks.append({"micro_skill_external_id": "NUM-FRAC-REP::MS06", "exercises": [
    mcq("EX001","hard","La fraction 7/4 est-elle supérieure ou inférieure à 1 ?",
        ["Supérieure à 1","Inférieure à 1","Égale à 1","On ne peut pas savoir"],"Supérieure à 1",
        "7/4 > 1 car le numérateur (7) est plus grand que le dénominateur (4)."),
    sa("EX002","hard","Écris 11/3 sous forme de nombre mixte.","3 2/3",
        "11 ÷ 3 = 3 reste 2, donc 11/3 = 3 + 2/3 = 3 2/3.",accepted=["3 2/3","3+2/3"]),
    mcq("EX003","hard","Quel nombre mixte correspond à 9/4 ?",
        ["2 1/4","2 1/2","1 3/4","3 1/4"],"2 1/4","9 ÷ 4 = 2 reste 1, donc 9/4 = 2 1/4."),
    tf("EX004","medium","La fraction 5/5 est égale à 1.",True,"5/5 = 5 ÷ 5 = 1."),
]})

# ── Assemble output ──
payload = {
    "schema_version": "1.0",
    "metadata": {"domain": "Numération", "grade": "CM2", "country": "Bénin", "generated": True},
    "exercises": blocks,
}

total = sum(len(b["exercises"]) for b in blocks)
out = "backend/exercices_cm2_numeration.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"✓ {out}: {len(blocks)} blocs, {total} exercices")
