"""increase race_class column size

Revision ID: <auto_generated>
Revises: <previous_revision>
Create Date: <auto_generated>
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '<keep the auto-generated value>'
down_revision = '<keep the auto-generated value>'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Increase race_class from 50 to 200 characters
    op.alter_column(
        'races',
        'race_class',
        existing_type=sa.String(50),
        type_=sa.String(200),
        schema='racing'
    )

    # Also increase these while we're at it (they might have long values too)
    op.alter_column(
        'races',
        'age_restriction',
        existing_type=sa.String(50),
        type_=sa.String(100),
        schema='racing'
    )

    op.alter_column(
        'races',
        'sex_restriction',
        existing_type=sa.String(50),
        type_=sa.String(100),
        schema='racing'
    )

    op.alter_column(
        'races',
        'track_condition',
        existing_type=sa.String(50),
        type_=sa.String(100),
        schema='racing'
    )


def downgrade() -> None:
    # Revert back to original sizes
    op.alter_column(
        'races',
        'race_class',
        existing_type=sa.String(200),
        type_=sa.String(50),
        schema='racing'
    )

    op.alter_column(
        'races',
        'age_restriction',
        existing_type=sa.String(100),
        type_=sa.String(50),
        schema='racing'
    )

    op.alter_column(
        'races',
        'sex_restriction',
        existing_type=sa.String(100),
        type_=sa.String(50),
        schema='racing'
    )

    op.alter_column(
        'races',
        'track_condition',
        existing_type=sa.String(100),
        type_=sa.String(50),
        schema='racing'
    )