"""Update Table grafana_sources and kibana_sources to include bearer_token based authentication

Revision ID: 2eb00a606d65
Revises: bc551387b797
Create Date: 2025-01-31 10:21:48.077480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2eb00a606d65'
down_revision: Union[str, None] = 'bc551387b797'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_sources', sa.Column('created_by_id', sa.Integer(), nullable=True))
    op.drop_constraint('data_sources_ibfk_1', 'data_sources', type_='foreignkey')
    op.create_foreign_key(None, 'data_sources', 'users', ['created_by_id'], ['id'])
    op.drop_column('data_sources', 'created_by')
    op.add_column('grafana_sources', sa.Column('bearer_token', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.alter_column('grafana_sources', 'auth_type',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Enum('BASIC', 'BEARER', name='authtype'),
               nullable=False)
    op.add_column('kibana_sources', sa.Column('bearer_token', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.alter_column('kibana_sources', 'auth_type',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.Enum('BASIC', 'BEARER', name='authtype'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('kibana_sources', 'auth_type',
               existing_type=sa.Enum('BASIC', 'BEARER', name='authtype'),
               type_=mysql.VARCHAR(length=255),
               nullable=True)
    op.drop_column('kibana_sources', 'bearer_token')
    op.alter_column('grafana_sources', 'auth_type',
               existing_type=sa.Enum('BASIC', 'BEARER', name='authtype'),
               type_=mysql.VARCHAR(length=255),
               nullable=True)
    op.drop_column('grafana_sources', 'bearer_token')
    op.add_column('data_sources', sa.Column('created_by', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'data_sources', type_='foreignkey')
    op.create_foreign_key('data_sources_ibfk_1', 'data_sources', 'users', ['created_by'], ['id'])
    op.drop_column('data_sources', 'created_by_id')
    # ### end Alembic commands ###
