"""Backfill `Skill.trimester` + `Skill.week_order` pour les compétences CM2.

Active le pivot UX « compagnon-annuel » (cf. iter 8-10) qui restait dormant
tant que `Skill.trimester` / `Skill.week_order` étaient NULL — le FE retombait
sur l'heuristique « premier skill non-maîtrisé » (cf. CurrentLessonHero.tsx).

Heuristique :
  - Skills d'un domain de préparation CEP (`preparation-cep-*`,
    `preparation-au-cep`) → trimestre 3 (révisions), répartis sur les 10 sem.
  - Autres skills → T1 (14 sem) puis T2 (13 sem), dans l'ordre
    (effective domain order, skill.order). 27 « slots-semaine » couvrent
    chaque matière.
  - Calage par index linéaire : slot = floor(i * total_slots / N).

Idempotent : ne réécrit jamais une valeur non-NULL existante. Le `--dry-run`
n'effectue aucun commit.

Usage :
    docker compose exec api python -m app.scripts.backfill_curriculum_sequencing
    docker compose exec api python -m app.scripts.backfill_curriculum_sequencing --dry-run
"""
from __future__ import annotations

import argparse
import asyncio
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.content import Domain, Subject

T1_WEEKS = 14
T2_WEEKS = 13
T3_WEEKS = 10
NON_CEP_SLOTS = T1_WEEKS + T2_WEEKS  # 27

CEP_DOMAIN_SLUGS = {
    "preparation-cep-francais",
    "preparation-cep-es",
    "preparation-cep-est",
    "preparation-au-cep",
}


@dataclass(frozen=True)
class SkillSequencingInput:
    subject_slug: str
    domain_slug: str
    domain_order: int
    skill_order: int
    skill_key: str  # identifiant opaque pour relier la sortie à la skill réelle


def _slot_to_trimester_week(slot: int) -> tuple[int, int]:
    """Mappe un index 0..26 vers (trimester, week) sur T1+T2."""
    if slot < T1_WEEKS:
        return 1, slot + 1
    return 2, slot - T1_WEEKS + 1


def compute_assignments(
    skills: list[SkillSequencingInput],
) -> dict[str, tuple[int, int]]:
    """Calcule {skill_key: (trimester, week_order)} pour un lot de skills.

    Logique pure (testable sans DB) : partitionne par matière, route les
    skills CEP-prep vers T3, distribue le reste sur T1+T2 dans l'ordre
    (domain.order, skill.order).
    """
    by_subject: dict[str, list[SkillSequencingInput]] = defaultdict(list)
    for sk in skills:
        by_subject[sk.subject_slug].append(sk)

    assignments: dict[str, tuple[int, int]] = {}
    for subject_slug, items in by_subject.items():
        non_cep = [s for s in items if s.domain_slug not in CEP_DOMAIN_SLUGS]
        cep = [s for s in items if s.domain_slug in CEP_DOMAIN_SLUGS]

        non_cep.sort(key=lambda s: (s.domain_order, s.skill_order))
        cep.sort(key=lambda s: (s.domain_order, s.skill_order))

        n = len(non_cep)
        for i, sk in enumerate(non_cep):
            slot = (i * NON_CEP_SLOTS) // max(n, 1)
            assignments[sk.skill_key] = _slot_to_trimester_week(slot)

        m = len(cep)
        for j, sk in enumerate(cep):
            assignments[sk.skill_key] = (3, (j * T3_WEEKS) // max(m, 1) + 1)

    return assignments


async def backfill(dry_run: bool = False, session=None) -> dict[str, int]:
    """Renvoie {subject_slug: nb de skills mis à jour}.

    Si `session` est fourni (tests), on l'utilise tel quel sans commit/rollback
    automatique — laisse l'appelant gérer la transaction.
    """
    owns_session = session is None
    if owns_session:
        session = AsyncSessionLocal()

    stats: dict[str, int] = defaultdict(int)
    skipped_already_set = 0
    total_active = 0

    try:
        result = await session.execute(
            select(Subject).options(
                selectinload(Subject.domains).selectinload(Domain.skills)
            )
        )
        subjects = result.scalars().all()

        inputs: list[SkillSequencingInput] = []
        skill_by_key = {}
        for subject in subjects:
            for domain in subject.domains:
                for sk in domain.skills:
                    if not sk.is_active:
                        continue
                    total_active += 1
                    if sk.trimester is not None and sk.week_order is not None:
                        skipped_already_set += 1
                        continue
                    key = str(sk.id)
                    skill_by_key[key] = (subject.slug, sk)
                    inputs.append(
                        SkillSequencingInput(
                            subject_slug=subject.slug,
                            domain_slug=domain.slug,
                            domain_order=domain.order or 0,
                            skill_order=sk.order or 0,
                            skill_key=key,
                        )
                    )

        assignments = compute_assignments(inputs)
        for key, (trimester, week) in assignments.items():
            subject_slug, sk = skill_by_key[key]
            if sk.trimester is None:
                sk.trimester = trimester
            if sk.week_order is None:
                sk.week_order = week
            stats[subject_slug] += 1

        if owns_session:
            if dry_run:
                await session.rollback()
            else:
                await session.commit()
    finally:
        if owns_session:
            await session.close()

    print("── Backfill curriculum sequencing ──")
    print(f"  Mode           : {'DRY-RUN (rollback)' if dry_run else 'COMMIT'}")
    print(f"  Skills actifs  : {total_active}")
    print(f"  Déjà séquencés : {skipped_already_set} (laissés intacts)")
    for slug, count in sorted(stats.items()):
        print(f"  {slug:38s} : {count} mis à jour")
    return dict(stats)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Aucun commit, juste le compteur")
    args = parser.parse_args()
    asyncio.run(backfill(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
