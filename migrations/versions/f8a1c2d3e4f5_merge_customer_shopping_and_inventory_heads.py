"""Merge customer-shopping and inventory-reservation heads.

Revision ID: f8a1c2d3e4f5
Revises: 7ac2d937e08b, c72a9321f0de
Create Date: 2026-11-13

This revision intentionally contains no schema operations.  It records that
both independently-created branches have been applied before subsequent
migrations are considered current.
"""


revision = "f8a1c2d3e4f5"
down_revision = ("7ac2d937e08b", "c72a9321f0de")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
