import re
from urllib.parse import urlsplit

from flask import Blueprint, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Brand
from .admin import _csrf_token, _valid_csrf_token, admin_required


admin_brands_bp = Blueprint("admin_brands", __name__, url_prefix="/admin/brands")


@admin_brands_bp.before_request
def protect_brand_posts():
    if request.method == "POST" and not _valid_csrf_token():
        return render_template("admin/login.html", error="Your form session expired. Please try again.", csrf_token=_csrf_token()), 400


def _brand_values(form):
    name = form.get("name", "").strip()
    slug = form.get("slug", "").strip().lower()
    description = form.get("description", "").strip() or None
    logo_url = form.get("logo_url", "").strip() or None
    if not name or len(name) > 120:
        raise ValueError("Brand name is required and must be 120 characters or fewer.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 140:
        raise ValueError("Slug must use lowercase letters, numbers, and single hyphens.")
    if logo_url:
        parsed = urlsplit(logo_url)
        if len(logo_url) > 500 or parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Brand logos must use a valid HTTPS URL.")
    return {"name": name, "slug": slug, "description": description, "logo_url": logo_url, "is_active": form.get("is_active") == "on"}


def _render_form(brand=None, error=None, status=200):
    return render_template("admin/brands/form.html", brand=brand, error=error, csrf_token=_csrf_token()), status


@admin_brands_bp.get("")
@admin_required
def listing():
    brands = Brand.query.order_by(Brand.name.asc(), Brand.id.asc()).all()
    return render_template("admin/brands/list.html", brands=brands, csrf_token=_csrf_token())


@admin_brands_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create():
    if request.method == "GET":
        return _render_form()
    try:
        values = _brand_values(request.form)
        if Brand.query.filter_by(slug=values["slug"]).first():
            raise ValueError("A brand with this slug already exists.")
        db.session.add(Brand(**values))
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return _render_form(error=str(error), status=400)
    except Exception:
        db.session.rollback()
        return _render_form(error="Unable to save the brand.", status=500)
    return redirect(url_for("admin_brands.listing"))


@admin_brands_bp.route("/<int:brand_id>/edit", methods=["GET", "POST"])
@admin_required
def edit(brand_id):
    brand = db.session.get(Brand, brand_id)
    if brand is None:
        return render_template("404.html"), 404
    if request.method == "GET":
        return _render_form(brand)
    try:
        values = _brand_values(request.form)
        duplicate = Brand.query.filter(Brand.slug == values["slug"], Brand.id != brand.id).first()
        if duplicate:
            raise ValueError("A brand with this slug already exists.")
        for field, value in values.items():
            setattr(brand, field, value)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        return _render_form(brand, str(error), 400)
    except Exception:
        db.session.rollback()
        return _render_form(brand, "Unable to update the brand.", 500)
    return redirect(url_for("admin_brands.listing"))


@admin_brands_bp.post("/<int:brand_id>/toggle")
@admin_required
def toggle(brand_id):
    brand = db.session.get(Brand, brand_id)
    if brand is None:
        return render_template("404.html"), 404
    brand.is_active = not brand.is_active
    db.session.commit()
    return redirect(url_for("admin_brands.listing"))
