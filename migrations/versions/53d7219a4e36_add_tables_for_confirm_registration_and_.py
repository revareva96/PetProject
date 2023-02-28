"""add tables for confirm registration and recover password

Revision ID: 53d7219a4e36
Revises: 4eaf8797564a
Create Date: 2022-12-28 18:32:13.681151

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '53d7219a4e36'
down_revision = '4eaf8797564a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'users_confirm_registration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('confirm_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirm', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['data.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='data',
    )
    op.create_table(
        'users_recover_password',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('confirm_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirm', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['data.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='data',
    )
    op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=True), schema='data')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'admin', schema='data')
    op.drop_table('users_recover_password', schema='data')
    op.drop_table('users_confirm_registration', schema='data')
    # ### end Alembic commands ###
