"""added ad_account_name to data_sources

Revision ID: 93e25f7f9906
Revises: f0892fcaf98e
Create Date: 2024-02-22 17:24:21.260594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93e25f7f9906'
down_revision = 'f0892fcaf98e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_sources', sa.Column('ad_account_name', sa.String(), nullable=True), schema='public')


def downgrade():
    op.drop_column('data_sources', 'ad_account_name', schema='public')
