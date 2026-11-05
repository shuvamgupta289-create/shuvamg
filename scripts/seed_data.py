from decimal import Decimal
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CATEGORIES = [
    {"name": "Men's Sneakers", "slug": "mens-sneakers", "description": "Everyday and performance sneakers for men."},
    {"name": "Women's Sneakers", "slug": "womens-sneakers", "description": "Comfortable and expressive sneakers for women."},
    {"name": "Unisex Sneakers", "slug": "unisex-sneakers", "description": "Versatile sneaker styles designed for everyone."},
    {"name": "Performance Sneakers", "slug": "performance-sneakers", "description": "Training and running footwear for active days."},
]

BRANDS = [
    {"name": "Nike", "slug": "nike", "description": "Innovation-led sportswear and sneakers.", "logo_url": "/static/images/brands/nike.svg"},
    {"name": "Adidas", "slug": "adidas", "description": "Sport and streetwear with global heritage.", "logo_url": "/static/images/brands/adidas.svg"},
    {"name": "New Balance", "slug": "new-balance", "description": "Comfort-focused sneakers with timeless design.", "logo_url": "/static/images/brands/new-balance.svg"},
    {"name": "Puma", "slug": "puma", "description": "Sport-inspired footwear with bold energy.", "logo_url": "/static/images/brands/puma.svg"},
    {"name": "Reebok", "slug": "reebok", "description": "Classic athletic footwear and lifestyle sneakers.", "logo_url": "/static/images/brands/reebok.svg"},
    {"name": "Vans", "slug": "vans", "description": "Original action sports footwear and culture.", "logo_url": "/static/images/brands/vans.svg"},
    {"name": "ASICS", "slug": "asics", "description": "Performance footwear built for movement.", "logo_url": "/static/images/brands/asics.svg"},
]

PRODUCT_IMAGES = {
    "old-skool-classic": "https://assets.vans.com/images/t_img/c_fill,g_center,f_auto,h_2500,w_2000/v1747942442/VN000D3HY28-HERO/Old-Skool-Shoe-VANS-Black-White-HERO.png",
    "rs-x-heritage": "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_1200,h_1200/global/398210/03/sv01/fnd/PNA/fmt/png",
    "club-c-revenge": "https://www.reebok.com/cdn/shop/files/100032883_SLC_eCom.jpg?v=1764594542&width=1200",
    "574-core-trainer": "https://nb.scene7.com/is/image/NB/ml574evg_nb_02_i?$pdpflexf2$=&hei=1200&wid=1200",
    "air-max-dn8": "https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto%2Cu_9ddf04c7-2a9a-4d76-add1-d15af8f0263d%2Cc_scale%2Cfl_relative%2Cw_1.0%2Ch_1.0%2Cfl_layer_apply/76c32da1-45ce-4f1f-b7c8-3a4481d79eeb/AIR%2BMAX%2BDN8.png",
    "forum-low-classic": "https://assets.adidas.com/images/w_1200,f_auto,q_auto/c11bc0d2b836462bb787af9e013e3574_9366/Forum_Low_Shoes_White_IE7166_01_standard.jpg",
}

