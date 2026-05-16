"""Tests pour cleanup_domain_order (iter 21)."""
from app.scripts.cleanup_domain_order import TARGET_DOMAIN_ORDER


def test_target_mapping_couvre_maths():
    maths = TARGET_DOMAIN_ORDER["mathematiques"]
    expected = {
        "numeration",
        "operations",
        "grandeurs-et-mesures",
        "geometrie",
        "organisation-de-donnees",
        "proportionnalite",
        "preparation-au-cep",
    }
    assert set(maths.keys()) == expected


def test_target_mapping_valeurs_uniques_et_consecutives():
    """Les valeurs d'ordre doivent être 1..N sans doublon — sinon l'admin
    UI réaffiche des domaines dans un ordre arbitraire."""
    for subject_slug, mapping in TARGET_DOMAIN_ORDER.items():
        values = list(mapping.values())
        assert sorted(values) == list(range(1, len(values) + 1)), (
            f"{subject_slug}: ordre non-consécutif {values}"
        )


def test_preparation_cep_passe_en_dernier():
    """Le domaine CEP doit recevoir le plus grand `order` — c'est de la
    révision, on le place en fin de séquence pédagogique."""
    maths = TARGET_DOMAIN_ORDER["mathematiques"]
    max_order = max(maths.values())
    assert maths["preparation-au-cep"] == max_order


def test_numeration_first():
    """Programme MEMP CM2 : numération avant opérations, opérations avant le reste."""
    maths = TARGET_DOMAIN_ORDER["mathematiques"]
    assert maths["numeration"] == 1
    assert maths["operations"] == 2
