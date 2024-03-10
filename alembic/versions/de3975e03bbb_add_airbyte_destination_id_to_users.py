"""add airbyte_destination_id to users

add airbyte_source_id to data_sources

Revision ID: de3975e03bbb
Revises: 93e25f7f9906
Create Date: 2024-03-09 21:26:19.393954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de3975e03bbb'
down_revision = '93e25f7f9906'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('airbyte_destination_id', sa.String(), nullable=True))
    op.add_column('data_sources', sa.Column('airbyte_source_id', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'airbyte_destination_id')
    op.drop_column('data_sources', 'airbyte_source_id')
