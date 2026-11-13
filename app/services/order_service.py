from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select, update

from ..extensions import db
from ..models import Order, OrderItem, Payment, Product, ProductVariant
from ..utils.time import utc_now


class OrderValidationError(ValueError):
    pass


def get_available_variant(variant_id, product_id, quantity=1, lock=False):
    if quantity < 1:
        raise OrderValidationError("Quantity must be at least one.")

    statement = (
        select(ProductVariant)
        .join(Product, Product.id == ProductVariant.product_id)
        .where(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
            ProductVariant.is_active.is_(True),
            Product.is_active.is_(True),
        )
    )
    if lock:
        statement = statement.with_for_update()
    variant = db.session.execute(statement).scalar_one_or_none()
    if variant is None:
        raise OrderValidationError("The selected product variant is not available.")
    if variant.stock_quantity < quantity:
        raise OrderValidationError("The selected variant does not have enough stock.")
    return variant


def create_pending_order(
    *,
    payment_method,
    customer,
    checkout_token,
    user_id=None,
    items=None,
    variant_id=None,
    product_id=None,
    quantity=1,
):
    existing_order = db.session.execute(
        select(Order).where(Order.checkout_token == checkout_token).with_for_update()
    ).scalar_one_or_none()
    if existing_order is not None:
        if existing_order.payment_method != payment_method:
            raise OrderValidationError("This checkout token cannot be reused for another payment method.")
        return existing_order

    requested_items = items
    if requested_items is None:
        requested_items = [{"variant_id": variant_id, "product_id": product_id, "quantity": quantity}]
    if not requested_items:
        raise OrderValidationError("Your cart is empty.")

    validated = []
    subtotal = Decimal("0.00")
    for requested in requested_items:
        try:
            selected_quantity = int(requested["quantity"])
            selected_variant_id = int(requested["variant_id"])
            selected_product_id = int(requested["product_id"])
        except (KeyError, TypeError, ValueError) as error:
            raise OrderValidationError("A cart item is invalid.") from error
        variant = get_available_variant(selected_variant_id, selected_product_id, selected_quantity, lock=True)
        unit_price = variant.effective_price
        line_total = unit_price * selected_quantity
        subtotal += line_total
        validated.append((variant, selected_quantity, unit_price, line_total))

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
    for variant, selected_quantity, unit_price, line_total in validated:
        order.items.append(
            OrderItem(
                product_id=variant.product_id,
                product_variant_id=variant.id,
                product_name=variant.product.name,
                sku=variant.sku,
                size=variant.size,
                color=variant.color,
                unit_price=unit_price,
                quantity=selected_quantity,
                line_total=line_total,
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
    if payment_method == "paytm":
        reserve_order_stock(order)
    return order


def reserve_order_stock(order):
    """Atomically reserve inventory for an unpaid Paytm order."""
    if order.stock_reserved or order.stock_deducted:
        return order
    for item in order.items:
        result = db.session.execute(
            update(ProductVariant)
            .where(
                ProductVariant.id == item.product_variant_id,
                ProductVariant.product_id == item.product_id,
                ProductVariant.is_active.is_(True),
                ProductVariant.stock_quantity >= item.quantity,
            )
            .values(stock_quantity=ProductVariant.stock_quantity - item.quantity)
        )
        if result.rowcount != 1:
            raise OrderValidationError("The selected variant no longer has enough stock.")
    order.stock_reserved = True
    return order


def release_order_stock(order):
    """Release a Paytm reservation or restore deducted stock once only."""
    if order.stock_reserved:
        for item in order.items:
            db.session.execute(
                update(ProductVariant)
                .where(ProductVariant.id == item.product_variant_id)
                .values(stock_quantity=ProductVariant.stock_quantity + item.quantity)
            )
        order.stock_reserved = False
    elif order.stock_deducted:
        for item in order.items:
            db.session.execute(
                update(ProductVariant)
                .where(ProductVariant.id == item.product_variant_id)
                .values(stock_quantity=ProductVariant.stock_quantity + item.quantity)
            )
        order.stock_deducted = False
    return order


def mark_order_failed(order, response_message=None):
    if order.payment_status in {"paid", "paid_needs_review", "failed", "expired"}:
        return order
    release_order_stock(order)
    order.status = "failed"
    order.payment_status = "failed"
    if order.payment is not None:
        order.payment.status = "failed"
        order.payment.response_message = (response_message or "Payment was not successful.")[:255]
    return order


def mark_order_paid(order, transaction_id=None, response_code=None, response_message=None):
    if order.payment_status in {"paid", "paid_needs_review"}:
        return order
    if order.stock_reserved:
        order.stock_reserved = False
        order.stock_deducted = True
    elif not order.stock_deducted:
        reserve_order_stock(order)
        order.stock_reserved = False
        order.stock_deducted = True

    order.status = "confirmed"
    order.payment_status = "paid"
    order.payment.status = "success"
    order.payment.provider_transaction_id = transaction_id
    order.payment.response_code = response_code
    order.payment.response_message = response_message
    order.payment.paid_at = utc_now()
    return order


def mark_order_cod(order):
    if order.payment_status != "pending":
        raise OrderValidationError("This order cannot be placed as COD.")
    for item in order.items:
        variant = get_available_variant(item.product_variant_id, item.product_id, item.quantity, lock=True)
        variant.stock_quantity -= item.quantity
    order.stock_deducted = True
    order.status = "confirmed"
    order.payment_status = "pending_cod"
    order.payment.status = "cod_pending"
    return order