CATALOG_PRODUCTS = [
    # brand, model, slug, category, INR price, color, description
    ("nike", "Air Max Dn8", "air-max-dn8", "mens-sneakers", "14995", "Black", "A modern Air Max design with a responsive feel for everyday movement."),
    ("nike", "Air Force 1 '07", "air-force-1-07", "unisex-sneakers", "8995", "White", "A durable low-top basketball original with clean leather styling."),
    ("nike", "Dunk Low Retro", "dunk-low-retro", "unisex-sneakers", "10295", "White/Black", "A versatile court silhouette with layered panels and a classic profile."),
    ("nike", "Air Jordan 1 Low", "air-jordan-1-low", "mens-sneakers", "11295", "White/Red", "A low-cut Jordan design with heritage basketball details."),
    ("nike", "Air Max 90", "air-max-90", "mens-sneakers", "12795", "White/Grey", "A streetwear staple with visible Air cushioning and a layered upper."),
    ("nike", "Pegasus 41", "pegasus-41", "performance-sneakers", "11895", "Black/White", "A neutral daily running shoe designed for cushioned road miles."),
    ("nike", "Vomero 18", "vomero-18", "performance-sneakers", "14995", "White/Blue", "A plush road-running model built for comfortable everyday training."),
    ("nike", "Blazer Low '77", "blazer-low-77", "unisex-sneakers", "7995", "White/Black", "A low-profile retro basketball shoe with a simple leather look."),
    ("nike", "Court Vision Low", "court-vision-low", "mens-sneakers", "6495", "White/Navy", "A court-inspired everyday low-top with a clean, familiar shape."),
    ("nike", "P-6000", "p-6000", "mens-sneakers", "9995", "Silver/White", "A retro running-inspired sneaker with layered mesh and synthetic panels."),

    ("adidas", "Forum Low Classic", "forum-low-classic", "unisex-sneakers", "10499", "White", "A low-profile court classic with signature heritage details."),
    ("adidas", "Superstar II", "superstar-ii", "unisex-sneakers", "8999", "White/Black", "A shell-toe original with a leather upper and timeless street style."),
    ("adidas", "Samba OG", "samba-og", "unisex-sneakers", "10999", "White/Black", "A football-inspired icon with a low profile and gum rubber outsole."),
    ("adidas", "Ultraboost 5", "ultraboost-5", "performance-sneakers", "15999", "Black", "A cushioned road-running shoe with a breathable knit upper."),
    ("adidas", "Gazelle Indoor", "gazelle-indoor", "unisex-sneakers", "10999", "Green/White", "A terrace classic with a soft suede upper and translucent gum sole."),
    ("adidas", "Campus 00s", "campus-00s", "unisex-sneakers", "9999", "Grey/White", "A substantial campus silhouette with a suede finish and padded collar."),
    ("adidas", "Stan Smith", "stan-smith", "unisex-sneakers", "8999", "White/Green", "A minimalist tennis classic with a clean leather-inspired finish."),
    ("adidas", "Adizero SL2", "adizero-sl2", "performance-sneakers", "11999", "White/Blue", "A lightweight daily trainer made for steady road-running sessions."),
    ("adidas", "Response CL", "response-cl", "mens-sneakers", "9999", "White/Grey", "A layered running-inspired sneaker with a technical retro look."),
    ("adidas", "Handball Spezial", "handball-spezial", "unisex-sneakers", "9999", "Navy/White", "A low-profile indoor-court classic with suede and gum details."),

    ("puma", "RS-X Heritage", "rs-x-heritage", "mens-sneakers", "11499", "Orange", "A statement runner-inspired silhouette with layered texture."),
    ("puma", "Suede Classic", "suede-classic", "unisex-sneakers", "6999", "Black/White", "A long-running streetwear staple finished with a soft suede upper."),
    ("puma", "Palermo", "palermo", "unisex-sneakers", "7999", "White/Green", "A terrace-inspired low-top with a T-toe and classic gum sole."),
    ("puma", "Future Rider", "future-rider", "mens-sneakers", "7999", "White/Blue", "A lightweight retro runner with a distinctive ridged outsole."),
    ("puma", "Caven 2.0", "caven-2", "mens-sneakers", "5999", "White/Black", "A court-inspired sneaker with layered panels for daily wear."),
    ("puma", "Deviate Nitro 3", "deviate-nitro-3", "performance-sneakers", "15999", "Black/Yellow", "A responsive road-running shoe designed for faster training sessions."),
    ("puma", "Speedcat OG", "speedcat-og", "unisex-sneakers", "9999", "Black/White", "A low-profile motorsport-inspired sneaker with a sleek suede look."),
    ("puma", "Slipstream Lo", "slipstream-lo", "unisex-sneakers", "8999", "White/Blue", "A basketball-rooted low-top with a bold, panelled leather profile."),
    ("puma", "Easy Rider", "easy-rider", "unisex-sneakers", "7999", "Green/White", "A vintage running silhouette with a lightweight everyday feel."),
    ("puma", "R78 Voyage", "r78-voyage", "womens-sneakers", "5999", "White/Pink", "A casual retro runner with a comfortable platform-inspired profile."),

    ("new-balance", "574 Core Trainer", "574-core-trainer", "womens-sneakers", "8999", "Grey", "A dependable lifestyle trainer balancing cushioning and classic style."),
    ("new-balance", "550", "550", "unisex-sneakers", "11999", "White/Green", "A vintage basketball-inspired low-top with a structured leather look."),
    ("new-balance", "327", "327", "unisex-sneakers", "10999", "White/Blue", "A heritage running design with an oversized N and trail-inspired outsole."),
    ("new-balance", "9060", "9060", "unisex-sneakers", "17999", "Grey", "A modern lifestyle silhouette with sculpted lines and a cushioned sole."),
    ("new-balance", "2002R", "2002r", "mens-sneakers", "14999", "Grey/Blue", "A retro running-inspired shoe with layered mesh and suede panels."),
    ("new-balance", "990v6", "990v6", "mens-sneakers", "22999", "Grey", "A premium made-for-running heritage silhouette with refined cushioning."),
    ("new-balance", "Fresh Foam X 1080v14", "fresh-foam-x-1080v14", "performance-sneakers", "16999", "Black/White", "A soft, neutral road-running shoe for comfortable daily mileage."),
    ("new-balance", "530", "530", "unisex-sneakers", "9999", "White/Silver", "A technical-inspired everyday sneaker with a breathable mesh upper."),
    ("new-balance", "1906R", "1906r", "mens-sneakers", "15999", "White/Silver", "A retro performance runner look with layered mesh and synthetic overlays."),
    ("new-balance", "574 Legacy", "574-legacy", "unisex-sneakers", "10999", "Navy/Grey", "A refreshed take on the 574 with familiar everyday comfort."),

    ("reebok", "Club C Revenge", "club-c-revenge", "unisex-sneakers", "9799", "White", "A clean court-inspired sneaker with a confident everyday finish."),
    ("reebok", "Classic Leather", "classic-leather", "unisex-sneakers", "7999", "White", "A simple heritage runner with a soft leather upper and low profile."),
    ("reebok", "Nano X5", "nano-x5", "performance-sneakers", "12999", "Black/White", "A stable training shoe designed for varied gym and workout sessions."),
    ("reebok", "Classic Nylon", "classic-nylon", "mens-sneakers", "6999", "Navy/White", "A lightweight retro runner with nylon and suede-inspired panels."),
    ("reebok", "FloatZig 1", "floatzig-1", "performance-sneakers", "13999", "White/Orange", "A modern running shoe with a responsive, sculpted platform feel."),
    ("reebok", "BB 4000 II", "bb-4000-ii", "unisex-sneakers", "7999", "White/Green", "A basketball-inspired court shoe with a durable everyday build."),
    ("reebok", "Club C 85 Vintage", "club-c-85-vintage", "unisex-sneakers", "8999", "Chalk/Green", "A vintage court staple with understated branding and a soft finish."),
    ("reebok", "Zig Kinetica 2.5", "zig-kinetica-25", "mens-sneakers", "11999", "Black/Red", "A bold lifestyle runner with a distinctive zigzag-inspired sole."),
    ("reebok", "Workout Plus", "workout-plus", "unisex-sneakers", "7499", "White/Chalk", "A low-cut training classic with a clean leather look."),
    ("reebok", "Premier Road Modern", "premier-road-modern", "mens-sneakers", "12999", "White/Grey", "A technical retro runner with layered details and a supportive feel."),

    ("vans", "Old Skool Classic", "old-skool-classic", "unisex-sneakers", "7499", "Black/White", "An iconic low-top built around the original side stripe."),
    ("vans", "Authentic", "authentic", "unisex-sneakers", "5999", "Black", "A simple low-top canvas shoe with the original Vans profile."),
    ("vans", "Sk8-Hi", "sk8-hi", "unisex-sneakers", "7999", "Black/White", "A high-top skate shoe with padded support and the signature side stripe."),
    ("vans", "Knu Skool", "knu-skool", "unisex-sneakers", "8999", "Black/White", "A chunky 90s-inspired skate silhouette with a padded tongue."),
    ("vans", "Era", "era", "unisex-sneakers", "5999", "Navy/White", "A classic low-top skate shoe with a padded collar and canvas upper."),
    ("vans", "Classic Slip-On", "classic-slip-on", "unisex-sneakers", "5999", "Black/White Checkerboard", "An easy slip-on canvas shoe with elastic side accents."),
    ("vans", "UltraRange EXO", "ultrarange-exo", "mens-sneakers", "9999", "Black/White", "A versatile lightweight shoe made for comfortable all-day wear."),
    ("vans", "Old Skool Platform", "old-skool-platform", "womens-sneakers", "8499", "Black/White", "The classic side-stripe low-top with a raised platform sole."),
    ("vans", "Checkerboard Slip-On", "checkerboard-slip-on", "unisex-sneakers", "6499", "Checkerboard", "A slip-on classic finished in the recognizable checkerboard pattern."),
    ("vans", "Sk8-Low", "sk8-low", "unisex-sneakers", "7499", "Black/White", "A low-cut take on the Sk8-Hi with signature skate styling."),

    ("asics", "GEL-Kayano 31", "gel-kayano-31", "performance-sneakers", "15999", "Black/White", "A supportive road-running shoe designed for stable daily training."),
    ("asics", "GEL-Nimbus 27", "gel-nimbus-27", "performance-sneakers", "16999", "White/Blue", "A highly cushioned neutral running shoe for long road sessions."),
    ("asics", "GEL-1130", "gel-1130", "unisex-sneakers", "9999", "White/Silver", "A retro running-inspired design with breathable mesh and GEL comfort."),
    ("asics", "GT-2160", "gt-2160", "unisex-sneakers", "11999", "White/Grey", "A technical archive-inspired sneaker with a streamlined runner profile."),
    ("asics", "GEL-NYC", "gel-nyc", "unisex-sneakers", "13999", "White/Grey", "A layered lifestyle runner combining heritage-inspired details."),
    ("asics", "Novablast 5", "novablast-5", "performance-sneakers", "13999", "Black/Orange", "A lightweight neutral running shoe with an energetic ride."),
    ("asics", "GEL-Venture 6", "gel-venture-6", "mens-sneakers", "7999", "Black/Grey", "A durable trail-inspired shoe for everyday wear and light paths."),
    ("asics", "GEL-Quantum 360 VIII", "gel-quantum-360-viii", "mens-sneakers", "15999", "Black/Silver", "A futuristic lifestyle sneaker with cushioning-inspired GEL design."),
    ("asics", "GEL-Cumulus 26", "gel-cumulus-26", "performance-sneakers", "12999", "White/Blue", "A neutral daily road-running shoe with a smooth, cushioned feel."),
    ("asics", "GT-2000 13", "gt-2000-13", "performance-sneakers", "11999", "Black/Blue", "A supportive everyday running shoe built for dependable training."),
]

