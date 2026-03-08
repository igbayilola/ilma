"""Generate real exercises for Géométrie domain (35 micro-skills)."""
import json

def B(eid, typ, diff, text, **kw):
    d = {"exercise_id": eid, "type": typ, "difficulty": diff, "text": text,
         "points": {"easy":1,"medium":2,"hard":3}[diff],
         "time_limit_seconds": {"easy":45,"medium":60,"hard":90}[diff]}
    d.update(kw)
    return d

def mcq(eid,d,t,ch,a,ex,h="Réfléchis bien.",**kw): return B(eid,"mcq",d,t,choices=ch,correct_answer=a,explanation=ex,hint=h,**kw)
def tf(eid,d,t,a,ex,h="Réfléchis bien."): return B(eid,"true_false",d,t,correct_answer=a,explanation=ex,hint=h)
def fb(eid,d,t,a,ex,h="Complète.",blanks=None):
    r=B(eid,"fill_blank",d,t,correct_answer=a,explanation=ex,hint=h)
    if blanks: r["blanks"]=blanks
    return r
def ni(eid,d,t,a,ex,h="Calcule.",tol=0):
    r=B(eid,"numeric_input",d,t,correct_answer=a,explanation=ex,hint=h)
    if tol: r["tolerance"]=tol
    return r
def sa(eid,d,t,a,ex,h="Écris.",acc=None):
    r=B(eid,"short_answer",d,t,correct_answer=a,explanation=ex,hint=h)
    if acc: r["accepted_answers"]=acc
    return r
def order(eid,d,t,items,a,ex,h="Mets dans l'ordre."): return B(eid,"ordering",d,t,items=items,correct_answer=a,explanation=ex,hint=h)
def ec(eid,d,t,err,a,ex,h="Trouve l'erreur."): return B(eid,"error_correction",d,t,erroneous_content=err,correct_answer=a,explanation=ex,hint=h)
def gs(eid,d,t,steps,a,ex,h="Suis les étapes."): return B(eid,"guided_steps",d,t,steps=steps,correct_answer=a,explanation=ex,hint=h)
def jus(eid,d,t,a,ex,h="Justifie.",rub=None):
    r=B(eid,"justification",d,t,correct_answer=a,explanation=ex,hint=h)
    if rub: r["scoring_rubric"]=rub
    return r
def tr(eid,d,t,nl,a,ex,h="Observe."): return B(eid,"tracing",d,t,number_line=nl,correct_answer=a,explanation=ex,hint=h)
def match(eid,d,t,l,r_,a,ex,h="Associe."): return B(eid,"matching",d,t,left_items=l,right_items=r_,correct_answer=a,explanation=ex,hint=h)

blocks = []

# GEO-FIG-DECRIRE
blocks.append({"micro_skill_external_id":"GEO-FIG-DECRIRE::MS01","exercises":[
    mcq("EX001","easy","Comment s'appelle le point où deux côtés d'un polygone se rencontrent ?",
        ["Un sommet","Un côté","Un angle","Une diagonale"],"Un sommet","Le point de rencontre de deux côtés est un sommet."),
    match("EX002","medium","Associe chaque terme à sa définition.",
        ["Sommet","Côté","Diagonale"],["Point de rencontre de 2 côtés","Segment reliant 2 sommets consécutifs","Segment reliant 2 sommets non consécutifs"],
        {"Sommet":"Point de rencontre de 2 côtés","Côté":"Segment reliant 2 sommets consécutifs","Diagonale":"Segment reliant 2 sommets non consécutifs"},
        "Sommet = point d'intersection des côtés; côté = segment entre sommets consécutifs; diagonale = segment entre sommets non consécutifs."),
    fb("EX003","easy","Un cercle a un ___, un ___ et un ___.","centre, rayon, diamètre","Les éléments principaux du cercle sont le centre, le rayon et le diamètre."),
    mcq("EX004","medium","Combien de diagonales possède un rectangle ?",["2","4","1","3"],"2","Un rectangle a exactement 2 diagonales."),
]})

blocks.append({"micro_skill_external_id":"GEO-FIG-DECRIRE::MS02","exercises":[
    mcq("EX001","medium","Pour tracer un angle droit, j'utilise :",["Une équerre","Un compas","Un rapporteur","Une règle seule"],"Une équerre","L'équerre sert à tracer et vérifier les angles droits."),
    tf("EX002","easy","On utilise le compas pour tracer un cercle.",True,"Le compas permet de tracer un cercle en gardant l'écartement constant."),
    tr("EX003","medium","Trace un segment de 7 cm à la règle.",{"min":0,"max":10,"step":1,"target":7},7,"Un segment de 7 cm va de 0 à 7 cm sur la règle."),
    mcq("EX004","medium","Pour vérifier qu'un angle est droit, je place :",["L'angle droit de l'équerre dans l'angle","Le compas au sommet","La règle le long du côté","Le rapporteur sur le sommet"],
        "L'angle droit de l'équerre dans l'angle","L'équerre permet de vérifier un angle droit en le plaçant dans le coin."),
]})

blocks.append({"micro_skill_external_id":"GEO-FIG-DECRIRE::MS03","exercises":[
    mcq("EX001","medium","Pour reproduire un triangle sur un quadrillage, je dois repérer :",
        ["Les coordonnées des 3 sommets","Seulement la longueur d'un côté","Le centre du triangle","La couleur du triangle"],
        "Les coordonnées des 3 sommets","Pour reproduire, il faut connaître la position de chaque sommet."),
    tr("EX002","hard","Reproduis un carré de côté 4 cm.",{"min":0,"max":8,"step":1,"target":4},4,
        "Un carré de 4 cm a 4 côtés égaux et 4 angles droits."),
    tf("EX003","medium","Pour reproduire une figure hors quadrillage, on peut utiliser la règle et le compas.",True,
        "La règle mesure les longueurs et le compas reporte les distances."),
    mcq("EX004","hard","Quelle information est indispensable pour reproduire un losange hors quadrillage ?",
        ["Les longueurs des deux diagonales","Seulement un côté","La couleur","Le nombre de sommets"],
        "Les longueurs des deux diagonales","Un losange est défini par ses diagonales (perpendiculaires et se coupant en leur milieu)."),
]})

