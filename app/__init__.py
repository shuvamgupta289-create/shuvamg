import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from flask import Flask, render_template
from flask.logging import default_handler
from flask.sessions import SecureCookieSessionInterface

from config import config_by_name, get_database_url, _engine_options_for_url
from .extensions import db, migrate
from . import models
from .routes.admin import admin_bp, register_admin_cli
from .routes.admin_products import admin_products_bp
from .routes.admin_brands import admin_brands_bp
from .routes.admin_inventory import admin_inventory_bp
from .routes.admin_orders import admin_orders_bp
from .routes.checkout import checkout_bp
from .routes.customer_auth import customer_auth_bp
from .routes.customer_shopping import customer_shopping_bp
from .routes.main import main_bp


class StepzoneSessionInterface(SecureCookieSessionInterface):
    """Apply Remember Me expiry only to opted-in customer sessions."""

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

    if selected_config == "production":
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            message = "SECRET_KEY must be set in the production environment."
            app.logger.error(message)
            raise RuntimeError(message)
        app.config["SECRET_KEY"] = secret_key
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

    return app
