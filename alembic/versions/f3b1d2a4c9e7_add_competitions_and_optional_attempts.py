"""add_competitions_and_optional_attempts

Revision ID: f3b1d2a4c9e7
Revises: 8ed30049b774
Create Date: 2026-07-13 17:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3b1d2a4c9e7"
down_revision: Union[str, Sequence[str], None] = "8ed30049b774"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "competitions" not in tables:
        op.create_table(
            "competitions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("season", sa.String(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.create_index("ix_competitions_user_id", "competitions", ["user_id"])
        op.create_index("ix_competitions_user_id_name", "competitions", ["user_id", "name"], unique=True)

    if "game_stats" in tables:
        columns = {column["name"]: column for column in inspector.get_columns("game_stats")}
        indexes = {index["name"] for index in inspector.get_indexes("game_stats")}
        foreign_keys = {fk["name"] for fk in inspector.get_foreign_keys("game_stats") if fk.get("name")}

        with op.batch_alter_table("game_stats") as batch_op:
            if "competition_id" not in columns:
                batch_op.add_column(sa.Column("competition_id", sa.Integer(), nullable=True))
            if "ft_attempted" in columns:
                batch_op.alter_column("ft_attempted", existing_type=sa.Integer(), nullable=True)
            if "fg2_attempted" in columns:
                batch_op.alter_column("fg2_attempted", existing_type=sa.Integer(), nullable=True)
            if "fg3_attempted" in columns:
                batch_op.alter_column("fg3_attempted", existing_type=sa.Integer(), nullable=True)

            if "fk_game_stats_competition_id_competitions" not in foreign_keys:
                batch_op.create_foreign_key(
                    "fk_game_stats_competition_id_competitions",
                    "competitions",
                    ["competition_id"],
                    ["id"],
                )

        if "ix_game_stats_competition_id" not in indexes:
            op.create_index("ix_game_stats_competition_id", "game_stats", ["competition_id"])


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "game_stats" in tables:
        columns = {column["name"]: column for column in inspector.get_columns("game_stats")}
        indexes = {index["name"] for index in inspector.get_indexes("game_stats")}
        foreign_keys = {fk["name"] for fk in inspector.get_foreign_keys("game_stats") if fk.get("name")}

        if "ix_game_stats_competition_id" in indexes:
            op.drop_index("ix_game_stats_competition_id", table_name="game_stats")

        with op.batch_alter_table("game_stats") as batch_op:
            if "fk_game_stats_competition_id_competitions" in foreign_keys:
                batch_op.drop_constraint("fk_game_stats_competition_id_competitions", type_="foreignkey")

            if "competition_id" in columns:
                batch_op.drop_column("competition_id")
            if "ft_attempted" in columns:
                batch_op.alter_column("ft_attempted", existing_type=sa.Integer(), nullable=False)
            if "fg2_attempted" in columns:
                batch_op.alter_column("fg2_attempted", existing_type=sa.Integer(), nullable=False)
            if "fg3_attempted" in columns:
                batch_op.alter_column("fg3_attempted", existing_type=sa.Integer(), nullable=False)

    if "competitions" in tables:
        indexes = {index["name"] for index in inspector.get_indexes("competitions")}
        if "ix_competitions_user_id_name" in indexes:
            op.drop_index("ix_competitions_user_id_name", table_name="competitions")
        if "ix_competitions_user_id" in indexes:
            op.drop_index("ix_competitions_user_id", table_name="competitions")
        op.drop_table("competitions")
