"""Add product images and customer shopping lists

Revision ID: 7ac2d937e08b
Revises: 5553345f2a2f
Create Date: 2026-11-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "7ac2d937e08b"
down_revision = "5553345f2a2f"
branch_labels = None
depends_on = None


PRODUCT_IMAGES = {
    "old-skool-classic": "https://assets.vans.com/images/t_img/c_fill,g_center,f_auto,h_2500,w_2000/v1747942442/VN000D3HY28-HERO/Old-Skool-Shoe-VANS-Black-White-HERO.png",
    "rs-x-heritage": "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_1200,h_1200/global/398210/03/sv01/fnd/PNA/fmt/png",
    "club-c-revenge": "https://www.reebok.com/cdn/shop/files/100032883_SLC_eCom.jpg?v=1764594542&width=1200",
    "574-core-trainer": "https://nb.scene7.com/is/image/NB/ml574evg_nb_02_i?$pdpflexf2$=&hei=1200&wid=1200",
    "air-max-dn8": "https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto%2Cu_9ddf04c7-2a9a-4d76-add1-d15af8f0263d%2Cc_scale%2Cfl_relative%2Cw_1.0%2Ch_1.0%2Cfl_layer_apply/76c32da1-45ce-4f1f-b7c8-3a4481d79eeb/AIR%2BMAX%2BDN8.png",
    "forum-low-classic": "https://assets.adidas.com/images/w_1200,f_auto,q_auto/c11bc0d2b836462bb787af9e013e3574_9366/Forum_Low_Shoes_White_IE7166_01_standard.jpg",
}


def upgrade():
    op.add_column("products", sa.Column("image_url", sa.String(length=1000), nullable=True))
    products = sa.table("products", sa.column("slug", sa.String()), sa.column("image_url", sa.String(length=1000)))
    for slug, image_url in PRODUCT_IMAGES.items():
        op.execute(products.update().where(products.c.slug == slug).values(image_url=image_url))

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_variant_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantity >= 1", name="ck_cart_items_positive_quantity"),
        sa.ForeignKeyConstraint(["product_variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_variant_id", name="uq_cart_items_user_variant"),
    )
    op.create_index(op.f("ix_cart_items_product_variant_id"), "cart_items", ["product_variant_id"], unique=False)
    op.create_index(op.f("ix_cart_items_user_id"), "cart_items", ["user_id"], unique=False)

    op.create_table(
        "wishlist_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlist_items_user_product"),
    )
    op.create_index(op.f("ix_wishlist_items_product_id"), "wishlist_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_wishlist_items_user_id"), "wishlist_items", ["user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_wishlist_items_user_id"), table_name="wishlist_items")
    op.drop_index(op.f("ix_wishlist_items_product_id"), table_name="wishlist_items")
    op.drop_table("wishlist_items")
    op.drop_index(op.f("ix_cart_items_user_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_product_variant_id"), table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_column("products", "image_url")
