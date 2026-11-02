import re
import unittest
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Order, OrderItem, Product, User
from config import config_by_name


TestingConfig = type(
    "TestingConfig",
    (),
    {
        "SECRET_KEY": "test-secret-products",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
    },
)
config_by_name["product_testing"] = TestingConfig


class AdminProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("product_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()
        cls.brand = Brand(name="Test Brand", slug="test-brand")
        cls.category = Category(name="Test Category", slug="test-category")
        cls.product = Product(
            name="Test Sneaker",
            slug="test-sneaker",
            brand=cls.brand,
            category=cls.category,
            base_price=Decimal("4999.00"),
            description="Test product",
        )
        admin = User(
            email="admin-products@example.com",
            password_hash=generate_password_hash("CorrectHorseBatteryStaple!"),
            first_name="Product",
            last_name="Admin",
            role="admin",
        )
        db.session.add_all([cls.brand, cls.category, cls.product, admin])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def setUp(self):
        self.client = self.app.test_client()
        login_page = self.client.get("/admin/login")
        self.csrf = re.search(r'name="csrf_token" value="([^"]+)"', login_page.get_data(as_text=True)).group(1)
        response = self.client.post(
            "/admin/login",
            data={
                "csrf_token": self.csrf,
                "email": "admin-products@example.com",
                "password": "CorrectHorseBatteryStaple!",
            },
        )
        self.assertEqual(response.status_code, 302)
        dashboard = self.client.get("/admin/")
        self.csrf = re.search(r'name="csrf_token" value="([^"]+)"', dashboard.get_data(as_text=True)).group(1)

    def product_data(self, **overrides):
        data = {
            "csrf_token": self.csrf,
            "name": "Fresh Sneaker",
            "slug": "fresh-sneaker",
            "brand_id": self.brand.id,
            "category_id": self.category.id,
            "base_price": "5999.00",
            "description": "Fresh test sneaker",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_listing_and_unauthorized_access(self):
        self.assertEqual(self.client.get("/admin/products").status_code, 200)
        listing = self.client.get("/admin/products").get_data(as_text=True)
        self.assertTrue("Test Sneaker" in listing or "Fresh Sneaker" in listing or "Updated Sneaker" in listing)
        self.assertEqual(self.app.test_client().get("/admin/products").status_code, 302)

    def test_create_and_duplicate_slug_validation(self):
        created = self.client.post("/admin/products/new", data=self.product_data())
        self.assertEqual(created.status_code, 302)
        self.assertIsNotNone(Product.query.filter_by(slug="fresh-sneaker").first())
        duplicate = self.client.post("/admin/products/new", data=self.product_data())
        self.assertEqual(duplicate.status_code, 400)

    def test_edit_and_toggle_product(self):
        response = self.client.post(
            f"/admin/products/{self.product.id}/edit",
            data=self.product_data(name="Updated Sneaker", slug="updated-sneaker"),
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.product)
        self.assertEqual(self.product.name, "Updated Sneaker")
        self.assertEqual(self.product.slug, "updated-sneaker")
        toggle = self.client.post(f"/admin/products/{self.product.id}/toggle", data={"csrf_token": self.csrf})
        self.assertEqual(toggle.status_code, 302)
        db.session.refresh(self.product)
        self.assertFalse(self.product.is_active)

    def test_csrf_and_order_referenced_delete_protection(self):
        missing_csrf = self.client.post(f"/admin/products/{self.product.id}/toggle")
        self.assertEqual(missing_csrf.status_code, 400)
        order = Order(
            order_number="SZ-TEST-ORDER",
            checkout_token="test-order-token",
            status="confirmed",
            payment_method="cod",
            payment_status="pending_cod",
            subtotal=Decimal("4999.00"),
            shipping_fee=Decimal("0.00"),
            total_amount=Decimal("4999.00"),
            customer_name="Test Customer",
            customer_email="customer@example.com",
            customer_phone="9999999999",
            shipping_address="Test Address",
            shipping_city="Test City",
            shipping_state="Test State",
            shipping_postal_code="000000",
        )
        order.items.append(OrderItem(product=self.product, product_variant_id=1, product_name=self.product.name, sku="TEST-SKU", size="7", unit_price=Decimal("4999.00"), quantity=1, line_total=Decimal("4999.00")))
        db.session.add(order)
        db.session.commit()
        response = self.client.post(f"/admin/products/{self.product.id}/delete", data={"csrf_token": self.csrf})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(db.session.get(Product, self.product.id))


if __name__ == "__main__":
    unittest.main()
