from functools import wraps
import hmac
import secrets
from datetime import datetime, timedelta

import click
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Order, Product, ProductVariant, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _csrf_token():
    token = session.get("admin_csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["admin_csrf_token"] = token
    return token


def _valid_csrf_token():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("admin_csrf_token", "")
    return bool(submitted and expected and hmac.compare_digest(submitted, expected))


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("admin_user_id")
        if user_id is None:
            return redirect(url_for("admin.login"))
        user = db.session.get(User, user_id)
        if user is None or not user.is_active or user.role != "admin":
            session.clear()
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.before_request
def protect_admin_posts():
    if request.method == "POST" and not _valid_csrf_token():
        return render_template("admin/login.html", error="Your form session expired. Please try again.", csrf_token=_csrf_token()), 400


@admin_bp.get("/login")
def login():
    if session.get("admin_user_id"):
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html", csrf_token=_csrf_token())


@admin_bp.post("/login")
def login_submit():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = User.query.filter_by(email=email, role="admin", is_active=True).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return render_template(
            "admin/login.html",
            error="Invalid administrator credentials.",
            csrf_token=_csrf_token(),
        ), 401

    session.clear()
    session.permanent = True
    session["admin_user_id"] = user.id
    session["admin_csrf_token"] = secrets.token_urlsafe(32)
    return redirect(url_for("admin.dashboard"))


@admin_bp.get("/")
@admin_required
def dashboard():
    low_stock_threshold = 5
    paid_sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(Order.payment_status == "paid").scalar() or 0
    today = datetime.utcnow().date()
    chart_start = datetime.combine(today - timedelta(days=6), datetime.min.time())
    sales_rows = (
        db.session.query(func.date(Order.created_at), func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.payment_status == "paid", Order.created_at >= chart_start)
        .group_by(func.date(Order.created_at))
        .all()
    )
    sales_by_day = {str(day): amount for day, amount in sales_rows}
    sales_overview = [
        {"label": (today - timedelta(days=offset)).strftime("%d %b"), "amount": sales_by_day.get(str(today - timedelta(days=offset)), 0)}
        for offset in range(6, -1, -1)
    ]
    max_sales = max((entry["amount"] for entry in sales_overview), default=0)
    for entry in sales_overview:
        entry["width"] = int((entry["amount"] / max_sales) * 100) if max_sales else 0
    recent_orders = Order.query.order_by(Order.created_at.desc(), Order.id.desc()).limit(8).all()
    low_stock = (
        ProductVariant.query.options(joinedload(ProductVariant.product))
        .filter(ProductVariant.stock_quantity.between(1, low_stock_threshold), ProductVariant.is_active.is_(True))
        .order_by(ProductVariant.stock_quantity, ProductVariant.id)
        .limit(8)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats={
            "products": Product.query.count(),
            "variants": ProductVariant.query.count(),
            "orders": Order.query.count(),
            "sales": paid_sales,
            "pending_orders": Order.query.filter_by(status="pending").count(),
            "low_stock": ProductVariant.query.filter(ProductVariant.stock_quantity.between(1, low_stock_threshold), ProductVariant.is_active.is_(True)).count(),
            "out_of_stock": ProductVariant.query.filter(ProductVariant.stock_quantity == 0, ProductVariant.is_active.is_(True)).count(),
        },
        recent_orders=recent_orders,
        low_stock_variants=low_stock,
        sales_overview=sales_overview,
        csrf_token=_csrf_token(),
    )


@admin_bp.post("/logout")
@admin_required
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


def register_admin_cli(app):
    @app.cli.command("create-admin")
    @click.option("--email", prompt=True, help="Administrator email address")
    @click.option("--first-name", prompt=True, help="Administrator first name")
    @click.option("--last-name", prompt=True, help="Administrator last name")
    def create_admin(email, first_name, last_name):
        """Create the first administrator without exposing the password."""
        email = email.strip().lower()
        if not email or "@" not in email:
            raise click.ClickException("A valid administrator email is required.")
        if User.query.filter_by(email=email).first() is not None:
            raise click.ClickException("A user with that email already exists.")

        password = click.prompt("Administrator password", hide_input=True, confirmation_prompt=True)
        if len(password) < 12:
            raise click.ClickException("Administrator password must be at least 12 characters.")

        db.session.add(
            User(
                email=email,
                password_hash=generate_password_hash(password),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                role="admin",
                is_active=True,
            )
        )
        db.session.commit()
        click.echo("Administrator created successfully.")