blocks.append({"micro_skill_external_id":"GEO-FIG-DECRIRE::MS04","exercises":[
    ec("EX001","hard","Un élève a tracé un rectangle dont les côtés mesurent 5 cm et 3 cm, mais un angle n'est pas droit.",
        "Rectangle avec un angle non droit","Refaire le tracé en vérifiant chaque angle avec l'équerre",
        "Un rectangle doit avoir 4 angles droits. Utilisez l'équerre pour vérifier."),
    mcq("EX002","medium","Comment vérifier que deux segments tracés ont la même longueur ?",
        ["Mesurer chacun avec la règle","Les regarder à l'œil","Compter les angles","Utiliser le rapporteur"],
        "Mesurer chacun avec la règle","La règle graduée permet de mesurer et comparer les longueurs."),
    tf("EX003","medium","Pour vérifier l'alignement de 3 points, on peut utiliser une règle.",True,
        "Si la règle passe par les 3 points, ils sont alignés."),
    ec("EX004","hard","Le cercle tracé par un élève n'a pas un rayon constant (l'écartement du compas a bougé).",
        "Cercle irrégulier","Retracer en maintenant l'écartement du compas fixe",
        "Le compas doit garder le même écartement pendant tout le tracé."),
]})

# GEO-CERCLE
blocks.append({"micro_skill_external_id":"GEO-CERCLE::MS01","exercises":[
    mcq("EX001","easy","Le segment qui relie le centre du cercle à un point du cercle s'appelle :",
        ["Le rayon","Le diamètre","La corde","L'arc"],"Le rayon","Le rayon va du centre à n'importe quel point du cercle."),
    match("EX002","medium","Associe chaque élément du cercle à sa définition.",
        ["Rayon","Diamètre","Corde"],["Du centre à un point du cercle","Corde passant par le centre","Segment entre 2 points du cercle"],
        {"Rayon":"Du centre à un point du cercle","Diamètre":"Corde passant par le centre","Corde":"Segment entre 2 points du cercle"},
        "Rayon = centre→point, diamètre = plus grande corde (passe par le centre), corde = segment entre 2 points."),
    tf("EX003","easy","Le diamètre est toujours le double du rayon.",True,"D = 2 × r, toujours."),
    fb("EX004","medium","Le ___ est la plus longue corde du cercle.","diamètre","Le diamètre passe par le centre et est la corde la plus longue."),
]})

blocks.append({"micro_skill_external_id":"GEO-CERCLE::MS02","exercises":[
    mcq("EX001","medium","Pour tracer un cercle de rayon 5 cm, j'écarte mon compas de :",
        ["5 cm","10 cm","2,5 cm","15 cm"],"5 cm","L'écartement du compas = le rayon."),
    gs("EX002","medium","Trace un cercle de centre O et de rayon 4 cm.",
        [{"instruction":"Place le point O","expected":"Point O marqué"},
         {"instruction":"Écarte le compas de 4 cm","expected":"Écartement de 4 cm"},
         {"instruction":"Trace le cercle en gardant la pointe sur O","expected":"Cercle complet"}],
        "Cercle de centre O et rayon 4 cm","Pointe sèche sur O, écartement 4 cm, tracer sans bouger la pointe."),
    tf("EX003","easy","Pour tracer un cercle de diamètre 6 cm, j'écarte le compas de 6 cm.",False,
        "Le compas s'écarte du rayon, pas du diamètre. Rayon = 6/2 = 3 cm."),
    tr("EX004","medium","Trace un cercle de rayon 3 cm.",{"min":0,"max":6,"step":1,"target":3},3,
        "Écartement du compas = 3 cm."),
]})

blocks.append({"micro_skill_external_id":"GEO-CERCLE::MS03","exercises":[
    ni("EX001","easy","Le rayon d'un cercle est 8 cm. Quel est son diamètre ?",16,"D = 2 × r = 2 × 8 = 16 cm."),
    ni("EX002","easy","Le diamètre d'un cercle est 14 cm. Quel est son rayon ?",7,"r = D ÷ 2 = 14 ÷ 2 = 7 cm."),
    mcq("EX003","medium","Un cercle a un diamètre de 2,5 cm. Son rayon est :",["1,25 cm","5 cm","0,5 cm","2,5 cm"],"1,25 cm",
        "r = D/2 = 2,5/2 = 1,25 cm."),
    ni("EX004","medium","Le rayon d'un cercle est 3,5 cm. Calcule le diamètre.",7,"D = 2 × 3,5 = 7 cm.",tol=0.1),
]})

# GEO-ANGLES
blocks.append({"micro_skill_external_id":"GEO-ANGLES::MS01","exercises":[
    mcq("EX001","easy","Un angle de 45° est :",["Aigu","Droit","Obtus","Plat"],"Aigu","Un angle aigu mesure entre 0° et 90°."),
    order("EX002","easy","Classe ces angles du plus petit au plus grand.",
        ["Aigu (30°)","Droit (90°)","Obtus (120°)","Plat (180°)"],["Aigu (30°)","Droit (90°)","Obtus (120°)","Plat (180°)"],
        "30° < 90° < 120° < 180°."),
    mcq("EX003","medium","Un angle de 90° est :",["Un angle droit","Un angle aigu","Un angle obtus","Un angle plat"],"Un angle droit",
        "90° = angle droit."),
    tf("EX004","easy","Un angle de 135° est un angle obtus.",True,"Un angle obtus est entre 90° et 180°. 135° est obtus."),
]})

