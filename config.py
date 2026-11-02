import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return f"sqlite:///{BASE_DIR / 'stepzone.db'}"

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    parsed_url = urlsplit(database_url)
    query = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    query["sslmode"] = "require"
    return urlunsplit(parsed_url._replace(query=urlencode(query)))


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret")
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    PAYTM_MID = os.getenv("PAYTM_MID")
    PAYTM_MERCHANT_KEY = os.getenv("PAYTM_MERCHANT_KEY")
    PAYTM_WEBSITE = os.getenv("PAYTM_WEBSITE")
    PAYTM_ENVIRONMENT = os.getenv("PAYTM_ENVIRONMENT", "staging")
    PAYTM_CALLBACK_URL = os.getenv("PAYTM_CALLBACK_URL", "http://127.0.0.1:5000/payment/paytm/callback")
    PAYTM_INITIATE_URL = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction"
    PAYTM_STATUS_URL = "https://securegw-stage.paytm.in/v3/order/status"
    PAYTM_CHECKOUT_JS_URL = "https://securegw-stage.paytm.in/merchantpgpui/checkoutjs/merchants/{mid}.js"
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
    BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "STEPZONE")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
