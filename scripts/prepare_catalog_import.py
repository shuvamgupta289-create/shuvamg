"""Prepare a dry-run STEPZONE catalog comparison without production access.

This standard-library-only tool reads the dedicated SQLite catalog in read-only
mode. It never imports Flask configuration, reads environment variables, or opens
a PostgreSQL connection. Production writes are not implemented.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATABASE = PROJECT_ROOT / "local_test_data" / "stepzone_catalog_test.sqlite3"
REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_JSON_REPORT = REPORTS_DIR / "catalog_import_dry_run.json"
DEFAULT_MARKDOWN_REPORT = REPORTS_DIR / "catalog_import_dry_run.md"

# Sanitized production facts supplied by the user and identified as verified.
# The tool does not independently query or verify a live production database.
USER_PRODUCTION_SNAPSHOT: dict[str, Any] = {
    "source": "User-provided verified sanitized production snapshot; offline only",
    "brands_complete": True,
    "products_complete": True,
    "categories_complete": True,
    "variants_complete": True,
    "reported_counts": {"active_brands": 7, "active_products": 6, "variants": 18},
    "brands": [
        {"id": 1, "slug": "nike", "name": "Nike", "is_active": True},
        {"id": 2, "slug": "adidas", "name": "Adidas", "is_active": True},
        {"id": 3, "slug": "new-balance", "name": "New Balance", "is_active": True},
        {"id": 4, "slug": "puma", "name": "Puma", "is_active": True},
        {"id": 5, "slug": "reebok", "name": "Reebok", "is_active": True},
        {"id": 6, "slug": "vans", "name": "Vans", "is_active": True},
        {"id": 7, "slug": "asics", "name": "Asics", "is_active": True},
    ],
    "categories": [
        {"id": 1, "slug": "mens-sneakers", "name": "Men's Sneakers", "is_active": True},
        {"id": 2, "slug": "womens-sneakers", "name": "Women's Sneakers", "is_active": True},
        {"id": 3, "slug": "unisex-sneakers", "name": "Unisex Sneakers", "is_active": True},
        {"id": 4, "slug": "performance-sneakers", "name": "Performance Sneakers", "is_active": True},
    ],
    "products": [
        {"id": 1, "name": "Air Max Dn8", "slug": "air-max-dn8", "brand_id": 1, "category_id": 1, "base_price": "14995"},
        {"id": 2, "name": "Forum Low Classic", "slug": "forum-low-classic", "brand_id": 2, "category_id": 3, "base_price": "10499"},
        {"id": 3, "name": "574 Core Trainer", "slug": "574-core-trainer", "brand_id": 3, "category_id": 2, "base_price": "8999"},
        {"id": 4, "name": "Club C Revenge", "slug": "club-c-revenge", "brand_id": 5, "category_id": 3, "base_price": "9799"},
        {"id": 5, "name": "RS-X Heritage", "slug": "rs-x-heritage", "brand_id": 4, "category_id": 1, "base_price": "11499"},
        {"id": 6, "name": "Old Skool Classic", "slug": "old-skool-classic", "brand_id": 6, "category_id": 3, "base_price": "7499"},
    ],
    "variants": [
        {"product_id": 1, "sku": "SZ-NIKE-DN8-08-BLK", "size": 8, "color": "Black", "price": "14995", "stock_quantity": 12},
        {"product_id": 1, "sku": "SZ-NIKE-DN8-09-BLK", "size": 9, "color": "Black", "price": "14995", "stock_quantity": 10},
        {"product_id": 1, "sku": "SZ-NIKE-DN8-10-BLK", "size": 10, "color": "Black", "price": "14995", "stock_quantity": 8},
        {"product_id": 2, "sku": "SZ-ADI-FORUM-07-WHT", "size": 7, "color": "White", "price": "10499", "stock_quantity": 14},
        {"product_id": 2, "sku": "SZ-ADI-FORUM-08-WHT", "size": 8, "color": "White", "price": "10499", "stock_quantity": 12},
        {"product_id": 2, "sku": "SZ-ADI-FORUM-09-WHT", "size": 9, "color": "White", "price": "10499", "stock_quantity": 9},
        {"product_id": 3, "sku": "SZ-NB-574-06-GRY", "size": 6, "color": "Grey", "price": "8999", "stock_quantity": 10},
        {"product_id": 3, "sku": "SZ-NB-574-07-GRY", "size": 7, "color": "Grey", "price": "8999", "stock_quantity": 12},
        {"product_id": 3, "sku": "SZ-NB-574-08-GRY", "size": 8, "color": "Grey", "price": "8999", "stock_quantity": 8},
        {"product_id": 4, "sku": "SZ-REEBOK-CCR-07-WHT", "size": 7, "color": "White", "price": "9799", "stock_quantity": 11},
        {"product_id": 4, "sku": "SZ-REEBOK-CCR-08-WHT", "size": 8, "color": "White", "price": "9799", "stock_quantity": 13},
        {"product_id": 4, "sku": "SZ-REEBOK-CCR-09-WHT", "size": 9, "color": "White", "price": "9799", "stock_quantity": 7},
        {"product_id": 5, "sku": "SZ-PUMA-RSX-08-ORG", "size": 8, "color": "Orange", "price": "11499", "stock_quantity": 8},
        {"product_id": 5, "sku": "SZ-PUMA-RSX-09-ORG", "size": 9, "color": "Orange", "price": "11499", "stock_quantity": 10},
        {"product_id": 5, "sku": "SZ-PUMA-RSX-10-ORG", "size": 10, "color": "Orange", "price": "11499", "stock_quantity": 6},
        {"product_id": 6, "sku": "SZ-VANS-OS-07-BLK", "size": 7, "color": "Black", "price": "7499", "stock_quantity": 15},
        {"product_id": 6, "sku": "SZ-VANS-OS-08-BLK", "size": 8, "color": "Black", "price": "7499", "stock_quantity": 14},
        {"product_id": 6, "sku": "SZ-VANS-OS-09-BLK", "size": 9, "color": "Black", "price": "7499", "stock_quantity": 10},
    ],
}

LOCAL_COLUMNS = {
    "brands": "id, slug, name, is_active",
    "categories": "id, slug, name, is_active",
    "products": "id, category_id, brand_id, name, slug, description, image_url, base_price, is_active",
    "product_variants": "id, product_id, sku, size, color, price, stock_quantity, is_active",
}


class PreparationError(RuntimeError):
    """Raised when a source cannot be safely compared."""


def _decimal_text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return format(Decimal(str(value)).quantize(Decimal("0.01")), "f")
    except (InvalidOperation, ValueError):
        return str(value)


def _size_key(value: Any) -> str:
    """Compare numeric shoe sizes consistently when snapshots use ints."""
    try:
        return format(Decimal(str(value)).normalize(), "f")
    except (InvalidOperation, ValueError):
        return str(value).strip().casefold()


def read_local_catalog(path: Path = LOCAL_DATABASE) -> dict[str, Any]:
    resolved = path.resolve()
    if resolved != LOCAL_DATABASE.resolve():
        raise PreparationError("Only local_test_data/stepzone_catalog_test.sqlite3 may be read.")
    if not resolved.is_file():
        raise PreparationError("The dedicated local SQLite catalog is missing.")

    connection = sqlite3.connect(f"{resolved.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        missing = sorted(set(LOCAL_COLUMNS) - tables)
        if missing:
            raise PreparationError("Local catalog is missing tables: " + ", ".join(missing))
        result = {
            table: [dict(row) for row in connection.execute(f"SELECT {columns} FROM {table}")]
            for table, columns in LOCAL_COLUMNS.items()
        }
        # Limit referential checks to catalog rows; customer/order/cart/wishlist
        # and payment tables are not read by this tool.
        result["foreign_key_violations"] = [
            tuple(row)
            for table in ("products", "product_variants")
            for row in connection.execute(f"PRAGMA foreign_key_check({table})")
        ]
        return result
    finally:
        connection.close()


def load_snapshot(path: Path | None) -> dict[str, Any]:
    if path is None:
        return USER_PRODUCTION_SNAPSHOT
    resolved = path.resolve()
    if resolved.name.lower().startswith(".env") or resolved.suffix.lower() != ".json":
        raise PreparationError("Snapshot input must be a sanitized JSON file, never an environment file.")
    try:
        snapshot = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PreparationError("Could not read the offline catalog snapshot JSON.") from error
    if not isinstance(snapshot, dict):
        raise PreparationError("Snapshot must be a JSON object.")

    for collection in ("brands", "products", "categories", "variants"):
        value = snapshot.get(collection)
        if value is not None and (
            not isinstance(value, list) or any(not isinstance(row, dict) for row in value)
        ):
            raise PreparationError(f"Snapshot field '{collection}' must be an array or null.")
    if snapshot.get("brands") is None or snapshot.get("products") is None:
        raise PreparationError("Snapshot must include brands and products arrays, even when empty.")

    completeness = {
        "brands_complete": snapshot.get("brands_complete", False),
        "products_complete": snapshot.get("products_complete", False),
        "categories_complete": snapshot.get("categories_complete", False),
        "variants_complete": snapshot.get("variants_complete", False),
    }
    if any(not isinstance(value, bool) for value in completeness.values()):
        raise PreparationError("Snapshot completeness flags must be JSON booleans.")
    snapshot.update(completeness)
    snapshot.setdefault("reported_counts", {})

    for row in snapshot["brands"]:
        if not isinstance(row.get("id"), int) or not isinstance(row.get("slug"), str):
            raise PreparationError("Each production brand needs an integer id and string slug.")
    for row in snapshot["products"]:
        if not isinstance(row.get("slug"), str) or not isinstance(row.get("brand_id"), int):
            raise PreparationError("Each production product needs a string slug and integer brand_id.")
        if snapshot["products_complete"] and (
            not isinstance(row.get("id"), int)
            or not isinstance(row.get("category_id"), int)
            or "name" not in row
            or "base_price" not in row
        ):
            raise PreparationError("A complete production product row needs id, category_id, name, and base_price.")
    for row in snapshot.get("categories") or []:
        if not isinstance(row.get("id"), int) or not isinstance(row.get("slug"), str):
            raise PreparationError("Each production category needs an integer id and string slug.")
    for row in snapshot.get("variants") or []:
        if not isinstance(row.get("sku"), str):
            raise PreparationError("Each supplied production variant needs a string SKU.")
        if not (isinstance(row.get("product_id"), int) or isinstance(row.get("product_slug"), str)):
            raise PreparationError("Each supplied production variant needs product_id or product_slug.")
        if snapshot["variants_complete"]:
            required = {"size", "color", "price", "stock_quantity"}
            if required - row.keys() or not isinstance(row.get("product_id"), int):
                raise PreparationError("A complete variant snapshot must include size, color, price, and stock_quantity for every SKU.")
    if snapshot["categories_complete"] and snapshot.get("categories") is None:
        raise PreparationError("categories_complete cannot be true when categories are unavailable.")
    if snapshot["variants_complete"] and snapshot.get("variants") is None:
        raise PreparationError("variants_complete cannot be true when variants are unavailable.")
    return snapshot


def _index(rows: list[dict[str, Any]], key: str) -> tuple[dict[Any, dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row.get(key), []).append(row)
    duplicates = [
        {"value": value, "count": len(items)}
        for value, items in sorted(groups.items(), key=lambda pair: str(pair[0]))
        if value is not None and len(items) > 1
    ]
    return {value: items[0] for value, items in groups.items() if value is not None}, duplicates


def _catalog_integrity(local: dict[str, Any]) -> list[str]:
    brands_by_id = {row["id"]: row for row in local["brands"]}
    categories_by_id = {row["id"]: row for row in local["categories"]}
    products_by_id = {row["id"]: row for row in local["products"]}
    issues = [f"SQLite catalog FK violation: {item}" for item in local["foreign_key_violations"]]
    for label, rows, key in (
        ("brand slug", local["brands"], "slug"),
        ("category slug", local["categories"], "slug"),
        ("product slug", local["products"], "slug"),
        ("variant SKU", local["product_variants"], "sku"),
    ):
        _, duplicates = _index(rows, key)
        issues.extend(f"Duplicate local {label} '{item['value']}' ({item['count']} rows)." for item in duplicates)
    for product in local["products"]:
        if product["brand_id"] not in brands_by_id:
            issues.append(f"Local product '{product['slug']}' has no brand row.")
        if product["category_id"] not in categories_by_id:
            issues.append(f"Local product '{product['slug']}' has no category row.")
    for variant in local["product_variants"]:
        if variant["product_id"] not in products_by_id:
            issues.append(f"Local SKU '{variant['sku']}' has no product row.")
    return issues


def build_comparison(local: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    local_brands_by_id = {row["id"]: row for row in local["brands"]}
    local_categories_by_id = {row["id"]: row for row in local["categories"]}
    local_products = local["products"]
    local_variants = local["product_variants"]
    local_products_by_slug, duplicate_local_slugs = _index(local_products, "slug")
    _, duplicate_local_skus = _index(local_variants, "sku")
    local_variants_by_product: dict[int, list[dict[str, Any]]] = {}
    for variant in local_variants:
        local_variants_by_product.setdefault(variant["product_id"], []).append(variant)

    production_brands = snapshot.get("brands") or []
    production_categories = snapshot.get("categories") or []
    production_products = snapshot.get("products") or []
    production_variants = snapshot.get("variants") or []
    brands_by_slug, duplicate_production_brand_slugs = _index(production_brands, "slug")
    brands_by_id = {row["id"]: row for row in production_brands}
    categories_by_slug, duplicate_production_category_slugs = _index(production_categories, "slug")
    categories_by_id = {row["id"]: row for row in production_categories}
    products_by_slug, duplicate_production_slugs = _index(production_products, "slug")
    products_by_id = {row["id"]: row for row in production_products if row.get("id") is not None}
    production_skus, duplicate_production_skus = _index(production_variants, "sku")
    _, duplicate_production_brand_ids = _index(production_brands, "id")
    _, duplicate_production_category_ids = _index(production_categories, "id")
    _, duplicate_production_product_ids = _index(production_products, "id")

    source_issues = _catalog_integrity(local)
    for brand in local["brands"]:
        if not bool(brand["is_active"]):
            source_issues.append(f"Local brand '{brand['slug']}' is inactive.")
    for category in local["categories"]:
        if not bool(category["is_active"]):
            source_issues.append(f"Local category '{category['slug']}' is inactive.")

    production_fk_issues = [
        f"Production {label} ID {item['value']} is duplicated ({item['count']} rows)."
        for label, duplicates in (
            ("brand", duplicate_production_brand_ids),
            ("category", duplicate_production_category_ids),
            ("product", duplicate_production_product_ids),
        )
        for item in duplicates
    ]
    production_fk_issues.extend(
        f"Production {label} slug '{item['value']}' is duplicated ({item['count']} rows)."
        for label, duplicates in (("brand", duplicate_production_brand_slugs), ("category", duplicate_production_category_slugs))
        for item in duplicates
    )
    for product in production_products:
        if product.get("brand_id") not in brands_by_id:
            production_fk_issues.append(f"Production product '{product.get('slug')}' has an unresolved brand_id.")
        if product.get("category_id") not in categories_by_id:
            production_fk_issues.append(f"Production product '{product.get('slug')}' has an unresolved category_id.")
    production_variant_product_slug: dict[str, str | None] = {}
    for variant in production_variants:
        product_slug = variant.get("product_slug")
        if product_slug is None:
            parent = products_by_id.get(variant.get("product_id"))
            product_slug = parent.get("slug") if parent else None
        production_variant_product_slug[variant["sku"]] = product_slug
        if product_slug is None:
            production_fk_issues.append(f"Production SKU '{variant['sku']}' has an unresolved product relationship.")

    brand_issues = []
    for brand in local["brands"]:
        production_brand = brands_by_slug.get(brand["slug"])
        if production_brand is None:
            brand_issues.append({"slug": brand["slug"], "reason": "missing from production snapshot"})
        elif production_brand.get("is_active") is False:
            brand_issues.append({"slug": brand["slug"], "reason": "inactive in production snapshot"})

    category_issues = []
    if snapshot["categories_complete"]:
        for category in local["categories"]:
            production_category = categories_by_slug.get(category["slug"])
            if production_category is None:
                category_issues.append({"slug": category["slug"], "reason": "missing from production snapshot"})
            elif production_category.get("is_active") is False:
                category_issues.append({"slug": category["slug"], "reason": "inactive in production snapshot"})
    else:
        category_issues.append({"slugs": sorted(row["slug"] for row in local["categories"]), "reason": "production category rows/IDs were not supplied"})

    product_conflicts: list[dict[str, Any]] = [
        {"slug": item["value"], "reason": "duplicate local product slug", "count": item["count"]}
        for item in duplicate_local_slugs
    ]
    product_conflicts.extend(
        {"slug": item["value"], "reason": "duplicate production product slug", "count": item["count"]}
        for item in duplicate_production_slugs
    )
    product_differences: list[dict[str, Any]] = []
    matched_products: list[dict[str, Any]] = []
    product_candidates: list[dict[str, Any]] = []
    conflicts_by_slug = {item["slug"] for item in product_conflicts}

    for local_product in sorted(local_products, key=lambda row: row["slug"]):
        slug = local_product["slug"]
        local_brand = local_brands_by_id.get(local_product["brand_id"])
        local_category = local_categories_by_id.get(local_product["category_id"])
        existing = products_by_slug.get(slug)
        if existing is None:
            if snapshot["products_complete"]:
                brand = brands_by_slug.get(local_brand["slug"]) if local_brand else None
                category = categories_by_slug.get(local_category["slug"]) if local_category else None
                ready = bool(
                    brand
                    and brand.get("is_active") is not False
                    and category
                    and category.get("is_active") is not False
                    and slug not in conflicts_by_slug
                    and not source_issues
                    and not production_fk_issues
                )
                product_candidates.append({
                    "slug": slug,
                    "name": local_product["name"],
                    "brand_slug": local_brand["slug"] if local_brand else None,
                    "brand_id": brand.get("id") if brand else None,
                    "category_slug": local_category["slug"] if local_category else None,
                    "category_id": category.get("id") if category else None,
                    "description": local_product["description"],
                    "image_url": local_product["image_url"],
                    "image_present": bool((local_product.get("image_url") or "").strip()),
                    "base_price": _decimal_text(local_product["base_price"]),
                    "is_active": bool(local_product["is_active"]),
                    "insert_ready": ready,
                })
            continue

        production_brand = brands_by_id.get(existing.get("brand_id"))
        production_category = categories_by_id.get(existing.get("category_id"))
        comparisons: dict[str, dict[str, Any]] = {}
        if local_brand:
            prod_brand_slug = production_brand.get("slug") if production_brand else None
            comparisons["brand_slug"] = {"local": local_brand["slug"], "production": prod_brand_slug, "match": local_brand["slug"] == prod_brand_slug}
            if local_brand["slug"] != prod_brand_slug:
                conflict = {"slug": slug, "reason": "existing product brand assignment differs", "local_brand_slug": local_brand["slug"], "production_brand_slug": prod_brand_slug}
                product_conflicts.append(conflict)
                conflicts_by_slug.add(slug)
        for field in ("name", "description", "image_url", "is_active"):
            if field in existing:
                local_value = bool(local_product[field]) if field == "is_active" else local_product[field]
                prod_value = bool(existing[field]) if field == "is_active" else existing[field]
                match = local_value == prod_value
                comparisons[field] = {"local": local_value, "production": prod_value, "match": match}
                if not match:
                    product_differences.append({"slug": slug, "field": field, "local": local_value, "production": prod_value})
        if "base_price" in existing:
            local_value = _decimal_text(local_product["base_price"])
            prod_value = _decimal_text(existing["base_price"])
            match = local_value == prod_value
            comparisons["base_price"] = {"local": local_value, "production": prod_value, "match": match}
            if not match:
                product_differences.append({"slug": slug, "field": "base_price", "local": local_value, "production": prod_value})
        if local_category and (existing.get("category_id") is not None or snapshot["categories_complete"]):
            prod_category_slug = production_category.get("slug") if production_category else None
            comparisons["category_slug"] = {"local": local_category["slug"], "production": prod_category_slug, "match": local_category["slug"] == prod_category_slug}
            if local_category["slug"] != prod_category_slug:
                product_conflicts.append({"slug": slug, "reason": "existing product category assignment differs", "local_category_slug": local_category["slug"], "production_category_slug": prod_category_slug})
                conflicts_by_slug.add(slug)
        matched_products.append({
            "slug": slug,
            "production_id": existing.get("id"),
            "brand_id": existing.get("brand_id"),
            "brand_slug": production_brand.get("slug") if production_brand else None,
            "comparisons": comparisons,
            "production_fields_not_supplied": [field for field in ("description", "image_url") if field not in existing],
        })

    local_variants_by_sku, duplicate_local_skus = _index(local_variants, "sku")
    duplicate_sku_conflicts: list[dict[str, Any]] = [
        {"sku": item["value"], "reason": "duplicate local SKU", "count": item["count"]}
        for item in duplicate_local_skus
    ]
    duplicate_sku_conflicts.extend(
        {"sku": item["value"], "reason": "duplicate production SKU", "count": item["count"]}
        for item in duplicate_production_skus
    )
    variant_differences: list[dict[str, Any]] = []
    matched_variants: list[dict[str, Any]] = []
    variant_candidates: list[dict[str, Any]] = []

    product_candidate_by_slug = {row["slug"]: row for row in product_candidates}
    if snapshot["variants_complete"]:
        for sku, local_variant in sorted(local_variants_by_sku.items()):
            production_variant = production_skus.get(sku)
            local_product = next((row for row in local_products if row["id"] == local_variant["product_id"]), None)
            local_product_slug = local_product["slug"] if local_product else None
            if production_variant is None:
                production_product = products_by_slug.get(local_product_slug)
                if production_product is None:
                    parent_ready = bool(product_candidate_by_slug.get(local_product_slug, {}).get("insert_ready"))
                else:
                    parent_ready = local_product_slug not in conflicts_by_slug
                variant_candidates.append({
                    "sku": sku,
                    "product_slug": local_product_slug,
                    "size": local_variant["size"],
                    "color": local_variant["color"],
                    "price": _decimal_text(local_variant["price"]),
                    "stock_quantity": local_variant["stock_quantity"],
                    "is_active": bool(local_variant["is_active"]),
                    "insert_ready": bool(
                        parent_ready
                        and local_product_slug is not None
                        and not any(item["value"] == sku for item in duplicate_local_skus)
                        and not any(item["value"] == sku for item in duplicate_production_skus)
                        and not production_fk_issues
                    ),
                })
                continue
            production_product_slug = production_variant_product_slug.get(sku)
            comparisons: dict[str, dict[str, Any]] = {}
            relationship_match = production_product_slug == local_product_slug
            comparisons["product_slug"] = {
                "local": local_product_slug,
                "production": production_product_slug,
                "match": relationship_match,
            }
            if not relationship_match:
                duplicate_sku_conflicts.append({"sku": sku, "reason": "SKU belongs to a different product", "local_product_slug": local_product_slug, "production_product_slug": production_product_slug})
            for field in ("size", "color", "stock_quantity", "is_active"):
                if field in production_variant:
                    local_value = bool(local_variant[field]) if field == "is_active" else local_variant[field]
                    production_value = bool(production_variant[field]) if field == "is_active" else production_variant[field]
                    match = _size_key(local_value) == _size_key(production_value) if field == "size" else local_value == production_value
                    comparisons[field] = {"local": local_value, "production": production_value, "match": match}
                    if not match:
                        variant_differences.append({"sku": sku, "field": field, "local": local_value, "production": production_value})
            if "price" in production_variant:
                local_value = _decimal_text(local_variant["price"])
                production_value = _decimal_text(production_variant["price"])
                match = local_value == production_value
                comparisons["price"] = {"local": local_value, "production": production_value, "match": match}
                if not match:
                    variant_differences.append({"sku": sku, "field": "price", "local": local_value, "production": production_value})
            matched_variants.append({
                "sku": sku,
                "product_slug": local_product_slug,
                "comparisons": comparisons,
                "exact_match": all(item["match"] for item in comparisons.values()),
                "will_remain_untouched": True,
            })

    product_candidate_count = len(product_candidates) if snapshot["products_complete"] else None
    ready_products = [item for item in product_candidates if item["insert_ready"]]
    existing_local_slugs = {row["slug"] for row in local_products}
    unmatched_production_products = sorted(set(products_by_slug) - existing_local_slugs)
    matched_product_slugs = {item["slug"] for item in matched_products}
    variants_on_matched_products = sum(
        len(local_variants_by_product.get(product["id"], []))
        for product in local_products if product["slug"] in matched_product_slugs
    )
    variants_on_candidate_products = sum(
        len(local_variants_by_product.get(product["id"], []))
        for product in local_products if product["slug"] not in products_by_slug
    )

    if snapshot["variants_complete"]:
        ready_variants = [item for item in variant_candidates if item["insert_ready"]]
        variant_proposal_count: int | None = len(ready_variants)
        blocked_variant_count: int | None = len(variant_candidates) - len(ready_variants)
        variant_status = "complete snapshot compared; existing rows are comparison-only"
    else:
        ready_variants = []
        variant_proposal_count = None
        blocked_variant_count = None
        variant_status = "undetermined: complete production SKU/size/color/price/stock rows are unavailable"

    manual_decisions = []
    if not snapshot["categories_complete"]:
        manual_decisions.append("Supply production category IDs/slugs and active states before treating product candidates as insert-ready.")
    if not snapshot["variants_complete"]:
        manual_decisions.append("Supply all 18 existing production variant rows with SKU, product relationship, size, color, price, and stock; do not infer these from the local seed.")
    candidate_products_without_images = [item["slug"] for item in product_candidates if not item["image_present"]]
    if candidate_products_without_images:
        manual_decisions.append(f"{len(candidate_products_without_images)} new-product candidates have no local image URL; review fallback presentation before any future import.")
    if product_conflicts or duplicate_sku_conflicts or product_differences or variant_differences:
        manual_decisions.append("Review every reported existing-record difference or key conflict; existing values must remain untouched.")
    if source_issues or production_fk_issues or brand_issues or category_issues:
        manual_decisions.append("Resolve source/production foreign-key or missing/inactive brand/category issues before any later import review.")
    if duplicate_production_brand_slugs or duplicate_production_category_slugs or duplicate_production_slugs or duplicate_production_skus:
        manual_decisions.append("Resolve duplicate production keys before any later import review.")

    user_old_skool = next((row for row in production_products if row["slug"] == "old-skool-classic"), None)
    old_skool_brand = brands_by_id.get(user_old_skool.get("brand_id")) if user_old_skool else None
    old_skool_check = {
        "reported_brand_id": 6,
        "reported_brand_slug": "vans",
        "snapshot_brand_id": user_old_skool.get("brand_id") if user_old_skool else None,
        "snapshot_brand_slug": old_skool_brand.get("slug") if old_skool_brand else None,
        "brand_match": bool(user_old_skool and user_old_skool.get("brand_id") == 6 and old_skool_brand and old_skool_brand.get("slug") == "vans"),
        "variant_match": None if not snapshot["variants_complete"] else "see per-SKU comparisons",
        "stock_changes_allowed": False,
    }
    if user_old_skool and not old_skool_check["brand_match"]:
        product_conflicts.append({"slug": "old-skool-classic", "reason": "Old Skool Classic does not match the reported Vans brand id 6 relationship"})
        manual_decisions.append("Confirm Old Skool Classic remains linked to Vans brand ID 6.")

    local_image_count = sum(bool((row.get("image_url") or "").strip()) for row in local_products)
    local_summary = {
        "brands": len(local["brands"]),
        "categories": len(local["categories"]),
        "products": len(local_products),
        "variants": len(local_variants),
        "products_with_images": local_image_count,
        "products_without_images": len(local_products) - local_image_count,
        "variants_with_nonpositive_stock": sum(row["stock_quantity"] <= 0 for row in local_variants),
        "duplicate_product_slugs": duplicate_local_slugs,
        "duplicate_skus": duplicate_local_skus,
        "foreign_key_issues": source_issues,
    }

    if not snapshot["products_complete"]:
        product_status = "undetermined: production product snapshot is incomplete"
    elif not snapshot["categories_complete"]:
        product_status = f"{product_candidate_count} product candidates by slug; insert readiness blocked pending production category foreign keys"
    elif source_issues or production_fk_issues or brand_issues or category_issues or product_conflicts:
        product_status = "manual review required"
    else:
        product_status = "candidate products ready for human review"

    status = "manual_review_required" if manual_decisions or product_conflicts or duplicate_sku_conflicts or product_differences or variant_differences else "dry_run_plan_ready_for_review"
    if not snapshot["categories_complete"] or not snapshot["variants_complete"]:
        status = "awaiting_complete_production_snapshot"

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run_only",
        "production_connection_attempted": False,
        "production_writes_performed": False,
        "order_customer_cart_wishlist_payment_records_read_or_changed": False,
        "local_source": "local_test_data/stepzone_catalog_test.sqlite3 (read-only)",
        "production_snapshot_source": snapshot.get("source", "sanitized offline JSON snapshot"),
        "production_snapshot_completeness": {
            "brands": snapshot["brands_complete"],
            "products": snapshot["products_complete"],
            "categories": snapshot["categories_complete"],
            "variants": snapshot["variants_complete"],
            "variant_rows_received": len(production_variants),
            "variants_reported_by_user": snapshot.get("reported_counts", {}).get("variants"),
        },
        "status": status,
        "local_catalog_summary": local_summary,
        "production_snapshot_counts": {
            "brands_rows_received": len(production_brands),
            "products_rows_received": len(production_products),
            "categories_rows_received": len(production_categories) if snapshot["categories_complete"] else None,
            "variants_rows_received": len(production_variants) if snapshot["variants_complete"] else None,
            "reported_counts_from_user_snapshot": snapshot.get("reported_counts", {}),
        },
        "products_found_in_local_catalog": [
            {
                "slug": product["slug"],
                "name": product["name"],
                "brand_slug": local_brands_by_id.get(product["brand_id"], {}).get("slug"),
                "category_slug": local_categories_by_id.get(product["category_id"], {}).get("slug"),
                "image_present": bool((product.get("image_url") or "").strip()),
                "base_price": _decimal_text(product["base_price"]),
                "variant_count": len(local_variants_by_product.get(product["id"], [])),
            }
            for product in sorted(local_products, key=lambda row: row["slug"])
        ],
        "local_category_mappings_to_production": [
            {
                "slug": category["slug"],
                "local_id": category["id"],
                "production_id": categories_by_slug.get(category["slug"], {}).get("id"),
                "active": bool(categories_by_slug.get(category["slug"], {}).get("is_active")),
                "mapped": bool(categories_by_slug.get(category["slug"]) and categories_by_slug[category["slug"]].get("is_active") is not False),
            }
            for category in local["categories"]
        ],
        "local_brand_mappings_to_production": [
            {
                "slug": brand["slug"],
                "local_id": brand["id"],
                "production_id": brands_by_slug.get(brand["slug"], {}).get("id"),
                "active": bool(brands_by_slug.get(brand["slug"], {}).get("is_active")),
                "mapped": bool(brands_by_slug.get(brand["slug"]) and brands_by_slug[brand["slug"]].get("is_active") is not False),
            }
            for brand in local["brands"]
        ],
        "products_already_present_in_production": {
            "count": len(matched_products) if snapshot["products_complete"] else None,
            "items": matched_products,
            "unmatched_production_slugs": unmatched_production_products,
        },
        "products_proposed_for_insertion": {
            "candidate_count_by_slug": product_candidate_count,
            "insert_ready_count": len(ready_products),
            "items": ready_products,
            "blocked_items": [item for item in product_candidates if not item["insert_ready"]],
            "blocked_candidate_count": len(product_candidates) - len(ready_products),
            "candidates_without_images": candidate_products_without_images,
            "status": product_status,
            "candidate_slugs": [item["slug"] for item in product_candidates],
        },
        "existing_product_field_differences": product_differences,
        "conflicting_product_slugs": product_conflicts,
        "variants_on_matched_products_in_local_source": variants_on_matched_products,
        "local_variants_under_new_product_candidates": variants_on_candidate_products,
        "variants_already_present_in_production": {
            "supplied_snapshot_count": len(production_variants) if snapshot["variants_complete"] else None,
            "reported_count_from_user_snapshot": snapshot.get("reported_counts", {}).get("variants"),
            "snapshot_rows_received": len(production_variants) if snapshot["variants_complete"] else None,
            "matched_count": len(matched_variants) if snapshot["variants_complete"] else None,
            "exact_match_count": sum(item["exact_match"] for item in matched_variants) if snapshot["variants_complete"] else None,
            "with_differences_count": sum(not item["exact_match"] for item in matched_variants) if snapshot["variants_complete"] else None,
            "items": matched_variants,
        },
        "variants_proposed_for_insertion": {
            "count": variant_proposal_count,
            "items": ready_variants,
            "blocked_items": [item for item in variant_candidates if not item["insert_ready"]],
            "candidate_count": len(variant_candidates) if snapshot["variants_complete"] else None,
            "blocked_candidate_count": blocked_variant_count,
            "local_candidate_count_under_new_product_slugs": variants_on_candidate_products,
            "status": variant_status,
        },
        "existing_variant_field_differences": variant_differences if snapshot["variants_complete"] else None,
        "duplicate_skus": {
            "local_duplicates": duplicate_local_skus,
            "production_duplicates": duplicate_production_skus if snapshot["variants_complete"] else None,
            "ownership_or_data_conflicts": duplicate_sku_conflicts,
        },
        "duplicate_production_identifiers": {
            "brand_slugs": duplicate_production_brand_slugs,
            "brand_ids": duplicate_production_brand_ids,
            "category_slugs": duplicate_production_category_slugs,
            "category_ids": duplicate_production_category_ids,
            "product_slugs": duplicate_production_slugs,
            "product_ids": duplicate_production_product_ids,
            "variant_skus": duplicate_production_skus,
        },
        "missing_or_inactive_brands": brand_issues,
        "missing_or_inactive_categories": category_issues,
        "foreign_key_check": {"local_catalog_issues": source_issues, "production_snapshot_issues": production_fk_issues},
        "old_skool_classic_safety_check": old_skool_check,
        "existing_records_that_remain_untouched": {
            "policy": "No existing production product, variant, brand, price, description, image, stock, or relationship is changed by this dry-run tool.",
            "production_brand_slugs": sorted(brands_by_slug),
            "production_product_slugs": sorted(products_by_slug),
            "production_variant_skus": sorted(production_skus) if snapshot["variants_complete"] else None,
            "old_skool_classic_existing_variant_count_reported": 3,
            "customer_order_cart_wishlist_payment_records": "never read or modified",
        },
        "manual_decisions_required": sorted(set(manual_decisions)),
        "execution": {"supported": False, "reason": "A separate future writer requires code review and explicit approval."},
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["local_catalog_summary"]
    products = report["products_already_present_in_production"]["items"]
    product_plan = report["products_proposed_for_insertion"]
    variant_plan = report["variants_proposed_for_insertion"]
    variant_matches = report["variants_already_present_in_production"]["items"]
    lines = [
        "# STEPZONE production catalog comparison (dry run)",
        "",
        f"Generated: `{report['generated_at_utc']}`",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Production snapshot source:** {report['production_snapshot_source']}",
        "",
        "## Safety",
        "",
        "- Local SQLite was opened read-only.",
        "- The production data is the user-provided sanitized snapshot; no live database was queried.",
        "- No environment variables, migration, seed, or production write was used.",
        "- Existing production rows, stock, images, descriptions, prices, and relationships remain untouched.",
        "- Production execution is unsupported by this tool.",
        "",
        "## Local catalog",
        "",
        f"- Brands: {summary['brands']}",
        f"- Products: {summary['products']}",
        f"- Variants: {summary['variants']}",
        f"- Products with images: {summary['products_with_images']}",
        f"- Products without images: {summary['products_without_images']}",
        f"- Local duplicate product slugs: {len(summary['duplicate_product_slugs'])}",
        f"- Local duplicate SKUs: {len(summary['duplicate_skus'])}",
        f"- Local foreign-key issues: {len(summary['foreign_key_issues'])}",
        "",
        "## Brand and category mappings",
        "",
        f"- Local brands mapped to active production brands: {sum(item['mapped'] for item in report['local_brand_mappings_to_production'])}/{len(report['local_brand_mappings_to_production'])}.",
        f"- Local categories mapped to active production categories: {sum(item['mapped'] for item in report['local_category_mappings_to_production'])}/{len(report['local_category_mappings_to_production'])}.",
        "- Product candidates are insert-ready only when their active brand and category mappings and relationships validate.",
        "",
        "## Existing products compared",
        "",
        "| Slug | Result | Production brand | Compared fields |",
        "| --- | --- | --- | --- |",
    ]
    for product in products:
        comparisons = product["comparisons"]
        result = "match" if all(item["match"] for item in comparisons.values()) else "difference"
        fields = ", ".join(f"{name}={'match' if data['match'] else 'DIFFERENT'}" for name, data in comparisons.items())
        lines.append(f"| `{product['slug']}` | {result} | `{product.get('brand_slug')}` (ID {product.get('brand_id')}) | {fields or 'none'} |")
    lines.extend([
        "",
        f"- Supplied production products matched by slug: **{len(products)}**.",
        f"- Product field differences: **{len(report['existing_product_field_differences'])}**.",
        "- Product names, brand/category assignments, and base prices are compared. Description/image values were not supplied.",
        "",
        "## New products",
        "",
        f"- Local slugs absent from the production snapshot: **{product_plan['candidate_count_by_slug']}**.",
        f"- Validated product proposals: **{product_plan['insert_ready_count']}**.",
        f"- Blocked product candidates: **{product_plan['blocked_candidate_count']}**.",
        f"- Candidates without local image URLs: **{len(product_plan['candidates_without_images'])}**; none were invented.",
        "",
        "## Variants",
        "",
        f"- Production variants matched by SKU: **{len(variant_matches)}**.",
        f"- Existing variant field or relationship differences: **{len(report['existing_variant_field_differences'])}**.",
        f"- Local variant candidates absent from the production SKU snapshot: **{variant_plan['candidate_count']}**.",
        f"- Validated variant proposals: **{variant_plan['count']}**.",
        f"- Blocked variant candidates: **{variant_plan['blocked_candidate_count']}**.",
        "- Stock differences require manual review; no existing stock value is proposed for replacement.",
        "",
        "## Conflicts and manual review",
        "",
    ])
    conflicts = report["conflicting_product_slugs"] + report["duplicate_skus"]["ownership_or_data_conflicts"]
    differences = report["existing_product_field_differences"] + (report["existing_variant_field_differences"] or [])
    fk_issues = report["foreign_key_check"]["production_snapshot_issues"]
    lines.append(f"- Identifier, mapping, or foreign-key conflicts: **{len(conflicts) + len(fk_issues)}**.")
    lines.append(f"- Existing product/variant field differences: **{len(differences)}**.")
    if not conflicts and not differences and not fk_issues:
        lines.append("No duplicate identifiers, unresolved relationships, or supplied-field differences were detected.")
    else:
        lines.append("Review the detailed JSON conflict and difference entries. Existing records remain unchanged.")
    for decision in report["manual_decisions_required"]:
        lines.append(f"- {decision}")
    lines.extend([
        "",
        "## Old Skool Classic",
        "",
        f"- Production relationship matches Vans brand ID 6: **{report['old_skool_classic_safety_check']['brand_match']}**.",
        f"- Existing variants matched by SKU: **{sum(item['product_slug'] == 'old-skool-classic' for item in variant_matches)}**.",
        "- Existing product data and stock remain untouched.",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only STEPZONE catalog comparison; dry-run only.")
    parser.add_argument("--production-snapshot", type=Path, help="Optional sanitized offline JSON snapshot.")
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument("--execute-production", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.execute_production:
        print("Production execution is disabled. Use a separately reviewed and explicitly approved future writer.", file=sys.stderr)
        return 2
    try:
        local = read_local_catalog()
        snapshot = load_snapshot(args.production_snapshot)
        report = build_comparison(local, snapshot)
        paths = [args.json_report.resolve(), args.markdown_report.resolve()]
        if any(path.parent != REPORTS_DIR.resolve() for path in paths):
            raise PreparationError("Reports must be written directly under the project reports/ folder.")
        if paths[0] == paths[1] or any(path.name.lower().startswith(".env") for path in paths):
            raise PreparationError("Report paths must be distinct and cannot target environment files.")
        paths[0].parent.mkdir(parents=True, exist_ok=True)
        paths[0].write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths[1].write_text(render_markdown(report), encoding="utf-8")
    except PreparationError as error:
        print(f"Comparison stopped safely: {error}", file=sys.stderr)
        return 1
    print(f"JSON report: {paths[0]}")
    print(f"Markdown report: {paths[1]}")
    print(f"Local catalog: {report['local_catalog_summary']['products']} products, {report['local_catalog_summary']['variants']} variants")
    print(f"Production product matches: {report['products_already_present_in_production']['count']}")
    print(f"New-product candidates: {report['products_proposed_for_insertion']['candidate_count_by_slug']}")
    print(f"Exact variant insert count: {report['variants_proposed_for_insertion']['count']}")
    print("Production connection: none; production writes: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
