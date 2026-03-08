"""Generate exercises for Opérations domain — Part 1 (first 6 skills, 28 MS)."""
import json

def B(eid,typ,diff,text,**kw):
    d={"exercise_id":eid,"type":typ,"difficulty":diff,"text":text,
       "points":{"easy":1,"medium":2,"hard":3}[diff],
       "time_limit_seconds":{"easy":45,"medium":60,"hard":90}[diff]}
    d.update(kw); return d

def mcq(eid,d,t,ch,a,ex,h=""): return B(eid,"mcq",d,t,choices=ch,correct_answer=a,explanation=ex,hint=h)
def tf(eid,d,t,a,ex,h=""): return B(eid,"true_false",d,t,correct_answer=a,explanation=ex,hint=h)
def fb(eid,d,t,a,ex,h="",blanks=None):
    r=B(eid,"fill_blank",d,t,correct_answer=a,explanation=ex,hint=h)
    if blanks:r["blanks"]=blanks
    return r
def ni(eid,d,t,a,ex,h="",tol=0):
    r=B(eid,"numeric_input",d,t,correct_answer=a,explanation=ex,hint=h)
    if tol:r["tolerance"]=tol
    return r
def sa(eid,d,t,a,ex,h="",acc=None):
    r=B(eid,"short_answer",d,t,correct_answer=a,explanation=ex,hint=h)
    if acc:r["accepted_answers"]=acc
    return r
def ec(eid,d,t,err,a,ex,h=""): return B(eid,"error_correction",d,t,erroneous_content=err,correct_answer=a,explanation=ex,hint=h)
def gs(eid,d,t,steps,a,ex,h=""): return B(eid,"guided_steps",d,t,steps=steps,correct_answer=a,explanation=ex,hint=h)
def order(eid,d,t,items,a,ex,h=""): return B(eid,"ordering",d,t,items=items,correct_answer=a,explanation=ex,hint=h)

blocks = []

# OPS-CALCUL-MENTAL-TABLES (5 MS)
blocks.append({"micro_skill_external_id":"OPS-CALCUL-MENTAL-TABLES::MS01","exercises":[
    ni("EX001","easy","7 × 8 = ?",56,"7×8 = 56. C'est une table de multiplication à connaître par cœur."),
    ni("EX002","easy","9 × 6 = ?",54,"9×6 = 54."),
    mcq("EX003","medium","Quel est le produit de 12 × 7 ?",["84","72","96","77"],"84","12×7 = 84."),
    ni("EX004","medium","11 × 9 = ?",99,"11×9 = 99."),
]})
blocks.append({"micro_skill_external_id":"OPS-CALCUL-MENTAL-TABLES::MS02","exercises":[
    ni("EX001","easy","Le double de 35 est :",70,"35 × 2 = 70."),
    ni("EX002","easy","La moitié de 64 est :",32,"64 ÷ 2 = 32."),
    mcq("EX003","medium","Le double de 450 est :",["900","225","4500","90"],"900","450 × 2 = 900."),
    ni("EX004","medium","La moitié de 3 500 est :",1750,"3 500 ÷ 2 = 1 750."),
]})
blocks.append({"micro_skill_external_id":"OPS-CALCUL-MENTAL-TABLES::MS03","exercises":[
    ni("EX001","medium","Le quadruple de 25 est :",100,"25 × 4 = 100. (25×2=50, 50×2=100)","Double deux fois."),
    ni("EX002","medium","Le quart de 200 est :",50,"200 ÷ 4 = 50. (200÷2=100, 100÷2=50)"),
    mcq("EX003","hard","Le quadruple de 125 est :",["500","250","1250","50"],"500","125×4 = 500. (125×2=250, 250×2=500)"),
    ni("EX004","hard","Le quart de 1 600 est :",400,"1600÷4 = 400."),
]})
blocks.append({"micro_skill_external_id":"OPS-CALCUL-MENTAL-TABLES::MS04","exercises":[
    ni("EX001","easy","Le complément à 100 de 37 est :",63,"100 - 37 = 63.","100 - ? = 63"),
    ni("EX002","medium","Le complément à 1 000 de 645 est :",355,"1 000 - 645 = 355."),
    fb("EX003","easy","78 + ___ = 100.","22","100 - 78 = 22."),
    ni("EX004","medium","Le complément à 10 de 3,7 est :",6.3,"10 - 3,7 = 6,3.",tol=0.1),
]})
blocks.append({"micro_skill_external_id":"OPS-CALCUL-MENTAL-TABLES::MS05","exercises":[
    ni("EX001","medium","45 × 10 = ?",450,"On ajoute un zéro : 45 × 10 = 450."),
    ni("EX002","medium","3,5 × 100 = ?",350,"On décale la virgule de 2 rangs : 3,5 × 100 = 350."),
    ec("EX003","hard","Un élève écrit : 7,2 × 1000 = 72.","7,2 × 1000 = 72","7,2 × 1000 = 7 200",
        "On décale la virgule de 3 rangs vers la droite : 7,200 → 7 200."),
    ni("EX004","hard","450 ÷ 100 = ?",4.5,"On décale la virgule de 2 rangs vers la gauche : 4,50.",tol=0.01),
]})

