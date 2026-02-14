"""Add thread_id column to ai_workflow_state.

Revision ID: add_thread_id
Revises: add_agent_outputs
Create Date: 2026-02-06

Adds thread_id column for LangGraph checkpointing.
"""
from alembic import op
import sqlalchemy as sa

revision = "add_thread_id"
down_revision = "add_agent_outputs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_workflow_state",
        sa.Column("thread_id", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ai_workflow_state", "thread_id")
