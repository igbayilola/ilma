"""Convert legacy flat curriculum JSON (v1.x) to canonical v2.0 nested format.

Usage:
    python -m app.scripts.convert_legacy_json input.json > output.json
"""
import json
import sys


def convert(data: dict) -> dict:
    """Convert a legacy curriculum JSON to the v2.0 nested format."""
    subject_name = data.get("subject", "Mathématiques")
    grade_name = data.get("grade", "CM2")
    domain_info = data.get("domain", {})
    domain_name = domain_info.get("domain_name", "Numération")

    # Build micro_skill lookup: micro_skill_id -> definition
    ms_lookup: dict[str, dict] = {}
    for ms in data.get("micro_skills", []):
        ms_lookup[ms["micro_skill_id"]] = ms

    # Build skills with inline micro_skills
    skills_out = []
    for sk_idx, sk in enumerate(data.get("skills", []), start=1):
        micro_skills_out = []
        for ms_idx, ms_ext_id in enumerate(sk.get("micro_skill_ids_ordered", []), start=1):
            ms_def = ms_lookup.get(ms_ext_id)
            if not ms_def:
                continue
            micro_skills_out.append({
                "external_id": ms_ext_id,
                "name": ms_def["micro_skill_name"],
                "difficulty_index": ms_def.get("difficulty_index"),
                "estimated_time_minutes": ms_def.get("estimated_time_minutes"),
                "bloom_taxonomy_level": ms_def.get("bloom_taxonomy_level"),
                "mastery_threshold": ms_def.get("mastery_threshold"),
                "cep_frequency": ms_def.get("cep_frequency"),
                "prerequisites": ms_def.get("prerequisites_micro_skill_ids") or [],
                "recommended_exercise_types": ms_def.get("recommended_exercise_types") or [],
                "external_prerequisites": ms_def.get("external_prerequisites") or [],
                "order": ms_idx,
            })

        skills_out.append({
            "external_id": sk["skill_id"],
            "name": sk["skill_name"],
            "order": sk_idx,
            "cep_frequency": sk.get("cep_frequency"),
            "prerequisites": sk.get("prerequisites_skill_ids") or [],
            "common_mistakes": sk.get("common_mistakes") or [],
            "exercise_types": sk.get("exercise_types") or [],
            "mastery_threshold": sk.get("mastery_threshold"),
            "micro_skills": micro_skills_out,
        })

    # Derive slug from domain_id (e.g. MATH-CM2-NUM -> numeration via domain_name)
    domain_slug = domain_name.lower().strip()
    import re
    import unicodedata
    domain_slug = unicodedata.normalize("NFD", domain_slug)
    domain_slug = "".join(c for c in domain_slug if unicodedata.category(c) != "Mn")
    domain_slug = re.sub(r"[^a-z0-9\s-]", "", domain_slug)
    domain_slug = re.sub(r"[\s]+", "-", domain_slug)

    # Subject slug
    subject_slug = subject_name.lower().strip()
    subject_slug = unicodedata.normalize("NFD", subject_slug)
    subject_slug = "".join(c for c in subject_slug if unicodedata.category(c) != "Mn")
    subject_slug = re.sub(r"[^a-z0-9\s-]", "", subject_slug)
    subject_slug = re.sub(r"[\s]+", "-", subject_slug)

    # Grade slug
    grade_slug = grade_name.lower().strip()

    return {
        "schema_version": "2.0",
        "grade": {
            "name": grade_name,
            "slug": grade_slug,
            "description": f"{grade_name} — programme {data.get('country', 'BENIN')}",
        },
        "subjects": [
            {
                "name": subject_name,
                "slug": subject_slug,
                "icon": "calculator",
                "color": "#1E5AA8",
                "order": 1,
                "domains": [
                    {
                        "name": domain_name,
                        "slug": domain_slug,
                        "order": 1,
                        "skills": skills_out,
                    }
                ],
            }
        ],
    }


def _slugify(text: str) -> str:
    """Slug helper shared by converters."""
    import re
    import unicodedata
    text = unicodedata.normalize("NFD", text.lower().strip())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s]+", "-", text)[:120]


def convert_deep(data: dict, skip_domains: list[str] | None = None) -> dict:
    """Convert multi-domain *_deep.json* to v2.0 nested format.

    Micro-skills in this format are simple strings (not objects).
    Properties (bloom, difficulty, cep_frequency) are inherited from the parent skill.
    External IDs are generated as ``{skill_id}::MS{idx:02d}``.

    Args:
        data: The raw JSON dict from *_deep.json*.
        skip_domains: Optional list of domain_ids to skip (e.g. already imported with richer data).
    """
    subject_name = data.get("subject", "Mathématiques")
    grade_name = data.get("grade", "CM2")
    skip = set(skip_domains or [])

    domains_out = []
    for dom_idx, dom in enumerate(data.get("domains", []), start=1):
        dom_id = dom.get("domain_id", "")
        if dom_id in skip:
            continue

        skills_out = []
        for sk_idx, sk in enumerate(dom.get("skills", []), start=1):
            skill_id = sk["skill_id"]
            ms_strings = sk.get("micro_skills", [])

            micro_skills_out = []
            for ms_idx, ms_name in enumerate(ms_strings, start=1):
                ext_id = f"{skill_id}::MS{ms_idx:02d}"
                micro_skills_out.append({
                    "external_id": ext_id,
                    "name": ms_name,
                    "difficulty_index": sk.get("difficulty_index"),
                    "estimated_time_minutes": sk.get("estimated_time_minutes"),
                    "bloom_taxonomy_level": sk.get("bloom_taxonomy_level"),
                    "mastery_threshold": sk.get("mastery_threshold"),
                    "cep_frequency": sk.get("cep_frequency"),
                    "prerequisites": [],
                    "recommended_exercise_types": sk.get("exercise_types") or [],
                    "external_prerequisites": [],
                    "order": ms_idx,
                })

            skills_out.append({
                "external_id": skill_id,
                "name": sk["skill_name"],
                "order": sk_idx,
                "cep_frequency": sk.get("cep_frequency"),
                "prerequisites": sk.get("prerequisites") or [],
                "common_mistakes": sk.get("common_mistakes") or [],
                "exercise_types": sk.get("exercise_types") or [],
                "mastery_threshold": sk.get("mastery_threshold"),
                "micro_skills": micro_skills_out,
            })

        domains_out.append({
            "name": dom.get("domain_name", dom_id),
            "slug": _slugify(dom.get("domain_name", dom_id)),
            "order": dom_idx,
            "skills": skills_out,
        })

    return {
        "schema_version": "2.0",
        "grade": {
            "name": grade_name,
            "slug": grade_name.lower().strip(),
            "description": f"{grade_name} — programme {data.get('country', 'BENIN')}",
        },
        "subjects": [
            {
                "name": subject_name,
                "slug": _slugify(subject_name),
                "icon": "calculator",
                "color": "#1E5AA8",
                "order": 1,
                "domains": domains_out,
            }
        ],
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.convert_legacy_json <input.json>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    output = convert(data)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
