"""Offline SQLite tests for the guarded production catalogue writer."""

from decimal import Decimal
import os
import unittest

os.environ["PYTHON_DOTENV_DISABLED"] = "1"

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Product, ProductVariant
from scripts.import_catalog_production import (
    EXECUTION_CONFIRMATION,
    ImportSafetyError,
    _insert_records,
    approved_candidate_records,
    import_catalog,
    validate_approval,
)


TEST_CONFIG = type("CatalogImportTestConfig", (), {
    "SECRET_KEY": "test-only",
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
})


def variants(prefix="SZ-TEST"):
    return [
        {"sku": f"{prefix}-{size}", "size": str(size), "color": "Black", "price": Decimal("1000.00"), "stock_quantity": 5}
        for size in range(6, 12)
    ]


def record(slug="test-runner", category_slug="mens-sneakers", items=None):
    return {
        "slug": slug, "name": "Test Runner", "brand_slug": "nike", "category_slug": category_slug,
        "description": "Approved test description", "image_url": None,
        "base_price": Decimal("1000.00"), "variants": variants() if items is None else items,
        "approval_validated": True,
    }


def approval():
    return {
        "product_approved": True,
        "description_approved": True,
        "image_decision_approved": True,
        "edition_colorway_reviewed": True,
        "description": "Approved test description",
        "image_url": None,
        "image_fallback_approved": True,
    }


def plan_and_local(slug="test-runner", category_slug="mens-sneakers", category_id=1):
    local_variants = [
        {"id": i, "product_id": 1, **item} for i, item in enumerate(variants(), start=1)
    ]
    local = {
        "brands": [{"id": 1, "slug": "nike", "is_active": True}],
        "categories": [
            {"id": category_id, "slug": category_slug, "is_active": True}
        ],
        "products": [{"id": 1, "slug": slug, "name": "Test Runner", "brand_id": 1, "category_id": category_id, "base_price": "1000.00"}],
        "product_variants": local_variants,
    }
    candidate = {"slug": slug, "name": "Test Runner", "brand_slug": "nike", "category_slug": category_slug, "category_id": category_id, "base_price": "1000.00"}
    planned_variants = [
        {"sku": row["sku"], "product_slug": slug, "size": row["size"], "color": row["color"], "price": row["price"], "local_stock_quantity": row["stock_quantity"]}
        for row in local_variants
    ]
    plan = {"candidates": {"products": [candidate], "variants": planned_variants}}
    return plan, local, {slug: approval()}


class ProductionCatalogImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from config import config_by_name
        config_by_name["catalog_import_test"] = TEST_CONFIG
        cls.app = create_app("catalog_import_test")
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        with self.app.app_context():
            db.session.query(ProductVariant).delete()
            db.session.query(Product).delete()
            db.session.query(Brand).delete()
            db.session.query(Category).delete()
            db.session.commit()
            db.session.add_all([
                Brand(name="Nike", slug="nike", is_active=True),
                Category(name="Men's Sneakers", slug="mens-sneakers", is_active=True),
                Category(name="Unisex Sneakers", slug="unisex-sneakers", is_active=True),
            ])
            db.session.commit()

    def test_approval_requires_each_review_and_rejects_held_reebok(self):
        with self.assertRaises(ImportSafetyError):
            validate_approval("air-force-1-07", {"product_approved": True})
        with self.assertRaises(ImportSafetyError):
            validate_approval("zig-kinetica-25", {"product_approved": True})

    def test_asics_candidate_must_use_approved_unisex_category(self):
        local = {
            "brands": [{"id": 7, "slug": "asics", "is_active": True}],
            "categories": [{"id": 3, "slug": "unisex-sneakers", "is_active": True}],
            "products": [{"id": 68, "slug": "gel-quantum-360-viii", "name": "GEL-Quantum 360 VIII", "brand_id": 7, "category_id": 3, "base_price": "15999"}],
            "product_variants": [{"id": i, "product_id": 68, "sku": f"SZ-ASICS-{i}", "size": str(i), "color": "Black/Silver", "price": "15999", "stock_quantity": 5} for i in range(6)],
        }
        planned_variants = [{"sku": row["sku"], "product_slug": "gel-quantum-360-viii", "size": row["size"], "color": row["color"], "price": row["price"], "local_stock_quantity": row["stock_quantity"]} for row in local["product_variants"]]
        plan = {"candidates": {"products": [{"slug": "gel-quantum-360-viii", "name": "GEL-Quantum 360 VIII", "brand_slug": "asics", "category_slug": "unisex-sneakers", "category_id": 3, "base_price": "15999"}], "variants": planned_variants}}
        approval = {"product_approved": True, "description_approved": True, "image_decision_approved": True, "edition_colorway_reviewed": True, "description": "Approved description", "image_url": None, "image_fallback_approved": True}
        self.assertEqual(approved_candidate_records(plan, local, {"gel-quantum-360-viii": approval})[0]["category_slug"], "unisex-sneakers")

    def test_dry_run_performs_no_database_writes(self):
        plan, local, approvals = plan_and_local()
        with self.app.app_context():
            result = import_catalog(None, plan, local, approvals, dry_run=True)
            self.assertEqual(result["writes"], 0)
            self.assertEqual(Product.query.count(), 0)

    def test_explicit_execution_confirmation_is_required(self):
        plan, local, approvals = plan_and_local()
        with self.app.app_context():
            with self.assertRaises(ImportSafetyError):
                import_catalog(db.session, plan, local, approvals, dry_run=False, confirmation="")
            self.assertNotEqual(EXECUTION_CONFIRMATION, "")

    def test_sqlite_is_refused_for_execution(self):
        plan, local, approvals = plan_and_local()
        with self.app.app_context():
            with self.assertRaises(ImportSafetyError):
                import_catalog(db.session, plan, local, approvals, dry_run=False, confirmation=EXECUTION_CONFIRMATION)
            self.assertEqual(Product.query.count(), 0)

    def test_import_api_rejects_local_variants_changed_after_plan(self):
        plan, local, approvals = plan_and_local()
        local["product_variants"][0]["sku"] = "UNREVIEWED-SKU"
        with self.assertRaises(ImportSafetyError):
            import_catalog(None, plan, local, approvals, dry_run=True)

    def test_duplicate_sku_rolls_back_every_insert(self):
        bad = record(items=variants() + [variants()[0]])
        with self.app.app_context():
            with self.assertRaises(ImportSafetyError):
                with db.session.begin():
                    _insert_records(db.session, [bad], {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant})
            db.session.rollback()
            self.assertEqual(Product.query.count(), 0)
            self.assertEqual(ProductVariant.query.count(), 0)

    def test_duplicate_product_slug_rolls_back_every_insert(self):
        models = {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant}
        with self.app.app_context():
            with self.assertRaises(ImportSafetyError):
                with db.session.begin():
                    _insert_records(db.session, [record(), record()], models)
            db.session.rollback()
            self.assertEqual(Product.query.count(), 0)

    def test_missing_foreign_key_rolls_back_every_insert(self):
        bad = record("test-one")
        bad2 = record("test-two", category_slug="missing-category")
        with self.app.app_context():
            with self.assertRaises(ImportSafetyError):
                with db.session.begin():
                    _insert_records(db.session, [bad, bad2], {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant})
            db.session.rollback()
            self.assertEqual(Product.query.count(), 0)
            self.assertEqual(ProductVariant.query.count(), 0)

    def test_repeated_import_is_idempotent_and_preserves_existing_values(self):
        models = {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant}
        with self.app.app_context():
            with db.session.begin():
                first = _insert_records(db.session, [record()], models)
            self.assertEqual((first["products_inserted"], first["variants_inserted"]), (1, 6))
            product = Product.query.filter_by(slug="test-runner").one()
            product.description = "Keep this existing description"
            product.image_url = "/keep-existing.png"
            product.base_price = Decimal("1200.00")
            db.session.commit()
            before = (product.description, product.image_url, product.base_price)
            db.session.rollback()
            with self.assertRaises(ImportSafetyError):
                with db.session.begin():
                    _insert_records(db.session, [record()], models)
            db.session.rollback()
            product = Product.query.filter_by(slug="test-runner").one()
            self.assertEqual((product.description, product.image_url, product.base_price), before)
            self.assertEqual(ProductVariant.query.count(), 6)

    def test_second_identical_import_does_not_create_duplicates(self):
        models = {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant}
        with self.app.app_context():
            with db.session.begin():
                _insert_records(db.session, [record()], models)
            with db.session.begin():
                second = _insert_records(db.session, [record()], models)
            self.assertEqual((second["products_inserted"], second["variants_inserted"]), (0, 0))
            self.assertEqual(Product.query.count(), 1)
            self.assertEqual(ProductVariant.query.count(), 6)

    def test_existing_variant_stock_conflict_is_preserved_and_aborts(self):
        models = {"Brand": Brand, "Category": Category, "Product": Product, "ProductVariant": ProductVariant}
        with self.app.app_context():
            with db.session.begin():
                _insert_records(db.session, [record()], models)
            variant = ProductVariant.query.filter_by(sku="SZ-TEST-6").one()
            variant.stock_quantity = 17
            db.session.commit()
            with self.assertRaises(ImportSafetyError):
                with db.session.begin():
                    _insert_records(db.session, [record()], models)
            db.session.rollback()
            variant = ProductVariant.query.filter_by(sku="SZ-TEST-6").one()
            self.assertEqual(variant.stock_quantity, 17)

    def test_reviewed_plan_flags_puma_stock_without_authorizing_change(self):
        from scripts.import_catalog_production import load_plan
        plan = load_plan()
        discrepancy = plan["discrepancies"][0]
        self.assertEqual(discrepancy["sku"], "SZ-PUMA-RSX-08-ORG")
        self.assertEqual(discrepancy["action"], "MANUAL_REVIEW_PRESERVE_PRODUCTION_VALUE_NO_OVERWRITE")


if __name__ == "__main__":
    unittest.main()
