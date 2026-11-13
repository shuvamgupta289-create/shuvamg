from ..extensions import db
from ..utils.time import utc_now


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        db.UniqueConstraint("order_number", name="uq_orders_order_number"),
        db.UniqueConstraint("checkout_token", name="orders_checkout_token_key"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(40), nullable=False, index=True)
    checkout_token = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending", server_default="pending")
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(30), nullable=False, default="pending", server_default="pending")
    stock_reserved = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    stock_deducted = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    shipping_fee = db.Column(db.Numeric(12, 2), nullable=False, default=0, server_default="0")
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="INR", server_default="INR")
    customer_name = db.Column(db.String(160), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    user = db.relationship("User", backref=db.backref("orders", lazy=True))
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = db.relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_name = db.Column(db.String(180), nullable=False)
    sku = db.Column(db.String(80), nullable=False)
    size = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(80))
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")
    product_variant = db.relationship("ProductVariant")


class Payment(db.Model):
    __tablename__ = "payments"
    __table_args__ = (
        db.UniqueConstraint("provider_order_id", name="uq_payments_provider_order_id"),
        db.UniqueConstraint("provider_transaction_id", name="uq_payments_provider_transaction_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    provider = db.Column(db.String(20), nullable=False)
    provider_order_id = db.Column(db.String(80), nullable=False, index=True)
    provider_transaction_id = db.Column(db.String(120))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending", server_default="pending")
    response_code = db.Column(db.String(50))
    response_message = db.Column(db.String(255))
    email_status = db.Column(db.String(20), nullable=False, default="pending", server_default="pending")
    email_error = db.Column(db.Text)
    email_sent_at = db.Column(db.DateTime(timezone=True))
    paid_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    order = db.relationship("Order", back_populates="payment")
