"""adding youtube column

Revision ID: 3cf8952114cf
Revises: 6bf6613ece57
Create Date: 2024-01-05 15:34:59.357828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3cf8952114cf'
down_revision = '6bf6613ece57'
branch_labels = None
depends_on = None


def upgrade():
    # Add a new column youtube_refresh_token to the users table
    op.add_column('users', sa.Column('youtube_refresh_token', sa.String(), nullable=True), schema='public')

def downgrade():
    # Remove the youtube_refresh_token column from the users table
    op.drop_column('users', 'youtube_refresh_token', schema='public')
