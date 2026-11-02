from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from ..extensions import db
from ..models import Order, OrderItem, Payment, ProductVariant


class OrderValidationError(ValueError):
    pass


def get_available_variant(variant_id, product_id, quantity=1, lock=False):
    if quantity < 1:
        raise OrderValidationError("Quantity must be at least one.")

    statement = select(ProductVariant).where(
        ProductVariant.id == variant_id,
        ProductVariant.product_id == product_id,
        ProductVariant.is_active.is_(True),
    )
    if lock:
        statement = statement.with_for_update()
    variant = db.session.execute(statement).scalar_one_or_none()
    if variant is None:
        raise OrderValidationError("The selected product variant is not available.")
    if variant.stock_quantity < quantity:
        raise OrderValidationError("The selected variant does not have enough stock.")
    return variant


def create_pending_order(*, variant_id, product_id, quantity, payment_method, customer, checkout_token, user_id=None):
    existing_order = db.session.execute(
        select(Order).where(Order.checkout_token == checkout_token).with_for_update()
    ).scalar_one_or_none()
    if existing_order is not None:
        if existing_order.payment_method != payment_method:
            raise OrderValidationError("This checkout token cannot be reused for another payment method.")
        return existing_order

    variant = get_available_variant(variant_id, product_id, quantity, lock=True)
    unit_price = variant.effective_price
    subtotal = unit_price * quantity
    order_number = f"SZ-{uuid4().hex[:16].upper()}"

    order = Order(
        order_number=order_number,
        checkout_token=checkout_token,
        user_id=user_id,
        status="pending",
        payment_method=payment_method,
        payment_status="pending",
        subtotal=subtotal,
        shipping_fee=Decimal("0.00"),
        total_amount=subtotal,
        customer_name=customer["name"],
        customer_email=customer["email"],
        customer_phone=customer["phone"],
        shipping_address=customer["address"],
        shipping_city=customer["city"],
        shipping_state=customer["state"],
        shipping_postal_code=customer["postal_code"],
    )
    order.items.append(
        OrderItem(
            product_id=variant.product_id,
            product_variant_id=variant.id,
            product_name=variant.product.name,
            sku=variant.sku,
            size=variant.size,
            color=variant.color,
            unit_price=unit_price,
            quantity=quantity,
            line_total=subtotal,
        )
    )
    order.payment = Payment(
        provider="paytm" if payment_method == "paytm" else "cod",
        provider_order_id=order_number,
        amount=subtotal,
        status="pending",
    )
    db.session.add(order)
    db.session.flush()
    return order


def mark_order_paid(order, transaction_id=None, response_code=None, response_message=None):
    if order.payment_status == "paid":
        return order

    for item in order.items:
        variant = get_available_variant(item.product_variant_id, item.product_id, item.quantity, lock=True)
        variant.stock_quantity -= item.quantity

    order.status = "confirmed"
    order.payment_status = "paid"
    order.payment.status = "success"
    order.payment.provider_transaction_id = transaction_id
    order.payment.response_code = response_code
    order.payment.response_message = response_message
    order.payment.paid_at = datetime.utcnow()
    return order


def mark_order_cod(order):
    if order.payment_status != "pending":
        raise OrderValidationError("This order cannot be placed as COD.")
    for item in order.items:
        variant = get_available_variant(item.product_variant_id, item.product_id, item.quantity, lock=True)
        variant.stock_quantity -= item.quantity
    order.status = "confirmed"
    order.payment_status = "pending_cod"
    order.payment.status = "cod_pending"
    return order
