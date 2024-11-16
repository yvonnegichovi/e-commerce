"""changed load_user function

Revision ID: fb42231f8837
Revises: f3defe52b8d3
Create Date: 2024-11-13 16:41:39.077424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb42231f8837'
down_revision = 'f3defe52b8d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admin', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###