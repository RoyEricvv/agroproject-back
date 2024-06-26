"""add saldo to consumo

Revision ID: 28473610335a
Revises: 15e95dc8e2b0
Create Date: 2024-06-17 18:42:23.540101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28473610335a'
down_revision = '15e95dc8e2b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ConsumoSanitario', schema=None) as batch_op:
        batch_op.add_column(sa.Column('saldo', sa.Double(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ConsumoSanitario', schema=None) as batch_op:
        batch_op.drop_column('saldo')

    # ### end Alembic commands ###
