from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Product, ProductVariant
from ..utils.search import escape_like_value
from .admin import _csrf_token, _valid_csrf_token, admin_required

admin_inventory_bp = Blueprint("admin_inventory", __name__, url_prefix="/admin/inventory")
LOW_STOCK_THRESHOLD = 5


@admin_inventory_bp.before_request
def protect_inventory_posts():
    if request.method == "POST" and not _valid_csrf_token():
        return render_template("admin/login.html", error="Your form session expired. Please try again.", csrf_token=_csrf_token()), 400


def _variant_values(form):
    sku = form.get("sku", "").strip().upper()
    size = form.get("size", "").strip()
    color = form.get("color", "").strip() or None
    if not sku or len(sku) > 80 or not size or len(size) > 30:
        raise ValueError("SKU and size are required and must fit the catalog limits.")
    try:
        product_id = int(form.get("product_id", ""))
        stock_quantity = int(form.get("stock_quantity", ""))
    except (TypeError, ValueError) as error:
        raise ValueError("Select a product and enter a non-negative integer stock quantity.") from error
    if stock_quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")
    price_text = form.get("price", "").strip()
    try:
        price = Decimal(price_text) if price_text else None
    except InvalidOperation as error:
        raise ValueError("Price must be a valid amount.") from error
    if price is not None and (price < 0 or price.as_tuple().exponent < -2):
        raise ValueError("Price must be non-negative with no more than two decimals.")
    if db.session.get(Product, product_id) is None:
        raise ValueError("Select an existing product.")
    return {
        "product_id": product_id,
        "sku": sku,
        "size": size,
        "color": color,
        "price": price,
        "stock_quantity": stock_quantity,
        "is_active": form.get("is_active") == "on",
    }


def _variant_context(variant=None, error=None):
    return {
        "variant": variant,
        "products": Product.query.order_by(Product.name).all(),
        "csrf_token": _csrf_token(),
        "error": error,
    }


@admin_inventory_bp.get("")
@admin_required
def listing():
    product_filter = request.args.get("product_id", "").strip()
    size_filter = request.args.get("size", "").strip()
    stock_filter = request.args.get("stock_status", "all")
    query = ProductVariant.query.options(joinedload(ProductVariant.product)).join(Product)
    if product_filter.isdigit():
        query = query.filter(ProductVariant.product_id == int(product_filter))
    if size_filter:
        query = query.filter(ProductVariant.size.ilike(f"%{escape_like_value(size_filter)}%", escape="!"))
    if stock_filter == "out":
        query = query.filter(ProductVariant.stock_quantity == 0)
    elif stock_filter == "low":
        query = query.filter(ProductVariant.stock_quantity.between(1, LOW_STOCK_THRESHOLD))
    pagination = query.order_by(Product.name, ProductVariant.size, ProductVariant.sku).paginate(
        page=max(request.args.get("page", 1, type=int) or 1, 1), per_page=25, error_out=False
    )
    return render_template(
        "admin/inventory/list.html",
        variants=pagination.items,
        pagination=pagination,
        products=Product.query.order_by(Product.name).all(),
        product_filter=product_filter,
        size_filter=size_filter,
        stock_filter=stock_filter,
        low_stock_threshold=LOW_STOCK_THRESHOLD,
        csrf_token=_csrf_token(),
    )


@admin_inventory_bp.get("/new")
@admin_required
def new_variant():
    return render_template("admin/inventory/form.html", **_variant_context())


@admin_inventory_bp.post("/new")
@admin_required
def create_variant():
    try:
        values = _variant_values(request.form)
        if ProductVariant.query.filter_by(sku=values["sku"]).first() is not None:
            raise ValueError("A variant with this SKU already exists.")
        variant = ProductVariant(**values)
        db.session.add(variant)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return render_template("admin/inventory/form.html", **_variant_context(error=str(error))), 400
    except Exception:
        db.session.rollback()
        return render_template("admin/inventory/form.html", **_variant_context(error="Unable to create the variant.")), 500
    return redirect(url_for("admin_inventory.listing"))


@admin_inventory_bp.get("/<int:variant_id>/edit")
@admin_required
def edit_variant(variant_id):
    variant = db.session.get(ProductVariant, variant_id)
    if variant is None:
        return render_template("404.html"), 404
    return render_template("admin/inventory/form.html", **_variant_context(variant=variant))


@admin_inventory_bp.post("/<int:variant_id>/edit")
@admin_required
def update_variant(variant_id):
    variant = db.session.get(ProductVariant, variant_id)
    if variant is None:
        return render_template("404.html"), 404
    try:
        values = _variant_values(request.form)
        duplicate = ProductVariant.query.filter(ProductVariant.sku == values["sku"], ProductVariant.id != variant.id).first()
        if duplicate is not None:
            raise ValueError("A variant with this SKU already exists.")
        for field, value in values.items():
            setattr(variant, field, value)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return render_template("admin/inventory/form.html", **_variant_context(variant=variant, error=str(error))), 400
    except Exception:
        db.session.rollback()
        return render_template("admin/inventory/form.html", **_variant_context(variant=variant, error="Unable to update the variant.")), 500
    return redirect(url_for("admin_inventory.listing"))


@admin_inventory_bp.post("/<int:variant_id>/stock")
@admin_required
def update_stock(variant_id):
    variant = db.session.get(ProductVariant, variant_id)
    if variant is None:
        return render_template("404.html"), 404
    try:
        stock_quantity = int(request.form.get("stock_quantity", ""))
        if stock_quantity < 0:
            raise ValueError
        variant.stock_quantity = stock_quantity
        db.session.commit()
    except (TypeError, ValueError):
        db.session.rollback()
        return redirect(url_for("admin_inventory.listing", error="Stock must be a non-negative integer."))
    return redirect(url_for("admin_inventory.listing"))
