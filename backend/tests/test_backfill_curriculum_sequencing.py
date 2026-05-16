"""Tests pour le backfill curriculum trimestre/semaine (iter 19)."""
from app.scripts.backfill_curriculum_sequencing import (
    CEP_DOMAIN_SLUGS,
    NON_CEP_SLOTS,
    T1_WEEKS,
    T3_WEEKS,
    SkillSequencingInput,
    compute_assignments,
)


def _mk(subject: str, domain: str, d_order: int, s_order: int, key: str) -> SkillSequencingInput:
    return SkillSequencingInput(
        subject_slug=subject,
        domain_slug=domain,
        domain_order=d_order,
        skill_order=s_order,
        skill_key=key,
    )


def test_cep_skills_routed_to_t3():
    inputs = [
        _mk("francais", "preparation-cep-francais", 1, 1, "cep-1"),
        _mk("francais", "preparation-cep-francais", 1, 2, "cep-2"),
        _mk("francais", "grammaire", 2, 1, "gram-1"),
    ]
    result = compute_assignments(inputs)
    assert result["cep-1"][0] == 3
    assert result["cep-2"][0] == 3
    assert result["gram-1"][0] in (1, 2)


def test_non_cep_distribution_spans_t1_and_t2():
    # 30 skills > 27 slots → toutes les positions T1+T2 visitées au moins une fois.
    inputs = [_mk("francais", "grammaire", 1, i, f"sk-{i}") for i in range(30)]
    result = compute_assignments(inputs)
    trimesters = {result[f"sk-{i}"][0] for i in range(30)}
    assert trimesters == {1, 2}
    # Le premier skill démarre en T1.W1, le dernier en T2.W13.
    assert result["sk-0"] == (1, 1)
    assert result["sk-29"] == (2, T1_WEEKS - 14 + 13)  # T2.W13


def test_assignments_respect_schema_bounds():
    """Trimester ∈ {1,2,3}, week_order ∈ {1..15} (cf. schemas/content.py)."""
    inputs = []
    for i in range(50):
        inputs.append(_mk("mathematiques", "numeration", 1, i, f"num-{i}"))
    for i in range(5):
        inputs.append(_mk("mathematiques", "preparation-au-cep", 1, i, f"cep-{i}"))
    result = compute_assignments(inputs)
    for trimester, week in result.values():
        assert trimester in (1, 2, 3)
        assert 1 <= week <= 15


def test_domain_order_drives_sequencing():
    """domain.order détermine l'ordre de slot ; skill.order est tie-break."""
    inputs = [
        _mk("mathematiques", "operations", 2, 1, "op-1"),
        _mk("mathematiques", "numeration", 1, 1, "num-1"),
    ]
    result = compute_assignments(inputs)
    num_pos = result["num-1"]
    op_pos = result["op-1"]
    assert (num_pos[0], num_pos[1]) <= (op_pos[0], op_pos[1])


def test_idempotent_on_empty_input():
    assert compute_assignments([]) == {}


def test_cep_slugs_set_complet():
    # Garde-fou : si on renomme un domaine CEP en base, le test rappelle de mettre à jour la liste.
    assert "preparation-au-cep" in CEP_DOMAIN_SLUGS
    assert "preparation-cep-francais" in CEP_DOMAIN_SLUGS


def test_non_cep_slots_constant():
    assert NON_CEP_SLOTS == T1_WEEKS + 13  # T2_WEEKS
    assert T3_WEEKS == 10
