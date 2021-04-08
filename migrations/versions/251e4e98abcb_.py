"""empty message

Revision ID: 251e4e98abcb
Revises: 1aac71002a28
Create Date: 2021-04-06 19:08:00.399916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '251e4e98abcb'
down_revision = '1aac71002a28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('advertise_viewed', sa.Column('device_id', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('advertise_viewed', 'device_id')
    # ### end Alembic commands ###
