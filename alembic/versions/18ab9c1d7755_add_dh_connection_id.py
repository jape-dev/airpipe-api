"""add dh_connection_id

Revision ID: 18ab9c1d7755
Revises: ca40477c46b2
Create Date: 2024-02-10 14:09:08.445459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18ab9c1d7755'
down_revision = 'ca40477c46b2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_sources', sa.Column('dh_connection_id', sa.String(), nullable=True), schema='public')
    op.add_column('views', sa.Column('dh_connection_id', sa.String(), nullable=True), schema='public')



def downgrade():
    op.drop_column('data_sources', 'dh_connection_id', schema='public')
    op.drop_column('views', 'dh_connection_id', schema='public')
