import re
import unittest
from datetime import timedelta

from app import create_app
from app.extensions import db
from config import config_by_name


RateLimitTestingConfig = type(
    "RateLimitTestingConfig",
    (),
    {
        "SECRET_KEY": "rate-limit-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=2),
        "RATELIMIT_ENABLED": True,
        "RATELIMIT_STORAGE_URI": "memory://",
        "CUSTOMER_LOGIN_RATE_LIMIT": "1 per minute",
        "ADMIN_LOGIN_RATE_LIMIT": "1 per minute",
        "REGISTRATION_RATE_LIMIT": "1 per minute",
        "FORGOT_PASSWORD_RATE_LIMIT": "1 per minute",
    },
)
config_by_name["rate_limit_testing"] = RateLimitTestingConfig


class RateLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("rate_limit_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def csrf(self, client, path):
        page = client.get(path)
        return re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True)).group(1)

    def assert_throttled(self, client, path, data):
        first = client.post(path, data=data, environ_base={"REMOTE_ADDR": "192.0.2.10"})
        second = client.post(path, data=data, environ_base={"REMOTE_ADDR": "192.0.2.10"})
        self.assertNotEqual(first.status_code, 429)
        self.assertEqual(second.status_code, 429)
        self.assertIn("Too many requests", second.get_data(as_text=True))

    def test_all_sensitive_customer_and_admin_posts_are_rate_limited_per_ip(self):
        client = self.app.test_client()
        login_token = self.csrf(client, "/login")
        self.assert_throttled(client, "/login", {"csrf_token": login_token, "email": "missing@example.com", "password": "wrong"})

        admin_token = self.csrf(client, "/admin/login")
        self.assert_throttled(client, "/admin/login", {"csrf_token": admin_token, "email": "missing@example.com", "password": "wrong"})

        register_token = self.csrf(client, "/register")
        self.assert_throttled(client, "/register", {"csrf_token": register_token})

        forgot_token = self.csrf(client, "/forgot-password")
        self.assert_throttled(client, "/forgot-password", {"csrf_token": forgot_token, "email": "invalid"})


if __name__ == "__main__":
    unittest.main()
