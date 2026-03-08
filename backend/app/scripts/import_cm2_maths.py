"""Import all CM2 Maths curriculum files from cm2_maths/ directory.

Reads the 7 domain JSON files (deeeep format), converts them to a single
v2.0 curriculum payload, and imports via the curriculum_import_service.

Usage:
    cd backend
    python -m app.scripts.import_cm2_maths
"""
import asyncio
import json
import sys
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.schemas.content import CurriculumImportRequest
from app.scripts.convert_legacy_json import convert, _slugify
from app.services.curriculum_import_service import import_curriculum

# Ordered list of domain files (pedagogical progression)
DOMAIN_FILES_ORDERED = [
    "progamme_mathematiquesCM2_deeeep_NUM.json",   # 1. Numération
    "progamme_mathematiquesCM2_deeeep_OPS.json",   # 2. Opérations
    "progamme_mathematiquesCM2_deeeep_GEO.json",   # 3. Géométrie
    "progamme_mathematiquesCM2_deeeep_MES.json",   # 4. Grandeurs et Mesures
    "progamme_mathematiquesCM2_deeeep_PROP.json",  # 5. Proportionnalité
    "progamme_mathematiquesCM2_deeeep_DATA.json",  # 6. Organisation de données
    "progamme_mathematiquesCM2_deeeep_CEP.json",   # 7. Préparation au CEP
]


def build_combined_payload(cm2_maths_dir: Path) -> dict:
    """Load all domain files and merge into a single v2.0 curriculum payload."""
    all_domains = []

    for dom_order, filename in enumerate(DOMAIN_FILES_ORDERED, start=1):
        filepath = cm2_maths_dir / filename
        if not filepath.exists():
            print(f"  SKIP: {filename} not found", file=sys.stderr)
            continue

        with open(filepath, encoding="utf-8") as f:
            raw = json.load(f)

        # Use convert() to get v2.0 format for this single-domain file
        converted = convert(raw)

        # Extract the domain (convert() always produces exactly 1 subject with 1 domain)
        domain = converted["subjects"][0]["domains"][0]
        domain["order"] = dom_order  # Override with correct cross-domain order

        domain_name = raw["domain"]["domain_name"]
        n_skills = len(raw.get("skills", []))
        n_ms = len(raw.get("micro_skills", []))
        print(f"  [{dom_order}] {domain_name}: {n_skills} skills, {n_ms} micro-skills")

        all_domains.append(domain)

    # Build the combined payload
    return {
        "schema_version": "2.0",
        "grade": {
            "name": "CM2",
            "slug": "cm2",
            "description": "CM2 — programme BENIN",
        },
        "subjects": [
            {
                "name": "Mathématiques",
                "slug": "mathematiques",
                "icon": "calculator",
                "color": "#1E5AA8",
                "order": 1,
                "domains": all_domains,
            }
        ],
    }


async def run(cm2_maths_dir: Path) -> None:
    print("── Loading CM2 Maths curriculum files ──")
    combined = build_combined_payload(cm2_maths_dir)

    n_domains = len(combined["subjects"][0]["domains"])
    n_skills = sum(len(d["skills"]) for d in combined["subjects"][0]["domains"])
    n_ms = sum(
        len(ms)
        for d in combined["subjects"][0]["domains"]
        for sk in d["skills"]
        for ms in [sk.get("micro_skills", [])]
    )
    print(f"\n  Total: {n_domains} domains, {n_skills} skills, {n_ms} micro-skills")

    print("\n── Validating payload ──")
    payload = CurriculumImportRequest(**combined)
    print("  Payload valid.")

    print("\n── Importing into database ──")
    async with AsyncSessionLocal() as session:
        result = await import_curriculum(session, payload)

    print("\n── Import Results ──")
    print(f"  Grade levels : {result.grade_levels}")
    print(f"  Subjects     : {result.subjects}")
    print(f"  Domains      : {result.domains}")
    print(f"  Skills       : {result.skills}")
    print(f"  Micro-skills : {result.micro_skills}")
    print(f"  Created      : {result.created}")
    print(f"  Updated      : {result.updated}")
    if result.errors:
        print(f"  Errors       : {len(result.errors)}")
        for err in result.errors:
            print(f"    - {err}")
    else:
        print("  Errors       : 0")
    print("\nDone.")


def main() -> None:
    # Default path: <project_root>/cm2_maths
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    cm2_maths_dir = project_root / "cm2_maths"

    if len(sys.argv) > 1:
        cm2_maths_dir = Path(sys.argv[1])

    if not cm2_maths_dir.is_dir():
        print(f"Error: directory not found: {cm2_maths_dir}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run(cm2_maths_dir))


if __name__ == "__main__":
    main()
