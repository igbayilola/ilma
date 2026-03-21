"""Seed micro-lessons for core CM2 math skills.

Revision ID: m4d5e6f7g8h9
Revises: l3c4d5e6f7g8
Create Date: 2026-03-08 14:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "m4d5e6f7g8h9"
down_revision = "l3c4d5e6f7g8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO micro_lessons (id, skill_id, title, content_html, summary, duration_minutes, "order", is_active)
        SELECT
            gen_random_uuid(),
            s.id,
            v.title,
            v.content_html,
            v.summary,
            v.duration_minutes,
            v.lesson_order,
            true
        FROM skills s
        JOIN (VALUES
            -- Calcul mental
            ('Calcul mental (tables, compléments, ×/÷10-100-1000)',
             'Les astuces du calcul mental',
             '<h2>Le calcul mental, c''est un super-pouvoir !</h2>
<p>Le calcul mental te permet de résoudre des opérations rapidement, sans crayon ni calculatrice. Voici les techniques essentielles :</p>
<h3>1. Les tables de multiplication</h3>
<p>Connaître ses tables de 2 à 9 par cœur est la base. Astuce : la table de 9 a un truc magique — les chiffres des dizaines montent (0,1,2,3...) et ceux des unités descendent (9,8,7,6...). Exemple : 9×3 = 27, 9×4 = 36.</p>
<h3>2. Les compléments à 10, 100, 1000</h3>
<p>Pour trouver le complément à 10 : pense au chiffre qui manque. 7 + ? = 10 → 3. Pour 100 : 63 + ? = 100 → 37 (complément des dizaines + complément des unités). Pour 1000 : même principe avec les centaines.</p>
<h3>3. Multiplier et diviser par 10, 100, 1000</h3>
<p>Multiplier par 10 = ajouter un zéro (ou déplacer la virgule d''un rang vers la droite). 25 × 10 = 250. Diviser par 10 = enlever un zéro (ou déplacer la virgule vers la gauche). 340 ÷ 10 = 34.</p>',
             'Le calcul mental repose sur 3 piliers : les tables de multiplication, les compléments (à 10, 100, 1000) et la multiplication/division par 10, 100, 1000.',
             5, 1),

            -- Techniques opératoires
            ('Techniques opératoires (entiers) : +, −, ×, ÷ (reste)',
             'Poser et résoudre les 4 opérations',
             '<h2>Les 4 opérations avec les nombres entiers</h2>
<h3>L''addition posée</h3>
<p>On aligne les chiffres par colonne (unités sous unités, dizaines sous dizaines...). On additionne de droite à gauche. Si le total dépasse 9, on pose le chiffre des unités et on retient la dizaine.</p>
<h3>La soustraction posée</h3>
<p>Même alignement. On soustrait de droite à gauche. Si le chiffre du haut est plus petit, on emprunte 1 dizaine au chiffre de gauche (qui diminue de 1).</p>
<h3>La multiplication posée</h3>
<p>On multiplie par chaque chiffre du multiplicateur, en décalant d''un rang à chaque ligne. Puis on additionne les résultats partiels.</p>
<h3>La division euclidienne</h3>
<p>On cherche combien de fois le diviseur « entre » dans le dividende. Le résultat est le quotient, ce qui reste est le reste. Vérification : dividende = quotient × diviseur + reste.</p>',
             'Les 4 opérations se posent en colonnes alignées. Addition et soustraction : de droite à gauche avec retenues/emprunts. Multiplication : par chaque chiffre avec décalage. Division : quotient × diviseur + reste = dividende.',
             5, 1),

            -- Nombres entiers
            ('Lire, écrire, décomposer et recomposer les nombres entiers (0 à 1 milliard)',
             'Les grands nombres jusqu''à 1 milliard',
             '<h2>Lire et écrire les grands nombres</h2>
<p>Les nombres sont organisés en classes de 3 chiffres :</p>
<p><strong>Milliards | Millions | Milliers | Unités</strong></p>
<p>Chaque classe a ses centaines, dizaines et unités. Pour lire 345 678 912, on dit : « trois-cent-quarante-cinq millions six-cent-soixante-dix-huit mille neuf-cent-douze ».</p>
<h3>Décomposer un nombre</h3>
<p>Décomposer, c''est séparer le nombre selon la valeur de chaque chiffre :</p>
<p>345 678 = 3×100 000 + 4×10 000 + 5×1 000 + 6×100 + 7×10 + 8</p>
<h3>Recomposer un nombre</h3>
<p>C''est l''inverse : à partir des valeurs, on reforme le nombre. 2×1 000 000 + 5×1 000 + 3×100 + 7 = 2 005 307.</p>',
             'Les nombres entiers s''organisent en classes (milliards, millions, milliers, unités) de 3 chiffres chacune. Décomposer = séparer par valeur de position. Recomposer = reformer le nombre.',
             4, 1),

            -- Nombres décimaux
            ('Nombres décimaux : écrire, représenter, encadrer et arrondir',
             'Comprendre les nombres décimaux',
             '<h2>Qu''est-ce qu''un nombre décimal ?</h2>
<p>Un nombre décimal a une partie entière et une partie décimale, séparées par une virgule : <strong>12,75</strong>. La partie entière est 12, la partie décimale est 75 (7 dixièmes et 5 centièmes).</p>
<h3>Les positions après la virgule</h3>
<p>1er rang : les <strong>dixièmes</strong> (1/10). 2e rang : les <strong>centièmes</strong> (1/100). 3e rang : les <strong>millièmes</strong> (1/1000).</p>
<h3>Encadrer un nombre décimal</h3>
<p>Encadrer à l''unité : 12,75 → 12 &lt; 12,75 &lt; 13. Encadrer au dixième : 12,75 → 12,7 &lt; 12,75 &lt; 12,8.</p>
<h3>Arrondir</h3>
<p>On regarde le chiffre après la position demandée. S''il est ≥ 5, on arrondit au-dessus. S''il est &lt; 5, on arrondit en dessous. 12,75 arrondi à l''unité = 13 (car 7 ≥ 5).</p>',
             'Un nombre décimal a une partie entière et décimale. Après la virgule : dixièmes, centièmes, millièmes. Arrondir : si le chiffre suivant ≥ 5, on monte.',
             5, 1),

            -- Comparer nombres décimaux
            ('Comparer et ordonner les nombres décimaux',
             'Comparer des nombres décimaux',
             '<h2>Comment comparer deux nombres décimaux ?</h2>
<p>Règle d''or : on compare d''abord les <strong>parties entières</strong>. Si elles sont égales, on compare chiffre par chiffre après la virgule.</p>
<h3>Exemple</h3>
<p>Comparons 3,45 et 3,5 :</p>
<p>Parties entières : 3 = 3 → on continue. Dixièmes : 4 &lt; 5 → donc <strong>3,45 &lt; 3,5</strong>.</p>
<h3>Attention au piège !</h3>
<p>3,5 n''est PAS plus petit que 3,45 même si 5 &lt; 45 ! Il faut comparer position par position. 3,5 = 3,50 et 50 centièmes &gt; 45 centièmes.</p>
<h3>Ordonner</h3>
<p>Pour ranger du plus petit au plus grand (ordre croissant), on compare deux par deux en utilisant la règle ci-dessus.</p>',
             'Pour comparer des décimaux : d''abord les parties entières, puis chiffre par chiffre après la virgule. Attention : 3,5 > 3,45 car 50 centièmes > 45 centièmes.',
             4, 1),

            -- Fractions
            ('Représenter et interpréter des fractions (partage, quotient, rapport)',
             'Les fractions : partager, mesurer, comparer',
             '<h2>Qu''est-ce qu''une fraction ?</h2>
<p>Une fraction représente une partie d''un tout. Elle s''écrit <strong>numérateur/dénominateur</strong>. Le dénominateur dit en combien de parts égales on découpe. Le numérateur dit combien de parts on prend.</p>
<h3>Trois façons de voir une fraction</h3>
<p><strong>1. Partage :</strong> 3/4 d''une pizza = on coupe en 4 parts et on en prend 3.</p>
<p><strong>2. Quotient :</strong> 3/4 = 3 ÷ 4 = 0,75. C''est le résultat de la division.</p>
<p><strong>3. Rapport :</strong> 3/4 des élèves = 3 élèves sur 4 sont concernés.</p>
<h3>Fractions sur la droite numérique</h3>
<p>On divise chaque unité en parts égales (selon le dénominateur) et on avance du nombre de parts indiqué par le numérateur. 5/4 = 1 unité entière + 1/4.</p>',
             'Une fraction = numérateur/dénominateur. Elle peut représenter un partage, un quotient (division) ou un rapport. Sur la droite numérique, on découpe les unités en parts égales.',
             5, 1),

            -- Fraction d'un nombre
            ('Prendre une fraction d''un nombre (fraction d''une quantité)',
             'Calculer la fraction d''un nombre',
             '<h2>Prendre une fraction d''un nombre</h2>
<p>Pour calculer une fraction d''un nombre, on utilise cette méthode simple :</p>
<p><strong>Étape 1 :</strong> On divise le nombre par le dénominateur.</p>
<p><strong>Étape 2 :</strong> On multiplie le résultat par le numérateur.</p>
<h3>Exemple : 3/4 de 60</h3>
<p>Étape 1 : 60 ÷ 4 = 15 (un quart de 60)</p>
<p>Étape 2 : 15 × 3 = 45 (trois quarts de 60)</p>
<p>Donc 3/4 de 60 = <strong>45</strong>.</p>
<h3>Formule rapide</h3>
<p>a/b de N = (a × N) ÷ b = (N ÷ b) × a</p>
<h3>Exemple concret</h3>
<p>Un livre de 120 pages. Tu as lu les 2/5. Combien de pages as-tu lues ? 120 ÷ 5 = 24, puis 24 × 2 = <strong>48 pages</strong>.</p>',
             'Pour prendre a/b d''un nombre N : diviser N par b, puis multiplier par a. Formule : (N ÷ b) × a.',
             4, 1),

            -- Résoudre des problèmes
            ('Résoudre des problèmes à une ou plusieurs étapes',
             'Méthode pour résoudre un problème',
             '<h2>La méthode en 4 étapes</h2>
<h3>1. Je lis et je comprends</h3>
<p>Lis l''énoncé 2 fois. Souligne les données importantes (nombres, unités). Identifie la question posée.</p>
<h3>2. Je cherche l''opération</h3>
<p>Demande-toi : est-ce que je dois ajouter, retirer, multiplier ou partager ? Les mots-clés t''aident : « en tout » → addition, « de moins » → soustraction, « chacun » → division, « fois plus » → multiplication.</p>
<h3>3. Je calcule</h3>
<p>Pose l''opération proprement. Pour les problèmes à plusieurs étapes, procède étape par étape. Le résultat d''une étape sert pour la suivante.</p>
<h3>4. Je vérifie</h3>
<p>Mon résultat est-il logique ? Ai-je mis la bonne unité ? Ai-je répondu à la question ?</p>',
             'Méthode en 4 étapes : 1) Lire et comprendre, 2) Choisir l''opération, 3) Calculer étape par étape, 4) Vérifier le résultat et l''unité.',
             5, 1),

            -- Convertir unités de longueur
            ('Convertir les unités de longueur',
             'Les unités de longueur et leurs conversions',
             '<h2>Le tableau des unités de longueur</h2>
<p>De la plus grande à la plus petite :</p>
<p><strong>km → hm → dam → m → dm → cm → mm</strong></p>
<p>Chaque unité est <strong>10 fois plus grande</strong> que la suivante.</p>
<h3>Convertir avec le tableau</h3>
<p>Place le chiffre des unités dans la colonne de l''unité donnée, puis complète avec des zéros jusqu''à la colonne de l''unité demandée.</p>
<h3>Exemples</h3>
<p>3,5 km = ? m → On va de km à m (3 colonnes vers la droite) → 3 500 m.</p>
<p>250 cm = ? m → On va de cm à m (2 colonnes vers la gauche) → 2,50 m.</p>
<h3>Conversions utiles à retenir</h3>
<p>1 km = 1 000 m | 1 m = 100 cm | 1 m = 10 dm | 1 cm = 10 mm</p>',
             'Les unités de longueur : km, hm, dam, m, dm, cm, mm. Chaque unité = 10× la suivante. Pour convertir : utilise le tableau, déplace la virgule.',
             4, 1),

            -- Périmètre et aire du disque
            ('Périmètre et aire du disque ; aire de figures décomposables',
             'Périmètre et aire du disque',
             '<h2>Le cercle et le disque</h2>
<p>Le <strong>cercle</strong> est la ligne courbe. Le <strong>disque</strong> est la surface à l''intérieur.</p>
<h3>Périmètre du cercle (circonférence)</h3>
<p><strong>P = π × d</strong> ou <strong>P = 2 × π × r</strong></p>
<p>Avec d = diamètre et r = rayon. π ≈ 3,14.</p>
<p>Exemple : un cercle de rayon 5 cm → P = 2 × 3,14 × 5 = <strong>31,4 cm</strong>.</p>
<h3>Aire du disque</h3>
<p><strong>A = π × r²</strong></p>
<p>Exemple : rayon 5 cm → A = 3,14 × 5² = 3,14 × 25 = <strong>78,5 cm²</strong>.</p>
<h3>Figures décomposables</h3>
<p>Pour calculer l''aire d''une figure complexe, on la découpe en figures simples (rectangles, triangles, demi-disques) et on additionne les aires.</p>',
             'Périmètre du cercle = π × d (ou 2πr). Aire du disque = π × r². π ≈ 3,14. Pour les figures complexes, on décompose en figures simples.',
             5, 1),

            -- Multiplier nombres décimaux
            ('Multiplier des nombres décimaux',
             'La multiplication des nombres décimaux',
             '<h2>Multiplier avec des décimaux</h2>
<h3>Méthode</h3>
<p><strong>Étape 1 :</strong> Ignore les virgules et multiplie comme des entiers.</p>
<p><strong>Étape 2 :</strong> Compte le nombre total de chiffres après la virgule dans les deux facteurs.</p>
<p><strong>Étape 3 :</strong> Place la virgule dans le résultat en comptant autant de chiffres depuis la droite.</p>
<h3>Exemple : 2,3 × 1,5</h3>
<p>Étape 1 : 23 × 15 = 345</p>
<p>Étape 2 : 2,3 a 1 chiffre après la virgule + 1,5 a 1 chiffre = 2 chiffres au total</p>
<p>Étape 3 : 345 → on place la virgule 2 rangs avant : <strong>3,45</strong></p>
<h3>Vérification rapide</h3>
<p>2 × 1,5 = 3 et 2,3 × 1,5 devrait être un peu plus → 3,45 ✓</p>',
             'Pour multiplier des décimaux : multiplier sans virgule, compter les chiffres après la virgule dans les deux facteurs, puis placer la virgule dans le résultat.',
             4, 1),

            -- Diviser nombres décimaux
            ('Diviser des nombres décimaux',
             'La division des nombres décimaux',
             '<h2>Diviser avec des décimaux</h2>
<h3>Cas 1 : Dividende décimal, diviseur entier</h3>
<p>On pose la division normalement. Quand on « descend » le premier chiffre après la virgule du dividende, on place la virgule dans le quotient.</p>
<p>Exemple : 15,6 ÷ 4 → 15 ÷ 4 = 3 reste 3. On descend le 6 → 36 ÷ 4 = 9. Résultat : <strong>3,9</strong>.</p>
<h3>Cas 2 : Diviseur décimal</h3>
<p>On transforme pour avoir un diviseur entier : on multiplie les deux nombres par 10 (ou 100).</p>
<p>Exemple : 7,2 ÷ 0,3 → (7,2 × 10) ÷ (0,3 × 10) = 72 ÷ 3 = <strong>24</strong>.</p>
<h3>Astuce</h3>
<p>Diviser par 0,5 revient à multiplier par 2. Diviser par 0,25 revient à multiplier par 4.</p>',
             'Division avec décimaux : si le diviseur est entier, placer la virgule au quotient quand on descend les décimales. Si le diviseur est décimal, multiplier les deux par 10 ou 100.',
             5, 1),

            -- Proportionnalité
            ('Reconnaître une situation de proportionnalité',
             'La proportionnalité : reconnaître et appliquer',
             '<h2>Qu''est-ce que la proportionnalité ?</h2>
<p>Deux grandeurs sont proportionnelles quand on passe de l''une à l''autre en multipliant toujours par le <strong>même nombre</strong> (le coefficient de proportionnalité).</p>
<h3>Comment reconnaître la proportionnalité ?</h3>
<p>On vérifie que tous les quotients correspondants sont égaux :</p>
<p>2 kg → 6 €, 5 kg → 15 €, 8 kg → 24 €. Vérifions : 6÷2 = 3, 15÷5 = 3, 24÷8 = 3 → OUI, c''est proportionnel (coefficient = 3).</p>
<h3>Attention aux pièges !</h3>
<p>L''âge et la taille ne sont PAS proportionnels : un bébé de 1 an mesure 75 cm, mais à 10 ans on ne mesure pas 750 cm !</p>
<h3>Passage à l''unité</h3>
<p>Méthode efficace : trouve le prix (ou la valeur) pour 1 unité, puis multiplie. 3 cahiers coûtent 1 200 F → 1 cahier = 400 F → 7 cahiers = 2 800 F.</p>',
             'Proportionnalité = même coefficient multiplicateur. Vérifier en divisant les valeurs correspondantes. Méthode du passage à l''unité : trouver la valeur pour 1, puis multiplier.',
             5, 1),

            -- Mesure d'angles
            ('Mesure d''angles',
             'Mesurer et tracer des angles',
             '<h2>Les angles</h2>
<h3>Les types d''angles</h3>
<p><strong>Angle droit</strong> = 90°. <strong>Angle aigu</strong> = moins de 90°. <strong>Angle obtus</strong> = entre 90° et 180°. <strong>Angle plat</strong> = 180°.</p>
<h3>Mesurer avec le rapporteur</h3>
<p>1. Place le centre du rapporteur sur le sommet de l''angle.</p>
<p>2. Aligne le 0° avec un des côtés de l''angle.</p>
<p>3. Lis la graduation où passe l''autre côté.</p>
<h3>Tracer un angle</h3>
<p>1. Trace un premier côté (une demi-droite).</p>
<p>2. Place le rapporteur, centre sur l''origine.</p>
<p>3. Marque un point à la graduation voulue.</p>
<p>4. Trace le second côté en reliant l''origine au point.</p>',
             'Angle droit = 90°, aigu < 90°, obtus > 90°, plat = 180°. Pour mesurer : centre du rapporteur sur le sommet, aligner le 0° sur un côté, lire l''autre côté.',
             4, 1),

            -- Tableau de proportionnalité
            ('Tableau de proportionnalité : compléter et résoudre',
             'Le tableau de proportionnalité',
             '<h2>Compléter un tableau de proportionnalité</h2>
<h3>Méthode 1 : Le coefficient</h3>
<p>Trouve le nombre par lequel on multiplie la 1ère ligne pour obtenir la 2e. Applique-le partout.</p>
<p>Exemple : 3 → 12, coefficient = 4. Donc 5 → 5×4 = 20.</p>
<h3>Méthode 2 : Le passage à l''unité</h3>
<p>Ramène à 1 dans la première ligne, puis multiplie. Si 4 → 20, alors 1 → 5, donc 7 → 35.</p>
<h3>Méthode 3 : Les propriétés</h3>
<p><strong>Additivité :</strong> Si 3→15 et 5→25, alors 8→40 (car 3+5=8 et 15+25=40).</p>
<p><strong>Multiplicativité :</strong> Si 4→12, alors 8→24 (×2) et 12→36 (×3).</p>
<h3>Produit en croix</h3>
<p>a/b = c/d → a×d = b×c. Utile pour trouver une valeur manquante : 3/12 = 5/? → ? = (12×5)÷3 = 20.</p>',
             'Pour compléter un tableau de proportionnalité : coefficient multiplicateur, passage à l''unité, additivité/multiplicativité, ou produit en croix.',
             5, 1)
        ) AS v(skill_name, title, content_html, summary, duration_minutes, lesson_order)
        ON s.name = v.skill_name
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM micro_lessons")
