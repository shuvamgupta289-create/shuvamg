from flask import Blueprint, abort, current_app, jsonify, render_template, request, session, url_for
from decimal import Decimal, InvalidOperation
from sqlalchemy import and_, func, select, text
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Brand, Product, ProductVariant, User
from .customer_auth import customer_csrf_token
from .customer_shopping import get_wishlist_ids


main_bp = Blueprint("main", __name__)

LOCAL_BRAND_LOGOS = {
    "adidas": "images/brands/adidas.svg",
    "asics": "images/brands/asics.svg",
    "new-balance": "images/brands/new-balance.svg",
    "nike": "images/brands/nike.svg",
    "puma": "images/brands/puma.svg",
    "reebok": "images/brands/reebok.svg",
    "vans": "images/brands/vans.svg",
}

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

    brands = Brand.query.filter_by(is_active=True).order_by(Brand.name.asc(), Brand.id.asc()).all()
    return render_template(
        "index.html",
        featured_collections=featured_collections,
        products=products,
        trending_products=trending_products,
        new_arrivals=products[:3],
        wishlist_ids=wishlist_ids,
        csrf_token=customer_csrf_token(),
        brands=brands,
        brand_logos={slug: url_for("static", filename=path) for slug, path in LOCAL_BRAND_LOGOS.items()},
    )


@main_bp.get("/brands/<slug>")
def brand_detail(slug):
    brand = Brand.query.filter_by(slug=slug, is_active=True).first()
    if brand is None:
        abort(404)

    page = request.args.get("page", default=1, type=int)
    page = max(page or 1, 1)
    per_page = 9
    search = request.args.get("q", "").strip()[:100]
    size = request.args.get("size", "").strip()[:30]
    sort = request.args.get("sort", "newest")
    minimum = request.args.get("min_price", "").strip()[:20]
    maximum = request.args.get("max_price", "").strip()[:20]

    query = (
        Product.query.join(Brand, Product.brand_id == Brand.id)
        .filter(Product.brand_id == brand.id, Product.is_active.is_(True))
        .options(joinedload(Product.category), joinedload(Product.brand), joinedload(Product.variants))
        .filter(
            Product.variants.any(
                (ProductVariant.is_active.is_(True)) & (ProductVariant.stock_quantity > 0)
            )
        )
    )
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    variant_filters = [ProductVariant.is_active.is_(True), ProductVariant.stock_quantity > 0]
    if size:
        variant_filters.append(ProductVariant.size == size)
    try:
        if minimum:
            min_price = Decimal(minimum)
            if not min_price.is_finite() or min_price < 0:
                raise ValueError
            variant_filters.append(func.coalesce(ProductVariant.price, Product.base_price) >= min_price)
        if maximum:
            max_price = Decimal(maximum)
            if not max_price.is_finite() or max_price < 0:
                raise ValueError
            variant_filters.append(func.coalesce(ProductVariant.price, Product.base_price) <= max_price)
        if minimum and maximum and min_price > max_price:
            abort(400)
    except (TypeError, ValueError, InvalidOperation):
        abort(400)
    query = query.filter(Product.variants.any(and_(*variant_filters)))
    if sort == "price_asc":
        effective_price = (
            select(func.min(func.coalesce(ProductVariant.price, Product.base_price)))
            .where(ProductVariant.product_id == Product.id, ProductVariant.is_active.is_(True), ProductVariant.stock_quantity > 0)
            .correlate(Product)
            .scalar_subquery()
        )
        query = query.order_by(effective_price.asc(), Product.id.asc())
    elif sort == "price_desc":
        effective_price = (
            select(func.min(func.coalesce(ProductVariant.price, Product.base_price)))
            .where(ProductVariant.product_id == Product.id, ProductVariant.is_active.is_(True), ProductVariant.stock_quantity > 0)
            .correlate(Product)
            .scalar_subquery()
        )
        query = query.order_by(effective_price.desc(), Product.id.asc())
    else:
        sort = "newest"
        query = query.order_by(Product.created_at.desc(), Product.id.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    available_sizes = [
        row[0]
        for row in db.session.query(ProductVariant.size)
        .join(Product, Product.id == ProductVariant.product_id)
        .filter(
            Product.brand_id == brand.id,
            Product.is_active.is_(True),
            ProductVariant.is_active.is_(True),
            ProductVariant.stock_quantity > 0,
        )
        .distinct()
        .order_by(ProductVariant.size.asc())
        .all()
    ]
    user = db.session.get(User, session.get("customer_user_id")) if session.get("customer_user_id") else None
    wishlist_ids = get_wishlist_ids(user.id if user and user.is_active and user.role == "customer" else None)
    return render_template(
        "brands/detail.html",
        brand=brand,
        pagination=pagination,
        products=pagination.items,
        available_sizes=available_sizes,
        wishlist_ids=wishlist_ids,
        csrf_token=customer_csrf_token(),
        filters={"q": search, "size": size, "sort": sort, "min_price": minimum, "max_price": maximum},
    )


@main_bp.get("/search")
def product_search():
    search = request.args.get("q", "").strip()[:100]
    page = max(request.args.get("page", default=1, type=int) or 1, 1)
    query = Product.query.join(Brand, Product.brand_id == Brand.id).options(
        joinedload(Product.category), joinedload(Product.brand), joinedload(Product.variants)
    )
    if search:
        query = query.filter(
            Product.is_active.is_(True),
            Brand.is_active.is_(True),
            Product.variants.any(
                ProductVariant.is_active.is_(True) & (ProductVariant.stock_quantity > 0)
            ),
            Product.name.ilike(f"%{search}%") | Brand.name.ilike(f"%{search}%"),
        )
    else:
        query = query.filter(False)
    pagination = query.order_by(Product.created_at.desc(), Product.id.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    user = db.session.get(User, session.get("customer_user_id")) if session.get("customer_user_id") else None
    wishlist_ids = get_wishlist_ids(user.id if user and user.is_active and user.role == "customer" else None)
    return render_template(
        "search_results.html",
        search=search,
        pagination=pagination,
        products=pagination.items,
        wishlist_ids=wishlist_ids,
        csrf_token=customer_csrf_token(),
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
