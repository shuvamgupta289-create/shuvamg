from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import CartItem, Product, ProductVariant, User, WishlistItem
from ..services.order_service import OrderValidationError, get_available_variant
from .customer_auth import customer_csrf_token, customer_csrf_valid, customer_required, safe_next_url


customer_shopping_bp = Blueprint("customer_shopping", __name__)


def _active_customer():
    user_id = session.get("customer_user_id")
    user = db.session.get(User, user_id) if user_id else None
    if user is None or not user.is_active or user.role != "customer":
        return None
    return user


def _login_for_product(product, variant_id):
    next_url = url_for("main.product_detail", slug=product.slug, variant_id=variant_id)
    return redirect(url_for("customer_auth.login", next=next_url))


def _cart_items(user_id):
    return (
        CartItem.query.filter_by(user_id=user_id)
        .options(
            joinedload(CartItem.product_variant)
            .joinedload(ProductVariant.product)
            .joinedload(Product.brand),
            joinedload(CartItem.product_variant)
            .joinedload(ProductVariant.product)
            .joinedload(Product.category),
        )
        .order_by(CartItem.created_at, CartItem.id)
        .all()
    )


@customer_shopping_bp.post("/cart/add")
def add_to_cart():
    if not customer_csrf_valid():
        return ("Your form session expired. Refresh the page and try again.", 400)
    try:
        product_id = int(request.form.get("product_id", ""))
        variant_id = int(request.form.get("variant_id", ""))
        quantity = int(request.form.get("quantity", "1"))
    except (TypeError, ValueError):
        flash("Select a valid shoe size before adding the item.", "error")
        return redirect(url_for("main.home"))

    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if product is None:
        return render_template("404.html"), 404
    user = _active_customer()
    if user is None:
        return _login_for_product(product, variant_id)

    if quantity < 1 or quantity > 20:
        flash("Choose a quantity between 1 and 20.", "error")
        return redirect(url_for("main.product_detail", slug=product.slug))
    try:
        variant = get_available_variant(variant_id, product.id, quantity, lock=True)
        cart_item = CartItem.query.filter_by(user_id=user.id, product_variant_id=variant.id).with_for_update().first()
        new_quantity = quantity + (cart_item.quantity if cart_item else 0)
        if new_quantity > 20:
            raise OrderValidationError("The maximum quantity for an item is 20.")
        get_available_variant(variant.id, product.id, new_quantity, lock=True)
        if cart_item is None:
            cart_item = CartItem(user_id=user.id, product_variant_id=variant.id, quantity=new_quantity)
            db.session.add(cart_item)
        else:
            cart_item.quantity = new_quantity
        db.session.commit()
    except OrderValidationError as error:
        db.session.rollback()
        flash(str(error), "error")
        return redirect(url_for("main.product_detail", slug=product.slug))
    flash(f"{product.name} was added to your cart.", "success")
    return redirect(url_for("customer_shopping.cart"))


@customer_shopping_bp.get("/cart")
@customer_required
def cart(user):
    items = _cart_items(user.id)
    subtotal = sum((item.product_variant.effective_price * item.quantity for item in items), start=0)
    return render_template("cart.html", user=user, items=items, subtotal=subtotal, csrf_token=customer_csrf_token())


@customer_shopping_bp.post("/cart/items/<int:item_id>/update")
def update_cart_item(item_id):
    if not customer_csrf_valid():
        return ("Your form session expired. Refresh the page and try again.", 400)
    user = _active_customer()
    if user is None:
        return redirect(url_for("customer_auth.login", next=url_for("customer_shopping.cart")))
    item = CartItem.query.filter_by(id=item_id, user_id=user.id).with_for_update().first()
    if item is None:
        return render_template("404.html"), 404
    try:
        quantity = int(request.form.get("quantity", ""))
        if quantity < 1 or quantity > 20:
            raise OrderValidationError("Choose a quantity between 1 and 20.")
        get_available_variant(item.product_variant_id, item.product_variant.product_id, quantity, lock=True)
    except (TypeError, ValueError) as error:
        db.session.rollback()
        flash(str(error) or "Enter a valid quantity.", "error")
        return redirect(url_for("customer_shopping.cart"))
    item.quantity = quantity
    db.session.commit()
    flash("Your cart was updated.", "success")
    return redirect(url_for("customer_shopping.cart"))


@customer_shopping_bp.post("/cart/items/<int:item_id>/remove")
def remove_cart_item(item_id):
    if not customer_csrf_valid():
        return ("Your form session expired. Refresh the page and try again.", 400)
    user = _active_customer()
    if user is None:
        return redirect(url_for("customer_auth.login", next=url_for("customer_shopping.cart")))
    item = CartItem.query.filter_by(id=item_id, user_id=user.id).first()
    if item is None:
        return render_template("404.html"), 404
    db.session.delete(item)
    db.session.commit()
    flash("The item was removed from your cart.", "success")
    return redirect(url_for("customer_shopping.cart"))


@customer_shopping_bp.get("/wishlist")
@customer_required
def wishlist(user):
    items = (
        WishlistItem.query.filter_by(user_id=user.id)
        .options(joinedload(WishlistItem.product).joinedload(Product.brand), joinedload(WishlistItem.product).joinedload(Product.category))
        .order_by(WishlistItem.created_at.desc(), WishlistItem.id.desc())
        .all()
    )
    wishlist_ids = {item.product_id for item in items}
    products = [item.product for item in items if item.product.is_active]
    return render_template("wishlist.html", user=user, products=products, wishlist_ids=wishlist_ids, csrf_token=customer_csrf_token())


@customer_shopping_bp.post("/wishlist/<int:product_id>/toggle")
def toggle_wishlist(product_id):
    if not customer_csrf_valid():
        return ("Your form session expired. Refresh the page and try again.", 400)
    user = _active_customer()
    next_url = safe_next_url(request.form.get("next"))
    if user is None:
        return redirect(url_for("customer_auth.login", next=next_url))
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if product is None:
        return render_template("404.html"), 404
    item = WishlistItem.query.filter_by(user_id=user.id, product_id=product.id).first()
    if item is None:
        db.session.add(WishlistItem(user_id=user.id, product_id=product.id))
        flash(f"{product.name} was added to your wishlist.", "success")
    else:
        db.session.delete(item)
        flash(f"{product.name} was removed from your wishlist.", "success")
    db.session.commit()
    return redirect(next_url)


def get_wishlist_ids(user_id):
    if user_id is None:
        return set()
    return {
        product_id
        for (product_id,) in db.session.query(WishlistItem.product_id)
        .filter_by(user_id=user_id)
        .all()
    }
