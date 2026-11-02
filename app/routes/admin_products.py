from decimal import Decimal, InvalidOperation
import re

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Brand, Category, OrderItem, Product
from .admin import _csrf_token, _valid_csrf_token, admin_required

admin_products_bp = Blueprint("admin_products", __name__, url_prefix="/admin/products")


@admin_products_bp.before_request
def protect_product_posts():
    if request.method == "POST" and not _valid_csrf_token():
        return render_template("admin/login.html", error="Your form session expired. Please try again.", csrf_token=_csrf_token()), 400


def _product_form_values(form):
    name = form.get("name", "").strip()
    slug = form.get("slug", "").strip().lower()
    description = form.get("description", "").strip() or None
    if not name or len(name) > 180:
        raise ValueError("Product name is required and must be 180 characters or fewer.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 200:
        raise ValueError("Slug must use lowercase letters, numbers, and single hyphens.")
    try:
        brand_id = int(form.get("brand_id", ""))
        category_id = int(form.get("category_id", ""))
        base_price = Decimal(form.get("base_price", ""))
    except (TypeError, ValueError, InvalidOperation) as error:
        raise ValueError("Brand, category, and a valid price are required.") from error
    if base_price <= 0 or base_price.as_tuple().exponent < -2:
        raise ValueError("Price must be greater than zero with no more than two decimals.")
    if db.session.get(Brand, brand_id) is None or db.session.get(Category, category_id) is None:
        raise ValueError("Select an existing brand and category.")
    return {
        "name": name,
        "slug": slug,
        "description": description,
        "brand_id": brand_id,
        "category_id": category_id,
        "base_price": base_price,
        "is_active": form.get("is_active") == "on",
    }


def _form_context(product=None, error=None):
    return {
        "product": product,
        "brands": Brand.query.filter_by(is_active=True).order_by(Brand.name).all(),
        "categories": Category.query.filter_by(is_active=True).order_by(Category.name).all(),
        "csrf_token": _csrf_token(),
        "error": error,
    }


@admin_products_bp.get("")
@admin_required
def listing():
    products = (
        Product.query.options(joinedload(Product.brand), joinedload(Product.category))
        .order_by(Product.created_at.desc(), Product.id.desc())
        .all()
    )
    return render_template("admin/products/list.html", products=products, csrf_token=_csrf_token())


@admin_products_bp.get("/new")
@admin_required
def new_product():
    return render_template("admin/products/form.html", **_form_context())


@admin_products_bp.post("/new")
@admin_required
def create_product():
    try:
        values = _product_form_values(request.form)
        if Product.query.filter_by(slug=values["slug"]).first() is not None:
            raise ValueError("A product with this slug already exists.")
        product = Product(**values)
        db.session.add(product)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return render_template("admin/products/form.html", **_form_context(error=str(error))), 400
    except Exception:
        db.session.rollback()
        return render_template("admin/products/form.html", **_form_context(error="Unable to create the product.")), 500
    return redirect(url_for("admin_products.listing"))


@admin_products_bp.get("/<int:product_id>/edit")
@admin_required
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return render_template("404.html"), 404
    return render_template("admin/products/form.html", **_form_context(product=product))


@admin_products_bp.post("/<int:product_id>/edit")
@admin_required
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return render_template("404.html"), 404
    try:
        values = _product_form_values(request.form)
        duplicate = Product.query.filter(Product.slug == values["slug"], Product.id != product.id).first()
        if duplicate is not None:
            raise ValueError("A product with this slug already exists.")
        for field, value in values.items():
            setattr(product, field, value)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return render_template("admin/products/form.html", **_form_context(product=product, error=str(error))), 400
    except Exception:
        db.session.rollback()
        return render_template("admin/products/form.html", **_form_context(product=product, error="Unable to update the product.")), 500
    return redirect(url_for("admin_products.listing"))


@admin_products_bp.post("/<int:product_id>/toggle")
@admin_required
def toggle_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return render_template("404.html"), 404
    product.is_active = not product.is_active
    db.session.commit()
    return redirect(url_for("admin_products.listing"))


@admin_products_bp.post("/<int:product_id>/delete")
@admin_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return render_template("404.html"), 404
    if OrderItem.query.filter_by(product_id=product.id).first() is not None:
        return redirect(url_for("admin_products.listing", error="This product cannot be deleted because it is referenced by an order."))
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin_products.listing"))