# OPS-ESTIMER-VERIFIER (5 MS)
blocks.append({"micro_skill_external_id":"OPS-ESTIMER-VERIFIER::MS01","exercises":[
    ni("EX001","easy","Arrondis 3 478 à la centaine la plus proche.",3500,"3 478 → 3 500 (le chiffre des dizaines est 7 ≥ 5).",tol=0),
    mcq("EX002","medium","Arrondis 56 743 au millier le plus proche.",["57 000","56 000","56 700","56 800"],"57 000",
        "56 743 → 57 000 (743 ≥ 500)."),
    ni("EX003","medium","Arrondis 8 250 au millier le plus proche.",8000,"8 250 → 8 000 (250 < 500).",tol=0),
    fb("EX004","easy","Pour estimer 489 + 312, j'arrondis : 500 + ___ ≈ ___.","300, 800","489 ≈ 500, 312 ≈ 300, total ≈ 800."),
]})
blocks.append({"micro_skill_external_id":"OPS-ESTIMER-VERIFIER::MS02","exercises":[
    ni("EX001","medium","Arrondis 7,83 à l'unité pour estimer.",8,"7,83 ≈ 8 (0,83 ≥ 0,5).",tol=0),
    mcq("EX002","hard","Pour estimer 4,67 × 2,1, on arrondit à :",["5 × 2 = 10","4 × 2 = 8","5 × 3 = 15","4,7 × 2 = 9,4"],
        "5 × 2 = 10","4,67 ≈ 5, 2,1 ≈ 2. Estimation : 10."),
    ec("EX003","hard","Un élève arrondit 3,45 à l'unité et obtient 3.","3,45 ≈ 3","3,45 ≈ 3 (car 0,45 < 0,5, l'élève a raison !)",
        "En fait l'élève a raison : 0,45 < 0,5, donc on arrondit vers le bas à 3."),
    ni("EX004","medium","Arrondis 12,345 au dixième.",12.3,"12,345 → 12,3 (le centième est 4 < 5).",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"OPS-ESTIMER-VERIFIER::MS03","exercises":[
    mcq("EX001","medium","Avant de calculer 498 × 21, l'ordre de grandeur est environ :",
        ["10 000","1 000","100 000","500"],"10 000","500 × 20 = 10 000."),
    sa("EX002","hard","Donne un ordre de grandeur de 3 890 ÷ 19.","200",
        "4 000 ÷ 20 = 200.",acc=["200","environ 200","≈ 200"]),
    mcq("EX003","medium","L'ordre de grandeur de 52 × 48 est :",["2 500","250","25 000","500"],
        "2 500","50 × 50 = 2 500."),
    mcq("EX004","hard","L'ordre de grandeur de 9,8 × 5,1 est :",["50","10","100","500"],"50","10 × 5 = 50."),
]})
blocks.append({"micro_skill_external_id":"OPS-ESTIMER-VERIFIER::MS04","exercises":[
    gs("EX001","hard","Vérifie que 456 + 289 = 745 en utilisant l'opération inverse.",
        [{"instruction":"L'opération inverse de l'addition est la soustraction","expected":"Soustraction"},
         {"instruction":"Calcule 745 - 289","expected":"456"},
         {"instruction":"Le résultat correspond au premier terme, donc c'est correct","expected":"Vérifié"}],
        "745 - 289 = 456 ✓","On vérifie une addition par la soustraction."),
    ec("EX002","hard","Un élève trouve 234 × 5 = 1 270. Vérifie par l'opération inverse.",
        "234 × 5 = 1 270","234 × 5 = 1 170","1 270 ÷ 5 = 254 ≠ 234. Le bon résultat est 1 170 (1 170 ÷ 5 = 234)."),
    sa("EX003","hard","Comment vérifier que 756 ÷ 12 = 63 ?","63 × 12 = 756",
        "On multiplie le quotient par le diviseur : 63 × 12 = 756 ✓.",acc=["63 × 12","63 × 12 = 756","12 × 63"]),
    mcq("EX004","medium","Pour vérifier une soustraction a - b = c, on calcule :",
        ["c + b et on vérifie qu'on obtient a","a + b","c - b","a × b"],"c + b et on vérifie qu'on obtient a",
        "La vérification d'une soustraction se fait par addition."),
]})
blocks.append({"micro_skill_external_id":"OPS-ESTIMER-VERIFIER::MS05","exercises":[
    ec("EX001","hard","Un élève calcule 45 + 78 = 1 023. Ce résultat est-il plausible ?",
        "45 + 78 = 1 023","45 + 78 = 123","1 023 est absurde : 50 + 80 = 130. Le bon résultat est 123."),
    mcq("EX002","hard","Un élève trouve 12 × 8 = 106. Ce résultat est :",
        ["Absurde (trop grand)","Correct","Trop petit","Presque correct"],"Absurde (trop grand)",
        "10 × 8 = 80, 12 × 8 devrait être un peu plus, autour de 96."),
    ec("EX003","hard","Problème : « Kofi a 250 F et achète 3 cahiers à 75 F chacun. Il lui reste 25 F. » Vérifie.",
        "250 - 3×75 = 25","250 - 225 = 25 ✓","3 × 75 = 225. 250 - 225 = 25. C'est correct."),
    mcq("EX004","medium","Pour estimer si 789 - 456 ≈ 333 est correct, on calcule :",
        ["800 - 450 = 350, c'est proche de 333","789 + 456","333 × 2","789 ÷ 456"],
        "800 - 450 = 350, c'est proche de 333","L'estimation confirme que 333 est plausible."),
]})

# OPS-TECHNIQUES-OPERATOIRES-ENTIERS (6 MS)
blocks.append({"micro_skill_external_id":"OPS-TECHNIQUES-OPERATOIRES-ENTIERS::MS01","exercises":[
    ni("EX001","medium","Pose et effectue : 4 567 + 3 895 = ?",8462,"4 567 + 3 895 = 8 462 (avec retenues)."),
    gs("EX002","medium","Calcule 2 786 + 5 437 en posant l'addition.",
        [{"instruction":"Unités : 6+7=13, on pose 3 retenue 1","expected":"3, retenue 1"},
         {"instruction":"Dizaines : 8+3+1=12, on pose 2 retenue 1","expected":"2, retenue 1"},
         {"instruction":"Centaines : 7+4+1=12, on pose 2 retenue 1","expected":"2, retenue 1"},
         {"instruction":"Milliers : 2+5+1=8","expected":"8"}],
        "8 223","2 786 + 5 437 = 8 223."),
    ec("EX003","hard","Un élève pose 3 456 + 2 789 et obtient 5 145.",
        "3 456 + 2 789 = 5 145","3 456 + 2 789 = 6 245","L'élève a oublié une retenue. Le bon résultat est 6 245."),
    ni("EX004","medium","678 + 9 456 = ?",10134,"678 + 9 456 = 10 134."),
]})
blocks.append({"micro_skill_external_id":"OPS-TECHNIQUES-OPERATOIRES-ENTIERS::MS02","exercises":[
    ni("EX001","medium","Pose et effectue : 8 003 - 4 567 = ?",3436,"8 003 - 4 567 = 3 436 (avec emprunts)."),
    gs("EX002","hard","Calcule 5 000 - 2 347 en posant la soustraction.",
        [{"instruction":"Unités : 0-7 impossible, emprunt → 10-7=3","expected":"3"},
         {"instruction":"Dizaines : 9(après emprunt)-4=5 → mais 0-1 pour l'emprunt : 9-4=5","expected":"5"},
         {"instruction":"Centaines : 9-3=6","expected":"6"},
         {"instruction":"Milliers : 4-2=2","expected":"2"}],
        "2 653","5 000 - 2 347 = 2 653."),
    ec("EX003","hard","Un élève trouve 7 200 - 3 856 = 4 456.",
        "7 200 - 3 856 = 4 456","7 200 - 3 856 = 3 344","L'élève a fait une erreur d'emprunt. Le bon résultat est 3 344."),
    ni("EX004","hard","10 000 - 6 789 = ?",3211,"10 000 - 6 789 = 3 211."),
]})
blocks.append({"micro_skill_external_id":"OPS-TECHNIQUES-OPERATOIRES-ENTIERS::MS03","exercises":[
    ni("EX001","medium","356 × 7 = ?",2492,"356 × 7 = 2 492."),
    gs("EX002","hard","Pose et effectue 245 × 36.",
        [{"instruction":"245 × 6 = 1 470","expected":"1 470"},
         {"instruction":"245 × 30 = 7 350","expected":"7 350"},
         {"instruction":"1 470 + 7 350 = 8 820","expected":"8 820"}],
        "8 820","245 × 36 = 8 820."),
    ec("EX003","hard","Un élève calcule 123 × 45 et obtient 5 435.",
        "123 × 45 = 5 435","123 × 45 = 5 535","123×5=615, 123×40=4920, 615+4920=5535."),
    ni("EX004","hard","508 × 23 = ?",11684,"508 × 23 = 11 684."),
]})
blocks.append({"micro_skill_external_id":"OPS-TECHNIQUES-OPERATOIRES-ENTIERS::MS04","exercises":[
    ni("EX001","hard","Effectue 847 ÷ 7. Donne le quotient.",121,"847 ÷ 7 = 121."),
    gs("EX002","hard","Pose la division 965 ÷ 5.",
        [{"instruction":"9 ÷ 5 = 1, reste 4","expected":"1, reste 4"},
         {"instruction":"46 ÷ 5 = 9, reste 1","expected":"9, reste 1"},
         {"instruction":"15 ÷ 5 = 3, reste 0","expected":"3, reste 0"}],
        "193","965 ÷ 5 = 193."),
    ni("EX003","hard","Quel est le reste de 500 ÷ 7 ?",3,"500 = 7 × 71 + 3. Le reste est 3."),
    ec("EX004","hard","Un élève dit que 156 ÷ 6 = 27.","156÷6=27","156÷6=26","6 × 27 = 162 ≠ 156. 6 × 26 = 156."),
]})
blocks.append({"micro_skill_external_id":"OPS-TECHNIQUES-OPERATOIRES-ENTIERS::MS05","exercises":[
    ni("EX001","hard","Effectue 4 536 ÷ 24. Donne le quotient.",189,"4 536 ÷ 24 = 189."),
    gs("EX002","hard","Pose 7 350 ÷ 35.",
        [{"instruction":"73 ÷ 35 = 2, reste 3","expected":"2, reste 3"},
         {"instruction":"35 ÷ 35 = 1, reste 0","expected":"1, reste 0"},
         {"instruction":"0 ÷ 35 = 0","expected":"0"}],
        "210","7 350 ÷ 35 = 210."),
    ni("EX003","hard","Quel est le quotient de 1 248 ÷ 16 ?",78,"1 248 ÷ 16 = 78."),
    ec("EX004","hard","Un élève trouve 2 520 ÷ 42 = 70.","2520÷42=70","2520÷42=60",
        "42 × 70 = 2 940 ≠ 2 520. 42 × 60 = 2 520."),
]})
blocks.append({"micro_skill_external_id":"OPS-TECHNIQUES-OPERATOIRES-ENTIERS::MS06","exercises":[
    ec("EX001","hard","Un élève additionne : 345 + 67 et aligne le 6 sous le 4 et le 7 sous le 5.",
        "Mauvais alignement : 345 + 67 en décalant","Il faut aligner les unités : 5 sous 7, 4 sous 6.",
        "En posant une opération, les unités doivent être alignées."),
    mcq("EX002","hard","L'erreur la plus fréquente en soustraction est :",
        ["Oublier les emprunts","Additionner au lieu de soustraire","Inverser les chiffres","Écrire à l'envers"],
        "Oublier les emprunts","L'oubli d'emprunt est l'erreur la plus courante en soustraction."),
    ec("EX003","hard","Un élève multiplie 23 × 45 : il fait 23×5=105, 23×4=82, et additionne 105+82=187.",
        "23×4=82 et position","23×40=920, pas 23×4. 105+920=1035.",
        "Le 4 de 45 vaut 40, pas 4. On doit décaler d'un rang."),
    sa("EX004","hard","Quelle erreur courante fait-on souvent en division ?",
        "Oublier de descendre un chiffre ou mal estimer le quotient partiel",
        "Les erreurs courantes : oublier de descendre un chiffre, mal estimer le quotient.",
        acc=["oublier de descendre","mal estimer","quotient partiel"]),
]})

# OPS-DECIMAUX-MULTIPLIER (4 MS)
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-MULTIPLIER::MS01","exercises":[
    gs("EX001","medium","Calcule 3,5 × 4,2 (étape 1 : ignore la virgule).",
        [{"instruction":"Calcule 35 × 42 (sans virgule)","expected":"1 470"}],
        "1 470","On multiplie d'abord comme des entiers : 35 × 42 = 1 470."),
    ni("EX002","medium","Pour calculer 2,7 × 3,1, multiplie d'abord 27 × 31 =",837,"27 × 31 = 837."),
    ni("EX003","hard","Pour 0,45 × 1,2, multiplie 45 × 12 =",540,"45 × 12 = 540."),
    gs("EX004","hard","Calcule 6,25 × 0,8 : étape 1.",
        [{"instruction":"Ignore les virgules : 625 × 8","expected":"5 000"}],
        "5 000","625 × 8 = 5 000."),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-MULTIPLIER::MS02","exercises":[
    mcq("EX001","medium","Dans 3,5 × 4,2, combien de chiffres après la virgule au total dans les facteurs ?",
        ["2","1","3","0"],"2","3,5 a 1 décimale + 4,2 a 1 décimale = 2 décimales."),
    fb("EX002","hard","Dans 0,45 × 1,2, le nombre total de décimales est ___.","3",
        "0,45 a 2 décimales + 1,2 a 1 décimale = 3 décimales."),
    mcq("EX003","medium","6,1 × 2,05 : combien de décimales dans le produit ?",["3","2","1","4"],"3",
        "6,1 (1 décimale) × 2,05 (2 décimales) = 3 décimales."),
    ni("EX004","hard","Dans 0,003 × 0,02, combien de décimales au total ?",5,"3 + 2 = 5 décimales."),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-MULTIPLIER::MS03","exercises":[
    ni("EX001","hard","3,5 × 4,2 = ? (on a trouvé 35×42=1470, 2 décimales)",14.70,"1 470 avec 2 décimales → 14,70.",tol=0.01),
    ni("EX002","hard","0,45 × 1,2 = ? (on a trouvé 45×12=540, 3 décimales)",0.540,"540 avec 3 décimales → 0,540.",tol=0.001),
    ec("EX003","hard","Un élève calcule 2,5 × 1,3 et obtient 325.",
        "2,5×1,3=325","2,5×1,3=3,25","25×13=325, 2 décimales → 3,25."),
    ni("EX004","hard","6,25 × 0,8 = ?",5.0,"625×8=5000, 3 décimales → 5,000.",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-MULTIPLIER::MS04","exercises":[
    mcq("EX001","hard","Pour vérifier 3,5 × 4,2 = 14,7, on estime : 4 × 4 = 16. 14,7 est-il plausible ?",
        ["Oui, c'est proche de 16","Non, c'est trop loin","On ne peut pas savoir","Il faudrait 16 exactement"],
        "Oui, c'est proche de 16","14,7 est proche de 16, le résultat est plausible."),
    ec("EX002","hard","Un élève trouve 5,2 × 3,8 = 1,976. Vérifie par estimation.",
        "5,2×3,8=1,976","5,2×3,8=19,76","Estimation : 5 × 4 = 20. 1,976 est trop petit. Le bon résultat est 19,76."),
    sa("EX003","hard","Estime 9,8 × 5,1 et compare avec le résultat exact 49,98.","50",
        "10 × 5 = 50. 49,98 ≈ 50 ✓.",acc=["50","≈50","environ 50"]),
    mcq("EX004","hard","2,1 × 0,9 devrait être :",["Proche de 2","Proche de 20","Proche de 0,2","Proche de 200"],
        "Proche de 2","2 × 1 = 2. Le résultat (1,89) est proche de 2."),
]})

