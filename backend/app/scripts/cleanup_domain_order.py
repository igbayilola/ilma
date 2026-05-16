"""Cleanup `Domain.order` pour les domaines maths CM2.

Contexte : à la création du contenu, les 7 domaines maths ont été insérés
avec `order=1` (donnée historique). Les autres matières ont un ordre
pédagogique correct.

L'override `SUBJECT_DOMAIN_ORDER_OVERRIDE` du backfill iter 19 contournait
le problème. Ce script l'absorbe en base, après quoi l'override peut être
retiré et tout le reste du système (admin UI, FE explorer, fallback picker)
voit le bon ordre.

Idempotent : ne touche que les rows dont l'ordre diffère du mapping cible.

Usage :
    docker compose exec api python -m app.scripts.cleanup_domain_order
    docker compose exec api python -m app.scripts.cleanup_domain_order --dry-run
"""
from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.content import Subject

# Mapping cible (subject_slug → domain_slug → order pédagogique).
# Aligné sur le programme MEMP CM2. Les autres matières sont déjà OK et
# n'apparaissent pas ici.
TARGET_DOMAIN_ORDER: dict[str, dict[str, int]] = {
    "mathematiques": {
        "numeration": 1,
        "operations": 2,
        "grandeurs-et-mesures": 3,
        "geometrie": 4,
        "organisation-de-donnees": 5,
        "proportionnalite": 6,
        "preparation-au-cep": 7,
    },
}


async def cleanup(dry_run: bool = False, session=None) -> dict[str, int]:
    """Renvoie {subject_slug: nb de domaines mis à jour}.

    Si `session` est fourni (tests), on n'ouvre/ne commit pas.
    """
    owns_session = session is None
    if owns_session:
        session = AsyncSessionLocal()

    stats: dict[str, int] = {}
    unknown_domains: list[str] = []

    try:
        result = await session.execute(
            select(Subject)
            .where(Subject.slug.in_(list(TARGET_DOMAIN_ORDER.keys())))
            .options(selectinload(Subject.domains))
        )
        subjects = result.scalars().all()

        for subject in subjects:
            mapping = TARGET_DOMAIN_ORDER.get(subject.slug, {})
            updated = 0
            seen_slugs = set()
            for domain in subject.domains:
                seen_slugs.add(domain.slug)
                target = mapping.get(domain.slug)
                if target is None:
                    unknown_domains.append(f"{subject.slug}/{domain.slug}")
                    continue
                if domain.order != target:
                    domain.order = target
                    updated += 1
            # Domains présents dans le mapping mais absents en base — signal
            # que le mapping est obsolète vs. le contenu.
            for expected in mapping:
                if expected not in seen_slugs:
                    unknown_domains.append(
                        f"{subject.slug}/{expected} (dans mapping, absent en base)"
                    )
            stats[subject.slug] = updated

        if owns_session:
            if dry_run:
                await session.rollback()
            else:
                await session.commit()
    finally:
        if owns_session:
            await session.close()

    print("── Cleanup Domain.order ──")
    print(f"  Mode : {'DRY-RUN (rollback)' if dry_run else 'COMMIT'}")
    for slug, count in sorted(stats.items()):
        print(f"  {slug:38s} : {count} domaines réordonnés")
    if unknown_domains:
        print("  ⚠ Mismatch mapping/base :")
        for entry in unknown_domains:
            print(f"    - {entry}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Aucun commit")
    args = parser.parse_args()
    asyncio.run(cleanup(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
