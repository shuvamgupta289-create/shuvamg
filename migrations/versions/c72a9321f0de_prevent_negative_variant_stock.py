"""Prevent negative inventory quantities.

Revision ID: c72a9321f0de
Revises: b43e55b9a110
Create Date: 2026-11-13
"""
from alembic import op


revision = "c72a9321f0de"
down_revision = "b43e55b9a110"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.create_check_constraint(
            "ck_product_variants_stock_nonnegative", "stock_quantity >= 0"
        )


def downgrade():
    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.drop_constraint(
            "ck_product_variants_stock_nonnegative", type_="check"
        )
