"""made view start and end date nullable

Revision ID: f0892fcaf98e
Revises: 18ab9c1d7755
Create Date: 2024-02-17 11:31:53.877585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0892fcaf98e'
down_revision = '18ab9c1d7755'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('views', 'start_date', nullable=True)
    op.alter_column('views', 'end_date', nullable=True)   


def downgrade():
    op.alter_column('views', 'start_date', nullable=False)
    op.alter_column('views', 'end_date', nullable=False)
