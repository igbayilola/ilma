"""Generate exercise JSON files from curriculum data.

Usage:
    python scripts/generate_exercises.py NUM  # or OPS, GEO, MES
    python scripts/generate_exercises.py ALL  # generate all 4
"""
import json, sys, random, os

random.seed(42)

# Map French type names → engine enum values
TYPE_MAP = {
    "Choix multiples": "mcq", "QCM": "mcq",
    "Vrai/Faux": "true_false",
    "Compléter": "fill_blank",
    "Réponse numérique": "numeric_input",
    "Réponse courte": "short_answer",
    "Classement": "ordering",
    "Glisser-déposer": "matching",
    "Correction d'erreur": "error_correction",
    "Problème contextualisé": "contextual_problem",
    "Étapes guidées": "guided_steps",
    "Justification": "justification",
    "Tracer": "tracing",
    "Construction": "tracing",
}

DIFF_BY_INDEX = {1: "easy", 2: "easy", 3: "medium", 4: "medium",
                 5: "medium", 6: "hard", 7: "hard", 8: "hard"}

BLOOM_BY_INDEX = {1: "remember", 2: "remember", 3: "understand", 4: "apply",
                  5: "apply", 6: "analyze", 7: "evaluate", 8: "create"}


def load_curriculum(tag):
    path = f"cm2_maths/progamme_mathematiquesCM2_deeeep_{tag}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_types_for_ms(ms):
    """Get list of engine-type strings for a micro-skill."""
    raw = ms.get("recommended_exercise_types", [])
    types = []
    for r in raw:
        t = TYPE_MAP.get(r)
        if t and t not in types:
            types.append(t)
    # Ensure at least mcq
    if not types:
        types = ["mcq"]
    return types


def make_exercise(ms, ex_num, ex_type, domain_tag):
    """Create a single exercise dict for a micro-skill."""
    ms_id = ms["micro_skill_id"]
    ms_name = ms["micro_skill_name"]
    diff_idx = ms.get("difficulty_index", 3)
    difficulty = DIFF_BY_INDEX.get(diff_idx, "medium")
    bloom = BLOOM_BY_INDEX.get(diff_idx, "apply")

    eid = f"EX{ex_num:03d}"
    base = {
        "exercise_id": eid,
        "type": ex_type,
        "difficulty": difficulty,
        "points": 1 if difficulty == "easy" else (2 if difficulty == "medium" else 3),
        "time_limit_seconds": 45 if difficulty == "easy" else (60 if difficulty == "medium" else 90),
        "bloom_level": bloom,
        "ilma_level": f"ilma_{diff_idx}",
        "tags": [domain_tag, ms_id.split("::")[0]],
    }

    # Dispatch to type-specific generator
    gen = GENERATORS.get(ex_type, gen_mcq)
    return gen(base, ms_name, ms_id, ex_num, difficulty)


# ── Type-specific generators ──────────────────────────────

def gen_mcq(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Concernant « {ms_name} », quelle affirmation est correcte ?",
        "choices": [
            f"La réponse A est correcte pour {ms_name}",
            f"La réponse B est une erreur fréquente",
            f"La réponse C est incorrecte",
            f"La réponse D est un piège courant",
        ],
        "correct_answer": f"La réponse A est correcte pour {ms_name}",
        "explanation": f"La bonne réponse concerne {ms_name}. Les autres choix représentent des erreurs fréquentes.",
        "hint": f"Réfléchis à ce que signifie « {ms_name} ».",
    })
    return base


def gen_true_false(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Vrai ou Faux : L'exercice suivant illustre correctement « {ms_name} ».",
        "correct_answer": True,
        "explanation": f"C'est vrai. Cet énoncé illustre bien {ms_name}.",
        "hint": f"Pense à la définition de « {ms_name} ».",
    })
    return base


def gen_fill_blank(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Complète : Pour {ms_name}, la valeur manquante est ___.",
        "blanks": ["___"],
        "correct_answer": "la bonne valeur",
        "explanation": f"Il fallait compléter avec la valeur correcte liée à {ms_name}.",
        "hint": f"Applique la règle de {ms_name}.",
    })
    return base


def gen_numeric(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Calcule le résultat pour cet exercice de {ms_name}.",
        "tolerance": 0.01,
        "correct_answer": 42,
        "explanation": f"Le résultat correct est obtenu en appliquant {ms_name}.",
        "hint": f"Utilise la méthode apprise pour {ms_name}.",
    })
    return base


def gen_short_answer(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Réponds en une phrase : que signifie « {ms_name} » ?",
        "accepted_answers": [ms_name],
        "correct_answer": ms_name,
        "explanation": f"{ms_name} est un concept important en mathématiques CM2.",
        "hint": f"Réfléchis aux mots clés de « {ms_name} ».",
    })
    return base


def gen_ordering(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Range les éléments dans le bon ordre pour {ms_name}.",
        "items": ["Étape 1", "Étape 2", "Étape 3", "Étape 4"],
        "correct_answer": ["Étape 1", "Étape 2", "Étape 3", "Étape 4"],
        "explanation": f"L'ordre correct suit la logique de {ms_name}.",
        "hint": "Commence par la première étape logique.",
    })
    return base


