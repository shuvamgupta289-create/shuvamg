from flask import Blueprint, jsonify, render_template
from sqlalchemy.orm import joinedload

from ..models import Product

main_bp = Blueprint("main", __name__)


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

    brands = ["NIKE", "adidas", "NEW BALANCE", "PUMA", "VANS", "ASICS"]

    return render_template(
        "index.html",
        featured_collections=featured_collections,
        products=products,
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

    variants = [variant for variant in product.variants if variant.is_active]
    return render_template("product_detail.html", product=product, variants=variants)


@main_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})
