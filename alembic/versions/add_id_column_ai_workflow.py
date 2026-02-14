"""Add id column to ai_workflow_state if missing.

Revision ID: add_id_ai_workflow
Revises: add_thread_id
Create Date: 2026-02-06

Legacy ai_workflow_state may lack id (serial PK). This migration adds it.
"""
from alembic import op

revision = "add_id_ai_workflow"
down_revision = "add_thread_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add id column only if it doesn't exist (legacy schema may lack it)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'ai_workflow_state' AND column_name = 'id'
            ) THEN
                ALTER TABLE ai_workflow_state ADD COLUMN id SERIAL UNIQUE NOT NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE ai_workflow_state DROP COLUMN IF EXISTS id CASCADE")
