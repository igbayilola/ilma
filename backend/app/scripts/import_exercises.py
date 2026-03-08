"""CLI script to import exercises from a multi-micro-skill JSON file.

Usage:
    python -m app.scripts.import_exercises <path_to_json>
"""
import asyncio
import json
import sys

from app.db.session import AsyncSessionLocal
from app.schemas.content import ExerciseFileImportRequest
from app.services.exercise_import_service import import_exercises_file


async def run(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    payload = ExerciseFileImportRequest(**raw)
    print(f"Fichier valide — {len(payload.exercises)} bloc(s) micro-skill détecté(s).")

    async with AsyncSessionLocal() as session:
        result = await import_exercises_file(session, payload)

    print("\n── Exercise Import Results ──")
    print(f"  Micro-skills traités : {result.micro_skills_processed}")
    print(f"  Créées               : {result.created}")
    print(f"  Mises à jour         : {result.updated}")
    print(f"  Ignorées             : {result.skipped}")
    if result.errors:
        print(f"  Erreurs              : {len(result.errors)}")
        for err in result.errors:
            print(f"    - {err}")
    else:
        print("  Erreurs              : 0")
    print("Done.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.import_exercises <path_to_json>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(sys.argv[1]))


if __name__ == "__main__":
    main()
