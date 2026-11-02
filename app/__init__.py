import os

from flask import Flask

from config import config_by_name
from .extensions import db, migrate
from . import models
from .routes.admin import admin_bp, register_admin_cli
from .routes.admin_products import admin_products_bp
from .routes.admin_inventory import admin_inventory_bp
from .routes.admin_orders import admin_orders_bp
from .routes.checkout import checkout_bp
from .routes.customer_auth import customer_auth_bp
from .routes.main import main_bp


def create_app(config_name=None):
    app = Flask(__name__)
    selected_config = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(selected_config, config_by_name["development"]))

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(main_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(customer_auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_products_bp)
    app.register_blueprint(admin_inventory_bp)
    app.register_blueprint(admin_orders_bp)
    register_admin_cli(app)

    return app
