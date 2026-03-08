"""CLI script to import a curriculum JSON file into the database.

Usage:
    python -m app.scripts.import_curriculum <path_to_json>
"""
import asyncio
import json
import sys

from app.db.session import AsyncSessionLocal
from app.schemas.content import CurriculumImportRequest
from app.services.curriculum_import_service import import_curriculum


async def run(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    payload = CurriculumImportRequest(**raw)

    async with AsyncSessionLocal() as session:
        result = await import_curriculum(session, payload)

    print("\n── Curriculum Import Results ──")
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
    print("Done.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.import_curriculum <path_to_json>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(sys.argv[1]))


if __name__ == "__main__":
    main()
