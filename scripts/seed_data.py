from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Product, ProductVariant


CATEGORIES = [
    {
        "name": "Men's Sneakers",
        "slug": "mens-sneakers",
        "description": "Everyday and performance sneakers for men.",
    },
    {
        "name": "Women's Sneakers",
        "slug": "womens-sneakers",
        "description": "Comfortable and expressive sneakers for women.",
    },
    {
        "name": "Unisex Sneakers",
        "slug": "unisex-sneakers",
        "description": "Versatile sneaker styles designed for everyone.",
    },
    {
        "name": "Performance Sneakers",
        "slug": "performance-sneakers",
        "description": "Training and running footwear for active days.",
    },
]

BRANDS = [
    {"name": "Nike", "slug": "nike", "description": "Innovation-led sportswear and sneakers."},
    {"name": "Adidas", "slug": "adidas", "description": "Sport and streetwear with global heritage."},
    {"name": "New Balance", "slug": "new-balance", "description": "Comfort-focused sneakers with timeless design."},
    {"name": "Puma", "slug": "puma", "description": "Sport-inspired footwear with bold energy."},
    {"name": "Reebok", "slug": "reebok", "description": "Classic athletic footwear and lifestyle sneakers."},
    {"name": "Vans", "slug": "vans", "description": "Original action sports footwear and culture."},
    {"name": "Asics", "slug": "asics", "description": "Performance footwear built for movement."},
]

PRODUCTS = [
    {
        "name": "Air Max Dn8",
        "slug": "air-max-dn8",
        "brand_slug": "nike",
        "category_slug": "mens-sneakers",
        "description": "A responsive everyday sneaker with a streamlined Air design.",
        "base_price": Decimal("14995.00"),
        "variants": [
            ("SZ-NIKE-DN8-08-BLK", "8", "Black", 12),
            ("SZ-NIKE-DN8-09-BLK", "9", "Black", 10),
            ("SZ-NIKE-DN8-10-BLK", "10", "Black", 8),
        ],
    },
    {
        "name": "Forum Low Classic",
        "slug": "forum-low-classic",
        "brand_slug": "adidas",
        "category_slug": "unisex-sneakers",
        "description": "A low-profile court classic with signature heritage details.",
        "base_price": Decimal("10499.00"),
        "variants": [
            ("SZ-ADI-FORUM-07-WHT", "7", "White", 14),
            ("SZ-ADI-FORUM-08-WHT", "8", "White", 12),
            ("SZ-ADI-FORUM-09-WHT", "9", "White", 9),
        ],
    },
    {
        "name": "574 Core Trainer",
        "slug": "574-core-trainer",
        "brand_slug": "new-balance",
        "category_slug": "womens-sneakers",
        "description": "A dependable lifestyle trainer balancing cushioning and classic style.",
        "base_price": Decimal("8999.00"),
        "variants": [
            ("SZ-NB-574-06-GRY", "6", "Grey", 10),
            ("SZ-NB-574-07-GRY", "7", "Grey", 12),
            ("SZ-NB-574-08-GRY", "8", "Grey", 8),
        ],
    },
    {
        "name": "Club C Revenge",
        "slug": "club-c-revenge",
        "brand_slug": "reebok",
        "category_slug": "unisex-sneakers",
        "description": "A clean court-inspired sneaker with a confident everyday finish.",
        "base_price": Decimal("9799.00"),
        "variants": [
            ("SZ-REEBOK-CCR-07-WHT", "7", "White", 11),
            ("SZ-REEBOK-CCR-08-WHT", "8", "White", 13),
            ("SZ-REEBOK-CCR-09-WHT", "9", "White", 7),
        ],
    },
    {
        "name": "RS-X Heritage",
        "slug": "rs-x-heritage",
        "brand_slug": "puma",
        "category_slug": "mens-sneakers",
        "description": "A statement runner-inspired silhouette with layered texture.",
        "base_price": Decimal("11499.00"),
        "variants": [
            ("SZ-PUMA-RSX-08-ORG", "8", "Orange", 9),
            ("SZ-PUMA-RSX-09-ORG", "9", "Orange", 10),
            ("SZ-PUMA-RSX-10-ORG", "10", "Orange", 6),
        ],
    },
    {
        "name": "Old Skool Classic",
        "slug": "old-skool-classic",
        "brand_slug": "vans",
        "category_slug": "unisex-sneakers",
        "description": "An iconic low-top built around the original side stripe.",
        "base_price": Decimal("7499.00"),
        "variants": [
            ("SZ-VANS-OS-07-BLK", "7", "Black", 15),
            ("SZ-VANS-OS-08-BLK", "8", "Black", 14),
            ("SZ-VANS-OS-09-BLK", "9", "Black", 10),
        ],
    },
]


def get_or_create_by_slug(model, values):
    record = model.query.filter_by(slug=values["slug"]).first()
    if record is not None:
        return record, False
    record = model(**values)
    db.session.add(record)
    return record, True


def seed_data():
    counts = {"categories_created": 0, "brands_created": 0, "products_created": 0, "variants_created": 0}

    for values in CATEGORIES:
        _, created = get_or_create_by_slug(Category, values)
        if created:
            counts["categories_created"] += 1

    for values in BRANDS:
        _, created = get_or_create_by_slug(Brand, values)
        if created:
            counts["brands_created"] += 1

    db.session.flush()

    for values in PRODUCTS:
        product = Product.query.filter_by(slug=values["slug"]).first()
        if product is None:
            product = Product(
                name=values["name"],
                slug=values["slug"],
                description=values["description"],
                base_price=values["base_price"],
                brand_id=Brand.query.filter_by(slug=values["brand_slug"]).one().id,
                category_id=Category.query.filter_by(slug=values["category_slug"]).one().id,
            )
            db.session.add(product)
            counts["products_created"] += 1
            db.session.flush()

        for sku, size, color, stock_quantity in values["variants"]:
            variant = ProductVariant.query.filter_by(sku=sku).first()
            if variant is None:
                db.session.add(
                    ProductVariant(
                        product_id=product.id,
                        sku=sku,
                        size=size,
                        color=color,
                        price=product.base_price,
                        stock_quantity=stock_quantity,
                    )
                )
                counts["variants_created"] += 1

    db.session.commit()
    return counts


if __name__ == "__main__":
    with create_app("development").app_context():
        print(seed_data())
