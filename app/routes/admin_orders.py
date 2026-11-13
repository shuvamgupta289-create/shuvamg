from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Order
from ..services.order_service import release_order_stock
from ..utils.search import escape_like_value
from .admin import _csrf_token, _valid_csrf_token, admin_required

admin_orders_bp = Blueprint("admin_orders", __name__, url_prefix="/admin/orders")

ORDER_STATUSES = ("pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "failed", "expired", "paid_needs_review")
STATUS_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"processing", "cancelled"},
    "processing": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
    "paid_needs_review": {"cancelled"},
    "failed": set(),
    "expired": set(),
}


@admin_orders_bp.before_request
def protect_order_posts():
    if request.method == "POST" and not _valid_csrf_token():
        return render_template("admin/login.html", error="Your form session expired. Please try again.", csrf_token=_csrf_token()), 400


@admin_orders_bp.get("")
@admin_required
def listing():
    query = Order.query.options(joinedload(Order.items)).order_by(Order.created_at.desc(), Order.id.desc())
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    payment_status = request.args.get("payment_status", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    if search:
        pattern = f"%{escape_like_value(search)}%"
        query = query.filter(or_(Order.order_number.ilike(pattern, escape="!"), Order.customer_name.ilike(pattern, escape="!"), Order.customer_email.ilike(pattern, escape="!")))
    if status in ORDER_STATUSES:
        query = query.filter(Order.status == status)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    if date_from:
        try:
            query = query.filter(Order.created_at >= datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc))
        except ValueError:
            date_from = ""
    if date_to:
        try:
            query = query.filter(Order.created_at < datetime.strptime(date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc))
        except ValueError:
            date_to = ""
    pagination = query.paginate(page=max(request.args.get("page", 1, type=int) or 1, 1), per_page=25, error_out=False)
    return render_template(
        "admin/orders/list.html",
        orders=pagination.items,
        pagination=pagination,
        statuses=ORDER_STATUSES,
        search=search,
        status=status,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
        csrf_token=_csrf_token(),
    )


@admin_orders_bp.get("/<int:order_id>")
@admin_required
def detail(order_id):
    order = Order.query.options(joinedload(Order.items)).filter_by(id=order_id).first()
    if order is None:
        return render_template("404.html"), 404
    return render_template("admin/orders/detail.html", order=order, statuses=ORDER_STATUSES, csrf_token=_csrf_token())


@admin_orders_bp.post("/<int:order_id>/status")
@admin_required
def update_status(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        return render_template("404.html"), 404
    next_status = request.form.get("status", "").strip()
    if next_status not in STATUS_TRANSITIONS.get(order.status, set()):
        return render_template("admin/orders/detail.html", order=order, statuses=ORDER_STATUSES, csrf_token=_csrf_token(), error="That order status transition is not allowed."), 400
    if next_status == "cancelled":
        release_order_stock(order)
        if order.payment_status in {"paid", "paid_needs_review"}:
            order.payment_status = "refund_pending"
            if order.payment is not None:
                order.payment.status = "refund_pending"
    order.status = next_status
    db.session.commit()
    return redirect(url_for("admin_orders.detail", order_id=order.id))
