"""Generate exercises for Opérations domain — Part 2 (remaining 30 MS)."""
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
def cp(eid,d,t,sq,a,ex,h=""): return B(eid,"contextual_problem",d,t,sub_questions=sq,correct_answer=a,explanation=ex,hint=h)

blocks = []

# OPS-FRAC-ADD-SUB-EQDEN (5 MS)
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-EQDEN::MS01","exercises":[
    ni("EX001","medium","3/7 + 2/7 = ?/7. Quel est le numérateur ?",5,"3/7 + 2/7 = 5/7."),
    gs("EX002","medium","Calcule 4/9 + 3/9.",
        [{"instruction":"Les dénominateurs sont identiques (9)","expected":"Même dénominateur"},
         {"instruction":"Additionne les numérateurs : 4+3","expected":"7"},
         {"instruction":"Le résultat est 7/9","expected":"7/9"}],
        "7/9","Même dénominateur : on additionne les numérateurs."),
    mcq("EX003","medium","1/5 + 3/5 = ?",["4/5","4/10","3/5","1/5"],"4/5","1+3=4, dénominateur 5. Résultat : 4/5."),
    ni("EX004","medium","5/12 + 4/12 = ?/12.",9,"5+4=9 → 9/12."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-EQDEN::MS02","exercises":[
    ni("EX001","medium","7/8 - 3/8 = ?/8.",4,"7-3=4 → 4/8 = 1/2."),
    gs("EX002","medium","Calcule 5/6 - 2/6.",
        [{"instruction":"Les dénominateurs sont identiques (6)","expected":"Même dénominateur"},
         {"instruction":"Soustrais les numérateurs : 5-2","expected":"3"},
         {"instruction":"Résultat : 3/6 = 1/2","expected":"3/6"}],
        "3/6","5/6 - 2/6 = 3/6 = 1/2."),
    ni("EX003","medium","9/10 - 4/10 = ?/10.",5,"9-4=5 → 5/10."),
    mcq("EX004","medium","11/15 - 6/15 = ?",["5/15","5/30","17/15","6/15"],"5/15","11-6=5, dénominateur 15."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-EQDEN::MS03","exercises":[
    ni("EX001","hard","7/4 en nombre mixte : partie entière ?",1,"7÷4=1 reste 3 → 1 3/4."),
    fb("EX002","hard","9/5 = ___ ___/5.","1 4/5","9÷5=1 reste 4 → 1 4/5."),
    mcq("EX003","hard","11/3 en nombre mixte :",["3 2/3","3 1/3","2 3/3","4 1/3"],"3 2/3","11÷3=3 reste 2."),
    ni("EX004","hard","13/6 : partie entière ?",2,"13÷6=2 reste 1 → 2 1/6."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-EQDEN::MS04","exercises":[
    ni("EX001","hard","Simplifie 6/8. Numérateur de la fraction irréductible ?",3,"6/8 = 3/4 (÷2)."),
    ec("EX002","hard","Un élève simplifie 4/12 et obtient 2/4.","4/12=2/4","4/12=1/3","4÷4=1, 12÷4=3 → 1/3."),
    fb("EX003","hard","8/12 simplifié = ___","2/3","PGCD(8,12)=4. 8÷4=2, 12÷4=3."),
    mcq("EX004","hard","10/15 simplifié :",["2/3","1/3","5/3","10/15"],"2/3","÷5: 10/15=2/3."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-EQDEN::MS05","exercises":[
    ec("EX001","hard","Un élève calcule 2/5 + 3/5 = 5/10.","2/5+3/5=5/10","2/5+3/5=5/5=1",
        "On n'additionne PAS les dénominateurs. On garde le dénominateur commun : 5."),
    mcq("EX002","hard","L'erreur dans 3/7 + 2/7 = 5/14 est :",
        ["Le dénominateur a été additionné (7+7=14)","Le numérateur est faux","Le calcul est correct","Les fractions ne sont pas compatibles"],
        "Le dénominateur a été additionné (7+7=14)","On garde le dénominateur commun, on ne l'additionne pas."),
    ec("EX003","hard","Erreur : 4/9 + 5/9 = 9/18.","4/9+5/9=9/18","4/9+5/9=9/9=1",
        "Le dénominateur reste 9, pas 18. 4+5=9, résultat 9/9=1."),
    sa("EX004","hard","Quelle est l'erreur typique quand on additionne des fractions de même dénominateur ?",
        "Additionner aussi les dénominateurs",
        "L'erreur fréquente est d'additionner les dénominateurs au lieu de les garder.",
        acc=["additionner les dénominateurs","dénominateurs additionnés"]),
]})

# OPS-FRAC-ADD-SUB-DIFDEN (5 MS)
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-DIFDEN::MS01","exercises":[
    gs("EX001","hard","Trouve un dénominateur commun pour 1/3 et 1/4.",
        [{"instruction":"Multiples de 3 : 3, 6, 9, 12...","expected":"3,6,9,12"},
         {"instruction":"Multiples de 4 : 4, 8, 12...","expected":"4,8,12"},
         {"instruction":"Le plus petit commun est 12","expected":"12"}],
        "12","Le PPCM de 3 et 4 est 12."),
    fb("EX002","hard","Dénominateur commun pour 1/2 et 1/5 : ___","10","Multiples de 2 : 2,4,6,8,10. Multiples de 5 : 5,10. PPCM = 10."),
    mcq("EX003","hard","Quel dénominateur commun pour 2/3 et 5/6 ?",["6","18","9","3"],"6","6 est un multiple de 3 et de 6."),
    ni("EX004","hard","Dénominateur commun pour 3/4 et 5/8 ?",8,"8 est un multiple de 4 et de 8."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-DIFDEN::MS02","exercises":[
    gs("EX001","hard","Réduis 1/3 et 1/4 au même dénominateur (12).",
        [{"instruction":"1/3 = ?/12 → 1×4=4, 3×4=12","expected":"4/12"},
         {"instruction":"1/4 = ?/12 → 1×3=3, 4×3=12","expected":"3/12"}],
        "4/12 et 3/12","1/3 = 4/12, 1/4 = 3/12."),
    fb("EX002","hard","2/5 = ___/10","4/10","2×2=4, 5×2=10 → 4/10."),
    ni("EX003","hard","3/4 au dénominateur 12 : numérateur ?",9,"3×3=9, 4×3=12 → 9/12."),
    gs("EX004","hard","Réduis 2/3 et 5/6 au même dénominateur.",
        [{"instruction":"Dénominateur commun = 6","expected":"6"},
         {"instruction":"2/3 = 4/6","expected":"4/6"},
         {"instruction":"5/6 reste 5/6","expected":"5/6"}],
        "4/6 et 5/6","2/3 = 4/6 (×2), 5/6 reste 5/6."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-DIFDEN::MS03","exercises":[
    gs("EX001","hard","Calcule 1/3 + 1/4.",
        [{"instruction":"Dénominateur commun : 12","expected":"12"},
         {"instruction":"1/3 = 4/12, 1/4 = 3/12","expected":"4/12 et 3/12"},
         {"instruction":"4/12 + 3/12 = 7/12","expected":"7/12"}],
        "7/12","1/3 + 1/4 = 4/12 + 3/12 = 7/12."),
    ni("EX002","hard","1/2 + 1/3 = ?/6.",5,"3/6 + 2/6 = 5/6."),
    ni("EX003","hard","2/5 + 1/10 = ?/10.",5,"4/10 + 1/10 = 5/10."),
    mcq("EX004","hard","3/4 + 1/6 = ?",["11/12","4/10","7/12","3/10"],"11/12","9/12 + 2/12 = 11/12."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-DIFDEN::MS04","exercises":[
    gs("EX001","hard","Calcule 3/4 - 1/3.",
        [{"instruction":"Dénominateur commun : 12","expected":"12"},
         {"instruction":"3/4 = 9/12, 1/3 = 4/12","expected":"9/12 et 4/12"},
         {"instruction":"9/12 - 4/12 = 5/12","expected":"5/12"}],
        "5/12","3/4 - 1/3 = 9/12 - 4/12 = 5/12."),
    ni("EX002","hard","5/6 - 1/2 = ?/6.",2,"5/6 - 3/6 = 2/6 = 1/3."),
    ni("EX003","hard","7/8 - 1/4 = ?/8.",5,"7/8 - 2/8 = 5/8."),
    mcq("EX004","hard","2/3 - 1/4 = ?",["5/12","1/7","3/12","1/12"],"5/12","8/12 - 3/12 = 5/12."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-ADD-SUB-DIFDEN::MS05","exercises":[
    ec("EX001","hard","Un élève réduit 1/3 au dénominateur 6 et obtient 1/6.",
        "1/3 = 1/6","1/3 = 2/6","Il faut multiplier numérateur et dénominateur par 2 : 1×2=2, 3×2=6."),
    mcq("EX002","hard","L'erreur dans la réduction 2/5 = 4/15 est :",
        ["Le numérateur a été multiplié par 2 mais le dénominateur par 3","Le numérateur est faux","Le dénominateur est faux","C'est correct"],
        "Le numérateur a été multiplié par 2 mais le dénominateur par 3",
        "Il faut multiplier les deux par le MÊME nombre. 2/5 = 6/15 (×3)."),
    ec("EX003","hard","Erreur : 3/4 + 2/3 = 5/7 (l'élève a additionné numérateurs ET dénominateurs).",
        "3/4+2/3=5/7","3/4+2/3 = 9/12+8/12 = 17/12",
        "On ne peut pas additionner directement des fractions de dénominateurs différents. Il faut réduire au même dénominateur."),
    sa("EX004","hard","Quelle est l'erreur la plus courante en addition de fractions de dénominateurs différents ?",
        "Additionner directement les numérateurs et les dénominateurs sans réduire",
        "L'erreur classique : a/b + c/d = (a+c)/(b+d), ce qui est faux.",
        acc=["additionner numérateurs et dénominateurs","sans réduire","pas réduire"]),
]})

# OPS-FRAC-X-ENT (4 MS)
blocks.append({"micro_skill_external_id":"OPS-FRAC-X-ENT::MS01","exercises":[
    mcq("EX001","medium","2/5 × 3 signifie :",["2/5 + 2/5 + 2/5","2 × 3 / 5 × 3","2/15","5/3"],
        "2/5 + 2/5 + 2/5","Multiplier une fraction par un entier = additionner la fraction autant de fois."),
    sa("EX002","medium","Explique 3/4 × 2 comme une addition répétée.","3/4 + 3/4",
        "3/4 × 2 = 3/4 + 3/4 = 6/4.",acc=["3/4 + 3/4","3/4+3/4"]),
    tf("EX003","medium","5/7 × 4 = 5/7 + 5/7 + 5/7 + 5/7.",True,"C'est la définition de la multiplication par un entier."),
    mcq("EX004","easy","1/3 × 3 = ?",["1","3/9","1/9","3"],"1","1/3 + 1/3 + 1/3 = 3/3 = 1."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-X-ENT::MS02","exercises":[
    gs("EX001","hard","Calcule 3/5 × 4.",
        [{"instruction":"Multiplie le numérateur par l'entier : 3×4","expected":"12"},
         {"instruction":"Le dénominateur ne change pas : 5","expected":"5"},
         {"instruction":"Résultat : 12/5","expected":"12/5"}],
        "12/5","3/5 × 4 = 12/5."),
    ni("EX002","hard","2/7 × 5 = ?/7.",10,"2×5=10, dénominateur 7 → 10/7."),
    ni("EX003","hard","4/9 × 3 = ?/9.",12,"4×3=12 → 12/9 = 4/3."),
    mcq("EX004","hard","5/8 × 6 = ?",["30/8","11/8","5/48","30/48"],"30/8","5×6=30, dénominateur 8 → 30/8 = 15/4."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-X-ENT::MS03","exercises":[
    fb("EX001","hard","12/5 en nombre mixte = ___ ___/5.","2 2/5","12÷5=2 reste 2 → 2 2/5."),
    ni("EX002","hard","30/8 simplifié : numérateur ?",15,"30/8 = 15/4 (÷2). En mixte : 3 3/4."),
    mcq("EX003","hard","7/3 × 2 = 14/3 = ?",["4 2/3","4 1/3","5 2/3","3 2/3"],"4 2/3","14÷3=4 reste 2 → 4 2/3."),
    fb("EX004","hard","20/6 simplifié = ___","10/3","÷2 : 20/6=10/3 = 3 1/3."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-X-ENT::MS04","exercises":[
    ec("EX001","hard","Un élève calcule 2/3 × 5 = 10/15.","2/3×5=10/15","2/3×5=10/3",
        "On multiplie SEULEMENT le numérateur : 2×5=10. Le dénominateur reste 3."),
    mcq("EX002","hard","L'erreur dans 4/7 × 3 = 12/21 est :",
        ["Le dénominateur a aussi été multiplié par 3","Le numérateur est faux","C'est correct","Le résultat devrait être entier"],
        "Le dénominateur a aussi été multiplié par 3","Seul le numérateur est multiplié. 4×3=12, dénominateur reste 7 → 12/7."),
    ec("EX003","hard","Erreur : 3/8 × 4 = 12/32.","3/8×4=12/32","3/8×4=12/8=3/2",
        "Le dénominateur ne change pas quand on multiplie par un entier."),
    sa("EX004","hard","Quelle erreur fait-on souvent quand on multiplie une fraction par un entier ?",
        "Multiplier aussi le dénominateur",
        "L'erreur classique : multiplier numérateur ET dénominateur, au lieu du numérateur seul.",
        acc=["multiplier le dénominateur","dénominateur multiplié","numérateur et dénominateur"]),
]})

# OPS-FRAC-PART-QUANT (5 MS)
blocks.append({"micro_skill_external_id":"OPS-FRAC-PART-QUANT::MS01","exercises":[
    mcq("EX001","medium","Pour calculer les 3/4 de 80, le « tout » est :",["80","3","4","60"],"80",
        "Le « tout » est la quantité de référence : 80."),
    sa("EX002","medium","Dans « les 2/5 de 150 élèves », que représente le « tout » ?","150",
        "150 élèves est la quantité de référence.",acc=["150","150 élèves"]),
    mcq("EX003","medium","La fraction « 2/5 » signifie :",["2 parts sur un total de 5","5 parts sur un total de 2","2+5","2÷5 seulement"],
        "2 parts sur un total de 5","Le numérateur = parts prises, le dénominateur = parts totales."),
    tf("EX004","easy","Pour trouver 1/4 de 100, je divise 100 par 4.",True,"1/4 de 100 = 100÷4 = 25."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-PART-QUANT::MS02","exercises":[
    ni("EX001","medium","Calcule 1/5 de 350.",70,"350 ÷ 5 = 70."),
    gs("EX002","hard","Calcule 1/8 de 240.",
        [{"instruction":"Divise 240 par le dénominateur (8)","expected":"240 ÷ 8 = 30"}],
        "30","1/8 de 240 = 240÷8 = 30."),
    cp("EX003","hard","Moussa a 600 F. Il dépense 1/3 de son argent. Combien a-t-il dépensé ?",
        [{"text":"Que faut-il calculer ?","answer":"1/3 de 600"},
         {"text":"Calcule","answer":"600 ÷ 3 = 200 F"}],
        "200 F","1/3 de 600 = 200 F."),
    ni("EX004","hard","1/6 de 420 = ?",70,"420 ÷ 6 = 70."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-PART-QUANT::MS03","exercises":[
    gs("EX001","hard","Calcule 3/4 de 80.",
        [{"instruction":"1/4 de 80 = 80÷4","expected":"20"},
         {"instruction":"3/4 de 80 = 3 × 20","expected":"60"}],
        "60","3/4 de 80 = 60."),
    ni("EX002","hard","2/5 de 150 = ?",60,"150÷5=30, 30×2=60."),
    cp("EX003","hard","Une classe a 40 élèves. Les 3/8 sont des filles. Combien y a-t-il de filles ?",
        [{"text":"1/8 de 40 ?","answer":"5"},
         {"text":"3/8 de 40 ?","answer":"15"}],
        "15 filles","40÷8=5, 5×3=15."),
    ni("EX004","hard","5/6 de 180 = ?",150,"180÷6=30, 30×5=150."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-PART-QUANT::MS04","exercises":[
    mcq("EX001","hard","Pour calculer 3/4 de 2,8 km, il vaut mieux :",
        ["Convertir en mètres (2 800 m) puis calculer 3/4","Garder en km et diviser par 3",
         "Multiplier 3 × 4 × 2,8","Additionner 3 + 4 + 2,8"],
        "Convertir en mètres (2 800 m) puis calculer 3/4",
        "2 800 m ÷ 4 = 700 m, 700 × 3 = 2 100 m = 2,1 km."),
    cp("EX002","hard","Un commerçant a 0,75 kg de sucre. Il vend les 2/3. Combien vend-il ?",
        [{"text":"Convertis en grammes","answer":"750 g"},
         {"text":"2/3 de 750 g","answer":"750÷3=250, 250×2=500 g"}],
        "500 g","750÷3=250, 250×2=500 g = 0,5 kg."),
    mcq("EX003","hard","Pour les 3/5 de 1,5 L :",["On calcule 1,5÷5×3 = 0,9 L","On calcule 1,5×5÷3","On calcule 3÷5×1,5",
        "On ne peut pas"],
        "On calcule 1,5÷5×3 = 0,9 L","1,5÷5=0,3, 0,3×3=0,9 L."),
    sa("EX004","hard","Est-il plus facile de calculer 3/4 de 2,4 en fraction ou en décimal ?",
        "En décimal : 2,4 ÷ 4 = 0,6, puis 0,6 × 3 = 1,8",
        "En décimal, le calcul est direct.",acc=["décimal","en décimal"]),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-PART-QUANT::MS05","exercises":[
    ec("EX001","hard","Un élève calcule 1/4 de 200 : il fait 200 × 4 = 800.",
        "200×4=800","200÷4=50","Pour 1/n d'une quantité, on DIVISE par n, on ne multiplie pas."),
    ec("EX002","hard","Erreur : 2/3 de 90 = 90÷2×3 = 135.","90÷2×3=135","90÷3×2=60",
        "On divise par le dénominateur (3), pas le numérateur (2). 90÷3=30, 30×2=60."),
    mcq("EX003","hard","L'erreur dans « 3/5 de 100 = 100÷3×5 = 166 » est :",
        ["L'élève a divisé par le numérateur au lieu du dénominateur","Le calcul est correct",
         "Il faut multiplier","L'unité est fausse"],
        "L'élève a divisé par le numérateur au lieu du dénominateur",
        "Correct : 100÷5=20, 20×3=60."),
    sa("EX004","hard","Quelle erreur courante fait-on avec les fractions d'une quantité ?",
        "Confondre multiplier et diviser, ou inverser numérateur et dénominateur",
        "Les erreurs fréquentes : diviser par le numérateur, oublier l'unité.",
        acc=["inverser","confondre multiplier et diviser","diviser par le numérateur"]),
]})

# OPS-FRAC-RETROUVER-TOUT (5 MS)
blocks.append({"micro_skill_external_id":"OPS-FRAC-RETROUVER-TOUT::MS01","exercises":[
    mcq("EX001","hard","Les 3/5 d'un nombre valent 60. La fraction connue est :",
        ["3/5","60/3","5/3","60/5"],"3/5","3/5 est la fraction donnée, 60 est la valeur correspondante."),
    sa("EX002","hard","Les 2/7 de la récolte = 140 kg. Identifie la fraction et la valeur.",
        "Fraction : 2/7, valeur : 140 kg","2/7 est la fraction, 140 kg est la valeur.",
        acc=["2/7 et 140","fraction 2/7, valeur 140"]),
    mcq("EX003","hard","Si 4/9 d'un prix = 200 F, que faut-il trouver ?",
        ["Le prix total (le tout)","4 fois 200","9 fois 200","200 ÷ 4"],
        "Le prix total (le tout)","On cherche le tout dont 4/9 vaut 200 F."),
    fb("EX004","hard","Les 5/8 de la distance = 250 m. La fraction connue est ___, la valeur est ___.","5/8, 250 m",
        "La fraction est 5/8, la valeur est 250 m."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-RETROUVER-TOUT::MS02","exercises":[
    gs("EX001","hard","Les 3/5 d'un nombre valent 60. Retrouve 1/5.",
        [{"instruction":"3/5 = 60, donc 1/5 = 60 ÷ 3","expected":"20"}],
        "20","1/5 = 60 ÷ 3 = 20."),
    ni("EX002","hard","Les 2/7 d'un poids = 140 g. 1/7 = ?",70,"140 ÷ 2 = 70 g."),
    ni("EX003","hard","Les 4/9 d'un prix = 360 F. 1/9 = ?",90,"360 ÷ 4 = 90 F."),
    gs("EX004","hard","Les 5/6 d'un trajet = 250 km. Retrouve 1/6.",
        [{"instruction":"5/6 = 250, donc 1/6 = 250 ÷ 5","expected":"50"}],
        "50 km","250 ÷ 5 = 50 km."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-RETROUVER-TOUT::MS03","exercises":[
    gs("EX001","hard","Les 3/5 d'un nombre valent 60. Retrouve le tout.",
        [{"instruction":"1/5 = 60 ÷ 3 = 20","expected":"20"},
         {"instruction":"Le tout = 5/5 = 20 × 5","expected":"100"}],
        "100","1/5=20, le tout=20×5=100."),
    ni("EX002","hard","Les 2/7 = 140. Le tout = ?",490,"1/7=70, tout=70×7=490."),
    cp("EX003","hard","Akouavi a dépensé les 3/4 de son argent, soit 450 F. Combien avait-elle au départ ?",
        [{"text":"1/4 = ?","answer":"450÷3=150"},
         {"text":"Le tout (4/4) = ?","answer":"150×4=600"}],
        "600 F","1/4=150, tout=600 F."),
    ni("EX004","hard","Les 5/8 d'une récolte = 200 kg. Récolte totale = ?",320,"1/8=40, tout=40×8=320 kg."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-RETROUVER-TOUT::MS04","exercises":[
    gs("EX001","hard","Vérifie : si le tout = 100 et la fraction est 3/5, alors 3/5 de 100 = 60.",
        [{"instruction":"Calcule 3/5 de 100","expected":"100÷5=20, 20×3=60"},
         {"instruction":"Compare avec la valeur donnée","expected":"60 = 60 ✓"}],
        "Vérifié : 3/5 de 100 = 60 ✓","On vérifie en recalculant la fraction du tout trouvé."),
    ec("EX002","hard","Un élève trouve le tout = 80 pour 2/5 = 40. Vérifie.",
        "Le tout = 80","2/5 de 80 = 32 ≠ 40. Le tout est faux.","2/5 de 80 = 32, pas 40. Le vrai tout = 100 (40÷2×5)."),
    sa("EX003","hard","Comment vérifier le tout quand on connaît k/n = valeur ?","Calculer k/n du tout trouvé et vérifier qu'on obtient la valeur",
        "On recalcule la fraction du résultat pour vérifier.",acc=["recalculer","vérifier","k/n du tout"]),
    ec("EX004","hard","3/4 d'un prix = 150 F. Un élève dit le tout = 400 F. Vrai ?",
        "Tout = 400","3/4 de 400 = 300 ≠ 150. Le tout = 200 F.","3/4 de 200 = 150 ✓. Le tout est 200 F."),
]})
blocks.append({"micro_skill_external_id":"OPS-FRAC-RETROUVER-TOUT::MS05","exercises":[
    ec("EX001","hard","Les 3/5 = 60. L'élève calcule : 60 ÷ 5 = 12, tout = 12 × 3 = 36.",
        "60÷5×3=36","60÷3×5=100","L'élève a divisé par le dénominateur (5) au lieu du numérateur (3). Correct : 60÷3=20, 20×5=100."),
    mcq("EX002","hard","Erreur typique : diviser par n au lieu de k dans k/n = valeur. Si 2/7 = 140, l'élève fait :",
        ["140÷7=20, tout=20×2=40","140÷2=70, tout=70×7=490","140×2÷7=40","140+7=147"],
        "140÷7=20, tout=20×2=40","L'erreur est d'inverser les rôles de k et n. Correct : 140÷2=70, 70×7=490."),
    ec("EX003","hard","4/5 = 80. L'élève confond part et tout : il dit le tout = 80.","Tout=80",
        "Tout=100","80 est la PARTIE (4/5), pas le tout. 1/5=20, tout=100."),
    sa("EX004","hard","Quelles sont les deux erreurs courantes pour retrouver le tout à partir de k/n ?",
        "1) Diviser par n au lieu de k. 2) Confondre la partie et le tout.",
        "Erreurs : inverser k et n dans la division, confondre la partie avec le tout.",
        acc=["diviser par n","confondre partie et tout","inverser"]),
]})

# OPS-PB-MULTI (6 MS)
blocks.append({"micro_skill_external_id":"OPS-PB-MULTI::MS01","exercises":[
    mcq("EX001","medium","Dans le problème « Kofi achète 3 cahiers à 250 F et 2 stylos à 150 F. Combien dépense-t-il ? », les données sont :",
        ["3 cahiers, 250 F/cahier, 2 stylos, 150 F/stylo","Seulement 3 et 2","Le total","Kofi"],
        "3 cahiers, 250 F/cahier, 2 stylos, 150 F/stylo","Les données numériques utiles sont les quantités et les prix."),
    sa("EX002","medium","Quel est la question posée dans : « Un jardin fait 15 m de long et 8 m de large. Quelle est son aire ? » ?",
        "Quelle est l'aire du jardin","On cherche l'aire du rectangle.",acc=["aire","aire du jardin","quelle est son aire"]),
    gs("EX003","hard","Identifie les données et la question : « Moussa parcourt 2,5 km en 30 min. Quelle est sa vitesse en km/h ? »",
        [{"instruction":"Données","expected":"2,5 km, 30 min"},
         {"instruction":"Question","expected":"Vitesse en km/h"},
         {"instruction":"Unités","expected":"km et min → km/h"}],
        "Données : 2,5 km, 30 min. Question : vitesse en km/h.","Il faut repérer les nombres, les unités et ce qu'on cherche."),
    mcq("EX004","medium","La question « Combien reste-t-il ? » demande :",
        ["Une soustraction","Une addition","Une multiplication","Une division"],
        "Une soustraction","« Reste » indique une soustraction."),
]})
blocks.append({"micro_skill_external_id":"OPS-PB-MULTI::MS02","exercises":[
    gs("EX001","hard","Organise : « Un marchand achète 50 mangues à 100 F pièce. Il en vend 35 à 150 F. Quel est son bénéfice ? »",
        [{"instruction":"Coût d'achat : 50 × 100 F","expected":"5 000 F"},
         {"instruction":"Recette de vente : 35 × 150 F","expected":"5 250 F"},
         {"instruction":"Bénéfice = recette - coût","expected":"250 F"}],
        "250 F","On organise : achat, vente, puis bénéfice."),
    mcq("EX002","hard","Pour organiser un problème à étapes, il est utile de :",
        ["Faire un schéma ou un tableau","Deviner la réponse","Lire une seule fois","Copier l'énoncé"],
        "Faire un schéma ou un tableau","Un tableau ou schéma aide à structurer les informations."),
    fb("EX003","hard","Pour le problème : « 4 amis partagent 2 400 F. Chacun en dépense 1/3. Combien reste-t-il à chacun ? » — Nombre d'étapes : ___","2",
        "Étape 1 : part de chacun = 2400÷4=600. Étape 2 : reste = 600 - 600÷3 = 400."),
    sa("EX004","medium","Quel outil utilises-tu pour organiser les données d'un problème ?",
        "Un tableau ou un schéma","Un tableau ou un schéma permet de structurer les données.",acc=["tableau","schéma","dessin"]),
]})
blocks.append({"micro_skill_external_id":"OPS-PB-MULTI::MS03","exercises":[
    mcq("EX001","hard","Kofi a 5 000 F. Il achète 3 livres à 1 200 F chacun. Combien lui reste-t-il ? Opérations :",
        ["Multiplication puis soustraction","Addition puis multiplication","Soustraction puis division","Addition seule"],
        "Multiplication puis soustraction","3 × 1 200 = 3 600, puis 5 000 - 3 600 = 1 400 F."),
    sa("EX002","hard","Un rectangle a un périmètre de 50 cm et une longueur de 15 cm. Quelle opération pour trouver la largeur ?",
        "Soustraction puis division","P = 2(L+l), donc l = (50-2×15)/2 = 10 cm.",acc=["soustraction","soustraction et division"]),
    gs("EX003","hard","Quelles opérations pour : « 240 billes partagées en 6 sacs. On retire 5 billes de chaque sac. Combien dans chaque sac ? »",
        [{"instruction":"Opération 1 : 240 ÷ 6","expected":"Division"},
         {"instruction":"Opération 2 : résultat - 5","expected":"Soustraction"}],
        "Division puis soustraction","240÷6=40, 40-5=35 billes."),
    mcq("EX004","hard","Pour un prix TTC (prix HT + 10% de taxe), on utilise :",
        ["Multiplication puis addition","Division seule","Soustraction","Aucune de ces réponses"],
        "Multiplication puis addition","Taxe = prix × 10/100, puis TTC = prix + taxe."),
]})
blocks.append({"micro_skill_external_id":"OPS-PB-MULTI::MS04","exercises":[
    cp("EX001","hard","Un terrain rectangulaire fait 45 m de long et 30 m de large. On veut le clôturer (prix : 250 F/m) et semer du gazon (150 F/m²).",
        [{"text":"Périmètre ?","answer":"2×(45+30) = 150 m"},
         {"text":"Coût clôture ?","answer":"150 × 250 = 37 500 F"},
         {"text":"Aire ?","answer":"45 × 30 = 1 350 m²"},
         {"text":"Coût gazon ?","answer":"1 350 × 150 = 202 500 F"}],
        "Clôture : 37 500 F, gazon : 202 500 F, total : 240 000 F","Périmètre pour la clôture, aire pour le gazon."),
    ni("EX002","hard","Adjo achète 4 kg de riz à 350 F/kg et 2 kg de sucre à 500 F/kg. Combien dépense-t-elle ?",
        2400,"4×350=1400, 2×500=1000, total=2400 F."),
    gs("EX003","hard","Un bus transporte 45 élèves. Au 1er arrêt, 12 descendent et 8 montent. Au 2e arrêt, 15 descendent.",
        [{"instruction":"Après 1er arrêt : 45-12+8","expected":"41"},
         {"instruction":"Après 2e arrêt : 41-15","expected":"26"}],
        "26 élèves","45-12+8=41, 41-15=26."),
    ni("EX004","hard","Prix total : 3 stylos à 75 F + 5 cahiers à 200 F + 1 sac à 2 500 F.",
        3725,"3×75=225, 5×200=1000, 1×2500=2500. Total=3725 F."),
]})
blocks.append({"micro_skill_external_id":"OPS-PB-MULTI::MS05","exercises":[
    sa("EX001","hard","Le résultat du problème est 35 billes. Rédige une réponse complète.",
        "Il reste 35 billes dans chaque sac.","La réponse doit être une phrase avec l'unité.",
        acc=["35 billes","Il reste 35 billes"]),
    mcq("EX002","hard","Une bonne réponse à un problème de maths contient :",
        ["Une phrase, le nombre et l'unité","Juste le nombre","Juste le calcul","Le dessin"],
        "Une phrase, le nombre et l'unité","La réponse est une phrase complète avec l'unité."),
    ec("EX003","hard","Un élève répond « 150 » au lieu de « Il reste 150 F à Kofi ».",
        "150","Il reste 150 F à Kofi.","La réponse doit être une phrase avec l'unité et le contexte."),
    gs("EX004","hard","Rédige la réponse : « L'aire du terrain est de 1 350 m². »",
        [{"instruction":"Commence par une phrase de réponse","expected":"L'aire du terrain est de..."},
         {"instruction":"Indique le nombre","expected":"1 350"},
         {"instruction":"Ajoute l'unité","expected":"m²"}],
        "L'aire du terrain est de 1 350 m².","Phrase + nombre + unité."),
]})
blocks.append({"micro_skill_external_id":"OPS-PB-MULTI::MS06","exercises":[
    ec("EX001","hard","Un élève trouve que 3 cahiers à 200 F coûtent 900 F.",
        "3×200=900","3×200=600","3 × 200 = 600, pas 900. L'élève a multiplié par un mauvais nombre."),
    gs("EX002","hard","Vérifie : périmètre d'un rectangle 12×8 = 32 cm.",
        [{"instruction":"Calcule 2×(12+8)","expected":"2×20=40"},
         {"instruction":"Compare avec 32","expected":"40 ≠ 32, erreur !"}],
        "Le périmètre est 40 cm, pas 32.","2×(12+8) = 40."),
    sa("EX003","hard","Comment vérifier la réponse d'un problème ?","Refaire le calcul ou utiliser l'opération inverse",
        "On peut refaire le calcul ou vérifier par l'opération inverse.",
        acc=["refaire","opération inverse","vérifier"]),
    mcq("EX004","hard","Un résultat est vraisemblable si :",
        ["Il est cohérent avec les données et l'ordre de grandeur","Il est un nombre rond","Il est positif","Il est inférieur à 100"],
        "Il est cohérent avec les données et l'ordre de grandeur","La vraisemblance = cohérence avec les données."),
]})

# Load part 1 and merge
with open("_ops_part1.json") as f:
    part1 = json.load(f)

all_blocks = part1 + blocks

payload = {
    "schema_version": "1.0",
    "metadata": {"domain": "Opérations", "grade": "CM2", "country": "Bénin", "generated": True},
    "exercises": all_blocks,
}
total = sum(len(b["exercises"]) for b in all_blocks)
out = "backend/exercices_cm2_operations.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

import os
os.remove("_ops_part1.json")
print(f"✓ {out}: {len(all_blocks)} blocs, {total} exercices")