def gen_matching(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Associe chaque élément de gauche à son correspondant pour {ms_name}.",
        "left_items": ["Élément A", "Élément B", "Élément C"],
        "right_items": ["Correspond à A", "Correspond à B", "Correspond à C"],
        "correct_answer": {"Élément A": "Correspond à A", "Élément B": "Correspond à B", "Élément C": "Correspond à C"},
        "explanation": f"Les associations correctes suivent les règles de {ms_name}.",
        "hint": "Cherche les liens logiques entre les deux colonnes.",
    })
    return base


def gen_error_correction(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Trouve et corrige l'erreur dans le calcul suivant lié à « {ms_name} ».",
        "erroneous_content": f"Calcul erroné pour {ms_name}",
        "correct_answer": f"Calcul corrigé pour {ms_name}",
        "explanation": f"L'erreur courante est liée à {ms_name}. La correction applique la bonne règle.",
        "hint": "Vérifie chaque étape du calcul.",
    })
    return base


def gen_contextual(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Problème : Résous ce problème en utilisant {ms_name}.",
        "sub_questions": [
            {"text": "Quelle est la donnée importante ?", "answer": "La donnée clé"},
            {"text": "Quel calcul faut-il faire ?", "answer": "Le calcul approprié"},
        ],
        "correct_answer": "Réponse complète au problème",
        "explanation": f"Ce problème se résout en appliquant {ms_name} étape par étape.",
        "hint": "Lis bien l'énoncé et repère les données utiles.",
    })
    return base


def gen_guided_steps(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Suis les étapes pour résoudre cet exercice de {ms_name}.",
        "steps": [
            {"instruction": "Étape 1 : Identifie les données", "expected": "Les données sont..."},
            {"instruction": "Étape 2 : Applique la méthode", "expected": "On applique..."},
            {"instruction": "Étape 3 : Calcule le résultat", "expected": "Le résultat est..."},
        ],
        "correct_answer": "Résultat final",
        "explanation": f"En suivant les étapes de {ms_name}, on arrive au bon résultat.",
        "hint": "Suis chaque étape dans l'ordre.",
    })
    return base


def gen_justification(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Justifie ta réponse : pourquoi cette méthode est correcte pour « {ms_name} » ?",
        "scoring_rubric": "1pt: identification correcte, 1pt: justification claire, 1pt: vocabulaire approprié",
        "correct_answer": f"La méthode est correcte car elle applique la règle de {ms_name}.",
        "explanation": f"Une bonne justification utilise le vocabulaire de {ms_name} et explique le raisonnement.",
        "hint": "Utilise des mots comme 'parce que', 'donc', 'car'.",
    })
    return base


def gen_tracing(base, ms_name, ms_id, n, diff):
    base.update({
        "text": f"Place ou trace l'élément demandé pour {ms_name}.",
        "number_line": {"min": 0, "max": 100, "step": 10, "target": 50},
        "correct_answer": 50,
        "explanation": f"Le tracé correct suit les règles de {ms_name}.",
        "hint": "Observe bien la graduation.",
    })
    return base


GENERATORS = {
    "mcq": gen_mcq, "true_false": gen_true_false, "fill_blank": gen_fill_blank,
    "numeric_input": gen_numeric, "short_answer": gen_short_answer,
    "ordering": gen_ordering, "matching": gen_matching,
    "error_correction": gen_error_correction, "contextual_problem": gen_contextual,
    "guided_steps": gen_guided_steps, "justification": gen_justification,
    "tracing": gen_tracing,
}


def generate_domain(tag, out_name):
    """Generate exercise file for a domain."""
    data = load_curriculum(tag)
    domain_name = data["domain"]["domain_name"]
    micro_skills = data["micro_skills"]

    blocks = []
    for ms in micro_skills:
        types = get_types_for_ms(ms)
        exercises = []
        for i, t in enumerate(types[:4], 1):  # max 4 exercises per MS
            ex = make_exercise(ms, i, t, tag)
            exercises.append(ex)
        blocks.append({
            "micro_skill_external_id": ms["micro_skill_id"],
            "exercises": exercises,
        })

    payload = {
        "schema_version": "1.0",
        "metadata": {
            "domain": domain_name,
            "grade": "CM2",
            "country": "Bénin",
            "generated": True,
        },
        "exercises": blocks,
    }

    out_path = f"backend/{out_name}"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    total = sum(len(b["exercises"]) for b in blocks)
    print(f"✓ {out_name}: {len(blocks)} blocs, {total} exercices")
    return total


DOMAINS = {
    "NUM": "exercices_cm2_numeration.json",
    "OPS": "exercices_cm2_operations.json",
    "GEO": "exercices_cm2_geometrie.json",
    "MES": "exercices_cm2_mesures.json",
}


if __name__ == "__main__":
    tag = sys.argv[1].upper() if len(sys.argv) > 1 else "ALL"
    # Project root is two levels up from this script (backend/scripts/ → project root)
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    if tag == "ALL":
        total = 0
        for t, name in DOMAINS.items():
            total += generate_domain(t, name)
        print(f"\nTotal: {total} exercices générés")
    elif tag in DOMAINS:
        generate_domain(tag, DOMAINS[tag])
    else:
        print(f"Unknown domain: {tag}. Use NUM, OPS, GEO, MES, or ALL")
        sys.exit(1)
