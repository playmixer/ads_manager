"""empty message

Revision ID: 8cb85bb60b10
Revises: b48ec3d31993
Create Date: 2021-04-08 10:22:56.835529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cb85bb60b10'
down_revision = 'b48ec3d31993'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('time_end', sa.DATETIME(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'time_end')
    # ### end Alembic commands ###