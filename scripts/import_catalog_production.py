"""Guarded STEPZONE production catalogue importer.

The CLI is dry-run by default. Production writes require an approval manifest,
the explicit --execute-production switch, a confirmation phrase, and a Supabase
PostgreSQL destination. This module never loads dotenv files.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from decimal import Decimal
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "reports" / "production_catalog_import_plan.json"
LOCAL_DB = ROOT / "local_test_data" / "stepzone_catalog_test.sqlite3"
APPROVALS_PATH = ROOT / "reports" / "catalog_import_approvals.json"
HOLD_SLUGS = {"zig-kinetica-25"}
PROTECTED_PRODUCT_SLUGS = {
    "air-max-dn8", "forum-low-classic", "574-core-trainer",
    "club-c-revenge", "rs-x-heritage", "old-skool-classic",
}
PROTECTED_SKUS = {
    "SZ-NIKE-DN8-08-BLK", "SZ-NIKE-DN8-09-BLK", "SZ-NIKE-DN8-10-BLK",
    "SZ-ADI-FORUM-07-WHT", "SZ-ADI-FORUM-08-WHT", "SZ-ADI-FORUM-09-WHT",
    "SZ-NB-574-06-GRY", "SZ-NB-574-07-GRY", "SZ-NB-574-08-GRY",
    "SZ-REEBOK-CCR-07-WHT", "SZ-REEBOK-CCR-08-WHT", "SZ-REEBOK-CCR-09-WHT",
    "SZ-PUMA-RSX-08-ORG", "SZ-PUMA-RSX-09-ORG", "SZ-PUMA-RSX-10-ORG",
    "SZ-VANS-OS-07-BLK", "SZ-VANS-OS-08-BLK", "SZ-VANS-OS-09-BLK",
}
EXECUTION_CONFIRMATION = "STEPZONE PRODUCTION IMPORT CONFIRMED"


class ImportSafetyError(RuntimeError):
    """Raised when import preconditions are not satisfied."""


def load_plan(path: Path = PLAN_PATH) -> dict[str, Any]:
    if path.resolve() != PLAN_PATH.resolve():
        raise ImportSafetyError("Only the reviewed production import plan may be used.")
    plan = json.loads(path.read_text(encoding="utf-8-sig"))
    if plan.get("production_connection_attempted") or plan.get("production_writes_performed"):
        raise ImportSafetyError("The plan must remain an offline preparation artifact.")
    if plan.get("mode") != "OFFLINE_PREPARATION_ONLY" or plan.get("safety", {}).get("production_execution_script_created") is not True:
        raise ImportSafetyError("Reviewed plan safety state is missing.")
    if plan.get("held", {}).get("product", {}).get("slug") != "zig-kinetica-25":
        raise ImportSafetyError("The Reebok hold record is missing from the reviewed plan.")
    return plan


def validate_approval(slug: str, approval: dict[str, Any]) -> None:
    if slug in HOLD_SLUGS:
        raise ImportSafetyError(f"Held product '{slug}' cannot be approved for import.")
    required_true = (
        "product_approved",
        "description_approved",
        "image_decision_approved",
        "edition_colorway_reviewed",
    )
    if any(approval.get(field) is not True for field in required_true):
        raise ImportSafetyError(f"Product '{slug}' lacks all required explicit approvals.")
    if not isinstance(approval.get("description"), str) or not approval["description"].strip():
        raise ImportSafetyError(f"Product '{slug}' needs approved description text.")
    if approval.get("image_url") is not None and not isinstance(approval.get("image_url"), str):
        raise ImportSafetyError(f"Product '{slug}' has an invalid approved image URL.")
    if approval.get("image_url") is None and approval.get("image_fallback_approved") is not True:
        raise ImportSafetyError(f"Product '{slug}' needs an approved image or explicit fallback approval.")


def approved_candidate_records(
    plan: dict[str, Any], local: dict[str, Any], approvals: dict[str, Any]
) -> list[dict[str, Any]]:
    candidate_rows = plan.get("candidates", {}).get("products", [])
    candidates = {row["slug"]: row for row in candidate_rows}
    if len(candidates) != len(candidate_rows):
        raise ImportSafetyError("Reviewed plan contains duplicate candidate product slugs.")
    local_products = {row["slug"]: row for row in local["products"]}
    brands = {row["id"]: row for row in local["brands"]}
    categories = {row["id"]: row for row in local["categories"]}
    variants_by_product: dict[int, list[dict[str, Any]]] = {}
    for variant in local["product_variants"]:
        variants_by_product.setdefault(variant["product_id"], []).append(variant)
    unknown = set(approvals) - set(candidates)
    if unknown:
        raise ImportSafetyError("Approval manifest contains a non-candidate or held product.")
    records = []
    local_slug_counts: dict[str, int] = {}
    local_sku_counts: dict[str, int] = {}
    for row in local["products"]:
        local_slug_counts[row["slug"]] = local_slug_counts.get(row["slug"], 0) + 1
    for row in local["product_variants"]:
        local_sku_counts[row["sku"]] = local_sku_counts.get(row["sku"], 0) + 1
    planned_variants: dict[str, dict[str, dict[str, Any]]] = {}
    for row in plan.get("candidates", {}).get("variants", []):
        slug, sku = row.get("product_slug"), row.get("sku")
        if slug not in candidates or not isinstance(sku, str):
            raise ImportSafetyError("Reviewed plan contains a variant outside its product candidate list.")
        planned_variants.setdefault(slug, {})
        if sku in planned_variants[slug]:
            raise ImportSafetyError(f"Reviewed plan contains duplicate candidate SKU '{sku}'.")
        planned_variants[slug][sku] = row
    for slug, approval in sorted(approvals.items()):
        validate_approval(slug, approval)
        if slug in PROTECTED_PRODUCT_SLUGS or local_slug_counts.get(slug) != 1:
            raise ImportSafetyError(f"Product '{slug}' is protected or its local slug is duplicated.")
        product = local_products.get(slug)
        candidate = candidates.get(slug)
        if product is None or candidate is None:
            raise ImportSafetyError(f"Approved product '{slug}' is absent from the reviewed local catalog plan.")
        brand = brands.get(product["brand_id"])
        category = categories.get(product["category_id"])
        if not brand or not category or not brand["is_active"] or not category["is_active"]:
            raise ImportSafetyError(f"Product '{slug}' has an unresolved or inactive brand/category mapping.")
        if brand["slug"] != candidate["brand_slug"] or category["slug"] != candidate["category_slug"]:
            raise ImportSafetyError(f"Product '{slug}' mapping differs from the reviewed plan.")
        if (product["name"] != candidate.get("name")
                or Decimal(str(product["base_price"])) != Decimal(str(candidate.get("base_price")))
                or category["id"] != candidate.get("category_id")):
            raise ImportSafetyError(f"Product '{slug}' values differ from the reviewed plan.")
        if slug == "gel-quantum-360-viii" and category["slug"] != "unisex-sneakers":
            raise ImportSafetyError("ASICS GEL-Quantum 360 VIII must remain Unisex Sneakers.")
        variants = variants_by_product.get(product["id"], [])
        if (len(variants) != 6 or Decimal(str(product["base_price"])) <= 0
                or any(int(row["stock_quantity"]) <= 0 or Decimal(str(row["price"])) <= 0 for row in variants)
                or any(local_sku_counts.get(row["sku"]) != 1 or row["sku"] in PROTECTED_SKUS for row in variants)):
            raise ImportSafetyError(f"Product '{slug}' must have six positive-stock local variants.")
        reviewed_variants = planned_variants.get(slug, {})
        if set(reviewed_variants) != {row["sku"] for row in variants}:
            raise ImportSafetyError(f"Product '{slug}' local SKU set differs from the reviewed plan.")
        for variant in variants:
            reviewed = reviewed_variants[variant["sku"]]
            if (str(variant["size"]) != str(reviewed.get("size"))
                    or variant["color"] != reviewed.get("color")
                    or Decimal(str(variant["price"])) != Decimal(str(reviewed.get("price")))
                    or variant["stock_quantity"] != reviewed.get("local_stock_quantity")):
                raise ImportSafetyError(f"Local SKU '{variant['sku']}' values differ from the reviewed plan.")
        records.append({
            "slug": slug,
            "name": product["name"],
            "brand_slug": brand["slug"],
            "category_slug": category["slug"],
            "description": approval["description"].strip(),
            "image_url": approval.get("image_url"),
            "base_price": product["base_price"],
            "variants": variants,
        })
    return records


def _insert_records(session: Any, records: list[dict[str, Any]], models: dict[str, Any]) -> dict[str, Any]:
    """Insert missing approved rows in the caller's active transaction."""
    Product = models["Product"]
    ProductVariant = models["ProductVariant"]
    Brand = models["Brand"]
    Category = models["Category"]
    result = {"products_inserted": 0, "variants_inserted": 0, "products_existing": 0, "variants_existing": 0, "puma_stock_discrepancies": []}
    seen_slugs: set[str] = set()
    seen_skus: set[str] = set()
    for record in records:
        slug = record["slug"]
        if slug in HOLD_SLUGS:
            raise ImportSafetyError("Held Reebok product reached insertion stage.")
        if slug in PROTECTED_PRODUCT_SLUGS:
            raise ImportSafetyError("An existing production product reached insertion stage.")
        if slug in seen_slugs:
            raise ImportSafetyError(f"Duplicate product slug in input: {slug}")
        seen_slugs.add(slug)
        brand = session.query(Brand).filter_by(slug=record["brand_slug"], is_active=True).one_or_none()
        category = session.query(Category).filter_by(slug=record["category_slug"], is_active=True).one_or_none()
        if brand is None or category is None:
            raise ImportSafetyError(f"Missing active foreign-key mapping for '{slug}'.")
        existing = session.query(Product).filter_by(slug=slug).one_or_none()
        if existing is None:
            product = Product(
                name=record["name"], slug=slug, brand_id=brand.id, category_id=category.id,
                description=record["description"], image_url=record["image_url"],
                base_price=record["base_price"], is_active=True,
            )
            session.add(product)
            session.flush()
            result["products_inserted"] += 1
        else:
            if existing.brand_id != brand.id or existing.category_id != category.id:
                raise ImportSafetyError(f"Existing product '{slug}' has conflicting brand/category; it was not changed.")
            if (existing.name != record["name"]
                    or Decimal(str(existing.base_price)) != Decimal(str(record["base_price"]))
                    or existing.description != record["description"]
                    or existing.image_url != record["image_url"]):
                raise ImportSafetyError(f"Existing product '{slug}' differs from the approved source; it was not changed.")
            product = existing
            result["products_existing"] += 1
        for source in record["variants"]:
            sku = source["sku"]
            if sku in PROTECTED_SKUS:
                raise ImportSafetyError(f"Existing production SKU '{sku}' is preservation-only.")
            if sku in seen_skus:
                raise ImportSafetyError(f"Duplicate SKU in input: {sku}")
            seen_skus.add(sku)
            existing_variant = session.query(ProductVariant).filter_by(sku=sku).one_or_none()
            if existing_variant is not None:
                if existing_variant.product_id != product.id:
                    raise ImportSafetyError(f"SKU '{sku}' already belongs to another product; it was not changed.")
                field_differences = []
                for field in ("size", "color", "price", "stock_quantity"):
                    existing_value, source_value = getattr(existing_variant, field), source[field]
                    differs = (Decimal(str(existing_value)) != Decimal(str(source_value))) if field == "price" else existing_value != source_value
                    if differs:
                        field_differences.append(field)
                if field_differences == ["stock_quantity"] and sku == "SZ-PUMA-RSX-08-ORG":
                    result["puma_stock_discrepancies"].append({"sku": sku, "production_stock": existing_variant.stock_quantity, "local_stock": source["stock_quantity"], "action": "preserve production stock"})
                elif field_differences:
                    raise ImportSafetyError(f"Existing SKU '{sku}' differs in {', '.join(field_differences)}; it was not changed.")
                result["variants_existing"] += 1
                continue
            session.add(ProductVariant(
                product_id=product.id, sku=sku, size=source["size"], color=source["color"],
                price=source["price"], stock_quantity=source["stock_quantity"], is_active=True,
            ))
            result["variants_inserted"] += 1
    return result


