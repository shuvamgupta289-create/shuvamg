from decimal import Decimal
from secrets import token_urlsafe
from urllib.parse import urlencode

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Product, ProductVariant
from ..models import User
from .customer_auth import customer_required
from ..services.order_service import OrderValidationError, create_pending_order, get_available_variant, mark_order_cod, mark_order_paid
from ..services.email_service import send_order_confirmation
from ..services.paytm_service import PaytmConfigurationError, PaytmGatewayError, initiate_transaction, verify_callback, verify_payment

checkout_bp = Blueprint("checkout", __name__)


def _checkout_error(message, status=400, product=None, variant=None, quantity=None, checkout_token=None):
    return render_template(
        "checkout.html",
        error=message,
        product=product,
        variant=variant,
        quantity=quantity,
        checkout_token=checkout_token,
    ), status


def _customer_details(form, user):
    fields = ("name", "email", "phone", "address", "city", "state", "postal_code")
    defaults = {
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "phone": user.phone or "",
        "address": user.address or "",
        "city": user.city or "",
        "state": user.state or "",
        "postal_code": user.postal_code or "",
    }
    values = {field: form.get(field, defaults[field]).strip() for field in fields}
    if any(not value for value in values.values()):
        raise OrderValidationError("Please complete all delivery details.")
    return values


def _selected_variant(form):
    try:
        product_id = int(form.get("product_id", ""))
        variant_id = int(form.get("variant_id", ""))
        quantity = int(form.get("quantity", "1"))
    except (TypeError, ValueError) as error:
        raise OrderValidationError("The selected product variant is invalid.") from error
    product = Product.query.options(joinedload(Product.brand), joinedload(Product.category)).filter_by(id=product_id, is_active=True).first()
    if product is None:
        raise OrderValidationError("The selected product is not available.")
    variant = get_available_variant(variant_id, product_id, quantity)
    return product, variant, quantity


def _checkout_token(form):
    token = form.get("checkout_token", "").strip()
    if not token:
        raise OrderValidationError("This checkout session is invalid. Please return to the product page.")
    return token


@checkout_bp.get("/checkout")
@customer_required
def checkout_page(user):
    if not request.args.get("product_id"):
        return render_template("checkout.html", error="Select a product and size before continuing.", user=user)
    try:
        product, variant, quantity = _selected_variant(request.args)
    except OrderValidationError as error:
        return _checkout_error(str(error))
    return render_template("checkout.html", product=product, variant=variant, quantity=quantity, user=user, checkout_token=token_urlsafe(32))


@checkout_bp.post("/checkout")
def checkout():
    user = db.session.get(User, session.get("customer_user_id")) if session.get("customer_user_id") else None
    if user is None or user.role != "customer" or not user.is_active:
        params = {key: request.form.get(key, "") for key in ("product_id", "variant_id", "quantity")}
        next_url = f"/checkout?{urlencode(params)}"
        return redirect(url_for("customer_auth.login", next=next_url))
    try:
        product, variant, quantity = _selected_variant(request.form)
    except OrderValidationError as error:
        return _checkout_error(str(error))
    return render_template("checkout.html", product=product, variant=variant, quantity=quantity, user=user, checkout_token=token_urlsafe(32))


@checkout_bp.post("/checkout/paytm")
@customer_required
def start_paytm_payment(user):
    product = variant = quantity = None
    checkout_token = request.form.get("checkout_token", "").strip()
    try:
        product, variant, quantity = _selected_variant(request.form)
        checkout_token = _checkout_token(request.form)
        customer = _customer_details(request.form, user)
        order = create_pending_order(
            variant_id=variant.id,
            product_id=product.id,
            quantity=quantity,
            payment_method="paytm",
            customer=customer,
            checkout_token=checkout_token,
            user_id=user.id,
        )
        checkout_data = initiate_transaction(order)
        db.session.commit()
    except (OrderValidationError, PaytmConfigurationError, PaytmGatewayError, ValueError) as error:
        db.session.rollback()
        return _checkout_error(str(error), product=product, variant=variant, quantity=quantity, checkout_token=checkout_token)
    except Exception:
        db.session.rollback()
        return _checkout_error("Paytm staging is temporarily unavailable.", 503, product, variant, quantity, checkout_token)

    return render_template(
        "paytm_checkout.html",
        merchant_id=current_app.config["PAYTM_MID"],
        order_id=checkout_data["order_id"],
        txn_token=checkout_data["txn_token"],
        amount=order.total_amount,
        checkout_js_url=current_app.config["PAYTM_CHECKOUT_JS_URL"],
    )


@checkout_bp.post("/checkout/cod")
@customer_required
def place_cod_order(user):
    product = variant = quantity = None
    checkout_token = request.form.get("checkout_token", "").strip()
    try:
        product, variant, quantity = _selected_variant(request.form)
        checkout_token = _checkout_token(request.form)
        customer = _customer_details(request.form, user)
        order = create_pending_order(
            variant_id=variant.id,
            product_id=product.id,
            quantity=quantity,
            payment_method="cod",
            customer=customer,
            checkout_token=checkout_token,
            user_id=user.id,
        )
        if order.payment_status == "pending_cod":
            return render_template("payment_result.html", order=order, title="Order confirmed", message="Your Cash on Delivery order has already been placed.")
        mark_order_cod(order)
        db.session.commit()
        send_order_confirmation(order.id)
    except OrderValidationError as error:
        db.session.rollback()
        return _checkout_error(str(error), product=product, variant=variant, quantity=quantity, checkout_token=checkout_token)
    except Exception:
        db.session.rollback()
        return _checkout_error("Unable to place the COD order.", 500, product, variant, quantity, checkout_token)

    return render_template("payment_result.html", order=order, title="Order confirmed", message="Your Cash on Delivery order has been placed.")


@checkout_bp.post("/payment/paytm/callback")
def paytm_callback():
    callback_data = request.form.to_dict()
    order_number = callback_data.get("ORDERID")
    if not order_number:
        return render_template("payment_result.html", title="Payment failed", message="Paytm returned an invalid order reference."), 400

    from ..models import Order

    order = Order.query.filter_by(order_number=order_number).with_for_update().first()
    if order is None:
        return render_template("payment_result.html", title="Payment failed", message="The payment order could not be found."), 404
    if order.payment_status == "paid":
        send_order_confirmation(order.id)
        return render_template("payment_result.html", order=order, title="Payment confirmed", message="This payment has already been confirmed.")

    try:
        if not verify_callback(callback_data):
            raise PaytmGatewayError("Paytm callback verification failed.")
        result_info, status_data = verify_payment(order.order_number)
        if result_info.get("resultStatus") != "TXN_SUCCESS":
            raise PaytmGatewayError("Paytm payment was not successful.")
        amount = status_data.get("txnAmount")
        if amount is None or Decimal(str(amount)) != order.total_amount:
            raise PaytmGatewayError("Paytm payment amount did not match the order.")
        mark_order_paid(
            order,
            transaction_id=status_data.get("txnId"),
            response_code=result_info.get("resultCode"),
            response_message=result_info.get("resultMsg"),
        )
        db.session.commit()
        send_order_confirmation(order.id)
    except PaytmGatewayError as error:
        db.session.rollback()
        return render_template("payment_result.html", order=order, title="Payment failed", message=str(error)), 400
    except Exception:
        db.session.rollback()
        return render_template("payment_result.html", title="Payment failed", message="Payment verification is temporarily unavailable."), 503

    return render_template("payment_result.html", order=order, title="Payment confirmed", message="Your Paytm payment has been confirmed.")
