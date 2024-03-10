"""add airbyte_connection_id to data_sources

Revision ID: b8ecf4830e28
Revises: de3975e03bbb
Create Date: 2024-03-09 22:38:15.444257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8ecf4830e28'
down_revision = 'de3975e03bbb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_sources', sa.Column('airbyte_connection_id', sa.String(), nullable=True))


def downgrade():
    op.drop_column('data_sources', 'airbyte_connection_id')