PRODUCTS = [
    {
        "brand_slug": brand_slug,
        "name": name,
        "slug": slug,
        "category_slug": category_slug,
        "description": description,
        "base_price": Decimal(price),
        "color": color,
    }
    for brand_slug, name, slug, category_slug, price, color, description in CATALOG_PRODUCTS
]

LEGACY_VARIANTS = {
    "air-max-dn8": [("SZ-NIKE-DN8-08-BLK", "8", "Black", 12), ("SZ-NIKE-DN8-09-BLK", "9", "Black", 10), ("SZ-NIKE-DN8-10-BLK", "10", "Black", 8)],
    "forum-low-classic": [("SZ-ADI-FORUM-07-WHT", "7", "White", 14), ("SZ-ADI-FORUM-08-WHT", "8", "White", 12), ("SZ-ADI-FORUM-09-WHT", "9", "White", 9)],
    "574-core-trainer": [("SZ-NB-574-06-GRY", "6", "Grey", 10), ("SZ-NB-574-07-GRY", "7", "Grey", 12), ("SZ-NB-574-08-GRY", "8", "Grey", 8)],
    "club-c-revenge": [("SZ-REEBOK-CCR-07-WHT", "7", "White", 11), ("SZ-REEBOK-CCR-08-WHT", "8", "White", 13), ("SZ-REEBOK-CCR-09-WHT", "9", "White", 7)],
    "rs-x-heritage": [("SZ-PUMA-RSX-08-ORG", "8", "Orange", 9), ("SZ-PUMA-RSX-09-ORG", "9", "Orange", 10), ("SZ-PUMA-RSX-10-ORG", "10", "Orange", 6)],
    "old-skool-classic": [("SZ-VANS-OS-07-BLK", "7", "Black", 15), ("SZ-VANS-OS-08-BLK", "8", "Black", 14), ("SZ-VANS-OS-09-BLK", "9", "Black", 10)],
}


