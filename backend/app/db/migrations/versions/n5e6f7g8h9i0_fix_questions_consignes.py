"""Fix questions missing consignes, pedagogical errors, and ambiguous texts.

Audit found:
- 20 error_correction without instruction prefix
- 9 contextual_problem without question
- 3 guided_steps without instruction
- 3 numeric_input without instruction
- 8 ordering with generic text (not real duplicates, but text should include data)
- 1 tracing without instruction
- 2 trick error_corrections where student is actually correct

Revision ID: n5e6f7g8h9i0
Revises: m4d5e6f7g8h9
Create Date: 2026-03-08 16:00:00.000000

"""
from alembic import op

revision = "n5e6f7g8h9i0"
down_revision = "m4d5e6f7g8h9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ══════════════════════════════════════════════════════════
    # 1. ERROR_CORRECTION: Add "Identifie et corrige l'erreur."
    # ══════════════════════════════════════════════════════════

    # Bulk-prefix all error_correction that don't already have an instruction
    op.execute("""
        UPDATE questions
        SET text = 'Identifie et corrige l''erreur. ' || text
        WHERE question_type = 'error_correction'
          AND text NOT ILIKE '%corrige%'
          AND text NOT ILIKE '%identifie%'
          AND text NOT ILIKE '%trouve%erreur%'
          AND text NOT ILIKE '%rectifie%'
    """)

    # Fix trick question: "Erreur : 450 cm = 4,5 m." is actually CORRECT
    # Change to a real error
    op.execute("""
        UPDATE questions
        SET text = 'Identifie et corrige l''erreur. Un élève écrit : 450 cm = 45 m.',
            correct_answer = '"450 cm = 4,5 m (on divise par 100, pas par 10)"',
            explanation = 'Pour convertir cm en m, on divise par 100. 450 ÷ 100 = 4,5. L''élève a divisé par 10 au lieu de 100.'
        WHERE id = '898bc2db-4445-4f7c-80b7-80a4c5e84e84'
    """)

    # Fix trick question: "Un élève arrondit 3,45 à l'unité et obtient 3." is actually CORRECT
    # Change to a real error
    op.execute("""
        UPDATE questions
        SET text = 'Identifie et corrige l''erreur. Un élève arrondit 3,65 à l''unité et obtient 3.',
            correct_answer = '"3,65 ≈ 4 (car 0,65 ≥ 0,5, on arrondit au-dessus)"',
            explanation = 'Pour arrondir à l''unité, on regarde le chiffre des dixièmes. 6 ≥ 5, donc on arrondit 3,65 à 4.'
        WHERE id = '27b3d16f-8e49-484b-8608-5c310e46df84'
    """)

    # ══════════════════════════════════════════════════════════
    # 2. CONTEXTUAL_PROBLEM: Add specific questions
    # ══════════════════════════════════════════════════════════

    # Population Bénin/Togo
    op.execute("""
        UPDATE questions
        SET text = 'La population du Bénin est d''environ 13 350 000 habitants. Celle du Togo est d''environ 8 680 000 habitants. a) Quel pays est le plus peuplé ? b) Calcule la différence de population entre les deux pays.'
        WHERE id = '94fc109e-224a-45ec-a6bd-e12bf6cbdc7f'
    """)

    # Diagramme en bâtons - écoles de Cotonou
    op.execute("""
        UPDATE questions
        SET text = 'Un diagramme en bâtons montre les inscriptions dans 4 écoles de Cotonou (échelle : 1 carreau = 20 élèves). École Zinsou : 7 carreaux, École Béhanzin : 9 carreaux, École Soglo : 5 carreaux, École Kérékou : 8 carreaux. a) Quelle école a le plus d''élèves et combien ? b) Quelle est la différence entre l''école la plus grande et la plus petite ? c) Combien d''élèves y a-t-il au total ?'
        WHERE id = '1870a191-7b24-4d16-93ba-40f4f8e1bd90'
    """)

    # Moyenne arithmétique - marchand de Bohicon
    op.execute("""
        UPDATE questions
        SET text = 'Un marchand de Bohicon a vendu des sacs de maïs pendant 5 jours. Ventes par jour : 12, 18, 15, 20, 10 sacs. Calcule la vente moyenne quotidienne de ce marchand.'
        WHERE id = '15e90a2e-ea48-46e0-b925-31db08bbc4ae'
    """)

    # Graphique tissu pagne
    op.execute("""
        UPDATE questions
        SET text = 'Le graphique du prix du tissu pagne au marché de Cotonou montre une droite passant par (0 ; 0) et (3 ; 4 500). a) Quel est le prix d''un mètre de tissu ? b) Combien coûtent 7 mètres ? c) Avec un budget de 12 000 FCFA, combien de mètres peut-on acheter ?'
        WHERE id = '5729d97d-3070-474a-91fa-f10f1419fdb1'
    """)

    # Sènou achète du maïs
    op.execute("""
        UPDATE questions
        SET text = 'Sènou achète du maïs au marché de Parakou. Voici ses achats : 2 kg pour 400 FCFA, 5 kg pour 1 000 FCFA, 8 kg pour 1 600 FCFA. Cette situation est-elle proportionnelle ? Si oui, quel est le coefficient et combien coûtent 10 kg ?'
        WHERE id = 'a6e5a76d-c7b3-402f-82c8-26af744bbfd2'
    """)

    # Terrain rectangulaire
    op.execute("""
        UPDATE questions
        SET text = 'Un terrain rectangulaire fait 45 m de long et 30 m de large. On veut le clôturer (prix : 250 F/m) et semer du gazon (150 F/m²). Calcule : a) le coût de la clôture, b) le coût du gazon, c) le coût total.'
        WHERE id = '954ea847-85d8-4889-8a7f-7f9ce87c996e'
    """)

    # Camion Cotonou-Parakou
    op.execute("""
        UPDATE questions
        SET text = 'Un camion part de Cotonou vers Parakou à 50 km/h. La route fait 400 km. a) Quelle distance a-t-il parcourue après 3 h ? b) Après 5 h ? c) Au bout de combien de temps aura-t-il parcouru la moitié du trajet ?'
        WHERE id = '8ab21e41-5e15-4d4c-a4ec-bf60446745c1'
    """)

    # Kofi va à l'école
    op.execute("""
        UPDATE questions
        SET text = 'Kofi part de chez lui à 7 h 15 et arrive à l''école à 7 h 45. Il marche à 4 km/h. Calcule la durée du trajet et la distance entre sa maison et l''école.'
        WHERE id = '94e772e0-17e8-4da9-a06a-2ced4aa917d2'
    """)

    # Boulangerie de Parakou
    op.execute("""
        UPDATE questions
        SET text = 'À la boulangerie de Parakou, 6 pains coûtent 1 500 FCFA. Amina veut acheter des pains pour une fête. a) Quel est le prix d''un pain ? b) Combien coûtent 15 pains ? c) Avec 5 000 FCFA, combien de pains peut-elle acheter au maximum ?'
        WHERE id = 'cd2257c2-b4bf-44d9-a8c4-502a3903f669'
    """)

    # ══════════════════════════════════════════════════════════
    # 3. GUIDED_STEPS: Add instructions where missing
    # ══════════════════════════════════════════════════════════

    # Durée entre 22h30 et 6h15
    op.execute("""
        UPDATE questions
        SET text = 'Calcule la durée entre 22h30 et 6h15 (le lendemain).'
        WHERE id = '12a5dcc9-eaec-4d83-a6bb-90a639a50d59'
    """)

    # Aire d'une figure composée
    op.execute("""
        UPDATE questions
        SET text = 'Calcule l''aire de la figure composée : un rectangle de 8×5 avec un triangle rectangle (base 3, hauteur 5) collé sur un côté.'
        WHERE id = '269706d0-ee08-42f4-93eb-0aa0180458a1'
    """)

    # Bus - arrêts
    op.execute("""
        UPDATE questions
        SET text = 'Un bus transporte 45 élèves. Au 1er arrêt, 12 descendent et 8 montent. Au 2e arrêt, 15 descendent. Combien d''élèves reste-t-il dans le bus ?'
        WHERE id = 'b002d9ba-20f0-48bf-8aa3-1b8918ee0005'
    """)

    # ══════════════════════════════════════════════════════════
    # 4. NUMERIC_INPUT: Add instructions where missing
    # ══════════════════════════════════════════════════════════

    # Cylindre rayon 7
    op.execute("""
        UPDATE questions
        SET text = 'Calcule la longueur L du rectangle du patron pour un cylindre de rayon 7 cm. (Utilise π ≈ 3,14)'
        WHERE id = '9c477a7a-9031-4c15-ad2c-f35c1b16f81e'
    """)

    # Cylindre rayon 4
    op.execute("""
        UPDATE questions
        SET text = 'Calcule la longueur du rectangle du patron d''un cylindre de rayon 4 cm : L = 2×π×r = ?'
        WHERE id = 'ee33d084-2192-403b-acf2-7466208f546d'
    """)

    # Prix total
    op.execute("""
        UPDATE questions
        SET text = 'Calcule le prix total : 3 stylos à 75 F + 5 cahiers à 200 F + 1 sac à 2 500 F.'
        WHERE id = 'c07b1a55-d702-4271-837f-4f2721b5f3dd'
    """)

    # ══════════════════════════════════════════════════════════
    # 5. TRACING: Add instruction where missing
    # ══════════════════════════════════════════════════════════

    op.execute("""
        UPDATE questions
        SET text = 'Effectue le glissement du point sur le quadrillage : 3 carreaux à droite et 2 carreaux vers le haut.'
        WHERE id = '2a6a80ab-2b7b-4546-8068-0034a994c185'
    """)

    # ══════════════════════════════════════════════════════════
    # 6. ORDERING: Make generic texts specific with data
    # ══════════════════════════════════════════════════════════

    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre croissant : 0,7 ; 0,67 ; 0,076 ; 0,706.'
        WHERE id = '16ac24f6-a42a-4725-a039-cc5821dfc97a'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre croissant : 3,45 ; 3,405 ; 3,5 ; 3,045.'
        WHERE id = '7686b0cc-30ac-4877-aad4-fb4238e248a9'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre croissant : 12,099 ; 12,1 ; 12,009 ; 12,91.'
        WHERE id = '9bc51bd8-832e-4613-b360-a1205c00cc3d'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre croissant : 5,6 ; 5,2 ; 5,9 ; 5,1.'
        WHERE id = '3d998cc2-70cb-46d2-a2b5-54ad651b9509'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre décroissant : 0,5 ; 0,55 ; 0,505 ; 0,055.'
        WHERE id = 'a706bf2c-ed42-4649-93a3-c3606e74254e'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre décroissant : 2,45 ; 2,54 ; 2,405 ; 2,5.'
        WHERE id = 'fc55ac71-63ff-4fb2-8721-0e18a93a0c0f'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre décroissant : 8,01 ; 8,1 ; 8,001 ; 8,101.'
        WHERE id = '152058b4-26cc-429b-aecd-79c66e8bf2c8'
    """)
    op.execute("""
        UPDATE questions SET text = 'Range dans l''ordre décroissant : 7,3 ; 7,8 ; 7,1 ; 7,5.'
        WHERE id = '3a298ff4-387c-47d5-9f00-49aabd06fda6'
    """)


def downgrade() -> None:
    # Not reversible — original texts are lost
    pass
