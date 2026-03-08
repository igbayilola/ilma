"""Generate exercises for Grandeurs et Mesures — Part 2 (remaining 25 MS)."""
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

# MES-VOL-PAVE-CUBE (6 MS)
blocks.append({"micro_skill_external_id":"MES-VOL-PAVE-CUBE::MS01","exercises":[
    mcq("EX001","easy","Un solide avec 6 faces rectangulaires est :",["Un pavé droit","Un cylindre","Une pyramide","Un cône"],"Un pavé droit","Le pavé droit a 6 faces rectangulaires."),
    order("EX002","easy","Classe ces solides : cube, pavé droit, cylindre, pyramide.",
        ["Cube","Pavé droit","Cylindre","Pyramide"],["Cube","Pavé droit","Cylindre","Pyramide"],"Quatre solides usuels."),
    tf("EX003","easy","Le cube est un cas particulier du pavé droit.",True,"Le cube est un pavé droit avec toutes les arêtes égales."),
    mcq("EX004","medium","Combien d'arêtes possède un pavé droit ?",["12","8","6","10"],"12","Un pavé droit a 12 arêtes, 8 sommets et 6 faces."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-PAVE-CUBE::MS02","exercises":[
    ni("EX001","medium","Volume d'un pavé droit : L=5 cm, l=3 cm, h=4 cm. V=?",60,"V = 5×3×4 = 60 cm³."),
    ni("EX002","medium","Volume d'un cube de 3 cm de côté ?",27,"V = 3³ = 27 cm³."),
    gs("EX003","hard","Calcule le volume d'un pavé droit de 12 cm × 8 cm × 5 cm.",
        [{"instruction":"V = L × l × h = 12 × 8 × 5","expected":"480 cm³"}],
        "480 cm³","12 × 8 × 5 = 480 cm³."),
    ni("EX004","hard","Volume d'un cube de 10 cm de côté ?",1000,"V = 10³ = 1 000 cm³."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-PAVE-CUBE::MS03","exercises":[
    mcq("EX001","medium","Dans un pavé droit, L, l et h représentent :",
        ["Longueur, largeur et hauteur","Longueur, largeur et luminosité","Trois longueurs identiques","Le périmètre"],
        "Longueur, largeur et hauteur","L=longueur, l=largeur, h=hauteur."),
    fb("EX002","medium","Un aquarium a : L=60 cm, l=___ cm, h=40 cm. On sait qu'il est vu de face : 60 cm de long et 30 cm de profondeur.","30",
        "La largeur (profondeur) est 30 cm."),
    mcq("EX003","medium","Sur un schéma de pavé droit, la hauteur est :",
        ["La dimension verticale","La plus grande dimension","Toujours 10 cm","Le périmètre"],
        "La dimension verticale","La hauteur est la dimension verticale."),
    tf("EX004","easy","Pour un cube, L = l = h.",True,"Toutes les arêtes d'un cube sont égales."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-PAVE-CUBE::MS04","exercises":[
    fb("EX001","medium","Les unités de volume sont : m³, ___ et cm³.","dm³","m³, dm³, cm³ sont les unités de volume."),
    mcq("EX002","medium","L'unité de volume la plus courante au CM2 est :",["cm³","m³","km³","mm³"],"cm³","Le cm³ est l'unité de base."),
    tf("EX003","medium","Le volume se mesure en cm² (centimètres carrés).",False,"Le volume se mesure en cm³ (centimètres cubes). cm² est pour les aires."),
    mcq("EX004","medium","1 m³ = ___ dm³.",["1 000","100","10","10 000"],"1 000","1 m³ = 1 000 dm³."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-PAVE-CUBE::MS05","exercises":[
    ni("EX001","hard","5 m³ = ___ dm³.",5000,"5 × 1 000 = 5 000 dm³."),
    ni("EX002","hard","3 500 cm³ = ___ dm³.",3.5,"3 500 ÷ 1 000 = 3,5 dm³.",tol=0.01),
    fb("EX003","hard","2,4 dm³ = ___ cm³.","2 400","2,4 × 1 000 = 2 400 cm³."),
    ni("EX004","hard","0,5 m³ = ___ cm³.",500000,"0,5 × 1 000 000 = 500 000 cm³."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-PAVE-CUBE::MS06","exercises":[
    ec("EX001","hard","Un élève calcule V = 5 m × 3 m × 2 m = 30 cm³.",
        "30 cm³","30 m³","Les dimensions sont en mètres, donc le volume est en m³, pas cm³."),
    mcq("EX002","hard","Un pavé de 10 cm × 5 cm × 2 cm a un volume de 100. L'unité est :",
        ["cm³","cm²","cm","m³"],"cm³","Les dimensions sont en cm, le volume est en cm³."),
    ec("EX003","hard","Volume = 4 m × 300 cm × 2 m. L'élève écrit V = 2 400 m³.",
        "2 400 m³","2,4 m³","300 cm = 3 m. V = 4×3×2 = 24 m³. (ou convertir tout en cm et obtenir 24 000 000 cm³)"),
    tf("EX004","hard","Si les dimensions sont en cm, le volume est automatiquement en cm³.",True,"Les unités sont cohérentes : cm × cm × cm = cm³."),
]})

# MES-VOL-CAP (4 MS)
blocks.append({"micro_skill_external_id":"MES-VOL-CAP::MS01","exercises":[
    tf("EX001","medium","1 litre = 1 dm³.",True,"C'est l'équivalence fondamentale volume/capacité."),
    fb("EX002","medium","1 L = 1 ___","dm³","1 litre correspond exactement à 1 décimètre cube."),
    mcq("EX003","medium","Un aquarium cubique de 1 dm d'arête contient :",["1 L","10 L","100 mL","1 mL"],"1 L","1 dm³ = 1 L."),
    ni("EX004","medium","5 L = ___ dm³.",5,"5 L = 5 dm³."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-CAP::MS02","exercises":[
    tf("EX001","medium","1 mL = 1 cm³.",True,"1 millilitre correspond à 1 centimètre cube."),
    fb("EX002","medium","1 cm³ = 1 ___","mL","1 cm³ = 1 millilitre."),
    mcq("EX003","medium","Un cube de 1 cm d'arête a un volume de 1 cm³ = :",["1 mL","1 L","1 dL","1 cL"],"1 mL","1 cm³ = 1 mL."),
    ni("EX004","medium","250 cm³ = ___ mL.",250,"250 cm³ = 250 mL."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-CAP::MS03","exercises":[
    ni("EX001","hard","3,5 L = ___ dm³.",3.5,"3,5 L = 3,5 dm³.",tol=0.01),
    ni("EX002","hard","500 mL = ___ cm³.",500,"500 mL = 500 cm³."),
    fb("EX003","hard","2 500 cm³ = ___ L.","2,5","2 500 cm³ = 2 500 mL = 2,5 L."),
    ni("EX004","hard","0,75 L = ___ cm³.",750,"0,75 L = 750 mL = 750 cm³."),
]})
blocks.append({"micro_skill_external_id":"MES-VOL-CAP::MS04","exercises":[
    cp("EX001","hard","Un aquarium mesure 40 cm × 25 cm × 30 cm. Quelle est sa contenance en litres ?",
        [{"text":"Volume en cm³ ?","answer":"40×25×30 = 30 000 cm³"},
         {"text":"En mL ?","answer":"30 000 mL"},
         {"text":"En L ?","answer":"30 L"}],
        "30 L","30 000 cm³ = 30 000 mL = 30 L."),
    gs("EX002","hard","Un bac cubique a 2 dm d'arête. Quelle est sa contenance ?",
        [{"instruction":"V = 2³ = 8 dm³","expected":"8 dm³"},
         {"instruction":"8 dm³ = 8 L","expected":"8 L"}],
        "8 L","2³ = 8 dm³ = 8 L."),
    ni("EX003","hard","Un seau de 15 L peut contenir combien de dm³ ?",15,"15 L = 15 dm³."),
    cp("EX004","hard","Un récipient cylindrique a un volume de 5 000 cm³. Combien de bouteilles de 0,5 L peut-on remplir ?",
        [{"text":"5 000 cm³ en L ?","answer":"5 L"},
         {"text":"5 ÷ 0,5 ?","answer":"10 bouteilles"}],
        "10 bouteilles","5 000 cm³ = 5 L. 5 ÷ 0,5 = 10."),
]})

# MES-CYL-PATRON (5 MS)
blocks.append({"micro_skill_external_id":"MES-CYL-PATRON::MS01","exercises":[
    mcq("EX001","easy","Un cylindre droit possède :",["2 bases circulaires et une surface latérale","1 base carrée","6 faces","Aucune base"],
        "2 bases circulaires et une surface latérale","Le cylindre a 2 disques (bases) et un rectangle enroulé."),
    order("EX002","easy","Classe : cube, cylindre, cône, sphère.",
        ["Cube","Cylindre","Cône","Sphère"],["Cube","Cylindre","Cône","Sphère"],"Solides de base."),
    tf("EX003","easy","Un cylindre droit a des bases circulaires.",True,"Les bases d'un cylindre droit sont des cercles identiques."),
    mcq("EX004","medium","Combien de faces a un cylindre droit ?",["3 (2 disques + 1 surface latérale)","2","6","4"],
        "3 (2 disques + 1 surface latérale)","2 bases + 1 surface courbe = 3 faces."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-PATRON::MS02","exercises":[
    mcq("EX001","medium","Le patron d'un cylindre est composé de :",
        ["2 disques et 1 rectangle","2 carrés et 1 rectangle","1 disque et 1 triangle","3 rectangles"],
        "2 disques et 1 rectangle","Le patron = 2 disques (bases) + 1 rectangle (surface latérale)."),
    fb("EX002","medium","Le patron du cylindre contient ___ disque(s) et ___ rectangle(s).","2, 1",
        "2 disques pour les bases + 1 rectangle pour la surface latérale."),
    tf("EX003","medium","La largeur du rectangle du patron correspond à la hauteur du cylindre.",True,
        "La largeur (ou hauteur) du rectangle = hauteur h du cylindre."),
    mcq("EX004","medium","Les 2 disques du patron sont :",["Identiques (même rayon)","De tailles différentes","Optionnels","Des carrés"],
        "Identiques (même rayon)","Les 2 bases ont le même rayon."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-PATRON::MS03","exercises":[
    gs("EX001","hard","Dessine le patron d'un cylindre de rayon 3 cm et hauteur 8 cm.",
        [{"instruction":"Trace 2 cercles de rayon 3 cm","expected":"2 disques de rayon 3 cm"},
         {"instruction":"Calcule la longueur du rectangle : 2×π×3 ≈ 18,84 cm","expected":"18,84 cm"},
         {"instruction":"Trace un rectangle de 18,84 cm × 8 cm","expected":"Rectangle tracé"}],
        "Patron : 2 disques r=3 + rectangle 18,84×8","Le patron se compose de 2 cercles et d'un rectangle."),
    ni("EX002","hard","Longueur du rectangle du patron pour un cylindre de rayon 5 cm ?",31.4,
        "L = 2×π×r = 2×3,14×5 = 31,4 cm.",tol=0.1),
    ni("EX003","hard","Largeur du rectangle du patron pour un cylindre de hauteur 12 cm ?",12,
        "La largeur du rectangle = la hauteur du cylindre = 12 cm."),
    gs("EX004","hard","Cylindre de diamètre 4 cm et hauteur 10 cm. Dimensions du rectangle du patron ?",
        [{"instruction":"r = D/2 = 2 cm","expected":"2 cm"},
         {"instruction":"L = 2×π×2 = 12,56 cm","expected":"12,56 cm"},
         {"instruction":"Largeur = h = 10 cm","expected":"10 cm"}],
        "Rectangle 12,56 cm × 10 cm","L = 2πr = 12,56 cm, largeur = 10 cm."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-PATRON::MS04","exercises":[
    ni("EX001","hard","Un cylindre de rayon 4 cm. La longueur du rectangle du patron = 2×π×r =",25.12,
        "2 × 3,14 × 4 = 25,12 cm.",tol=0.1),
    gs("EX002","hard","Montre que la longueur du rectangle = la circonférence de la base.",
        [{"instruction":"Quand on « déroule » la surface latérale, elle forme un rectangle","expected":"Rectangle déroulé"},
         {"instruction":"La longueur correspond au tour complet de la base = 2πr","expected":"L = 2πr"}],
        "L = 2πr = circonférence de la base","Le rectangle déroulé a pour longueur la circonférence."),
    ni("EX003","hard","Pour un cylindre de rayon 7 cm, L du rectangle =",43.96,"2×3,14×7 = 43,96 cm.",tol=0.1),
    mcq("EX004","hard","Si la longueur du rectangle du patron est 31,4 cm, le rayon du cylindre est :",
        ["5 cm","10 cm","15,7 cm","31,4 cm"],"5 cm","r = L/(2π) = 31,4/6,28 = 5 cm."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-PATRON::MS05","exercises":[
    ec("EX001","hard","Un élève dessine un patron avec un rectangle de 20 cm mais les disques ont un rayon de 5 cm (C=31,4 cm).",
        "Rectangle 20 cm et disques r=5","Rectangle 31,4 cm et disques r=5",
        "La longueur du rectangle doit être 2πr = 31,4 cm, pas 20 cm."),
    mcq("EX002","hard","Pour vérifier un patron, la longueur du rectangle doit être égale à :",
        ["2 × π × rayon du disque","Le diamètre","La hauteur","Le rayon"],
        "2 × π × rayon du disque","L = 2πr doit correspondre aux disques."),
    ec("EX003","hard","Un patron a des disques de rayon 3 cm et un rectangle de 19 cm × 10 cm.",
        "Rectangle 19 cm","Rectangle 18,84 cm (≈18,85)","2×3,14×3 = 18,84. Le rectangle est légèrement trop long."),
    tf("EX004","hard","Sur un patron correct, la longueur du rectangle = 2 × π × rayon des disques.",True,
        "C'est la condition de cohérence du patron du cylindre."),
]})

# MES-CYL-VOL-AIRES (6 MS)
blocks.append({"micro_skill_external_id":"MES-CYL-VOL-AIRES::MS01","exercises":[
    gs("EX001","hard","Calcule le volume d'un cylindre de rayon 3 cm et hauteur 10 cm.",
        [{"instruction":"Aire de base = π×r² = 3,14×9","expected":"28,26 cm²"},
         {"instruction":"V = aire × h = 28,26×10","expected":"282,6 cm³"}],
        "282,6 cm³","V = π×r²×h = 3,14×9×10 = 282,6 cm³."),
    ni("EX002","hard","Volume d'un cylindre : r=5 cm, h=8 cm ?",628,"3,14×25×8 = 628 cm³.",tol=1),
    ni("EX003","hard","Volume : r=7 cm, h=10 cm ?",1538.6,"3,14×49×10 = 1 538,6 cm³.",tol=1),
    gs("EX004","hard","Cylindre de diamètre 6 cm et hauteur 15 cm. Volume ?",
        [{"instruction":"r = 3 cm","expected":"3"},
         {"instruction":"V = π×9×15","expected":"3,14×9×15 = 423,9 cm³"}],
        "423,9 cm³","V = π×r²×h = 423,9 cm³."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-VOL-AIRES::MS02","exercises":[
    gs("EX001","hard","Calcule l'aire latérale d'un cylindre de rayon 4 cm et hauteur 10 cm.",
        [{"instruction":"A_lat = 2×π×r×h = 2×3,14×4×10","expected":"251,2 cm²"}],
        "251,2 cm²","A_lat = 2πrh = 251,2 cm²."),
    ni("EX002","hard","Aire latérale : r=5 cm, h=12 cm ?",376.8,"2×3,14×5×12 = 376,8 cm².",tol=1),
    ni("EX003","hard","Aire latérale : r=3 cm, h=20 cm ?",376.8,"2×3,14×3×20 = 376,8 cm².",tol=1),
    gs("EX004","hard","Cylindre de diamètre 10 cm, hauteur 8 cm. Aire latérale ?",
        [{"instruction":"r = 5 cm","expected":"5"},
         {"instruction":"A_lat = 2×3,14×5×8","expected":"251,2 cm²"}],
        "251,2 cm²","2πrh = 251,2 cm²."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-VOL-AIRES::MS03","exercises":[
    mcq("EX001","hard","L'aire latérale du cylindre est :",
        ["La surface du rectangle déroulé (sans les bases)","La surface totale","L'aire des 2 disques","Le volume"],
        "La surface du rectangle déroulé (sans les bases)","L'aire latérale ne comprend pas les bases."),
    sa("EX002","hard","Quelle est la différence entre aire latérale et aire totale d'un cylindre ?",
        "L'aire totale inclut les 2 bases circulaires en plus de l'aire latérale",
        "A_totale = A_latérale + 2×πr².",acc=["inclut les bases","ajoute les 2 disques","2 bases en plus"]),
    tf("EX003","hard","L'aire totale est toujours plus grande que l'aire latérale.",True,
        "A_totale = A_lat + 2πr² > A_lat (les bases ajoutent de la surface)."),
    mcq("EX004","hard","A_latérale = 2πrh. A_totale = ?",
        ["2πrh + 2πr²","2πrh + πr²","2πrh × 2","πr²h"],
        "2πrh + 2πr²","On ajoute l'aire des 2 bases : 2×πr²."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-VOL-AIRES::MS04","exercises":[
    gs("EX001","hard","Calcule l'aire totale d'un cylindre de rayon 3 cm et hauteur 10 cm.",
        [{"instruction":"A_lat = 2×3,14×3×10 = 188,4 cm²","expected":"188,4"},
         {"instruction":"Aire des 2 bases = 2×3,14×9 = 56,52 cm²","expected":"56,52"},
         {"instruction":"A_totale = 188,4 + 56,52","expected":"244,92 cm²"}],
        "244,92 cm²","A_totale = 2πrh + 2πr² = 244,92 cm²."),
    ni("EX002","hard","Aire totale : r=5 cm, h=8 cm ?",408.2,
        "A_lat = 2×3,14×5×8 = 251,2. Bases = 2×3,14×25 = 157. Total = 408,2.",tol=1),
    ni("EX003","hard","Aire totale : r=2 cm, h=7 cm ?",113.04,
        "A_lat = 2×3,14×2×7 = 87,92. Bases = 2×3,14×4 = 25,12. Total = 113,04.",tol=1),
    gs("EX004","hard","Cylindre de diamètre 6 cm et hauteur 12 cm. Aire totale ?",
        [{"instruction":"r = 3 cm","expected":"3"},
         {"instruction":"A_lat = 2×3,14×3×12 = 226,08","expected":"226,08"},
         {"instruction":"Bases = 2×3,14×9 = 56,52","expected":"56,52"},
         {"instruction":"Total = 282,6 cm²","expected":"282,6 cm²"}],
        "282,6 cm²","A_totale = 226,08 + 56,52 = 282,6 cm²."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-VOL-AIRES::MS05","exercises":[
    ec("EX001","hard","Un élève confond cm² et cm³ : « Le volume du cylindre est 300 cm² ».",
        "Volume = 300 cm²","Volume = 300 cm³","Le volume s'exprime en cm³ (cubes), pas cm² (carrés)."),
    mcq("EX002","hard","L'aire d'un cylindre s'exprime en ___ et le volume en ___.",
        ["cm² et cm³","cm³ et cm²","cm et cm²","L et mL"],"cm² et cm³","Aire = surface (²), volume = espace (³)."),
    ec("EX003","hard","Un élève calcule l'aire latérale en cm³ au lieu de cm².",
        "A_lat = 200 cm³","A_lat = 200 cm²","L'aire est une surface, donc cm² (pas cm³)."),
    tf("EX004","hard","Dans un problème de cylindre, les aires sont en cm² et les volumes en cm³.",True,
        "Aires = unités carrées, volumes = unités cubes."),
]})
blocks.append({"micro_skill_external_id":"MES-CYL-VOL-AIRES::MS06","exercises":[
    ni("EX001","hard","Arrondis π×7² à l'unité.",154,"3,14159×49 = 153,94 ≈ 154.",tol=1),
    ec("EX002","hard","Un élève utilise π=3 et trouve V = 3×4²×10 = 480 cm³. Avec π≈3,14, V = ?",
        "480 cm³","502,4 cm³","3,14×16×10 = 502,4 cm³."),
    ni("EX003","hard","Arrondis au centième : 3,14159 × 25 = ?",78.54,
        "78,53975 ≈ 78,54.",tol=0.01),
    mcq("EX004","hard","Pour les calculs avec π au CM2, on utilise généralement :",
        ["π ≈ 3,14","π = 3","π = 22/7","π = 3,14159265"],"π ≈ 3,14",
        "Au CM2, on utilise π ≈ 3,14 pour les calculs."),
]})

# MES-CHANGES (4 MS)
blocks.append({"micro_skill_external_id":"MES-CHANGES::MS01","exercises":[
    fb("EX001","medium","1 EUR = ___ FCFA (taux fixe).","655,957","Le taux fixe EUR/FCFA est 655,957."),
    mcq("EX002","medium","Que signifie « 1 EUR = 655,957 FCFA » ?",
        ["1 euro vaut 655,957 francs CFA","1 FCFA vaut 655,957 euros","On additionne EUR et FCFA","Rien"],
        "1 euro vaut 655,957 francs CFA","Le taux de change indique la valeur d'1 unité dans l'autre monnaie."),
    tf("EX003","easy","1 dollar américain vaut plus que 1 franc CFA.",True,
        "1 USD ≈ 600 FCFA, donc 1 USD > 1 FCFA."),
    mcq("EX004","medium","Pour convertir des euros en FCFA, on :",
        ["Multiplie par le taux","Divise par le taux","Additionne le taux","Soustrait le taux"],
        "Multiplie par le taux","EUR → FCFA : on multiplie par 655,957."),
]})
blocks.append({"micro_skill_external_id":"MES-CHANGES::MS02","exercises":[
    mcq("EX001","medium","Pour convertir 50 EUR en FCFA (taux 655,957), on fait :",
        ["50 × 655,957","50 ÷ 655,957","655,957 ÷ 50","50 + 655,957"],
        "50 × 655,957","EUR → FCFA : multiplication."),
    gs("EX002","hard","Convertis 100 000 FCFA en EUR.",
        [{"instruction":"On divise par le taux : 100 000 ÷ 655,957","expected":"≈ 152,45 EUR"}],
        "≈ 152,45 EUR","FCFA → EUR : on divise par 655,957."),
    mcq("EX003","hard","Pour passer de FCFA à EUR, on :",
        ["Divise par 655,957","Multiplie par 655,957","Additionne 655,957","Soustrait"],
        "Divise par 655,957","FCFA → EUR : division."),
    gs("EX004","hard","20 EUR = ___ FCFA ?",
        [{"instruction":"20 × 655,957","expected":"13 119,14 FCFA"}],
        "13 119,14 FCFA","20 × 655,957 = 13 119,14 FCFA."),
]})
blocks.append({"micro_skill_external_id":"MES-CHANGES::MS03","exercises":[
    ni("EX001","medium","10 EUR en FCFA (arrondi à l'unité) ?",6560,"10×655,957 ≈ 6 560 FCFA.",tol=1),
    ni("EX002","hard","150 000 FCFA en EUR (arrondi à l'euro) ?",229,"150 000÷655,957 ≈ 228,66 ≈ 229 EUR.",tol=1),
    ec("EX003","hard","Un élève convertit 5 EUR : 5×655,957 = 3 279,785 et écrit 3 279,785 FCFA.",
        "3 279,785 FCFA","3 280 FCFA","En monnaie, on arrondit à l'unité : 3 280 FCFA."),
    ni("EX004","hard","Arrondis 50 000 ÷ 655,957 à l'euro.",76,"76,22 ≈ 76 EUR.",tol=1),
]})
blocks.append({"micro_skill_external_id":"MES-CHANGES::MS04","exercises":[
    ec("EX001","hard","Un élève convertit 10 EUR en FCFA et obtient 65,60 FCFA.",
        "65,60 FCFA","6 560 FCFA","L'élève a divisé au lieu de multiplier. 10 × 656 ≈ 6 560 FCFA."),
    mcq("EX002","hard","Si 1 EUR ≈ 656 FCFA, alors 1 000 EUR devrait donner environ :",
        ["656 000 FCFA","6 560 FCFA","65 600 FCFA","656 FCFA"],
        "656 000 FCFA","1 000 × 656 = 656 000 FCFA."),
    ec("EX003","hard","Un touriste reçoit 6 EUR pour 500 000 FCFA. Est-ce raisonnable ?",
        "6 EUR pour 500 000 FCFA","≈ 762 EUR","500 000 ÷ 656 ≈ 762 EUR. 6 EUR est absurde."),
    mcq("EX004","hard","Un objet coûte 50 000 FCFA ≈ 76 EUR. Est-ce plausible ?",
        ["Oui, car 76×656 ≈ 49 856","Non, c'est trop","Non, c'est trop peu","On ne peut pas vérifier"],
        "Oui, car 76×656 ≈ 49 856","76 × 656 ≈ 49 856 ≈ 50 000 FCFA ✓."),
]})

# MES-TEMPS-DUREES (6 MS)
blocks.append({"micro_skill_external_id":"MES-TEMPS-DUREES::MS01","exercises":[
    mcq("EX001","easy","Sur une horloge analogique, la petite aiguille indique :",
        ["Les heures","Les minutes","Les secondes","La date"],"Les heures","Petite aiguille = heures, grande aiguille = minutes."),
    ni("EX002","easy","Quand la grande aiguille est sur le 6, il est la demie. Si la petite aiguille est entre 3 et 4, il est :",
        3,"Il est 3h30. La petite aiguille pointe vers 3.",tol=0.5),
    mcq("EX003","medium","Quand la grande aiguille est sur le 3, il est :",
        ["15 minutes (et quart)","3 minutes","30 minutes","45 minutes"],"15 minutes (et quart)",
        "Chaque chiffre = 5 minutes. 3 × 5 = 15 minutes."),
    ni("EX004","medium","La grande aiguille est sur le 9. Combien de minutes ?",45,"9 × 5 = 45 minutes."),
]})
blocks.append({"micro_skill_external_id":"MES-TEMPS-DUREES::MS02","exercises":[
    mcq("EX001","medium","14h30 en format 12h :",["2h30 PM","2h30 AM","14h30","4h30 PM"],"2h30 PM","14-12=2, après-midi."),
    fb("EX002","medium","8:45 PM en format 24h = ___h___.","20h45","8+12=20 → 20h45."),
    mcq("EX003","easy","07:15 en format 12h :",["7h15 AM","7h15 PM","19h15","15h07"],"7h15 AM","Avant midi = AM."),
    ni("EX004","medium","23h15 en format 12h, c'est ___ h15 PM.",11,"23-12=11 → 11h15 PM."),
]})
blocks.append({"micro_skill_external_id":"MES-TEMPS-DUREES::MS03","exercises":[
    ni("EX001","easy","2 h = ___ min.",120,"2 × 60 = 120 minutes."),
    ni("EX002","medium","150 min = ___ h ___ min. Combien d'heures entières ?",2,"150 ÷ 60 = 2h30 → 2 heures entières."),
    fb("EX003","medium","1h45 = ___ min.","105","60 + 45 = 105 minutes."),
    ni("EX004","hard","200 min = ___ h ___ min. Nombre de minutes restantes ?",20,"200÷60=3h20 → 20 min restantes."),
]})
blocks.append({"micro_skill_external_id":"MES-TEMPS-DUREES::MS04","exercises":[
    gs("EX001","medium","Calcule la durée entre 8h15 et 11h45.",
        [{"instruction":"De 8h15 à 11h15 = 3h","expected":"3h"},
         {"instruction":"De 11h15 à 11h45 = 30 min","expected":"30 min"},
         {"instruction":"Total = 3h30","expected":"3h30"}],
        "3h30","8h15 → 11h45 = 3h30."),
    ni("EX002","hard","Durée entre 14h20 et 17h05 en minutes ?",165,"2h45 = 165 min."),
    gs("EX003","hard","Durée entre 22h30 et 6h15 (le lendemain).",
        [{"instruction":"22h30 à minuit = 1h30","expected":"1h30"},
         {"instruction":"Minuit à 6h15 = 6h15","expected":"6h15"},
         {"instruction":"Total = 7h45","expected":"7h45"}],
        "7h45","1h30 + 6h15 = 7h45."),
    ni("EX004","medium","Durée entre 9h00 et 12h30 en minutes ?",210,"3h30 = 210 min."),
]})
blocks.append({"micro_skill_external_id":"MES-TEMPS-DUREES::MS05","exercises":[
    cp("EX001","hard","Un train part à 7h45 et le trajet dure 3h20. À quelle heure arrive-t-il ?",
        [{"text":"7h45 + 3h = ?","answer":"10h45"},
         {"text":"10h45 + 20 min = ?","answer":"11h05"}],
        "11h05","7h45 + 3h20 = 11h05."),
    gs("EX002","hard","Akouavi part de chez elle à 6h50 et arrive à l'école à 7h25. Durée du trajet ?",
        [{"instruction":"De 6h50 à 7h00 = 10 min","expected":"10 min"},
         {"instruction":"De 7h00 à 7h25 = 25 min","expected":"25 min"},
         {"instruction":"Total = 35 min","expected":"35 min"}],
        "35 min","10 + 25 = 35 minutes."),
    ni("EX003","hard","Un match commence à 15h30 et dure 1h45. Heure de fin (en minutes après 17h) ?",15,
        "15h30 + 1h45 = 17h15 → 15 minutes après 17h."),
    cp("EX004","hard","Un bus arrive toutes les 45 min. Le premier bus passe à 6h00. À quelle heure passe le 3e bus ?",
        [{"text":"2e bus : 6h00 + 45 min =","answer":"6h45"},
         {"text":"3e bus : 6h45 + 45 min =","answer":"7h30"}],
        "7h30","6h00 → 6h45 → 7h30."),
]})
blocks.append({"micro_skill_external_id":"MES-TEMPS-DUREES::MS06","exercises":[
    ec("EX001","hard","Un élève calcule : départ 8h30, arrivée 7h15, durée = 1h15.",
        "Durée = 1h15","Impossible : l'arrivée (7h15) est avant le départ (8h30) !",
        "L'heure d'arrivée doit être après l'heure de départ."),
    mcq("EX002","hard","Un trajet de 8h00 à 9h30 dure :",["1h30","1h03","30 min","2h30"],"1h30",
        "De 8h00 à 9h30 = 1h30."),
    ec("EX003","hard","Un élève dit : « Un film de 13h45 à 16h00 dure 3h45 ».",
        "3h45","2h15","De 13h45 à 16h00 = 2h15, pas 3h45."),
    tf("EX004","hard","Une durée calculée doit toujours être positive.",True,
        "Si on obtient une durée négative, il y a une erreur dans le calcul ou les données."),
]})

# MES-CALENDRIER (4 MS)
blocks.append({"micro_skill_external_id":"MES-CALENDRIER::MS01","exercises":[
    mcq("EX001","easy","Combien de jours y a-t-il dans une semaine ?",["7","5","6","10"],"7","1 semaine = 7 jours."),
    fb("EX002","easy","Il y a ___ mois dans une année.","12","1 an = 12 mois."),
    mcq("EX003","easy","Quel mois a 28 ou 29 jours ?",["Février","Janvier","Mars","Avril"],"Février",
        "Février a 28 jours (29 les années bissextiles)."),
    order("EX004","easy","Range dans l'ordre : lundi, mercredi, vendredi, dimanche.",
        ["Lundi","Mercredi","Vendredi","Dimanche"],["Lundi","Mercredi","Vendredi","Dimanche"],"L'ordre des jours de la semaine."),
]})
blocks.append({"micro_skill_external_id":"MES-CALENDRIER::MS02","exercises":[
    fb("EX001","easy","Le 15 mars 2026 s'écrit aussi : ___/___/___.","15/03/2026","Format jour/mois/année."),
    mcq("EX002","easy","« 2026-03-15 » correspond à :",["15 mars 2026","3 mars 2026","15 mars 2016","Mars 2026"],
        "15 mars 2026","Format international : année-mois-jour."),
    fb("EX003","medium","Le 1er janvier 2026 s'écrit en format court : 01/___/2026.","01","Janvier = mois 01."),
    mcq("EX004","easy","Le 25/12/2025 est :",["Le 25 décembre 2025","Le 12 mai 2025","Le 25 mai 2012","Le 12 décembre 2025"],
        "Le 25 décembre 2025","25 = jour, 12 = décembre, 2025 = année."),
]})
blocks.append({"micro_skill_external_id":"MES-CALENDRIER::MS03","exercises":[
    ni("EX001","medium","Combien de jours entre le 10 mars et le 25 mars ?",15,"25 - 10 = 15 jours."),
    gs("EX002","hard","Combien de jours entre le 20 février et le 5 mars 2026 ?",
        [{"instruction":"Février a 28 jours en 2026. Du 20 au 28 février = 8 jours","expected":"8"},
         {"instruction":"Du 1er au 5 mars = 5 jours","expected":"5"},
         {"instruction":"Total = 13 jours","expected":"13"}],
        "13 jours","8 + 5 = 13 jours."),
    ni("EX003","medium","Du 1er au 30 juin, combien de jours ?",29,"30 - 1 = 29 jours."),
    ni("EX004","hard","Du 15 décembre au 10 janvier (mois suivant) ?",26,"16 jours en décembre (31-15) + 10 jours en janvier = 26."),
]})
blocks.append({"micro_skill_external_id":"MES-CALENDRIER::MS04","exercises":[
    cp("EX001","hard","L'école commence le 4 septembre et les vacances de Noël sont le 20 décembre. Combien de jours d'école ? (5 jours/semaine)",
        [{"text":"Nombre de semaines ≈ ?","answer":"≈ 15 semaines"},
         {"text":"Jours d'école ≈ ?","answer":"15 × 5 = 75 jours"}],
        "≈ 75 jours","Du 4 sept au 20 déc ≈ 15 semaines = 75 jours d'école."),
    gs("EX002","medium","La fête du village est dans 3 semaines et 4 jours à partir du lundi 1er mars. Quelle date ?",
        [{"instruction":"3 semaines = 21 jours","expected":"21"},
         {"instruction":"21 + 4 = 25 jours après le 1er mars","expected":"25"},
         {"instruction":"1 + 25 = 26 mars","expected":"26 mars"}],
        "26 mars","1er mars + 25 jours = 26 mars."),
    fb("EX003","medium","Un événement dure du 10 au 17 avril. Il dure ___ jours.","7","17 - 10 = 7 jours."),
    cp("EX004","hard","Kofi a un rendez-vous tous les 14 jours. Le premier est le 5 janvier. Quand sont les 2e et 3e rendez-vous ?",
        [{"text":"2e rendez-vous = 5 + 14 jours","answer":"19 janvier"},
         {"text":"3e rendez-vous = 19 + 14 jours","answer":"2 février"}],
        "19 janvier et 2 février","5+14=19 janv, 19+14=33→ 2 février (janvier a 31 jours)."),
]})

# Merge with part 1
with open("_mes_part1.json") as f:
    part1 = json.load(f)

all_blocks = part1 + blocks

payload = {
    "schema_version": "1.0",
    "metadata": {"domain": "Grandeurs et Mesures", "grade": "CM2", "country": "Bénin", "generated": True},
    "exercises": all_blocks,
}
total = sum(len(b["exercises"]) for b in all_blocks)
out = "backend/exercices_cm2_mesures.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

import os
os.remove("_mes_part1.json")
print(f"✓ {out}: {len(all_blocks)} blocs, {total} exercices")
