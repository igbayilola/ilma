"""Seed the database with curriculum data from a JSON file.

Usage (inside Docker):
    python -m scripts.seed_curriculum /data/progamme_mathematiquesCM2.json

The script is idempotent: it uses slug-based lookups to skip existing records.
"""

import asyncio
import json
import sys
import unicodedata
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import AsyncSessionLocal
from app.models.content import Subject, Domain, Skill


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


async def get_or_create(db: AsyncSession, model, defaults: dict, **lookup):
    """Return (instance, created) — lookup by unique fields, create if missing."""
    stmt = select(model)
    for k, v in lookup.items():
        stmt = stmt.where(getattr(model, k) == v)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if obj:
        return obj, False
    obj = model(**{**lookup, **defaults})
    db.add(obj)
    await db.flush()
    return obj, True


async def seed(json_path: str):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    subject_name = data["subject"]
    subject_slug = slugify(subject_name)

    async with AsyncSessionLocal() as db:
        async with db.begin():
            # 1. Subject
            subj, created = await get_or_create(
                db, Subject,
                defaults={"name": subject_name, "description": f"{data.get('grade', '')} - {data.get('country', '')}", "order": 0},
                slug=subject_slug,
            )
            status = "CREATED" if created else "EXISTS"
            print(f"[{status}] Subject: {subject_name} (slug={subject_slug}, id={subj.id})")

            # 2. Domains
            for d_idx, domain_data in enumerate(data.get("domains", [])):
                domain_name = domain_data["domain_name"]
                domain_slug = slugify(domain_data.get("domain_id", domain_name))

                dom, created = await get_or_create(
                    db, Domain,
                    defaults={"name": domain_name, "subject_id": subj.id, "description": None, "order": d_idx},
                    slug=domain_slug,
                )
                status = "CREATED" if created else "EXISTS"
                print(f"  [{status}] Domain: {domain_name} (slug={domain_slug}, id={dom.id})")

                # 3. Skills
                for s_idx, skill_data in enumerate(domain_data.get("skills", [])):
                    skill_name = skill_data["skill_name"]
                    skill_slug = slugify(skill_data.get("skill_id", skill_name))
                    skill_desc = skill_data.get("description", "")
                    ilma_path = skill_data.get("ilma_path", [])
                    if ilma_path:
                        skill_desc = f"{skill_desc}\n[Parcours ILMA : {' → '.join(ilma_path)}]".strip()

                    sk, created = await get_or_create(
                        db, Skill,
                        defaults={"name": skill_name, "domain_id": dom.id, "description": skill_desc, "order": s_idx},
                        slug=skill_slug,
                    )
                    status = "CREATED" if created else "EXISTS"
                    print(f"    [{status}] Skill: {skill_name} (slug={skill_slug})")

        print("\nSeed complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.seed_curriculum <path-to-json>")
        sys.exit(1)
    asyncio.run(seed(sys.argv[1]))
