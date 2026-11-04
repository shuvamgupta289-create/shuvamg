from datetime import datetime
from decimal import Decimal

from ..extensions import db


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (db.UniqueConstraint("slug", name="uq_categories_slug"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), nullable=False, index=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship("Product", back_populates="category")


class Brand(db.Model):
    __tablename__ = "brands"
    __table_args__ = (db.UniqueConstraint("slug", name="uq_brands_slug"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), nullable=False, index=True)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship("Product", back_populates="brand")


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (db.UniqueConstraint("slug", name="uq_products_slug"),)

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(1000))
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("Category", back_populates="products")
    brand = db.relationship("Brand", back_populates="products")
    variants = db.relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(db.Model):
    __tablename__ = "product_variants"
    __table_args__ = (db.UniqueConstraint("sku", name="uq_product_variants_sku"),)

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = db.Column(db.String(80), nullable=False, index=True)
    size = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(80))
    price = db.Column(db.Numeric(12, 2), nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", back_populates="variants")

    @property
    def effective_price(self) -> Decimal:
        return self.price if self.price is not None else self.product.base_price
