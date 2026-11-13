from flask import Blueprint, render_template, request
from sqlalchemy import func, literal, or_

from ..extensions import db
from ..models import Order, User
from ..utils.search import escape_like_value
from .admin import admin_required

admin_customers_bp = Blueprint("admin_customers", __name__, url_prefix="/admin/customers")


@admin_customers_bp.get("")
@admin_required
def listing():
    search = request.args.get("search", "").strip()
    order_count = (
        db.session.query(func.count(Order.id))
        .filter(Order.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    query = User.query.filter(User.role == "customer")
    if search:
        pattern = f"%{escape_like_value(search)}%"
        query = query.filter(
            or_(
                User.email.ilike(pattern, escape="!"),
                User.first_name.ilike(pattern, escape="!"),
                User.last_name.ilike(pattern, escape="!"),
                func.trim(User.first_name + literal(" ") + User.last_name).ilike(pattern, escape="!"),
            )
        )
    pagination = (
        query.add_columns(order_count.label("order_count"))
        .order_by(User.created_at.desc(), User.id.desc())
        .paginate(page=max(request.args.get("page", 1, type=int) or 1, 1), per_page=25, error_out=False)
    )
    return render_template(
        "admin/customers/list.html",
        customers=pagination.items,
        pagination=pagination,
        search=search,
    )


@admin_customers_bp.get("/<int:customer_id>")
@admin_required
def detail(customer_id):
    customer = User.query.filter_by(id=customer_id, role="customer").first()
    if customer is None:
        return render_template("404.html"), 404
    orders = Order.query.filter_by(user_id=customer.id).order_by(Order.created_at.desc(), Order.id.desc()).all()
    return render_template("admin/customers/detail.html", customer=customer, orders=orders)
