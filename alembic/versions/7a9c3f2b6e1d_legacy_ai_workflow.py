"""Legacy ai_workflow_state schema (revision from external migration).

Revision ID: 7a9c3f2b6e1d
Revises: 355fa847a82f
Create Date: (legacy)

Placeholder so alembic can resolve DB state. Table already exists with
legacy columns (ingestion_output, architecture_context, etc.).
"""
from alembic import op

revision = "7a9c3f2b6e1d"
down_revision = "355fa847a82f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Table already exists; no-op
    pass


def downgrade() -> None:
    pass
