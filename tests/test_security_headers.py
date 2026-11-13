import re
import unittest
from datetime import timedelta

from app import create_app
from app.extensions import db
from config import config_by_name


SecurityTestingConfig = type(
    "SecurityTestingConfig",
    (),
    {
        "SECRET_KEY": "security-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=2),
    },
)
config_by_name["security_testing"] = SecurityTestingConfig


class SecurityHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("security_testing")
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_security_headers_are_present_on_responses(self):
        response = self.app.test_client().get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["Referrer-Policy"], "strict-origin-when-cross-origin")

    def test_external_stylesheets_and_scripts_have_sha384_integrity(self):
        html = self.app.test_client().get("/").get_data(as_text=True)
        tags = re.findall(r"<(?:link|script)\b[^>]*(?:href|src)=\"https://[^\"]+\"[^>]*>", html)
        external_assets = [tag for tag in tags if "rel=\"stylesheet\"" in tag or "<script" in tag]
        self.assertGreaterEqual(len(external_assets), 5)
        for tag in external_assets:
            self.assertRegex(tag, r'integrity="sha384-[A-Za-z0-9+/=]+"')


if __name__ == "__main__":
    unittest.main()
