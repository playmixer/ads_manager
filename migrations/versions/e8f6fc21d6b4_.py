"""empty message

Revision ID: e8f6fc21d6b4
Revises: 251e4e98abcb
Create Date: 2021-04-07 10:50:10.112120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f6fc21d6b4'
down_revision = '251e4e98abcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hash', sa.String(length=200), nullable=False))
    op.add_column('user', sa.Column('salt', sa.String(length=200), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'salt')
    op.drop_column('user', 'password_hash')
    # ### end Alembic commands ###
