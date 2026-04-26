"""initial tables - boards, columns, cards

Revision ID: 9123c949d241
Revises:
Create Date: 2026-04-26 08:14:12.465768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9123c949d241'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'boards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('admin_token', sa.String(36), nullable=False, index=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), server_default=''),
        sa.Column('template', sa.String(50), server_default='retrospective'),
        sa.Column('ttl_hours', sa.Integer(), server_default='24'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('password_hash', sa.String(128), nullable=True),
        sa.Column('is_readonly_default', sa.Boolean(), server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'columns',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('board_id', sa.String(36), sa.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(50), nullable=False),
        sa.Column('color', sa.String(20), server_default='default'),
        sa.Column('position', sa.Integer(), server_default='0'),
    )

    op.create_table(
        'cards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('column_id', sa.String(36), sa.ForeignKey('columns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('author_name', sa.String(30), server_default='Anonymous'),
        sa.Column('votes', sa.Integer(), server_default='0'),
        sa.Column('color', sa.String(20), server_default='yellow'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('cards')
    op.drop_table('columns')
    op.drop_table('boards')
