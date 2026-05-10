"""Add app_config table with seed data.

Revision ID: k2b3c4d5e6f7
Revises: j1a2b3c4d5e6
Create Date: 2026-03-08 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "k2b3c4d5e6f7"
down_revision = "j1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE valuetype AS ENUM ('int', 'float', 'string', 'bool', 'json')")

    op.create_table(
        "app_config",
        sa.Column("key", sa.String(255), primary_key=True),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("category", sa.String(100), nullable=False, index=True),
        sa.Column("label", sa.String(255), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "value_type",
            postgresql.ENUM("int", "float", "string", "bool", "json", name="valuetype", create_type=False),
            nullable=False,
            server_default="string",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Seed default configuration values
    op.execute(
        """
        INSERT INTO app_config (key, value, category, label, description, value_type) VALUES
        ('freemium_daily_limit', '5', 'subscription', 'Limite quotidienne gratuit', 'Nombre d''exercices par jour pour les comptes gratuits', 'int'),
        ('smart_score_decay_rate', '0.05', 'scoring', 'Taux de décroissance', 'Pourcentage de décroissance hebdomadaire du SmartScore', 'float'),
        ('smart_score_streak_bonus', '0.02', 'scoring', 'Bonus série', 'Bonus par réponse correcte consécutive', 'float'),
        ('smart_score_max', '100', 'scoring', 'Score maximum', 'Score SmartScore maximum', 'int'),
        ('min_attempt_time_seconds', '2', 'anti_cheat', 'Temps minimum par question', 'Temps minimum en secondes pour valider une réponse (anti-triche)', 'int'),
        ('badge_streak_3_threshold', '3', 'badges', 'Seuil série 3', 'Nombre de réponses correctes consécutives pour le badge série 3', 'int'),
        ('badge_streak_10_threshold', '10', 'badges', 'Seuil série 10', 'Nombre de réponses correctes consécutives pour le badge série 10', 'int'),
        ('badge_mastery_threshold', '90', 'badges', 'Seuil maîtrise', 'Score minimum pour le badge maîtrise d''une compétence', 'int'),
        ('maintenance_mode', 'false', 'system', 'Mode maintenance', 'Activer le mode maintenance (503 pour toutes les requêtes)', 'bool'),
        ('registration_open', 'true', 'system', 'Inscriptions ouvertes', 'Autoriser les nouvelles inscriptions', 'bool'),
        ('min_app_version', '"1.0.0"', 'system', 'Version minimum', 'Version minimum de l''application requise', 'string'),
        ('promo_code_active', '""', 'marketing', 'Code promo actif', 'Code promotionnel actuellement actif', 'string'),
        ('monthly_price_xof', '2500', 'subscription', 'Prix mensuel (FCFA)', 'Prix de l''abonnement mensuel en FCFA', 'int'),
        ('payment_providers', '["kkiapay","fedapay"]', 'subscription', 'Fournisseurs paiement', 'Liste des fournisseurs de paiement actifs', 'json'),
        ('allowed_phone_prefixes', '["90","91","92","93","94","95","96","97"]', 'registration', 'Préfixes téléphone', 'Préfixes de numéros de téléphone autorisés (Bénin)', 'json')
        ON CONFLICT (key) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("app_config")
    op.execute("DROP TYPE IF EXISTS valuetype")
