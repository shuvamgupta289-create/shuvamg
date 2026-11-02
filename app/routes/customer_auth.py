from functools import wraps
import hmac
import re
import secrets
from urllib.parse import urlencode, urlsplit

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Order, User

customer_auth_bp = Blueprint("customer_auth", __name__)


def customer_csrf_token():
    token = session.get("customer_csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["customer_csrf_token"] = token
    return token


def customer_csrf_valid():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("customer_csrf_token", "")
    return bool(submitted and expected and hmac.compare_digest(submitted, expected))


def customer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("customer_user_id")
        if user_id is None:
            next_url = request.full_path.rstrip("?")
            return redirect(url_for("customer_auth.login", next=next_url))
        user = db.session.get(User, user_id)
        if user is None or not user.is_active or user.role != "customer":
            session.pop("customer_user_id", None)
            return redirect(url_for("customer_auth.login", next=request.path))
        return view(user, *args, **kwargs)

    return wrapped


def safe_next_url(value):
    if not value:
        return url_for("customer_auth.account")
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or not value.startswith("/") or value.startswith("//"):
        return url_for("customer_auth.account")
    return value


def _profile_values(form):
    full_name = form.get("full_name", "").strip()
    email = form.get("email", "").strip().lower()
    phone = form.get("phone", "").strip()
    password = form.get("password", "")
    confirmation = form.get("confirm_password", "")
    if len(full_name.split()) < 2 or len(full_name) > 160:
        raise ValueError("Enter your first and last name.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")
    if not re.fullmatch(r"[0-9+()\- ]{7,30}", phone):
        raise ValueError("Enter a valid phone number.")
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters.")
    if password != confirmation:
        raise ValueError("Passwords do not match.")
    first_name, last_name = full_name.split(maxsplit=1)
    return first_name, last_name, email, phone, password


@customer_auth_bp.get("/register")
def register():
    if session.get("customer_user_id"):
        return redirect(url_for("customer_auth.account"))
    return render_template("auth/register.html", csrf_token=customer_csrf_token())


@customer_auth_bp.post("/register")
def register_submit():
    if not customer_csrf_valid():
        return render_template("auth/register.html", error="Your form session expired. Please try again.", csrf_token=customer_csrf_token()), 400
    try:
        first_name, last_name, email, phone, password = _profile_values(request.form)
        if User.query.filter_by(email=email).first() is not None:
            raise ValueError("An account with that email already exists.")
        user = User(first_name=first_name, last_name=last_name, email=email, phone=phone, password_hash=generate_password_hash(password), role="customer", is_active=True)
        db.session.add(user)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return render_template("auth/register.html", error=str(error), csrf_token=customer_csrf_token()), 400
    return redirect(url_for("customer_auth.login", registered="1"))


@customer_auth_bp.get("/login")
def login():
    if session.get("customer_user_id"):
        return redirect(url_for("customer_auth.account"))
    return render_template("auth/login.html", csrf_token=customer_csrf_token(), next_url=safe_next_url(request.args.get("next")))


@customer_auth_bp.post("/login")
def login_submit():
    if not customer_csrf_valid():
        return render_template("auth/login.html", error="Your form session expired. Please try again.", csrf_token=customer_csrf_token(), next_url=safe_next_url(request.form.get("next"))), 400
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = User.query.filter_by(email=email, role="customer", is_active=True).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return render_template("auth/login.html", error="Invalid email or password.", csrf_token=customer_csrf_token(), next_url=safe_next_url(request.form.get("next"))), 401
    destination = safe_next_url(request.form.get("next"))
    session.pop("admin_user_id", None)
    session.clear()
    session.permanent = True
    session["customer_user_id"] = user.id
    session["customer_csrf_token"] = secrets.token_urlsafe(32)
    return redirect(destination)


@customer_auth_bp.post("/logout")
@customer_required
def logout(user):
    if not customer_csrf_valid():
        return render_template("auth/login.html", error="Your form session expired. Please try again.", csrf_token=customer_csrf_token()), 400
    session.pop("customer_user_id", None)
    session.pop("customer_csrf_token", None)
    return redirect(url_for("main.home"))


@customer_auth_bp.get("/account")
@customer_required
def account(user):
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc(), Order.id.desc()).all()
    return render_template("account/dashboard.html", user=user, orders=orders, csrf_token=customer_csrf_token())


@customer_auth_bp.post("/account/profile")
@customer_required
def update_profile(user):
    if not customer_csrf_valid():
        flash("Your form session expired. Please try again.", "error")
        return redirect(url_for("customer_auth.account"))
    try:
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        if len(full_name.split()) < 2 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or not re.fullmatch(r"[0-9+()\- ]{7,30}", phone):
            raise ValueError("Enter a valid name, email, and phone number.")
        duplicate = User.query.filter(User.email == email, User.id != user.id).first()
        if duplicate is not None:
            raise ValueError("That email is already in use.")
        user.first_name, user.last_name = full_name.split(maxsplit=1)
        user.email = email
        user.phone = phone
        user.address = request.form.get("address", "").strip() or None
        user.city = request.form.get("city", "").strip() or None
        user.state = request.form.get("state", "").strip() or None
        user.postal_code = request.form.get("postal_code", "").strip() or None
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        flash(str(error), "error")
        return redirect(url_for("customer_auth.account"))
    flash("Your profile details were saved.", "success")
    return redirect(url_for("customer_auth.account"))


@customer_auth_bp.get("/account/orders/<int:order_id>")
@customer_required
def order_detail(user, order_id):
    order = Order.query.filter_by(id=order_id, user_id=user.id).first()
    if order is None:
        return render_template("404.html"), 404
    return render_template("account/order_detail.html", user=user, order=order, csrf_token=customer_csrf_token())