blocks.append({"micro_skill_external_id":"GEO-ANGLES::MS02","exercises":[
    ni("EX001","medium","Mesure au rapporteur : l'angle entre les aiguilles d'une horloge à 3h.",90,
        "À 3h, les aiguilles forment un angle droit de 90°.","Place le centre du rapporteur au centre de l'horloge."),
    mcq("EX002","hard","Pour mesurer un angle, le centre du rapporteur doit être placé sur :",
        ["Le sommet de l'angle","Un côté de l'angle","À l'extérieur de l'angle","N'importe où"],
        "Le sommet de l'angle","Le centre du rapporteur se place toujours sur le sommet."),
    ni("EX003","medium","L'angle entre les deux côtés d'un triangle isocèle au sommet mesure 40°. Quelle est cette mesure ?",
        40,"L'angle au sommet est donné : 40°.",tol=1),
    ec("EX004","hard","Un élève lit 150° au lieu de 30° sur le rapporteur.",
        "150° au lieu de 30°","30°","L'élève a lu la mauvaise graduation (intérieure/extérieure). Il faut choisir la graduation qui part de 0° sur le bon côté."),
]})

blocks.append({"micro_skill_external_id":"GEO-ANGLES::MS03","exercises":[
    gs("EX001","hard","Construis un angle de 60° au rapporteur.",
        [{"instruction":"Trace un côté de l'angle (demi-droite)","expected":"Demi-droite tracée"},
         {"instruction":"Place le centre du rapporteur sur l'origine de la demi-droite","expected":"Centre placé"},
         {"instruction":"Repère 60° et marque un point","expected":"Point à 60°"},
         {"instruction":"Trace la deuxième demi-droite passant par ce point","expected":"Angle de 60° construit"}],
        "Angle de 60°","Après avoir tracé un côté, utilise le rapporteur pour repérer 60° et trace le second côté."),
    tr("EX002","medium","Construis un angle de 45°.",{"min":0,"max":180,"step":15,"target":45},45,
        "45° est la moitié d'un angle droit."),
    mcq("EX003","medium","Pour construire un angle de 120°, je repère sur le rapporteur :",
        ["120° sur la bonne graduation","60° et je double","90° + 30°","180° - 120°"],
        "120° sur la bonne graduation","On lit directement 120° sur le rapporteur."),
    tr("EX004","hard","Construis un angle de 75°.",{"min":0,"max":180,"step":15,"target":75},75,"75° est entre 60° et 90°."),
]})

blocks.append({"micro_skill_external_id":"GEO-ANGLES::MS04","exercises":[
    ni("EX001","hard","Un triangle a deux angles de 50° et 70°. Combien mesure le troisième angle ?",60,
        "50 + 70 = 120. 180 - 120 = 60°.","La somme des angles d'un triangle = 180°."),
    gs("EX002","hard","Calcule le 3e angle d'un triangle dont les deux autres mesurent 35° et 90°.",
        [{"instruction":"Additionne les deux angles connus","expected":"35 + 90 = 125"},
         {"instruction":"Soustrais de 180°","expected":"180 - 125 = 55"}],
        "55°","35 + 90 = 125. 180 - 125 = 55°."),
    ec("EX003","hard","Un élève dit que les angles d'un triangle mesurent 60°, 70° et 60°.",
        "60° + 70° + 60° = 190°","La somme ne fait pas 180° (elle fait 190°). L'élève s'est trompé.",
        "La somme des angles d'un triangle doit toujours être 180°."),
    ni("EX004","hard","Dans un triangle équilatéral, combien mesure chaque angle ?",60,
        "Triangle équilatéral : 3 angles égaux. 180 ÷ 3 = 60°."),
]})

