"""adding instagram column

Revision ID: f10b532b23d6
Revises: 3cf8952114cf
Create Date: 2024-01-07 11:06:49.661341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f10b532b23d6'
down_revision = '3cf8952114cf'
branch_labels = None
depends_on = None


def upgrade():
    # Add a new column instagram_access_token to the users table
    op.add_column('users', sa.Column('instagram_access_token', sa.String(), nullable=True), schema='public')

def downgrade():
    # Remove the instagram_access_token column from the users table
    op.drop_column('users', 'instagram_access_token', schema='public')
