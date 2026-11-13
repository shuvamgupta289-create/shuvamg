import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from flask import Flask, has_request_context, render_template, request
from flask_limiter.errors import RateLimitExceeded
from flask.logging import default_handler
from flask.sessions import SecureCookieSessionInterface

from config import config_by_name, get_database_url, _engine_options_for_url
from .extensions import db, limiter, migrate
from . import models
from .routes.admin import admin_bp, register_admin_cli
from .routes.admin_products import admin_products_bp
from .routes.admin_brands import admin_brands_bp
from .routes.admin_inventory import admin_inventory_bp
from .routes.admin_orders import admin_orders_bp
from .routes.admin_customers import admin_customers_bp
from .routes.checkout import checkout_bp
from .routes.customer_auth import customer_auth_bp
from .routes.customer_shopping import customer_shopping_bp
from .routes.main import main_bp


class StepzoneSessionInterface(SecureCookieSessionInterface):
    """Keep administrator auth in its own cookie and honor customer Remember Me."""

    def get_cookie_name(self, app):
        if has_request_context() and request.path.startswith("/admin"):
            return app.config.get("ADMIN_SESSION_COOKIE_NAME", "stepzone_admin_session")
        return app.config.get("SESSION_COOKIE_NAME", "session")

    def get_expiration_time(self, app, session):
        if session.permanent and session.get("customer_remember_me"):
            return datetime.now(timezone.utc) + timedelta(days=30)
        return super().get_expiration_time(app, session)


def _configure_logging(app):
    logger = app.logger
    if default_handler in logger.handlers:
        logger.removeHandler(default_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        )
        handler._stepzone_stderr_handler = True
        logger.addHandler(handler)


def _selected_config_name(config_name):
    app_env = (os.getenv("APP_ENV") or "").strip().lower()
    flask_env = (os.getenv("FLASK_ENV") or "").strip().lower()
    if "production" in {app_env, flask_env} or os.getenv("VERCEL"):
        return "production"
    return (config_name or app_env or flask_env or "development").strip().lower()


def create_app(config_name=None):
    app = Flask(__name__)
    app.session_interface = StepzoneSessionInterface()
    _configure_logging(app)

    selected_config = _selected_config_name(config_name)
    app.config.from_object(
        config_by_name.get(selected_config, config_by_name["development"])
    )
    is_test_config = "test" in selected_config.lower()
    app.config.setdefault("RATELIMIT_ENABLED", not is_test_config)
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")
    app.config.setdefault("CUSTOMER_LOGIN_RATE_LIMIT", "10 per 15 minutes")
    app.config.setdefault("ADMIN_LOGIN_RATE_LIMIT", "10 per 15 minutes")
    app.config.setdefault("REGISTRATION_RATE_LIMIT", "10 per 15 minutes")
    app.config.setdefault("FORGOT_PASSWORD_RATE_LIMIT", "5 per 15 minutes")
    app.config.setdefault("RATELIMIT_HEADERS_ENABLED", True)

    if selected_config == "production":
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            message = "SECRET_KEY must be set in the production environment."
            app.logger.error(message)
            raise RuntimeError(message)
        app.config["SECRET_KEY"] = secret_key
        paytm_environment = app.config.get("PAYTM_ENVIRONMENT", "staging")
        if paytm_environment not in {"staging", "production"}:
            raise RuntimeError("PAYTM_ENVIRONMENT must be either 'staging' or 'production'.")
        if paytm_environment == "production":
            missing_paytm = [
                key for key in ("PAYTM_MID", "PAYTM_MERCHANT_KEY", "PAYTM_WEBSITE", "PAYTM_CALLBACK_URL")
                if not app.config.get(key)
            ]
            if missing_paytm:
                message = "Production Paytm configuration is missing: " + ", ".join(missing_paytm)
                app.logger.error(message)
                raise RuntimeError(message)
        try:
            database_url = get_database_url(require_database=True)
        except RuntimeError:
            app.logger.exception("Production database configuration is invalid.")
            raise
    elif selected_config == "development":
        database_url = get_database_url()
    else:
        database_url = app.config["SQLALCHEMY_DATABASE_URI"]

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = _engine_options_for_url(database_url)

    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(main_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(customer_auth_bp)
    app.register_blueprint(customer_shopping_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_products_bp)
    app.register_blueprint(admin_brands_bp)
    app.register_blueprint(admin_inventory_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(admin_customers_bp)
    register_admin_cli(app)

    @app.errorhandler(500)
    def internal_server_error(error):
        original_exception = getattr(error, "original_exception", None)
        if original_exception is not None:
            app.logger.error(
                "Unhandled exception while handling a request.",
                exc_info=(
                    type(original_exception),
                    original_exception,
                    original_exception.__traceback__,
                ),
            )
        else:
            app.logger.error("Internal server error: %s", error)
        return render_template("500.html"), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return render_template("429.html"), 429

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://securegw-stage.paytm.in https://securegw.paytm.in; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com data:; "
            "img-src 'self' https: data:; "
            "connect-src 'self' https://securegw-stage.paytm.in https://securegw.paytm.in; "
            "frame-src https://securegw-stage.paytm.in https://securegw.paytm.in; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'self'",
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    return app
