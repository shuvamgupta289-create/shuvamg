import re
import unittest
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Order, User
from config import config_by_name


TestingConfig = type("CustomerTestingConfig", (), {"SECRET_KEY": "customer-test-secret", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SQLALCHEMY_TRACK_MODIFICATIONS": False, "SESSION_COOKIE_HTTPONLY": True, "SESSION_COOKIE_SAMESITE": "Lax", "SESSION_COOKIE_SECURE": False})
config_by_name["customer_testing"] = TestingConfig


class CustomerAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("customer_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()
        admin = User(email="customer-test-admin@example.com", password_hash=generate_password_hash("CorrectHorseBatteryStaple!"), first_name="Admin", last_name="User", role="admin")
        first = User(email="first@example.com", password_hash=generate_password_hash("CustomerPassword!"), first_name="First", last_name="Customer", phone="9999999999", role="customer")
        second = User(email="second@example.com", password_hash=generate_password_hash("CustomerPassword!"), first_name="Second", last_name="Customer", phone="8888888888", role="customer")
        db.session.add_all([admin, first, second])
        db.session.flush()
        cls.first = first
        cls.second = second
        cls.order = Order(order_number="SZ-CUSTOMER-1", checkout_token="customer-token-1", user_id=first.id, status="confirmed", payment_method="cod", payment_status="pending_cod", subtotal=Decimal("100"), shipping_fee=Decimal("0"), total_amount=Decimal("100"), customer_name="First Customer", customer_email="first@example.com", customer_phone="9999999999", shipping_address="Address", shipping_city="City", shipping_state="State", shipping_postal_code="000000")
        db.session.add(cls.order)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def setUp(self):
        self.first.email = "first@example.com"
        self.first.first_name = "First"
        self.first.last_name = "Customer"
        self.first.phone = "9999999999"
        self.first.address = None
        self.first.city = None
        self.first.state = None
        self.first.postal_code = None
        db.session.commit()

    def csrf(self, client, path="/login"):
        response = client.get(path)
        return re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)).group(1)

    def login(self, client, email="first@example.com"):
        response = client.post("/login", data={"csrf_token": self.csrf(client), "email": email, "password": "CustomerPassword!"})
        self.assertEqual(response.status_code, 302)

    def test_registration_and_duplicate_email(self):
        client = self.app.test_client()
        data = {"csrf_token": self.csrf(client, "/register"), "full_name": "New Customer", "email": "new@example.com", "phone": "7777777777", "password": "NewCustomerPassword!", "confirm_password": "NewCustomerPassword!"}
        self.assertEqual(client.post("/register", data=data).status_code, 302)
        self.assertEqual(client.post("/register", data=data).status_code, 400)
        created = User.query.filter_by(email="new@example.com").one()
        self.assertEqual(created.role, "customer")

    def test_login_logout_and_customer_cannot_access_admin(self):
        client = self.app.test_client()
        self.login(client)
        self.assertEqual(client.get("/account").status_code, 200)
        logout = client.post("/logout", data={"csrf_token": self.csrf(client, "/account")})
        self.assertEqual(logout.status_code, 302)
        self.assertEqual(client.get("/admin/").status_code, 302)

    def test_checkout_requires_login_and_returns_guest_to_cart(self):
        client = self.app.test_client()
        response = client.post("/checkout", data={"product_id": "42", "variant_id": "9", "quantity": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        self.assertEqual(parse_qs(urlsplit(response.location).query)["next"], ["/cart"])

    def test_order_ownership(self):
        first_client = self.app.test_client()
        self.login(first_client)
        self.assertEqual(first_client.get(f"/account/orders/{self.order.id}").status_code, 200)
        second_client = self.app.test_client()
        self.login(second_client, "second@example.com")
        self.assertEqual(second_client.get(f"/account/orders/{self.order.id}").status_code, 404)

    def test_profile_update_persists_all_fields(self):
        client = self.app.test_client()
        self.login(client)
        response = client.post("/account/profile", data={
            "csrf_token": self.csrf(client, "/account"),
            "full_name": "Updated Customer",
            "email": "updated@example.com",
            "phone": "7777777777",
            "address": "Updated Address",
            "city": "Updated City",
            "state": "Updated State",
            "postal_code": "123456",
        })
        self.assertEqual(response.status_code, 302)
        db.session.expire_all()
        updated = db.session.get(User, self.first.id)
        self.assertEqual((updated.first_name, updated.last_name), ("Updated", "Customer"))
        self.assertEqual((updated.email, updated.phone, updated.address, updated.city, updated.state, updated.postal_code), ("updated@example.com", "7777777777", "Updated Address", "Updated City", "Updated State", "123456"))

    def test_profile_update_rejects_bad_csrf_and_invalid_input(self):
        client = self.app.test_client()
        self.login(client)
        missing_csrf = client.post("/account/profile", data={"full_name": "Bad", "email": "bad@example.com", "phone": "1"}, follow_redirects=True)
        self.assertEqual(missing_csrf.status_code, 200)
        self.assertIn("form session expired", missing_csrf.get_data(as_text=True))
        invalid = client.post("/account/profile", data={"csrf_token": self.csrf(client, "/account"), "full_name": "Bad", "email": "bad@example.com", "phone": "1"}, follow_redirects=True)
        self.assertEqual(invalid.status_code, 200)
        self.assertIn("valid name", invalid.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
