import unittest
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree

from app import create_app
from app.extensions import db
from app.models import Brand, Product, ProductVariant
from config import config_by_name
from scripts.seed_data import PRODUCTS, seed_data


SeedTestingConfig = type(
    "SeedTestingConfig",
    (),
    {
        "SECRET_KEY": "seed-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=2),
        "DEBUG": True,
    },
)
config_by_name["seed_testing"] = SeedTestingConfig


class CatalogSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("seed_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def test_seed_catalog_is_complete_idempotent_and_discoverable(self):
        first_run = seed_data()
        self.assertEqual(first_run["products_created"], 70)
        self.assertEqual(first_run["variants_created"], 402)
        self.assertEqual(first_run["brands_created"], 7)
        self.assertEqual(len(PRODUCTS), 70)

        expected_logos = {
            "adidas": "adidas.svg",
            "asics": "asics.svg",
            "new-balance": "new-balance.svg",
            "nike": "nike.svg",
            "puma": "puma.svg",
            "reebok": "reebok.svg",
            "vans": "vans.svg",
        }
        logo_dir = Path(__file__).resolve().parents[1] / "app" / "static" / "images" / "brands"
        for slug, filename in expected_logos.items():
            root = ElementTree.parse(logo_dir / filename).getroot()
            self.assertTrue(root.tag.endswith("svg"))
            brand = Brand.query.filter_by(slug=slug).one()
            self.assertEqual(brand.logo_url, f"/static/images/brands/{filename}")
            products = Product.query.filter_by(brand_id=brand.id).all()
            self.assertEqual(len(products), 10)
            for product in products:
                variants = ProductVariant.query.filter_by(product_id=product.id, is_active=True).all()
                self.assertTrue(any(variant.stock_quantity > 0 for variant in variants))
                self.assertTrue(all(variant.product_id == product.id for variant in variants))
                self.assertTrue(product.category.is_active)

        product_count = Product.query.count()
        variant_count = ProductVariant.query.count()
        second_run = seed_data()
        self.assertEqual(second_run, {"categories_created": 0, "brands_created": 0, "brand_logos_updated": 0, "products_created": 0, "variants_created": 0})
        self.assertEqual(Product.query.count(), product_count)
        self.assertEqual(ProductVariant.query.count(), variant_count)
        self.assertEqual(product_count, 70)
        self.assertEqual(variant_count, 402)

        client = self.app.test_client()
        homepage = client.get("/").get_data(as_text=True)
        self.assertIn('/static/images/brands/nike.svg', homepage)
        self.assertIn('/static/images/brands/asics.svg', homepage)
        self.assertIn('/brands/new-balance', homepage)
        brand_page = client.get("/brands/nike").get_data(as_text=True)
        self.assertEqual(brand_page.count('class="product-card brand-product-card"'), 9)
        self.assertIn("Air Force 1", client.get("/brands/nike?q=Air+Force").get_data(as_text=True))
        next_page = client.get("/brands/nike?page=2").get_data(as_text=True)
        self.assertEqual(next_page.count('class="product-card brand-product-card"'), 1)
        filtered = client.get("/brands/asics?size=8&min_price=10000&sort=price_asc").get_data(as_text=True)
        self.assertIn("GEL-Kayano 31", filtered)
        search = client.get("/search?q=Air+Force+1").get_data(as_text=True)
        self.assertIn("Air Force 1", search)
        detail = client.get("/product/gel-kayano-31").get_data(as_text=True)
        self.assertIn("ASICS", detail)
        self.assertIn("GEL-Kayano 31", detail)


if __name__ == "__main__":
    unittest.main()
