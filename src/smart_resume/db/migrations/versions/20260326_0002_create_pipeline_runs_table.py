"""create pipeline runs table

Revision ID: 20260326_0002
Revises: 20260326_0001
Create Date: 2026-03-26 23:55:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260326_0002"
down_revision = "20260326_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    json_type: sa.TypeEngine[object]
    if bind.dialect.name == "postgresql":
        json_type = postgresql.JSONB(astext_type=sa.Text())
    else:
        json_type = sa.JSON()

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("iterations_used", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("data", json_type, nullable=False),
        sa.Column("output_docx_path", sa.String(), nullable=True),
        sa.Column("output_pdf_path", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pipeline_runs_user_id"), "pipeline_runs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pipeline_runs_user_id"), table_name="pipeline_runs")
    op.drop_table("pipeline_runs")