def get_or_create_by_slug(model, values):
    from app.extensions import db

    record = model.query.filter_by(slug=values["slug"]).first()
    if record is not None:
        return record, False
    record = model(**values)
    db.session.add(record)
    return record, True


def seed_data():
    from app.extensions import db
    from app.models import Brand, Category, Product, ProductVariant

    counts = {"categories_created": 0, "brands_created": 0, "brand_logos_updated": 0, "products_created": 0, "variants_created": 0}

    for values in CATEGORIES:
        _, created = get_or_create_by_slug(Category, values)
        if created:
            counts["categories_created"] += 1

    for values in BRANDS:
        brand, created = get_or_create_by_slug(Brand, values)
        if created:
            counts["brands_created"] += 1
        if brand.logo_url != values["logo_url"]:
            brand.logo_url = values["logo_url"]
            counts["brand_logos_updated"] += 1

    db.session.flush()

    for values in PRODUCTS:
        product = Product.query.filter_by(slug=values["slug"]).first()
        brand = Brand.query.filter_by(slug=values["brand_slug"]).one()
        category = Category.query.filter_by(slug=values["category_slug"]).one()
        if product is None:
            product = Product(
                name=values["name"],
                slug=values["slug"],
                description=values["description"],
                image_url=PRODUCT_IMAGES.get(values["slug"]),
                base_price=values["base_price"],
                brand_id=brand.id,
                category_id=category.id,
            )
            db.session.add(product)
            counts["products_created"] += 1
            db.session.flush()
        elif product.brand_id != brand.id or product.category_id != category.id:
            raise ValueError(
                f"Existing product '{values['slug']}' belongs to a different brand or category; no catalog rows were changed."
            )
        elif not product.image_url:
            product.image_url = PRODUCT_IMAGES.get(values["slug"])

        variants = LEGACY_VARIANTS.get(values["slug"])
        if variants is None:
            sku_prefix = values["slug"].upper().replace("-", "")
            variants = [
                (f"SZ-{sku_prefix}-{size}", size, values["color"], 6 + index % 5)
                for index, size in enumerate(("6", "7", "8", "9", "10", "11"))
            ]
        for sku, size, color, stock_quantity in variants:
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
            elif variant.product_id != product.id or variant.size != size or variant.color != color:
                raise ValueError(
                    f"Existing SKU '{sku}' belongs to a different product or variant; no catalog rows were changed."
                )

    db.session.commit()
    return counts


