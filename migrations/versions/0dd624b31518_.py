"""empty message

Revision ID: 0dd624b31518
Revises: e8f6fc21d6b4
Create Date: 2021-04-07 13:17:36.644566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dd624b31518'
down_revision = 'e8f6fc21d6b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sessions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('device_id', sa.String(length=200), nullable=True),
    sa.Column('ip', sa.String(length=15), nullable=True),
    sa.Column('time_created', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    # ### end Alembic commands ###