def import_catalog(session: Any, plan: dict[str, Any], local: dict[str, Any], approvals: dict[str, Any], *, dry_run: bool = True,
                   confirmation: str | None = None, models: dict[str, Any] | None = None) -> dict[str, Any]:
    records = approved_candidate_records(plan, local, approvals)
    if any(row.get("slug") in HOLD_SLUGS for row in records):
        raise ImportSafetyError("Held products are excluded.")
    if any(row.get("slug") in PROTECTED_PRODUCT_SLUGS for row in records):
        raise ImportSafetyError("The six existing production products are preservation-only.")
    if not dry_run and confirmation != EXECUTION_CONFIRMATION:
        raise ImportSafetyError("Production writes require the explicit confirmation phrase.")
    if not records and not dry_run:
        raise ImportSafetyError("No individually approved products were supplied for execution.")
    if not records:
        return {"dry_run": dry_run, "products_inserted": 0, "variants_inserted": 0, "products_existing": 0, "variants_existing": 0, "puma_stock_discrepancies": []}
    if models is None:
        from app.models import Brand, Category, Product, ProductVariant
        models = {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant}
    if dry_run:
        # This path is deliberately read-only: it reports counts and performs no add/flush/commit.
        return {"dry_run": True, "products_considered": len(records), "variants_considered": sum(len(row["variants"]) for row in records), "writes": 0}
    bind = session.get_bind()
    host = getattr(getattr(bind, "url", None), "host", None) or ""
    dialect = getattr(getattr(bind, "dialect", None), "name", "")
    if dialect != "postgresql" or not (host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")):
        raise ImportSafetyError("Execution is restricted to a Supabase PostgreSQL destination.")
    with session.begin():
        result = _insert_records(session, records, models)
    result["dry_run"] = False
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guarded STEPZONE product import; dry-run by default.")
    parser.add_argument("--approvals", type=Path, help="JSON approval manifest (never an environment file).")
    parser.add_argument("--execute-production", action="store_true", help="Enable the explicitly confirmed write path.")
    parser.add_argument("--confirm-production", default="", help="Type the required confirmation phrase exactly.")
    args = parser.parse_args(argv)
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    if not args.execute_production and args.confirm_production:
        parser.error("--confirm-production is only valid with --execute-production")
    if args.execute_production and args.confirm_production != EXECUTION_CONFIRMATION:
        parser.error("Production execution requires the separate confirmation phrase.")
    if args.approvals and args.approvals.resolve() != APPROVALS_PATH.resolve():
        parser.error("Use reports/catalog_import_approvals.json for product-specific approval records.")
    if args.execute_production and not args.approvals:
        parser.error("Production execution requires reports/catalog_import_approvals.json.")
    try:
        plan = load_plan()
        approvals = json.loads(args.approvals.read_text(encoding="utf-8")) if args.approvals else {}
        if not isinstance(approvals, dict):
            raise ImportSafetyError("Approval manifest must be a JSON object keyed by product slug.")
        if not args.execute_production and not approvals:
            result = {"dry_run": True, "candidate_products_awaiting_approval": plan["candidates"]["product_count"], "candidate_variants_awaiting_approval": plan["candidates"]["variant_count"], "approved_products": 0, "writes": 0, "database_connection": "none", "puma_stock_discrepancies": plan.get("discrepancies", [])}
            print(json.dumps(result, indent=2))
            return 0
        from scripts.prepare_catalog_import import read_local_catalog
        local = read_local_catalog(LOCAL_DB)
        # The explicit execution flag is the only way this code reaches create_app or a database session.
        if not args.execute_production:
            result = import_catalog(None, plan, local, approvals, dry_run=True)
            result.update({"database_connection": "none", "puma_stock_discrepancies": plan.get("discrepancies", [])})
        else:
            from app import create_app
            from app.extensions import db
            app = create_app("production")
            with app.app_context():
                result = import_catalog(db.session, plan, local, approvals, dry_run=False, confirmation=args.confirm_production)
                result["puma_stock_discrepancies"] = plan.get("discrepancies", [])
        print(json.dumps(result, indent=2, default=str))
        return 0
    except (ImportSafetyError, OSError, json.JSONDecodeError, RuntimeError) as error:
        print(f"Import refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
