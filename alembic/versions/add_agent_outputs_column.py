"""Add agent_outputs column to ai_workflow_state.

Revision ID: add_agent_outputs
Revises: 7a9c3f2b6e1d
Create Date: 2026-02-06

Adds agent_outputs JSONB column for DBs with legacy ai_workflow_state schema
(separate columns per stage instead of unified agent_outputs).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "add_agent_outputs"
down_revision = "7a9c3f2b6e1d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_workflow_state",
        sa.Column("agent_outputs", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ai_workflow_state", "agent_outputs")
