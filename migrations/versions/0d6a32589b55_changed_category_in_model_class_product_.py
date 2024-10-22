"""changed category in model class Product from unique to False

Revision ID: 0d6a32589b55
Revises: 28522ef8442a
Create Date: 2024-10-22 22:31:12.988877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d6a32589b55'
down_revision = '28522ef8442a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint('products_category_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.create_unique_constraint('products_category_key', ['category'])

    # ### end Alembic commands ###