def verify_local_catalog():
    from app.extensions import db
    from app.models import Brand, Product, ProductVariant

    expected_brand_slugs = {brand["slug"] for brand in BRANDS}
    brands = Brand.query.filter(Brand.slug.in_(expected_brand_slugs)).all()
    if {brand.slug for brand in brands} != expected_brand_slugs:
        raise RuntimeError("Local catalog verification failed: expected seven catalog brands.")

    products = Product.query.join(Brand).filter(Brand.slug.in_(expected_brand_slugs)).all()
    if len(products) != 70:
        raise RuntimeError(f"Local catalog verification failed: expected 70 products, found {len(products)}.")

    expected_products = {product["slug"]: product for product in PRODUCTS}
    variant_total = 0
    for product in products:
        expected = expected_products.get(product.slug)
        if expected is None or product.brand.slug != expected["brand_slug"]:
            raise RuntimeError(f"Local catalog verification failed: incorrect brand relationship for '{product.slug}'.")
        if product.base_price <= 0 or product.category.slug != expected["category_slug"]:
            raise RuntimeError(f"Local catalog verification failed: invalid price or category for '{product.slug}'.")
        expected_image = PRODUCT_IMAGES.get(product.slug)
        if expected_image and product.image_url != expected_image:
            raise RuntimeError(f"Local catalog verification failed: image mapping mismatch for '{product.slug}'.")
        variants = ProductVariant.query.filter_by(product_id=product.id).all()
        expected_sizes = (
            [variant[1] for variant in LEGACY_VARIANTS[product.slug]]
            if product.slug in LEGACY_VARIANTS
            else ["6", "7", "8", "9", "10", "11"]
        )
        expected_count = len(expected_sizes)
        if len(variants) != expected_count:
            raise RuntimeError(
                f"Local catalog verification failed: '{product.slug}' has {len(variants)} sizes; expected {expected_count}."
            )
        if {variant.size for variant in variants} != set(expected_sizes):
            raise RuntimeError(f"Local catalog verification failed: size list mismatch for '{product.slug}'.")
        if any(variant.stock_quantity <= 0 or variant.effective_price <= 0 for variant in variants):
            raise RuntimeError(f"Local catalog verification failed: invalid stock or price for '{product.slug}'.")
        if any(variant.product_id != product.id for variant in variants):
            raise RuntimeError(f"Local catalog verification failed: variant relationship mismatch for '{product.slug}'.")
        variant_total += len(variants)

    if variant_total != 402:
        raise RuntimeError(f"Local catalog verification failed: expected 402 variants, found {variant_total}.")

    for values in BRANDS:
        brand = next(brand for brand in brands if brand.slug == values["slug"])
        logo_path = Path(__file__).resolve().parents[1] / "app" / "static" / brand.logo_url.removeprefix("/static/")
        if brand.logo_url != values["logo_url"] or not logo_path.is_file():
            raise RuntimeError(f"Local catalog verification failed: local logo missing for '{brand.slug}'.")

    return {"brands": len(brands), "products": len(products), "variants": variant_total}


