"""added onboarding created at to user

Revision ID: ca40477c46b2
Revises: f10b532b23d6
Create Date: 2024-01-27 22:33:32.333337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca40477c46b2'
down_revision = 'f10b532b23d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('onboarding_stage_updated_at', sa.DateTime(), nullable=True), schema='public')


def downgrade():
    op.drop_column('onboarding_stage_updated_at', '', schema='public')
