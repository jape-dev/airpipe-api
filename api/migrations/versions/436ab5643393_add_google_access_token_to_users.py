"""add google access token to users

Revision ID: 436ab5643393
Revises: 
Create Date: 2023-04-04 07:47:13.778339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '436ab5643393'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('google_access_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('facebook_access_token', sa.String(), nullable=True))
    op.drop_column('users', 'access_token')


def downgrade():
    op.drop_column('users', 'google_access_token')
    op.drop_column('users', 'facebook_access_token')
    op.add_column('users', sa.Column('access_token', sa.String(), nullable=True))