def _run_local_only():
    # This mode must be isolated before importing the app/config modules.
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    for variable in ("DATABASE_URL", "APP_ENV", "FLASK_ENV", "VERCEL", "STEPZONE_ALLOW_REMOTE_SEED"):
        os.environ.pop(variable, None)

    import dotenv

    def prevent_dotenv_loading(*args, **kwargs):
        return False

    dotenv.load_dotenv = prevent_dotenv_loading

    from config import config_by_name

    project_root = Path(__file__).resolve().parents[1]
    local_database_path = project_root / "local_test_data" / "stepzone_catalog_test.sqlite3"
    local_database_path.parent.mkdir(parents=True, exist_ok=True)
    local_database_url = f"sqlite:///{local_database_path.as_posix()}"
    config_by_name["catalog_seed_local_only"] = type(
        "LocalCatalogSeedConfig",
        (),
        {
            "SECRET_KEY": "local-catalog-seed-only",
            "SQLALCHEMY_DATABASE_URI": local_database_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SAMESITE": "Lax",
            "SESSION_COOKIE_SECURE": False,
            "DEBUG": True,
        },
    )

    from app import create_app
    from app.extensions import db

    app = create_app("catalog_seed_local_only")
    with app.app_context():
        engine = db.engine
        if engine.url.get_backend_name() != "sqlite":
            raise SystemExit("Local-only safety check failed: database engine is not SQLite.")
        actual_database_path = Path(engine.url.database).resolve()
        if actual_database_path != local_database_path.resolve():
            raise SystemExit("Local-only safety check failed: database file is not the dedicated catalog test file.")

        db.create_all()
        counts = seed_data()
        verified = verify_local_catalog()
        print({"database_file": str(local_database_path), "seed_counts": counts, "verified": verified})


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the STEPZONE sneaker catalog.")
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Force a dedicated SQLite catalog test file; ignore database and deployment environment variables.",
    )
    arguments = parser.parse_args()

    if arguments.local_only:
        _run_local_only()
    else:
        from app import create_app

        app = create_app("development")
        if not app.debug or app.config.get("SESSION_COOKIE_SECURE"):
            raise SystemExit("Refusing to seed while the application is configured for production.")
        database_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if not database_url.startswith("sqlite:///") and os.getenv("STEPZONE_ALLOW_REMOTE_SEED") != "1":
            raise SystemExit(
                "Refusing to seed a remote database. Review the target, then set STEPZONE_ALLOW_REMOTE_SEED=1 for an approved non-production database."
            )
        from app.extensions import db

        with app.app_context():
            print(seed_data())
