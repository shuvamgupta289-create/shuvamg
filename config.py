import ipaddress
import logging
import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

_LOCAL_DATABASE_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _is_remote_postgres(parsed_url):
    if parsed_url.scheme not in {"postgresql+psycopg", "postgresql", "postgres"}:
        return False
    host = (parsed_url.hostname or "").lower().rstrip(".")
    if not host or host in _LOCAL_DATABASE_HOSTS or host.endswith(".localhost"):
        return False
    try:
        return not ipaddress.ip_address(host).is_loopback
    except ValueError:
        return True


def _engine_options_for_url(database_url):
    parsed_url = urlsplit(database_url)
    if parsed_url.scheme == "postgresql+psycopg":
        return {
            "pool_pre_ping": True,
            "pool_size": 1,
            "max_overflow": 0,
            "connect_args": {"prepare_threshold": None},
        }
    return {"pool_pre_ping": True}


def get_database_url(*, require_database=False):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        if require_database:
            message = (
                "DATABASE_URL must be set in production. Configure it with a "
                "Supabase PostgreSQL connection string."
            )
            logging.getLogger(__name__).error(message)
            raise RuntimeError(message)
        return f"sqlite:///{BASE_DIR / 'stepzone.db'}"

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    try:
        parsed_url = urlsplit(database_url)
    except ValueError as error:
        message = "DATABASE_URL is not a valid database URL."
        logging.getLogger(__name__).error(message)
        if require_database:
            raise RuntimeError(message) from error
        raise ValueError(message) from error

    if require_database and (
        parsed_url.scheme != "postgresql+psycopg" or not parsed_url.hostname
    ):
        message = (
            "DATABASE_URL must be a valid PostgreSQL URL in production; "
            "SQLite is not supported on Vercel."
        )
        logging.getLogger(__name__).error(message)
        raise RuntimeError(message)

    query = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    if _is_remote_postgres(parsed_url):
        query["sslmode"] = "require"
    return urlunsplit(parsed_url._replace(query=urlencode(query)))


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret")
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 1,
        "max_overflow": 0,
        "connect_args": {"prepare_threshold": None},
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    PAYTM_MID = os.getenv("PAYTM_MID")
    PAYTM_MERCHANT_KEY = os.getenv("PAYTM_MERCHANT_KEY")
    PAYTM_WEBSITE = os.getenv("PAYTM_WEBSITE")
    PAYTM_ENVIRONMENT = os.getenv("PAYTM_ENVIRONMENT", "staging")
    PAYTM_CALLBACK_URL = os.getenv(
        "PAYTM_CALLBACK_URL", "http://127.0.0.1:5000/payment/paytm/callback"
    )
    PAYTM_INITIATE_URL = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction"
    PAYTM_STATUS_URL = "https://securegw-stage.paytm.in/v3/order/status"
    PAYTM_CHECKOUT_JS_URL = "https://securegw-stage.paytm.in/merchantpgpui/checkoutjs/merchants/{mid}.js"
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
    BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "STEPZONE")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options_for_url(BaseConfig.SQLALCHEMY_DATABASE_URI)


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
