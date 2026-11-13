"""Track reserved and deducted order inventory.

Revision ID: b43e55b9a110
Revises: 0d7257d2ce69
Create Date: 2026-11-13
"""
from alembic import op
import sqlalchemy as sa


revision = "b43e55b9a110"
down_revision = "0d7257d2ce69"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders") as batch_op:
        batch_op.add_column(sa.Column("stock_reserved", sa.Boolean(), server_default=sa.false(), nullable=False))
        batch_op.add_column(sa.Column("stock_deducted", sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade():
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_column("stock_deducted")
        batch_op.drop_column("stock_reserved")
