"""add ctv session claim tokens

Revision ID: 9b1a2c3d4e5f
Revises: 676d2c3318fd
Create Date: 2026-02-25

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "9b1a2c3d4e5f"
down_revision: Union[str, None] = "676d2c3318fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ctvsession",
        sa.Column("claim_token_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column("ctvsession", sa.Column("claim_token_expires_at", sa.DateTime(), nullable=True))

    op.create_index(
        op.f("ix_ctvsession_claim_token_hash"),
        "ctvsession",
        ["claim_token_hash"],
        unique=False,
    )

    op.alter_column(
        "ctvsession",
        "pairing_code",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "ctvsession",
        "pairing_code",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
    )

    op.drop_index(op.f("ix_ctvsession_claim_token_hash"), table_name="ctvsession")
    op.drop_column("ctvsession", "claim_token_expires_at")
    op.drop_column("ctvsession", "claim_token_hash")