# OPS-DECIMAUX-DIVISER (5 MS)
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-DIVISER::MS01","exercises":[
    gs("EX001","hard","Divise 7,56 par 4.",
        [{"instruction":"7 ÷ 4 = 1, reste 3","expected":"1, reste 3"},
         {"instruction":"Place la virgule dans le quotient (après les unités)","expected":"1,"},
         {"instruction":"35 ÷ 4 = 8, reste 3","expected":"1,8 reste 3"},
         {"instruction":"36 ÷ 4 = 9","expected":"1,89"}],
        "1,89","7,56 ÷ 4 = 1,89."),
    ni("EX002","hard","14,4 ÷ 6 = ?",2.4,"14,4 ÷ 6 = 2,4.",tol=0.01),
    ec("EX003","hard","Un élève divise 9,6 par 3 et obtient 32.",
        "9,6÷3=32","9,6÷3=3,2","L'élève a oublié la virgule. 9,6÷3 = 3,2."),
    ni("EX004","hard","25,5 ÷ 5 = ?",5.1,"25,5 ÷ 5 = 5,1.",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-DIVISER::MS02","exercises":[
    gs("EX001","hard","Calcule 7 ÷ 4 en prolongeant la division.",
        [{"instruction":"7 ÷ 4 = 1, reste 3","expected":"1, reste 3"},
         {"instruction":"Ajoute un 0 : 30 ÷ 4 = 7, reste 2","expected":"1,7 reste 2"},
         {"instruction":"Ajoute un 0 : 20 ÷ 4 = 5","expected":"1,75"}],
        "1,75","7 ÷ 4 = 1,75."),
    ni("EX002","hard","Calcule 5 ÷ 8 en quotient décimal.",0.625,"5 ÷ 8 = 0,625.",tol=0.001),
    ni("EX003","hard","22 ÷ 8 = ?",2.75,"22 ÷ 8 = 2,75.",tol=0.01),
    gs("EX004","hard","Calcule 3 ÷ 4.",
        [{"instruction":"3 ÷ 4 = 0, reste 3","expected":"0,"},
         {"instruction":"30 ÷ 4 = 7, reste 2","expected":"0,7"},
         {"instruction":"20 ÷ 4 = 5","expected":"0,75"}],
        "0,75","3 ÷ 4 = 0,75."),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-DIVISER::MS03","exercises":[
    mcq("EX001","hard","Si on multiplie le dividende et le diviseur par 10, le quotient :",
        ["Ne change pas","Est multiplié par 10","Est divisé par 10","Est multiplié par 100"],
        "Ne change pas","a/b = (a×10)/(b×10). Le quotient reste identique."),
    gs("EX002","hard","Calcule 4,5 ÷ 0,5 en utilisant la propriété des quotients égaux.",
        [{"instruction":"Multiplie les deux par 10 : 45 ÷ 5","expected":"45 ÷ 5"},
         {"instruction":"Calcule 45 ÷ 5","expected":"9"}],
        "9","4,5 ÷ 0,5 = 45 ÷ 5 = 9."),
    sa("EX003","hard","6,3 ÷ 0,9 = ? (utilise la propriété des quotients égaux).","7",
        "63 ÷ 9 = 7.",acc=["7"]),
    mcq("EX004","hard","0,8 ÷ 0,4 = ?",["2","0,2","20","0,02"],"2","8 ÷ 4 = 2."),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-DIVISER::MS04","exercises":[
    ni("EX001","hard","Donne le quotient approché au dixième de 10 ÷ 3.",3.3,"10 ÷ 3 = 3,333… ≈ 3,3.",tol=0.05),
    mcq("EX002","hard","Le quotient de 7 ÷ 3 est :",["Un quotient approché (2,333…)","Un quotient exact (2,33)","Un nombre entier","Impossible"],
        "Un quotient approché (2,333…)","7/3 = 2,333… est un nombre décimal périodique."),
    ni("EX003","hard","Arrondis 22 ÷ 7 au centième.",3.14,"22 ÷ 7 = 3,142… ≈ 3,14.",tol=0.01),
    ec("EX004","hard","Un élève dit que 10 ÷ 3 = 3,3 exactement.",
        "10÷3 = 3,3 exactement","10÷3 ≈ 3,3 (quotient approché)","10 ÷ 3 = 3,333… c'est un quotient approché, pas exact."),
]})
blocks.append({"micro_skill_external_id":"OPS-DECIMAUX-DIVISER::MS05","exercises":[
    gs("EX001","hard","Vérifie que 7,56 ÷ 4 = 1,89 par multiplication.",
        [{"instruction":"Calcule 1,89 × 4","expected":"7,56"},
         {"instruction":"Compare avec le dividende","expected":"7,56 = 7,56 ✓"}],
        "1,89 × 4 = 7,56 ✓","La vérification par multiplication confirme le résultat."),
    ec("EX002","hard","Un élève trouve 12,5 ÷ 5 = 2,6. Vérifie.",
        "12,5÷5=2,6","12,5÷5=2,5","2,6 × 5 = 13 ≠ 12,5. Le bon résultat est 2,5 (2,5 × 5 = 12,5)."),
    sa("EX003","hard","Comment vérifier 24,8 ÷ 8 = 3,1 ?","3,1 × 8 = 24,8",
        "On multiplie quotient × diviseur.",acc=["3,1 × 8","3,1 × 8 = 24,8","8 × 3,1"]),
    mcq("EX004","hard","Si 6,3 ÷ 0,9 = 7, alors 7 × 0,9 devrait donner :",
        ["6,3","7","0,9","63"],"6,3","Vérification : 7 × 0,9 = 6,3 ✓."),
]})

# Save part 1
import json as _j
with open("_ops_part1.json","w") as f:
    _j.dump(blocks, f, ensure_ascii=False)
print(f"Part 1: {len(blocks)} blocks, {sum(len(b['exercises']) for b in blocks)} exercises")
