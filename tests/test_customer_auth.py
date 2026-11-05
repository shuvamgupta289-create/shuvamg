import re
import unittest
from datetime import timedelta
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Order, User
from config import config_by_name


TestingConfig = type("CustomerTestingConfig", (), {"SECRET_KEY": "customer-test-secret", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "SQLALCHEMY_TRACK_MODIFICATIONS": False, "SESSION_COOKIE_HTTPONLY": True, "SESSION_COOKIE_SAMESITE": "Lax", "SESSION_COOKIE_SECURE": False, "PERMANENT_SESSION_LIFETIME": timedelta(hours=2)})
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
        registration_page = client.get("/register")
        token = re.search(r'name="csrf_token" value="([^"]+)"', registration_page.get_data(as_text=True)).group(1)
        data = {"csrf_token": token, "first_name": "New", "last_name": "Customer", "email": "new@example.com", "phone": "7777777777", "password": "NewCustomerPassword!", "confirm_password": "NewCustomerPassword!"}
        response = client.post("/register", data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")
        created = User.query.filter_by(email="new@example.com").one()
        self.assertEqual(created.role, "customer")
        self.assertTrue(created.password_hash != data["password"])
        with client.session_transaction() as flask_session:
            self.assertEqual(flask_session["customer_user_id"], created.id)
            self.assertEqual(flask_session["customer_display_name"], "New")
            self.assertTrue(flask_session["customer_csrf_token"])
            self.assertNotEqual(flask_session["customer_csrf_token"], token)
            self.assertFalse(flask_session.permanent)
        self.assertIn("Welcome to STEPZONE! Your account has been created successfully.", client.get("/").get_data(as_text=True))

        duplicate_client = self.app.test_client()
        duplicate_data = {**data, "csrf_token": self.csrf(duplicate_client, "/register")}
        duplicate_response = duplicate_client.post("/register", data=duplicate_data)
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertIn("already exists", duplicate_response.get_data(as_text=True))

    def test_registration_returns_to_safe_shopping_destination(self):
        client = self.app.test_client()
        page = client.get("/register?next=%2Fcart")
        token = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True)).group(1)
        response = client.post("/register", data={
            "csrf_token": token,
            "next": "/cart",
            "first_name": "Next",
            "last_name": "Shopper",
            "email": "next-shopper@example.com",
            "password": "LongCustomerPassword!",
            "confirm_password": "LongCustomerPassword!",
        })
        self.assertEqual(response.location, "/cart")
        with client.session_transaction() as flask_session:
            self.assertEqual(flask_session["customer_display_name"], "Next")

    def test_registration_rejects_missing_or_external_next(self):
        client = self.app.test_client()
        page = client.get("/register?next=https%3A%2F%2Fevil.example")
        self.assertIn('name="next" value="/"', page.get_data(as_text=True))

    def test_registration_rejects_invalid_password_and_mismatch(self):
        client = self.app.test_client()
        token = self.csrf(client, "/register")
        common = {"csrf_token": token, "first_name": "Invalid", "last_name": "Password", "email": "invalid-password@example.com"}
        short_password = client.post("/register", data={**common, "password": "short", "confirm_password": "short"})
        self.assertEqual(short_password.status_code, 400)
        self.assertIn("at least 12 characters", short_password.get_data(as_text=True))
        mismatched = client.post("/register", data={**common, "password": "LongCustomerPassword!", "confirm_password": "DifferentPassword!"})
        self.assertEqual(mismatched.status_code, 400)
        self.assertIn("Passwords do not match", mismatched.get_data(as_text=True))

    def test_registration_csrf_failure_returns_a_fresh_token(self):
        client = self.app.test_client()
        page = client.get("/register")
        old_token = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True)).group(1)
        response = client.post("/register", data={"first_name": "No", "last_name": "Token"})
        self.assertEqual(response.status_code, 400)
        fresh_token = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)).group(1)
        self.assertNotEqual(old_token, fresh_token)
        self.assertIsNone(User.query.filter_by(email="no-token@example.com").first())

    def test_login_csrf_failure_refreshes_token_without_caching(self):
        client = self.app.test_client()
        login_page = client.get("/login?next=%2Fcart")
        self.assertEqual(login_page.headers.get("Cache-Control"), "no-store")
        self.assertIn('class="customer-login-body"', login_page.get_data(as_text=True))
        old_token = re.search(r'name="csrf_token" value="([^"]+)"', login_page.get_data(as_text=True)).group(1)
        missing = client.post("/login", data={"next": "/cart", "email": "first@example.com", "password": "CustomerPassword!"})
        self.assertEqual(missing.status_code, 400)
        missing_token = re.search(r'name="csrf_token" value="([^"]+)"', missing.get_data(as_text=True)).group(1)
        self.assertNotEqual(old_token, missing_token)
        failed = client.post("/login", data={"csrf_token": "wrong", "next": "/cart", "email": "first@example.com", "password": "CustomerPassword!"})
        self.assertEqual(failed.status_code, 400)
        self.assertEqual(failed.headers.get("Cache-Control"), "no-store")
        self.assertIn('class="customer-login-body"', failed.get_data(as_text=True))
        new_token = re.search(r'name="csrf_token" value="([^"]+)"', failed.get_data(as_text=True)).group(1)
        self.assertNotEqual(missing_token, new_token)
        self.assertIn('name="next" value="/cart"', failed.get_data(as_text=True))
        self.assertEqual(client.post("/login", data={"csrf_token": new_token, "next": "/cart", "email": "first@example.com", "password": "CustomerPassword!"}).location, "/cart")

    def test_login_page_has_accessible_controls_and_safe_registration_return(self):
        client = self.app.test_client()
        page = client.get("/login")
        markup = page.get_data(as_text=True)
        self.assertIn('name="register_next" value="/"', markup)
        self.assertIn('aria-label="Show password"', markup)
        self.assertIn('aria-pressed="false"', markup)
        self.assertIn('aria-live="polite"', markup)
        self.assertIn('name="next" value="/account"', markup)

    def test_login_rejects_unknown_email_and_wrong_password(self):
        client = self.app.test_client()
        token = self.csrf(client)
        for email, password in (("unknown@example.com", "CustomerPassword!"), ("first@example.com", "wrong-password")):
            response = client.post("/login", data={"csrf_token": token, "email": email, "password": password})
            self.assertEqual(response.status_code, 401)
            self.assertIn("Invalid email or password.", response.get_data(as_text=True))

    def test_logout_invalidates_pre_logout_csrf_token(self):
        client = self.app.test_client()
        self.login(client)
        stale_token = self.csrf(client, "/account")
        self.assertEqual(client.post("/logout", data={"csrf_token": stale_token}).status_code, 302)
        fresh_token = self.csrf(client, "/login")
        stale_post = client.post("/login", data={"csrf_token": stale_token, "email": "first@example.com", "password": "CustomerPassword!"})
        self.assertEqual(stale_post.status_code, 400)
        self.assertNotEqual(re.search(r'name="csrf_token" value="([^"]+)"', stale_post.get_data(as_text=True)).group(1), fresh_token)

    def test_admin_account_cannot_use_customer_login(self):
        client = self.app.test_client()
        token = self.csrf(client)
        response = client.post("/login", data={"csrf_token": token, "email": "customer-test-admin@example.com", "password": "CorrectHorseBatteryStaple!"})
        self.assertEqual(response.status_code, 401)
        with client.session_transaction() as flask_session:
            self.assertNotIn("customer_user_id", flask_session)

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
