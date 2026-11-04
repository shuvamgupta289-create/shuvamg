from flask import Blueprint, current_app, jsonify, render_template, session
from sqlalchemy import text
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Product, User
from .customer_auth import customer_csrf_token
from .customer_shopping import get_wishlist_ids


main_bp = Blueprint("main", __name__)

TRENDING_PRODUCT_SLUGS = (
    "old-skool-classic",
    "rs-x-heritage",
    "club-c-revenge",
    "574-core-trainer",
)


@main_bp.get("/")
def home():
    featured_collections = [
        {
            "eyebrow": "01 / EVERYDAY",
            "name": "Daily Rotation",
            "description": "Easy silhouettes for wherever the day takes you.",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=85",
        },
        {
            "eyebrow": "02 / PERFORMANCE",
            "name": "Move Different",
            "description": "Technical energy, built for your fastest pace.",
            "image": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=1200&q=85",
        },
        {
            "eyebrow": "03 / AFTER DARK",
            "name": "Night Shift",
            "description": "Statement pairs with a little more edge.",
            "image": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=1200&q=85",
        },
    ]
    products = (
        Product.query.options(joinedload(Product.category), joinedload(Product.brand))
        .filter(Product.is_active.is_(True))
        .order_by(Product.created_at.desc(), Product.id.desc())
        .all()
    )
    products_by_slug = {product.slug: product for product in products}
    trending_products = [
        products_by_slug[slug]
        for slug in TRENDING_PRODUCT_SLUGS
        if slug in products_by_slug
    ]
    user = db.session.get(User, session.get("customer_user_id")) if session.get("customer_user_id") else None
    wishlist_ids = get_wishlist_ids(user.id if user and user.is_active and user.role == "customer" else None)

    brands = ["NIKE", "adidas", "NEW BALANCE", "PUMA", "VANS", "ASICS"]
    return render_template(
        "index.html",
        featured_collections=featured_collections,
        products=products,
        trending_products=trending_products,
        new_arrivals=products[:3],
        wishlist_ids=wishlist_ids,
        csrf_token=customer_csrf_token(),
        brands=brands,
    )


@main_bp.get("/product/<slug>")
def product_detail(slug):
    product = (
        Product.query.options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.variants),
        )
        .filter(Product.slug == slug, Product.is_active.is_(True))
        .first()
    )
    if product is None:
        return render_template("404.html"), 404

    user = db.session.get(User, session.get("customer_user_id")) if session.get("customer_user_id") else None
    variants = [variant for variant in product.variants if variant.is_active]
    wishlist_ids = get_wishlist_ids(user.id if user and user.is_active and user.role == "customer" else None)
    return render_template(
        "product_detail.html",
        product=product,
        variants=variants,
        wishlist_ids=wishlist_ids,
        csrf_token=customer_csrf_token(),
    )


@main_bp.get("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        current_app.logger.exception("Database health check failed.")
        try:
            db.session.rollback()
        except Exception:
            current_app.logger.exception("Database health check rollback failed.")
        return (
            jsonify({"status": "error", "message": "Service temporarily unavailable."}),
            503,
        )
    return jsonify({"status": "ok"})
