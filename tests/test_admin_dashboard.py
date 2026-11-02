import re
import unittest
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Order, OrderItem, Payment, Product, ProductVariant, User
from config import config_by_name


BaseTestingConfig = {
    "SECRET_KEY": "dashboard-test-secret",
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
    "SESSION_COOKIE_SECURE": False,
}
config_by_name["dashboard_testing"] = type("DashboardTestingConfig", (), BaseTestingConfig)
config_by_name["dashboard_empty_testing"] = type("DashboardEmptyTestingConfig", (), BaseTestingConfig)


class AdminDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("dashboard_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()
        brand = Brand(name="Dashboard Brand", slug="dashboard-brand")
        category = Category(name="Dashboard Category", slug="dashboard-category")
        product = Product(name="Dashboard Sneaker", slug="dashboard-sneaker", brand=brand, category=category, base_price=Decimal("5000.00"))
        low_variant = ProductVariant(product=product, sku="DASH-LOW", size="8", stock_quantity=3, price=Decimal("5000.00"))
        out_variant = ProductVariant(product=product, sku="DASH-OUT", size="9", stock_quantity=0, price=Decimal("5000.00"))
        admin = User(email="dashboard-admin@example.com", password_hash=generate_password_hash("CorrectHorseBatteryStaple!"), first_name="Dashboard", last_name="Admin", role="admin")
        db.session.add_all([brand, category, product, low_variant, out_variant, admin])
        db.session.flush()
        order = Order(order_number="SZ-DASH-ORDER", checkout_token="dashboard-token", status="pending", payment_method="cod", payment_status="paid", subtotal=Decimal("5000"), shipping_fee=Decimal("0"), total_amount=Decimal("5000"), customer_name="Dashboard Customer", customer_email="dashboard@example.com", customer_phone="9999999999", shipping_address="Dashboard Address", shipping_city="City", shipping_state="State", shipping_postal_code="000000")
        order.items.append(OrderItem(product=product, product_variant=low_variant, product_name=product.name, sku=low_variant.sku, size=low_variant.size, color=low_variant.color, unit_price=Decimal("5000"), quantity=1, line_total=Decimal("5000")))
        order.payment = Payment(provider="cod", provider_order_id=order.order_number, amount=Decimal("5000"), status="success")
        db.session.add(order)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def admin_client(self):
        client = self.app.test_client()
        login = client.get("/admin/login")
        csrf = re.search(r'name="csrf_token" value="([^"]+)"', login.get_data(as_text=True)).group(1)
        client.post("/admin/login", data={"csrf_token": csrf, "email": "dashboard-admin@example.com", "password": "CorrectHorseBatteryStaple!"})
        return client

    def test_dashboard_requires_admin(self):
        self.assertEqual(self.app.test_client().get("/admin/").status_code, 302)

    def test_dashboard_shows_live_statistics_and_order(self):
        response = self.admin_client().get("/admin/")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Dashboard Sneaker", body)
        self.assertIn("SZ-DASH-ORDER", body)
        self.assertIn("₹5,000.00", body)
        self.assertIn("Low stock", body)
        self.assertIn("Out of stock", body)

    def test_empty_database_dashboard(self):
        empty_app = create_app("dashboard_empty_testing")
        with empty_app.app_context():
            db.create_all()
            admin = User(email="empty-admin@example.com", password_hash=generate_password_hash("CorrectHorseBatteryStaple!"), first_name="Empty", last_name="Admin", role="admin")
            db.session.add(admin)
            db.session.commit()
            client = empty_app.test_client()
            login = client.get("/admin/login")
            csrf = re.search(r'name="csrf_token" value="([^"]+)"', login.get_data(as_text=True)).group(1)
            client.post("/admin/login", data={"csrf_token": csrf, "email": "empty-admin@example.com", "password": "CorrectHorseBatteryStaple!"})
            response = client.get("/admin/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("No orders yet.", response.get_data(as_text=True))
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
