"""empty message

Revision ID: cea88de4e056
Revises: 17d988d54989
Create Date: 2025-02-24 09:22:34.153194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cea88de4e056'
down_revision = '17d988d54989'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
        batch_op.add_column(sa.Column('website', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('seeking_venue', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('genres')

    # ### end Alembic commands ###
