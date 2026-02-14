"""add ai_workflow_state table

Revision ID: add_ai_workflow
Revises: 355fa847a82f
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "add_ai_workflow"
down_revision = "355fa847a82f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_workflow_state",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_name", sa.String(length=100), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("current_state", sa.String(length=50), nullable=False),
        sa.Column("state_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_successful_state", sa.String(length=50), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("agent_outputs", JSONB, nullable=True),
        sa.Column("clarification_answers", JSONB, nullable=True),
        sa.Column("thread_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_name", "project_id"],
            ["projects.organization_name", "projects.project_id"],
            name="ai_workflow_state_project_fk",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ai_workflow_state")