# GEO-SYMM-POINT
blocks.append({"micro_skill_external_id":"GEO-SYMM-POINT::MS01","exercises":[
    mcq("EX001","medium","Dans une symétrie centrale de centre O, le symétrique d'un point A est un point A' tel que :",
        ["O est le milieu de [AA']","A et A' sont du même côté de O","AA' = AO","A' est sur le cercle de centre A"],
        "O est le milieu de [AA']","En symétrie centrale, le centre O est le milieu du segment [AA']."),
    tr("EX002","hard","Construis le symétrique du point A(3,2) par rapport au centre O(5,4).",
        {"min":0,"max":10,"step":1,"target":7},7,"A'(7,6) : xA' = 2×5-3=7, yA' = 2×4-2=6."),
    gs("EX003","medium","Construis le symétrique de A par rapport à O sur quadrillage.",
        [{"instruction":"Compte les carreaux de A à O horizontalement et verticalement","expected":"dx et dy comptés"},
         {"instruction":"Reporte la même distance de l'autre côté de O","expected":"Point A' placé"}],
        "Point A' symétrique de A par rapport à O","On prolonge [AO] d'une distance égale à AO de l'autre côté de O."),
    tf("EX004","medium","En symétrie centrale de centre O, les distances sont conservées : OA = OA'.",True,
        "Par définition, O est le milieu de [AA'], donc OA = OA'."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-POINT::MS02","exercises":[
    gs("EX001","hard","Construis le symétrique du segment [AB] par rapport au centre O.",
        [{"instruction":"Construis A', symétrique de A par rapport à O","expected":"A' placé"},
         {"instruction":"Construis B', symétrique de B par rapport à O","expected":"B' placé"},
         {"instruction":"Trace [A'B']","expected":"Segment [A'B'] tracé"}],
        "Segment [A'B'] symétrique de [AB]","On construit le symétrique de chaque extrémité, puis on trace le segment."),
    tf("EX002","medium","Le segment symétrique a la même longueur que le segment original.",True,
        "La symétrie centrale conserve les longueurs : AB = A'B'."),
    mcq("EX003","hard","Le symétrique d'un segment [AB] par rapport à O est :",
        ["Un segment [A'B'] de même longueur","Un segment plus court","Un arc de cercle","Un point"],
        "Un segment [A'B'] de même longueur","La symétrie centrale transforme un segment en un segment de même longueur."),
    tr("EX004","hard","Trace le symétrique du segment.",{"min":0,"max":10,"step":1,"target":5},5,"Le symétrique est de l'autre côté du centre."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-POINT::MS03","exercises":[
    gs("EX001","hard","Construis le symétrique du triangle ABC par rapport au centre O.",
        [{"instruction":"Construis A' symétrique de A","expected":"A' placé"},
         {"instruction":"Construis B' symétrique de B","expected":"B' placé"},
         {"instruction":"Construis C' symétrique de C","expected":"C' placé"},
         {"instruction":"Trace le triangle A'B'C'","expected":"Triangle image tracé"}],
        "Triangle A'B'C'","On construit le symétrique de chaque sommet, puis on trace la figure."),
    tf("EX002","hard","Le symétrique d'un triangle par symétrie centrale est un triangle de mêmes dimensions.",True,
        "La symétrie centrale conserve les longueurs et les angles."),
    mcq("EX003","hard","Pour construire le symétrique d'un carré par rapport à un point O, il faut construire le symétrique de :",
        ["Chaque sommet du carré","Un seul sommet","Le centre du carré","Les diagonales seulement"],
        "Chaque sommet du carré","On transforme chaque sommet pour obtenir la figure image."),
    match("EX004","medium","Associe chaque figure à son image par symétrie centrale.",
        ["Triangle","Carré","Cercle"],["Triangle de même taille","Carré de même taille","Cercle de même rayon"],
        {"Triangle":"Triangle de même taille","Carré":"Carré de même taille","Cercle":"Cercle de même rayon"},
        "La symétrie centrale conserve la forme et les dimensions."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-POINT::MS04","exercises":[
    tf("EX001","hard","Après une symétrie centrale, les longueurs sont conservées.",True,
        "La symétrie centrale est une isométrie : elle conserve les distances."),
    ec("EX002","hard","Un élève dit que le symétrique d'un carré de 4 cm de côté est un carré de 8 cm de côté.",
        "Carré de 8 cm","Carré de 4 cm","La symétrie centrale conserve les longueurs, donc le carré image a aussi 4 cm de côté."),
    mcq("EX003","hard","Après une symétrie centrale, l'aire d'une figure :",
        ["Reste la même","Double","Diminue de moitié","Change selon le centre"],
        "Reste la même","La symétrie centrale conserve les aires."),
    tf("EX004","hard","La symétrie centrale conserve les angles.",True,"Les angles sont conservés par symétrie centrale."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-POINT::MS05","exercises":[
    mcq("EX001","hard","La symétrie axiale et la symétrie centrale sont différentes car :",
        ["L'une utilise un axe (droite), l'autre un centre (point)","Elles sont identiques",
         "La symétrie axiale n'existe pas","La symétrie centrale utilise un axe"],
        "L'une utilise un axe (droite), l'autre un centre (point)","Axiale = par rapport à une droite, centrale = par rapport à un point."),
    order("EX002","hard","Classe ces transformations.",
        ["Symétrie axiale","Symétrie centrale","Translation","Rotation"],
        ["Symétrie axiale","Symétrie centrale","Translation","Rotation"],
        "Les 4 transformations du plan au programme."),
    ec("EX003","hard","Un élève confond symétrie axiale et centrale : il trace le symétrique d'un point par rapport à une droite en utilisant la méthode du centre.",
        "Méthode du centre appliquée à un axe","Il faut tracer la perpendiculaire à l'axe et reporter la distance",
        "En symétrie axiale, on trace la perpendiculaire à l'axe passant par le point."),
    tf("EX004","hard","En symétrie axiale, l'axe est la médiatrice du segment reliant un point à son image.",True,
        "L'axe est bien la médiatrice de [MM'] pour tout point M et son image M'."),
]})

# GEO-CENTRE-SYMM
blocks.append({"micro_skill_external_id":"GEO-CENTRE-SYMM::MS01","exercises":[
    mcq("EX001","medium","Laquelle de ces figures admet un centre de symétrie ?",
        ["Le rectangle","Le triangle scalène","Le trapèze quelconque","Le triangle isocèle"],"Le rectangle",
        "Le rectangle a un centre de symétrie : l'intersection de ses diagonales."),
    order("EX002","medium","Parmi : carré, rectangle, parallélogramme, triangle équilatéral — lesquels admettent un centre de symétrie ? Classe-les.",
        ["Carré","Rectangle","Parallélogramme","Triangle équilatéral"],
        ["Carré","Rectangle","Parallélogramme","Triangle équilatéral"],
        "Le carré, le rectangle et le parallélogramme ont un centre de symétrie. Attention : le triangle équilatéral n'en a pas."),
    tf("EX003","medium","Un cercle admet son centre comme centre de symétrie.",True,
        "Le centre du cercle est un centre de symétrie du cercle."),
    mcq("EX004","hard","Le parallélogramme admet-il un centre de symétrie ?",
        ["Oui, l'intersection des diagonales","Non","Oui, un sommet","Oui, le milieu d'un côté"],
        "Oui, l'intersection des diagonales","Les diagonales d'un parallélogramme se coupent en leur milieu, qui est le centre de symétrie."),
]})

blocks.append({"micro_skill_external_id":"GEO-CENTRE-SYMM::MS02","exercises":[
    gs("EX001","hard","Construis le centre de symétrie d'un rectangle ABCD.",
        [{"instruction":"Trace la diagonale [AC]","expected":"Diagonale AC tracée"},
         {"instruction":"Trace la diagonale [BD]","expected":"Diagonale BD tracée"},
         {"instruction":"Le centre de symétrie est l'intersection des diagonales","expected":"Point O marqué"}],
        "Point O, intersection des diagonales","Le centre de symétrie d'un rectangle est l'intersection de ses diagonales."),
    tr("EX002","hard","Marque le centre de symétrie du carré.",{"min":0,"max":8,"step":1,"target":4},4,
        "Le centre est au milieu du carré, à l'intersection des diagonales."),
    mcq("EX003","hard","Pour trouver le centre de symétrie d'un parallélogramme, on cherche :",
        ["L'intersection des diagonales","Le milieu d'un côté","Un sommet","Le point le plus éloigné"],
        "L'intersection des diagonales","Les diagonales se coupent en leur milieu = centre de symétrie."),
    tf("EX004","medium","Le centre de symétrie d'un cercle est le centre du cercle.",True,"Le centre du cercle est son centre de symétrie."),
]})

blocks.append({"micro_skill_external_id":"GEO-CENTRE-SYMM::MS03","exercises":[
    sa("EX001","hard","Pourquoi un triangle équilatéral n'a-t-il pas de centre de symétrie ?",
        "Il a 3 côtés et une symétrie d'ordre impair, il n'admet pas de centre de symétrie",
        "Un triangle n'a pas de centre de symétrie car aucun point ne permet de transformer chaque sommet en un autre sommet.",
        acc=["pas de centre de symétrie","symétrie d'ordre impair"]),
    ec("EX002","hard","Un élève dit que le triangle isocèle a un centre de symétrie.",
        "Le triangle isocèle a un centre de symétrie","Le triangle isocèle n'a PAS de centre de symétrie",
        "Aucun triangle n'a de centre de symétrie : un sommet ne peut correspondre à aucun autre par symétrie centrale."),
    mcq("EX003","hard","Laquelle de ces figures n'admet PAS de centre de symétrie ?",
        ["Le triangle","Le rectangle","Le carré","Le cercle"],"Le triangle",
        "Aucun triangle n'a de centre de symétrie."),
    jus("EX004","hard","Le trapèze non parallélogramme admet-il un centre de symétrie ? Justifie.",
        "Non, le trapèze non parallélogramme n'a pas de centre de symétrie",
        "Un trapèze non parallélogramme n'a qu'une seule paire de côtés parallèles, ce qui empêche la symétrie centrale.",
        rub="1pt: réponse correcte, 1pt: justification"),
]})

# GEO-SYMM-DROITE
blocks.append({"micro_skill_external_id":"GEO-SYMM-DROITE::MS01","exercises":[
    mcq("EX001","medium","En symétrie axiale, l'axe de symétrie est :",
        ["La médiatrice du segment [MM']","Le milieu de [MM']","Un côté de la figure","Le centre de la figure"],
        "La médiatrice du segment [MM']","L'axe est la médiatrice du segment reliant tout point à son image."),
    fb("EX002","medium","L'axe de symétrie est ___ au segment [PP'] et passe par son ___.","perpendiculaire, milieu",
        "L'axe est perpendiculaire à [PP'] et passe par le milieu de [PP']."),
    tf("EX003","medium","En symétrie axiale, le point et son image sont à égale distance de l'axe.",True,
        "Par définition, d(P,axe) = d(P',axe)."),
    mcq("EX004","hard","Si M est sur l'axe de symétrie, alors son image M' est :",
        ["M lui-même","De l'autre côté de l'axe","Le centre de la figure","Inexistant"],
        "M lui-même","Tout point de l'axe est son propre symétrique."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-DROITE::MS02","exercises":[
    gs("EX001","hard","Trace la perpendiculaire à la droite (d) passant par le point A.",
        [{"instruction":"Place l'équerre avec un côté de l'angle droit sur (d)","expected":"Équerre placée"},
         {"instruction":"Fais glisser l'équerre pour que l'autre côté passe par A","expected":"Alignement avec A"},
         {"instruction":"Trace la perpendiculaire","expected":"Droite perpendiculaire tracée"}],
        "Perpendiculaire à (d) passant par A","On utilise l'équerre pour tracer la perpendiculaire."),
    tr("EX002","hard","Trace la perpendiculaire à l'axe passant par le point donné.",
        {"min":0,"max":10,"step":1,"target":5},5,"La perpendiculaire forme un angle de 90° avec l'axe."),
    mcq("EX003","medium","Pour tracer la perpendiculaire à une droite, on utilise :",
        ["L'équerre","Le compas seul","La règle seule","Le rapporteur"],"L'équerre",
        "L'équerre permet de tracer des angles droits (perpendiculaires)."),
    tf("EX004","medium","Deux droites perpendiculaires forment un angle de 90°.",True,"Perpendiculaire = angle droit = 90°."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-DROITE::MS03","exercises":[
    gs("EX001","hard","Construis le symétrique du point A par rapport à l'axe (d).",
        [{"instruction":"Trace la perpendiculaire à (d) passant par A","expected":"Perpendiculaire tracée"},
         {"instruction":"Mesure la distance d(A, axe)","expected":"Distance mesurée"},
         {"instruction":"Reporte cette distance de l'autre côté de l'axe sur la perpendiculaire","expected":"A' placé"}],
        "Point A' symétrique de A","On trace la perpendiculaire, on mesure et on reporte la distance."),
    ni("EX002","medium","Le point A est à 4 cm de l'axe. À quelle distance de l'axe se trouve A' ?",4,
        "En symétrie axiale, le point et son image sont à la même distance de l'axe."),
    tr("EX003","hard","Reporte la distance du point à l'axe de l'autre côté.",
        {"min":0,"max":10,"step":1,"target":5},5,"La distance à l'axe est conservée."),
    tf("EX004","medium","Le symétrique d'un point situé à 3 cm de l'axe est à 3 cm de l'axe de l'autre côté.",True,
        "Les distances à l'axe sont conservées en symétrie axiale."),
]})

blocks.append({"micro_skill_external_id":"GEO-SYMM-DROITE::MS04","exercises":[
    gs("EX001","hard","Construis le symétrique du triangle ABC par rapport à l'axe (d).",
        [{"instruction":"Construis A' symétrique de A","expected":"A' placé"},
         {"instruction":"Construis B' symétrique de B","expected":"B' placé"},
         {"instruction":"Construis C' symétrique de C","expected":"C' placé"},
         {"instruction":"Trace le triangle A'B'C'","expected":"Triangle image tracé"}],
        "Triangle A'B'C'","On construit le symétrique de chaque sommet."),
    ec("EX002","hard","Un élève a construit le symétrique d'un triangle mais n'a pas respecté les distances à l'axe.",
        "Distances non respectées","Mesurer chaque distance à l'axe et reporter exactement",
        "Chaque point doit être à la même distance de l'axe que son image."),
    tf("EX003","hard","Le symétrique d'un carré par rapport à un axe est aussi un carré.",True,
        "La symétrie axiale conserve les longueurs et les angles : le carré image est identique."),
    mcq("EX004","hard","Quel outil est indispensable pour construire un symétrique par rapport à un axe ?",
        ["L'équerre (pour la perpendiculaire)","Le rapporteur","La calculatrice","Le compas uniquement"],
        "L'équerre (pour la perpendiculaire)","L'équerre sert à tracer les perpendiculaires à l'axe."),
]})

# GEO-AXES-SYMM
blocks.append({"micro_skill_external_id":"GEO-AXES-SYMM::MS01","exercises":[
    ni("EX001","medium","Combien d'axes de symétrie possède un carré ?",4,"Le carré a 4 axes : 2 diagonales + 2 médiatrices des côtés."),
    mcq("EX002","medium","Les axes de symétrie du carré sont :",
        ["Ses 2 diagonales et les 2 médiatrices de ses côtés","Seulement ses diagonales","Seulement les médiatrices","1 seul axe"],
        "Ses 2 diagonales et les 2 médiatrices de ses côtés","Le carré a 4 axes de symétrie."),
    tr("EX003","medium","Trace les 4 axes de symétrie du carré.",{"min":0,"max":8,"step":1,"target":4},4,
        "2 diagonales + 2 médiatrices des côtés."),
    tf("EX004","easy","Le carré a exactement 4 axes de symétrie.",True,"2 diagonales + 2 médiatrices = 4 axes."),
]})

blocks.append({"micro_skill_external_id":"GEO-AXES-SYMM::MS02","exercises":[
    ni("EX001","medium","Combien d'axes de symétrie possède un rectangle qui n'est pas un carré ?",2,
        "Le rectangle (non carré) a 2 axes : les 2 médiatrices des côtés. Ses diagonales ne sont pas des axes de symétrie."),
    tf("EX002","medium","Les diagonales d'un rectangle (non carré) sont des axes de symétrie.",False,
        "Les diagonales d'un rectangle non carré ne sont PAS des axes de symétrie (les côtés adjacents n'ont pas la même longueur)."),
    tr("EX003","medium","Trace les 2 axes de symétrie du rectangle.",{"min":0,"max":8,"step":1,"target":4},4,
        "Les 2 axes passent par les milieux des côtés opposés."),
    mcq("EX004","medium","Les axes de symétrie du rectangle passent par :",
        ["Les milieux des côtés opposés","Les sommets","Les diagonales","N'importe quel point"],
        "Les milieux des côtés opposés","Les axes sont les médiatrices des côtés."),
]})

blocks.append({"micro_skill_external_id":"GEO-AXES-SYMM::MS03","exercises":[
    mcq("EX001","medium","Combien d'axes de symétrie possède un cercle ?",
        ["Une infinité","4","2","1"],"Une infinité","Tout diamètre est un axe de symétrie du cercle."),
    sa("EX002","medium","Pourquoi tout diamètre du cercle est-il un axe de symétrie ?",
        "Chaque diamètre sépare le cercle en deux demi-cercles identiques",
        "Un diamètre coupe le cercle en deux parties superposables.",
        acc=["diamètre coupe en deux","deux moitiés identiques","demi-cercles identiques"]),
    tf("EX003","easy","Le cercle a exactement 2 axes de symétrie.",False,
        "Le cercle a une infinité d'axes de symétrie (tout diamètre)."),
    mcq("EX004","medium","Quel est l'axe de symétrie d'un cercle ?",
        ["N'importe quel diamètre","Le rayon","La tangente","La corde"],
        "N'importe quel diamètre","Tout diamètre est un axe de symétrie du cercle."),
]})

blocks.append({"micro_skill_external_id":"GEO-AXES-SYMM::MS04","exercises":[
    order("EX001","medium","Range ces triangles par nombre d'axes de symétrie croissant.",
        ["Triangle scalène (0)","Triangle isocèle (1)","Triangle équilatéral (3)"],
        ["Triangle scalène (0)","Triangle isocèle (1)","Triangle équilatéral (3)"],
        "Scalène: 0, isocèle: 1, équilatéral: 3."),
    mcq("EX002","medium","Combien d'axes de symétrie possède un triangle équilatéral ?",["3","1","2","6"],"3",
        "Le triangle équilatéral a 3 axes de symétrie (les médiatrices de chaque côté)."),
    mcq("EX003","medium","Le triangle isocèle a :",
        ["1 axe de symétrie","2 axes de symétrie","3 axes de symétrie","Aucun axe"],
        "1 axe de symétrie","L'axe passe par le sommet principal et le milieu de la base."),
    tf("EX004","easy","Un triangle scalène (3 côtés différents) n'a aucun axe de symétrie.",True,
        "Avec 3 côtés de longueurs différentes, aucune droite ne peut être axe de symétrie."),
]})

# GEO-GLISSEMENT
blocks.append({"micro_skill_external_id":"GEO-GLISSEMENT::MS01","exercises":[
    mcq("EX001","medium","Un glissement (translation) consiste à :",
        ["Déplacer une figure sans la tourner ni la retourner","Tourner une figure","Retourner une figure","Agrandir une figure"],
        "Déplacer une figure sans la tourner ni la retourner","Une translation déplace sans rotation ni retournement."),
    tf("EX002","easy","Lors d'un glissement, la figure change de taille.",False,
        "Le glissement conserve la forme et la taille de la figure."),
    match("EX003","medium","Associe chaque transformation à sa description.",
        ["Glissement","Symétrie axiale","Rotation"],["Déplacer sans tourner","Retourner par rapport à un axe","Tourner autour d'un point"],
        {"Glissement":"Déplacer sans tourner","Symétrie axiale":"Retourner par rapport à un axe","Rotation":"Tourner autour d'un point"},
        "Glissement = déplacement, symétrie = retournement, rotation = tourner."),
    mcq("EX004","medium","Après un glissement, les longueurs sont :",
        ["Conservées","Doublées","Divisées par 2","Changées"],
        "Conservées","Le glissement est une isométrie."),
]})

blocks.append({"micro_skill_external_id":"GEO-GLISSEMENT::MS02","exercises":[
    mcq("EX001","medium","Le vecteur de glissement indique :",
        ["La direction, le sens et la distance du déplacement","Seulement la distance","Seulement la direction","La forme de la figure"],
        "La direction, le sens et la distance du déplacement","Le vecteur caractérise complètement le glissement."),
    fb("EX002","medium","Un vecteur de glissement a trois caractéristiques : ___, ___ et ___.","direction, sens, longueur",
        "Un vecteur est défini par sa direction, son sens et sa norme (longueur)."),
    tr("EX003","hard","Sur un quadrillage, le glissement est de 3 carreaux à droite et 2 carreaux vers le haut.",
        {"min":0,"max":10,"step":1,"target":3},3,"Le vecteur se décompose en composantes horizontale et verticale."),
    mcq("EX004","medium","Si le vecteur de glissement pointe vers la droite sur 5 cm, la figure se déplace :",
        ["De 5 cm vers la droite","De 5 cm vers la gauche","De 10 cm vers la droite","Elle ne bouge pas"],
        "De 5 cm vers la droite","Le sens du vecteur donne le sens du déplacement."),
]})

blocks.append({"micro_skill_external_id":"GEO-GLISSEMENT::MS03","exercises":[
    gs("EX001","hard","Construis l'image du triangle ABC par le glissement de vecteur (4 carreaux à droite, 2 carreaux en haut).",
        [{"instruction":"Déplace A de 4 carreaux à droite et 2 en haut → A'","expected":"A' placé"},
         {"instruction":"Déplace B de 4 carreaux à droite et 2 en haut → B'","expected":"B' placé"},
         {"instruction":"Déplace C de la même manière → C'","expected":"C' placé"},
         {"instruction":"Trace le triangle A'B'C'","expected":"Triangle image tracé"}],
        "Triangle A'B'C'","Chaque sommet est déplacé du même vecteur."),
    tr("EX002","hard","Déplace le point de 3 carreaux vers la droite.",
        {"min":0,"max":10,"step":1,"target":3},3,"On ajoute 3 à la coordonnée horizontale."),
    mcq("EX003","hard","Pour construire l'image d'une figure par glissement, on déplace :",
        ["Chaque sommet du même vecteur","Un seul sommet","Le centre de la figure","Les côtés seulement"],
        "Chaque sommet du même vecteur","Tous les points se déplacent du même vecteur."),
    tf("EX004","hard","Lors d'un glissement sur quadrillage, tous les points se déplacent du même nombre de carreaux.",True,
        "Le vecteur est le même pour tous les points."),
]})

blocks.append({"micro_skill_external_id":"GEO-GLISSEMENT::MS04","exercises":[
    tf("EX001","hard","Après un glissement, les longueurs des côtés sont conservées.",True,
        "Le glissement (translation) est une isométrie : il conserve les distances."),
    ec("EX002","hard","Un élève dit qu'après un glissement, l'aire du carré de 3 cm de côté devient 12 cm².",
        "Aire = 12 cm²","Aire = 9 cm²","Le glissement conserve les aires. 3² = 9 cm²."),
    mcq("EX003","hard","Après un glissement, les angles sont :",
        ["Conservés","Doublés","Réduits de moitié","Nuls"],
        "Conservés","Le glissement conserve les angles."),
    tf("EX004","hard","Un glissement modifie le périmètre d'un rectangle.",False,
        "Le glissement conserve toutes les mesures : longueurs, aires, angles, périmètres."),
]})

# GEO-RESEAUX-CONNEXE
blocks.append({"micro_skill_external_id":"GEO-RESEAUX-CONNEXE::MS01","exercises":[
    mcq("EX001","easy","Dans un réseau, les points sont appelés :",
        ["Sommets","Côtés","Arêtes","Faces"],"Sommets","Les points d'un réseau (graphe) sont les sommets."),
    fb("EX002","easy","Les liens entre les sommets d'un réseau sont appelés ___.","arêtes",
        "Les connexions entre sommets sont des arêtes."),
    ni("EX003","medium","Un réseau a 4 sommets : A, B, C, D. Les arêtes sont AB, BC, CD, DA, AC. Combien d'arêtes y a-t-il ?",5,
        "On compte les liens : AB, BC, CD, DA, AC = 5 arêtes."),
    mcq("EX004","medium","Dans un réseau de 3 sommets tous reliés entre eux, combien y a-t-il d'arêtes ?",
        ["3","6","2","1"],"3","AB, AC, BC = 3 arêtes."),
]})

blocks.append({"micro_skill_external_id":"GEO-RESEAUX-CONNEXE::MS02","exercises":[
    mcq("EX001","medium","Un réseau est connexe si :",
        ["On peut aller de n'importe quel sommet à n'importe quel autre en suivant les arêtes",
         "Tous les sommets sont reliés directement","Il y a autant de sommets que d'arêtes","Il n'a pas de cycle"],
        "On peut aller de n'importe quel sommet à n'importe quel autre en suivant les arêtes",
        "Un réseau connexe permet de relier n'importe quelle paire de sommets par un chemin."),
    tf("EX002","medium","Si chaque sommet d'un réseau a au moins une arête, le réseau est forcément connexe.",False,
        "Faux : on peut avoir deux groupes séparés où chaque sommet a une arête sans être connectés entre eux."),
    order("EX003","medium","4 villages A, B, C, D. Routes : A-B, B-C, C-D. Ce réseau est-il connexe ? Range les villages de A à D.",
        ["A","B","C","D"],["A","B","C","D"],"Oui, le réseau est connexe : A→B→C→D."),
    mcq("EX004","medium","Combien d'arêtes minimum faut-il pour relier 4 sommets en un réseau connexe ?",
        ["3","4","6","2"],"3","Avec 3 arêtes on peut faire une chaîne A-B-C-D (minimum = n-1 arêtes)."),
]})

blocks.append({"micro_skill_external_id":"GEO-RESEAUX-CONNEXE::MS03","exercises":[
    mcq("EX001","medium","Un réseau avec 5 sommets et deux groupes séparés de sommets est :",
        ["Non connexe","Connexe","Impossible","Complet"],"Non connexe",
        "S'il y a des sommets isolés (non reliés au reste), le réseau est non connexe."),
    fb("EX002","medium","Sommets : A,B,C,D,E. Arêtes : A-B, B-C, D-E. Les sommets ___ et ___ forment un sous-ensemble isolé.",
        "D et E","D et E ne sont reliés qu'entre eux, pas au groupe A-B-C.",blanks=["D","E"]),
    tf("EX003","medium","Un réseau où le sommet F n'est relié à aucun autre est non connexe.",True,
        "Un sommet isolé rend le réseau non connexe."),
    mcq("EX004","hard","Comment rendre connexe un réseau qui a 2 composantes séparées {A,B} et {C,D} ?",
        ["Ajouter une arête entre un sommet de chaque composante","Supprimer une arête","Ajouter un sommet isolé","Rien à faire"],
        "Ajouter une arête entre un sommet de chaque composante",
        "Une seule arête entre les deux composantes suffit à les connecter."),
]})

blocks.append({"micro_skill_external_id":"GEO-RESEAUX-CONNEXE::MS04","exercises":[
    gs("EX001","hard","Montre que le réseau {A,B,C,D} avec arêtes A-B, B-C, C-D, A-D est connexe en exhibant un chemin de A à C.",
        [{"instruction":"Pars du sommet A","expected":"A"},
         {"instruction":"Utilise l'arête A-B pour aller en B","expected":"A → B"},
         {"instruction":"Utilise l'arête B-C pour aller en C","expected":"A → B → C"}],
        "Chemin : A → B → C","On peut aller de A à C par le chemin A-B-C."),
    sa("EX002","hard","Réseau : sommets A,B,C,D,E ; arêtes A-B, A-C, C-D, D-E. Donne un chemin de B à E.",
        "B → A → C → D → E","B-A-C-D-E est un chemin valide.",acc=["B-A-C-D-E","B→A→C→D→E","B A C D E"]),
    jus("EX003","hard","Le réseau {A,B,C} avec arêtes A-B et B-C est-il connexe ? Justifie.",
        "Oui, il est connexe car on peut relier A à C par A→B→C",
        "De A on va à B (arête A-B), de B on va à C (arête B-C). Tout sommet est accessible.",
        rub="1pt: réponse correcte, 1pt: chemin exhibé"),
    mcq("EX004","hard","Pour prouver qu'un réseau de 4 sommets est connexe, combien de chemins minimum faut-il trouver ?",
        ["Un chemin entre chaque paire de sommets, soit 6 paires","4 chemins","1 chemin","2 chemins"],
        "Un chemin entre chaque paire de sommets, soit 6 paires",
        "Il faut montrer que chaque paire de sommets est connectée. C(4,2) = 6 paires."),
]})

# ── Assemble ──
payload = {
    "schema_version": "1.0",
    "metadata": {"domain": "Géométrie", "grade": "CM2", "country": "Bénin", "generated": True},
    "exercises": blocks,
}
total = sum(len(b["exercises"]) for b in blocks)
out = "backend/exercices_cm2_geometrie.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
print(f"✓ {out}: {len(blocks)} blocs, {total} exercices")
