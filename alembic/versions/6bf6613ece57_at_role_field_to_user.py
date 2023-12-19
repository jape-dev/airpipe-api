"""at role field to user

Revision ID: 6bf6613ece57
Revises: 
Create Date: 2023-12-19 14:45:08.363098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bf6613ece57'
down_revision = None
branch_labels = None
depends_on = None


# Add role column to user table
def upgrade():
    # Add role column to user table
    op.add_column('users', sa.Column('role', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('users', 'role')
