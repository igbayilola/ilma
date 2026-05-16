"""Tests sur les bornes Pydantic de SkillBase / SkillUpdate (iter 27 P2).

Le calendrier scolaire CM2 (cf. frontend/utils/schoolCalendar.ts) a au
plus 14 semaines (T1). Un `week_order=15` n'est jamais affichable par le
picker, donc on resserre la borne `le=14` pour rejeter dès l'admin UI.
"""
import pytest
from pydantic import ValidationError

from app.schemas.content import SkillBase, SkillUpdate


def _base_payload(**overrides):
    base = {
        "name": "Test skill",
        "slug": "test-skill",
        "order": 1,
        "is_active": True,
    }
    base.update(overrides)
    return base


def test_week_order_accept_14():
    """T1 maxi = 14 semaines : la borne supérieure doit passer."""
    sk = SkillBase(**_base_payload(trimester=1, week_order=14))
    assert sk.week_order == 14


def test_week_order_reject_15():
    """15 sortait avant car le=15. Désormais rejeté (le=14)."""
    with pytest.raises(ValidationError):
        SkillBase(**_base_payload(trimester=1, week_order=15))


def test_week_order_reject_0():
    """1-indexé : 0 doit toujours être rejeté."""
    with pytest.raises(ValidationError):
        SkillBase(**_base_payload(trimester=1, week_order=0))


def test_skill_update_partial_respects_bounds():
    SkillUpdate(week_order=14)
    with pytest.raises(ValidationError):
        SkillUpdate(week_order=15)


def test_trimester_bounds_inchanged():
    SkillBase(**_base_payload(trimester=3, week_order=1))
    with pytest.raises(ValidationError):
        SkillBase(**_base_payload(trimester=4, week_order=1))
    with pytest.raises(ValidationError):
        SkillBase(**_base_payload(trimester=0, week_order=1))
