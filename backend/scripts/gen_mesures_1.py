"""Generate exercises for Grandeurs et Mesures — Part 1 (first 7 skills, 30 MS)."""
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
def order(eid,d,t,items,a,ex,h=""): return B(eid,"ordering",d,t,items=items,correct_answer=a,explanation=ex,hint=h)
def ec(eid,d,t,err,a,ex,h=""): return B(eid,"error_correction",d,t,erroneous_content=err,correct_answer=a,explanation=ex,hint=h)
def gs(eid,d,t,steps,a,ex,h=""): return B(eid,"guided_steps",d,t,steps=steps,correct_answer=a,explanation=ex,hint=h)
def cp(eid,d,t,sq,a,ex,h=""): return B(eid,"contextual_problem",d,t,sub_questions=sq,correct_answer=a,explanation=ex,hint=h)

blocks = []

# MES-LONGUEURS (3 MS)
blocks.append({"micro_skill_external_id":"MES-LONGUEURS::MS01","exercises":[
    ni("EX001","easy","Convertis 3,5 m en cm.",350,"3,5 m = 350 cm (×100)."),
    fb("EX002","medium","4,2 km = ___ m.","4 200","4,2 × 1 000 = 4 200 m."),
    ni("EX003","medium","850 mm = ___ cm.",85,"850 ÷ 10 = 85 cm."),
    ni("EX004","hard","2 750 m = ___ km.",2.75,"2 750 ÷ 1 000 = 2,75 km.",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"MES-LONGUEURS::MS02","exercises":[
    mcq("EX001","easy","Pour mesurer la longueur d'une salle de classe, on utilise :",["Le mètre","Le kilomètre","Le millimètre","Le centimètre"],"Le mètre","Une salle mesure quelques mètres."),
    mcq("EX002","easy","La distance Cotonou-Parakou s'exprime en :",["km","cm","mm","dm"],"km","Les grandes distances s'expriment en km."),
    sa("EX003","medium","Quelle unité convient pour la longueur d'un crayon ?","cm",
        "Un crayon mesure environ 15-20 cm.",acc=["cm","centimètre","centimètres"]),
    mcq("EX004","medium","L'épaisseur d'une pièce de monnaie se mesure en :",["mm","m","km","dm"],"mm","Environ 1-2 mm."),
]})
blocks.append({"micro_skill_external_id":"MES-LONGUEURS::MS03","exercises":[
    ec("EX001","medium","Un élève convertit 5 m en mm et obtient 500.","5 m = 500 mm","5 m = 5 000 mm",
        "1 m = 1 000 mm (×1 000, pas ×100)."),
    mcq("EX002","hard","3,2 km = ___ m. Le facteur de conversion est :",["×1 000","×100","×10","÷1 000"],"×1 000","1 km = 1 000 m."),
    ec("EX003","hard","Erreur : 450 cm = 4,5 m.","450 cm = 4,5 m","450 cm = 4,5 m — c'est correct !",
        "450 ÷ 100 = 4,5 m. L'élève a raison cette fois."),
    ec("EX004","hard","Un élève écrit 2,5 km = 250 m.","2,5 km = 250 m","2,5 km = 2 500 m","×1 000 : 2,5 × 1 000 = 2 500 m."),
]})

# MES-CAPACITES (3 MS)
blocks.append({"micro_skill_external_id":"MES-CAPACITES::MS01","exercises":[
    ni("EX001","medium","3,5 L = ___ cL.",350,"3,5 × 100 = 350 cL."),
    fb("EX002","medium","750 mL = ___ L.","0,75","750 ÷ 1 000 = 0,75 L."),
    ni("EX003","medium","2 L 5 dL = ___ dL.",25,"2 L = 20 dL, plus 5 dL = 25 dL."),
    ni("EX004","hard","4 500 mL = ___ L.",4.5,"4 500 ÷ 1 000 = 4,5 L.",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"MES-CAPACITES::MS02","exercises":[
    mcq("EX001","medium","Pour mesurer l'eau d'une piscine, on utilise :",["Les litres (L)","Les millilitres (mL)","Les centilitres (cL)","Les décilitres (dL)"],"Les litres (L)","Les grandes contenances s'expriment en litres."),
    mcq("EX002","medium","La contenance d'une cuillère à soupe est d'environ :",["15 mL","15 L","15 cL","15 dL"],"15 mL","Une cuillère à soupe = environ 15 mL."),
    sa("EX003","medium","Quelle unité pour le contenu d'une canette de soda ?","cL",
        "Une canette contient 33 cL.",acc=["cL","centilitre","centilitres"]),
    mcq("EX004","easy","Une bouteille d'eau contient 1,5 L. C'est la même chose que :",["150 cL","15 cL","1 500 cL","1,5 cL"],"150 cL","1,5 × 100 = 150 cL."),
]})
blocks.append({"micro_skill_external_id":"MES-CAPACITES::MS03","exercises":[
    cp("EX001","hard","Un bidon contient 5 L d'eau. On remplit des verres de 25 cL. Combien de verres peut-on remplir ?",
        [{"text":"Convertis 5 L en cL","answer":"500 cL"},
         {"text":"Divise par 25 cL","answer":"500 ÷ 25 = 20"}],
        "20 verres","5 L = 500 cL, 500 ÷ 25 = 20 verres."),
    gs("EX002","hard","Un réservoir de 20 L est rempli aux 3/4. Combien de litres contient-il ?",
        [{"instruction":"3/4 de 20 L = 20 × 3 ÷ 4","expected":"15 L"}],
        "15 L","3/4 de 20 = 15 L."),
    ni("EX003","hard","On mélange 750 mL de jus et 1,25 L d'eau. Total en L ?",2,
        "750 mL = 0,75 L. 0,75 + 1,25 = 2 L.",tol=0.01),
    cp("EX004","hard","Une bouteille de 1,5 L est partagée en 6 parts. Quelle est la contenance de chaque part en mL ?",
        [{"text":"1,5 L en mL ?","answer":"1 500 mL"},
         {"text":"1 500 ÷ 6 ?","answer":"250 mL"}],
        "250 mL","1 500 ÷ 6 = 250 mL."),
]})

# MES-MASSES (4 MS)
blocks.append({"micro_skill_external_id":"MES-MASSES::MS01","exercises":[
    fb("EX001","easy","3 kg = ___ g.","3 000","1 kg = 1 000 g, donc 3 kg = 3 000 g."),
    ni("EX002","medium","2,5 t = ___ kg.",2500,"2,5 × 1 000 = 2 500 kg."),
    fb("EX003","medium","4 500 g = ___ kg.","4,5","4 500 ÷ 1 000 = 4,5 kg."),
    ni("EX004","easy","750 g = ___ kg.",0.75,"750 ÷ 1 000 = 0,75 kg.",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"MES-MASSES::MS02","exercises":[
    ni("EX001","medium","5 200 g = ___ kg.",5.2,"5 200 ÷ 1 000 = 5,2 kg.",tol=0.01),
    fb("EX002","medium","3,45 kg = ___ g.","3 450","3,45 × 1 000 = 3 450 g."),
    ni("EX003","hard","0,75 t = ___ kg.",750,"0,75 × 1 000 = 750 kg."),
    ni("EX004","hard","6 250 kg = ___ t.",6.25,"6 250 ÷ 1 000 = 6,25 t.",tol=0.01),
]})
blocks.append({"micro_skill_external_id":"MES-MASSES::MS03","exercises":[
    mcq("EX001","easy","La masse d'un éléphant s'exprime en :",["tonnes","grammes","kilogrammes","milligrammes"],"tonnes","Bonne réponse."),
    mcq("EX002","easy","La masse d'une pomme est environ :",["150 g","150 kg","15 g","1,5 kg"],"150 g","Bonne réponse."),
    sa("EX003","medium","Quelle unité convient pour la masse d'un sac de riz ?","kg",
        "Un sac de riz pèse 25-50 kg.",acc=["kg","kilogramme","kilogrammes"]),
    mcq("EX004","medium","La masse d'un camion chargé est d'environ :",["20 t","20 kg","200 g","2 000 g"],"20 t","Bonne réponse."),
]})
blocks.append({"micro_skill_external_id":"MES-MASSES::MS04","exercises":[
    cp("EX001","hard","Un sac de riz pèse 25 kg. Un restaurateur en achète 3 et ajoute 500 g d'épices. Quel est le poids total en kg ?",
        [{"text":"3 sacs = ?","answer":"3 × 25 = 75 kg"},
         {"text":"500 g en kg ?","answer":"0,5 kg"},
         {"text":"Total ?","answer":"75,5 kg"}],
        "75,5 kg","75 + 0,5 = 75,5 kg."),
    gs("EX002","hard","Moussa porte 2 paniers : l'un pèse 3,5 kg, l'autre 4 750 g. Poids total en kg ?",
        [{"instruction":"Convertis 4 750 g en kg","expected":"4,75 kg"},
         {"instruction":"Additionne","expected":"3,5 + 4,75 = 8,25 kg"}],
        "8,25 kg","3,5 + 4,75 = 8,25 kg."),
    ni("EX003","hard","Un colis de 2,3 kg et un colis de 1 750 g. Total en g ?",4050,"2 300 + 1 750 = 4 050 g."),
    ni("EX004","hard","15 sacs de 50 kg = ___ t.",0.75,"15 × 50 = 750 kg = 0,75 t.",tol=0.01),
]})

# MES-AGRAIRES (4 MS)
blocks.append({"micro_skill_external_id":"MES-AGRAIRES::MS01","exercises":[
    fb("EX001","medium","1 ha = ___ m²","10 000","1 hectare = 10 000 m²."),
    fb("EX002","medium","1 a = ___ m²","100","1 are = 100 m²."),
    mcq("EX003","medium","1 ha = ___ a.",["100","10","1 000","10 000"],"100","1 ha = 100 a."),
    tf("EX004","medium","1 ha = 100 a = 10 000 m².",True,"Les deux égalités sont correctes."),
]})
blocks.append({"micro_skill_external_id":"MES-AGRAIRES::MS02","exercises":[
    ni("EX001","medium","3,5 ha = ___ m².",35000,"3,5 × 10 000 = 35 000 m²."),
    fb("EX002","hard","250 a = ___ ha.","2,5","250 ÷ 100 = 2,5 ha."),
    ni("EX003","hard","45 000 m² = ___ ha.",4.5,"45 000 ÷ 10 000 = 4,5 ha.",tol=0.01),
    ni("EX004","hard","1,2 ha = ___ a.",120,"1,2 × 100 = 120 a."),
]})
blocks.append({"micro_skill_external_id":"MES-AGRAIRES::MS03","exercises":[
    order("EX001","hard","Range du plus petit au plus grand : 2 ha, 150 a, 20 000 m², 3 ha.",
        ["150 a","2 ha","20 000 m²","3 ha"],["150 a","2 ha","20 000 m²","3 ha"],
        "150 a = 1,5 ha, 2 ha, 20 000 m² = 2 ha, 3 ha."),
    mcq("EX002","hard","Quelle superficie est la plus grande ?",["2,5 ha","200 a","18 000 m²","2 400 a"],
        "2 400 a","2 400 a = 24 ha, largement plus grand."),
    mcq("EX003","hard","350 a ___ 3 ha.",["350 a > 3 ha","350 a < 3 ha","350 a = 3 ha","On ne peut pas comparer"],
        "350 a > 3 ha","350 a = 3,5 ha > 3 ha."),
    ni("EX004","medium","2 ha + 50 a = ___ a.",250,"200 a + 50 a = 250 a."),
]})
blocks.append({"micro_skill_external_id":"MES-AGRAIRES::MS04","exercises":[
    cp("EX001","hard","Un paysan a un champ de 2,5 ha. Il veut partager en 5 parcelles égales. Quelle est l'aire de chaque parcelle en m² ?",
        [{"text":"2,5 ha en m²","answer":"25 000 m²"},
         {"text":"25 000 ÷ 5","answer":"5 000 m²"}],
        "5 000 m²","2,5 ha = 25 000 m², ÷5 = 5 000 m² par parcelle."),
    gs("EX002","hard","Un terrain rectangulaire fait 200 m × 150 m. Convertis son aire en ha.",
        [{"instruction":"Aire = 200 × 150","expected":"30 000 m²"},
         {"instruction":"Convertis en ha : 30 000 ÷ 10 000","expected":"3 ha"}],
        "3 ha","200 × 150 = 30 000 m² = 3 ha."),
    ni("EX003","hard","Deux parcelles : 1,5 ha et 8 000 m². Aire totale en m² ?",23000,"15 000 + 8 000 = 23 000 m²."),
    cp("EX004","hard","Un village dispose de 10 ha de terres cultivables. Chaque famille reçoit 50 a. Combien de familles sont servies ?",
        [{"text":"10 ha en a","answer":"1 000 a"},
         {"text":"1 000 ÷ 50","answer":"20 familles"}],
        "20 familles","10 ha = 1 000 a, 1 000 ÷ 50 = 20."),
]})

# MES-AIRES-DISQUE-FIG (6 MS)
blocks.append({"micro_skill_external_id":"MES-AIRES-DISQUE-FIG::MS01","exercises":[
    mcq("EX001","medium","Le périmètre se mesure en :",["cm, m, km","cm², m²","cm³, m³","L, mL"],"cm, m, km",
        "Le périmètre est une longueur, donc unités de longueur."),
    mcq("EX002","medium","L'aire se mesure en :",["cm², m²","cm, m","L","kg"],"cm², m²","L'aire est une surface, unités carrées."),
    order("EX003","easy","Range : périmètre, aire, volume — du plus simple au plus complexe.",
        ["Périmètre (1D)","Aire (2D)","Volume (3D)"],["Périmètre (1D)","Aire (2D)","Volume (3D)"],
        "1D → 2D → 3D."),
    tf("EX004","medium","Le périmètre d'un carré de 5 cm est 25 cm².",False,
        "Le périmètre = 4 × 5 = 20 cm (pas cm²). 25 cm² serait l'aire."),
]})
blocks.append({"micro_skill_external_id":"MES-AIRES-DISQUE-FIG::MS02","exercises":[
    ni("EX001","hard","Calcule le périmètre d'un cercle de rayon 7 cm. (π ≈ 3,14)",43.96,
        "P = 2 × π × r = 2 × 3,14 × 7 = 43,96 cm.",tol=0.1),
    ni("EX002","hard","Calcule l'aire d'un disque de rayon 5 cm. (π ≈ 3,14)",78.5,
        "A = π × r² = 3,14 × 25 = 78,5 cm².",tol=0.5),
    gs("EX003","hard","Un cercle a un diamètre de 10 cm. Calcule son aire.",
        [{"instruction":"r = D/2 = 10/2 = 5 cm","expected":"5 cm"},
         {"instruction":"A = π × r² = 3,14 × 25","expected":"78,5 cm²"}],
        "78,5 cm²","r = 5 cm, A = 3,14 × 25 = 78,5 cm²."),
    ec("EX004","hard","Un élève calcule l'aire avec A = π × D² et obtient 314 cm² pour D = 10 cm.",
        "π × D² = 314","A = π × r² = π × 5² = 78,5 cm²","Il faut utiliser le rayon, pas le diamètre. A = π × r²."),
]})
blocks.append({"micro_skill_external_id":"MES-AIRES-DISQUE-FIG::MS03","exercises":[
    gs("EX001","hard","Calcule l'aire d'un demi-cercle de rayon 6 cm.",
        [{"instruction":"Aire du disque entier = π × 6²","expected":"3,14 × 36 = 113,04 cm²"},
         {"instruction":"Demi-cercle = moitié","expected":"113,04 ÷ 2 = 56,52 cm²"}],
        "56,52 cm²","A = π × r² / 2 = 3,14 × 36 / 2 = 56,52 cm²."),
    ni("EX002","hard","Aire d'un demi-disque de rayon 10 cm ? (π ≈ 3,14)",157,
        "π × 100 / 2 = 157 cm².",tol=1),
    ni("EX003","hard","Demi-cercle de diamètre 8 cm. Aire ?",25.12,
        "r = 4 cm. A = π × 16 / 2 = 25,12 cm².",tol=0.5),
    mcq("EX004","hard","L'aire d'un demi-cercle de rayon r est :",
        ["π×r²/2","π×r²","2×π×r","π×r/2"],"π×r²/2","On divise l'aire du disque par 2."),
]})
blocks.append({"micro_skill_external_id":"MES-AIRES-DISQUE-FIG::MS04","exercises":[
    gs("EX001","hard","Un terrain a la forme d'un rectangle (10 m × 6 m) avec un demi-cercle à un bout (diamètre 6 m). Aire totale ?",
        [{"instruction":"Aire rectangle = 10 × 6","expected":"60 m²"},
         {"instruction":"Rayon demi-cercle = 3 m. Aire = π×9/2","expected":"14,13 m²"},
         {"instruction":"Total","expected":"74,13 m²"}],
        "74,13 m²","60 + 14,13 = 74,13 m²."),
    mcq("EX002","hard","Pour calculer l'aire d'une figure en L, on peut :",
        ["La découper en 2 rectangles et additionner les aires","Multiplier longueur × largeur seulement",
         "Utiliser la formule du cercle","Mesurer le périmètre"],
        "La découper en 2 rectangles et additionner les aires","On décompose en figures simples."),
    gs("EX003","hard","Aire d'une figure : rectangle 8×5 avec un triangle rectangle (base 3, hauteur 5) collé.",
        [{"instruction":"Aire rectangle = 8 × 5","expected":"40"},
         {"instruction":"Aire triangle = 3 × 5 / 2","expected":"7,5"},
         {"instruction":"Total","expected":"47,5"}],
        "47,5 cm²","40 + 7,5 = 47,5 cm²."),
    tf("EX004","hard","Pour une figure composée, on additionne les aires des figures simples qui la composent.",True,
        "On décompose puis on additionne les aires partielles."),
]})
blocks.append({"micro_skill_external_id":"MES-AIRES-DISQUE-FIG::MS05","exercises":[
    ni("EX001","hard","Rectangle 12×8 avec un carré 3×3 retiré. Aire ?",87,
        "12×8 = 96, 3×3 = 9, 96-9 = 87."),
    gs("EX002","hard","Un jardin carré de 10 m a une allée de 2 m de large tout autour. Aire du jardin seul ?",
        [{"instruction":"Côté jardin = 10 - 2×2 = 6 m","expected":"6 m"},
         {"instruction":"Aire = 6 × 6","expected":"36 m²"}],
        "36 m²","Le jardin intérieur mesure 6×6 = 36 m²."),
    ec("EX003","hard","Un élève calcule l'aire d'un L (6×4 + 3×2) et obtient 30 car il a compté la zone 3×2 deux fois.",
        "Aire = 30","Aire = 24 + 6 = 30, mais vérifier qu'il n'y a pas de double comptage",
        "Si les deux rectangles se chevauchent, il faut soustraire la zone commune."),
    ni("EX004","hard","Deux rectangles 5×3 et 4×3 qui partagent un carré 3×3. Aire totale ?",18,
        "15 + 12 - 9 = 18."),
]})
blocks.append({"micro_skill_external_id":"MES-AIRES-DISQUE-FIG::MS06","exercises":[
    ec("EX001","hard","Un élève calcule une aire de 500 cm² pour un terrain de 5 m × 10 m.",
        "500 cm²","50 m²","5 × 10 = 50. L'unité est m², pas cm²."),
    mcq("EX002","hard","10 000 cm² = ___ m².",["1","100","10","0,01"],"1","1 m² = 10 000 cm²."),
    ec("EX003","hard","Aire d'un cercle de rayon 3 m : « 28,26 cm² ».",
        "28,26 cm²","28,26 m²","L'aire est en m² puisque le rayon est en m."),
    tf("EX004","hard","1 m² = 100 cm².",False,"1 m² = 10 000 cm² (100 × 100)."),
]})

# Save part 1
with open("_mes_part1.json","w") as f:
    json.dump(blocks, f, ensure_ascii=False)
print(f"Mesures Part 1: {len(blocks)} blocks, {sum(len(b['exercises']) for b in blocks)} exercises")
