import re
import unittest
from datetime import timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Order, User
from app.utils.time import utc_now
from config import config_by_name


config_by_name["admin_customers_testing"] = type(
    "AdminCustomersTestingConfig",
    (),
    {
        "SECRET_KEY": "admin-customers-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "RATELIMIT_ENABLED": False,
    },
)


class AdminCustomerManagementTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("admin_customers_testing")
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.admin = User(
            email="customers-admin@example.com",
            password_hash=generate_password_hash("AdminPassword!123"),
            first_name="Store",
            last_name="Admin",
            role="admin",
        )
        self.customer = User(
            email="sneaker.buyer@example.com",
            password_hash=generate_password_hash("PrivatePassword!123"),
            first_name="Sneaker",
            last_name="Buyer",
            phone="9876543210",
            created_at=utc_now() - timedelta(days=20),
        )
        db.session.add_all([self.admin, self.customer])
        db.session.flush()
        db.session.add(
            Order(
                order_number="SZ-CUSTOMER-001",
                checkout_token="customer-order-token",
                user_id=self.customer.id,
                status="delivered",
                payment_method="cod",
                payment_status="paid",
                subtotal=Decimal("5000"),
                shipping_fee=Decimal("0"),
                total_amount=Decimal("5000"),
                customer_name="Sneaker Buyer",
                customer_email=self.customer.email,
                customer_phone=self.customer.phone,
                shipping_address="Somewhere",
                shipping_city="City",
                shipping_state="State",
                shipping_postal_code="123456",
            )
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def admin_client(self):
        client = self.app.test_client()
        login = client.get("/admin/login")
        csrf = re.search(r'name="csrf_token" value="([^"]+)"', login.get_data(as_text=True)).group(1)
        client.post(
            "/admin/login",
            data={"csrf_token": csrf, "email": self.admin.email, "password": "AdminPassword!123"},
        )
        return client

    def test_customer_routes_require_admin(self):
        client = self.app.test_client()
        self.assertEqual(client.get("/admin/customers").status_code, 302)
        self.assertEqual(client.get(f"/admin/customers/{self.customer.id}").status_code, 302)

    def test_list_searches_customers_and_shows_order_count_without_secrets(self):
        response = self.admin_client().get("/admin/customers?search=Sneaker%20Buyer")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.customer.email, body)
        self.assertIn("9876543210", body)
        self.assertIn("Sneaker Buyer", body)
        self.assertIn("1</td>", body)
        self.assertNotIn("PrivatePassword!123", body)
        self.assertNotIn(self.customer.password_hash, body)
        self.assertNotIn("last login", body.lower())

    def test_detail_shows_order_history_and_excludes_admin_accounts(self):
        client = self.admin_client()
        detail = client.get(f"/admin/customers/{self.customer.id}")
        body = detail.get_data(as_text=True)
        self.assertEqual(detail.status_code, 200)
        self.assertIn("SZ-CUSTOMER-001", body)
        self.assertIn("Order history", body)
        self.assertNotIn(self.customer.password_hash, body)
        self.assertEqual(client.get(f"/admin/customers/{self.admin.id}").status_code, 404)

    def test_customer_list_paginates_at_25(self):
        db.session.add_all(
            [
                User(
                    email=f"page-customer-{index}@example.com",
                    password_hash="unused-test-hash",
                    first_name="Page",
                    last_name=f"Customer{index}",
                    role="customer",
                )
                for index in range(26)
            ]
        )
        db.session.commit()
        client = self.admin_client()
        first = client.get("/admin/customers")
        self.assertEqual(first.status_code, 200)
        self.assertIn("Page 1 of 2", first.get_data(as_text=True))
        second = client.get("/admin/customers?page=2")
        self.assertEqual(second.status_code, 200)
        self.assertIn("Page 2 of 2", second.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
