import re
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User
from config import config_by_name


TestingConfig = type(
    "TestingConfig",
    (),
    {
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=2),
    },
)
config_by_name["testing"] = TestingConfig


class AdminAuthenticationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        admin = User(
            email="admin@example.com",
            password_hash=generate_password_hash("CorrectHorseBatteryStaple!"),
            first_name="Admin",
            last_name="User",
            role="admin",
        )
        customer = User(
            email="customer@example.com",
            password_hash=generate_password_hash("CustomerPassword!"),
            first_name="Customer",
            last_name="User",
            role="customer",
        )
        db.session.add_all([admin, customer])
        db.session.commit()
        cls.admin = admin

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def csrf_token(self, client):
        response = client.get("/admin/login")
        return re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)).group(1)

    def test_unauthorized_access_redirects(self):
        response = self.app.test_client().get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.location)

    def test_csrf_is_required(self):
        response = self.app.test_client().post(
            "/admin/login",
            data={"email": "admin@example.com", "password": "CorrectHorseBatteryStaple!"},
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_login_dashboard_and_logout(self):
        client = self.app.test_client()
        response = client.post(
            "/admin/login",
            data={
                "csrf_token": self.csrf_token(client),
                "email": "admin@example.com",
                "password": "CorrectHorseBatteryStaple!",
            },
        )
        self.assertEqual(response.status_code, 302)
        cookie = next((item for item in response.headers.getlist("Set-Cookie") if item.startswith("session=")), "")
        expires_text = next((part.split("=", 1)[1].strip() for part in cookie.split(";")[1:] if part.strip().lower().startswith("expires=")), "")
        self.assertTrue(expires_text)
        remaining = parsedate_to_datetime(expires_text) - datetime.now(timezone.utc)
        self.assertGreaterEqual(remaining, timedelta(hours=1, minutes=59))
        self.assertLessEqual(remaining, timedelta(hours=2, minutes=1))
        dashboard = client.get("/admin/")
        self.assertEqual(dashboard.status_code, 200)
        dashboard_token = re.search(r'name="csrf_token" value="([^"]+)"', dashboard.get_data(as_text=True)).group(1)
        logout = client.post("/admin/logout", data={"csrf_token": dashboard_token})
        self.assertEqual(logout.status_code, 302)
        self.assertEqual(client.get("/admin/").status_code, 302)

    def test_customer_role_cannot_login_to_admin(self):
        client = self.app.test_client()
        response = client.post(
            "/admin/login",
            data={
                "csrf_token": self.csrf_token(client),
                "email": "customer@example.com",
                "password": "CustomerPassword!",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_password_is_hashed(self):
        self.assertNotEqual(self.admin.password_hash, "CorrectHorseBatteryStaple!")
        self.assertTrue(check_password_hash(self.admin.password_hash, "CorrectHorseBatteryStaple!"))


if __name__ == "__main__":
    unittest.main()
