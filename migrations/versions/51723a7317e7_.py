"""empty message

Revision ID: 51723a7317e7
Revises: 0dd624b31518
Create Date: 2021-04-07 13:32:23.660286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51723a7317e7'
down_revision = '0dd624b31518'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('token', sa.String(length=200), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'token')
    # ### end Alembic commands ###