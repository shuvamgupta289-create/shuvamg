import re
import unittest
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Product, ProductVariant, User
from config import config_by_name


TestingConfig = type(
    "TestingConfig",
    (),
    {
        "SECRET_KEY": "test-secret-inventory",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
    },
)
config_by_name["inventory_testing"] = TestingConfig


class AdminInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("inventory_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()
        brand = Brand(name="Inventory Brand", slug="inventory-brand")
        category = Category(name="Inventory Category", slug="inventory-category")
        product = Product(name="Inventory Sneaker", slug="inventory-sneaker", brand=brand, category=category, base_price=Decimal("5000.00"))
        admin = User(email="inventory-admin@example.com", password_hash=generate_password_hash("CorrectHorseBatteryStaple!"), first_name="Inventory", last_name="Admin", role="admin")
        db.session.add_all([brand, category, product, admin])
        db.session.flush()
        cls.product = product
        cls.variant = ProductVariant(product=product, sku="INV-LOW-08", size="8", color="Black", price=Decimal("5100.00"), stock_quantity=3, is_active=True)
        db.session.add(cls.variant)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def setUp(self):
        self.client = self.app.test_client()
        login = self.client.get("/admin/login")
        csrf = re.search(r'name="csrf_token" value="([^"]+)"', login.get_data(as_text=True)).group(1)
        response = self.client.post("/admin/login", data={"csrf_token": csrf, "email": "inventory-admin@example.com", "password": "CorrectHorseBatteryStaple!"})
        self.assertEqual(response.status_code, 302)
        dashboard = self.client.get("/admin/")
        self.csrf = re.search(r'name="csrf_token" value="([^"]+)"', dashboard.get_data(as_text=True)).group(1)

    def test_unauthorized_access_redirects(self):
        self.assertEqual(self.app.test_client().get("/admin/inventory").status_code, 302)

    def test_listing_and_low_stock_filter(self):
        response = self.client.get("/admin/inventory?stock_status=low")
        self.assertEqual(response.status_code, 200)
        self.assertIn("INV-LOW-08", response.get_data(as_text=True))
        self.assertIn("Low stock", response.get_data(as_text=True))

    def test_stock_update_and_negative_validation(self):
        response = self.client.post(f"/admin/inventory/{self.variant.id}/stock", data={"csrf_token": self.csrf, "stock_quantity": "12"})
        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.variant)
        self.assertEqual(self.variant.stock_quantity, 12)
        invalid = self.client.post(f"/admin/inventory/{self.variant.id}/stock", data={"csrf_token": self.csrf, "stock_quantity": "-1"})
        self.assertEqual(invalid.status_code, 302)
        db.session.refresh(self.variant)
        self.assertEqual(self.variant.stock_quantity, 12)

    def test_variant_creation_and_edit(self):
        created = self.client.post("/admin/inventory/new", data={"csrf_token": self.csrf, "product_id": self.product.id, "sku": "INV-NEW-09", "size": "9", "color": "White", "price": "5200.00", "stock_quantity": "0", "is_active": "on"})
        self.assertEqual(created.status_code, 302)
        new_variant = ProductVariant.query.filter_by(sku="INV-NEW-09").one()
        edited = self.client.post(f"/admin/inventory/{new_variant.id}/edit", data={"csrf_token": self.csrf, "product_id": self.product.id, "sku": "INV-NEW-09-EDITED", "size": "10", "color": "Red", "price": "5300.00", "stock_quantity": "8", "is_active": "on"})
        self.assertEqual(edited.status_code, 302)
        db.session.refresh(new_variant)
        self.assertEqual((new_variant.sku, new_variant.size, new_variant.stock_quantity), ("INV-NEW-09-EDITED", "10", 8))

    def test_csrf_is_required(self):
        response = self.client.post(f"/admin/inventory/{self.variant.id}/stock", data={"stock_quantity": "4"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
