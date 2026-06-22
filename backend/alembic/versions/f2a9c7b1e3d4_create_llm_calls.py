"""create llm_calls table (auditoria de prompt/resposta do LLM)

Revision ID: f2a9c7b1e3d4
Revises: 35deac28de31
Create Date: 2026-06-20
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "f2a9c7b1e3d4"
down_revision: str | None = "35deac28de31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_calls",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("analysis_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("call_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("model", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("prompt_chars", sa.Integer(), nullable=False),
        sa.Column("response_chars", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_llm_calls_analysis_id"), "llm_calls", ["analysis_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_llm_calls_analysis_id"), table_name="llm_calls")
    op.drop_table("llm_calls")
