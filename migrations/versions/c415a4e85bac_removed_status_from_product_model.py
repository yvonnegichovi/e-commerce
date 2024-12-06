"""removed status from product model

Revision ID: c415a4e85bac
Revises: de0009e64a66
Create Date: 2024-12-04 18:01:35.526433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c415a4e85bac'
down_revision = 'de0009e64a66'
branch_labels = None
depends_on = None


def upgrade():
    # Remove the 'status' column from the 'products' table
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('status')


def downgrade():
    # Re-add the 'status' column to the 'products' table
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.VARCHAR(length=20), nullable=False))
    # ### end Alembic commands ###
