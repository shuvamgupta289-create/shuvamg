"""Synthetic, offline tests for the dry-run catalog comparison logic."""

from copy import deepcopy
import unittest

from scripts.prepare_catalog_import import (
    LOCAL_DATABASE,
    USER_PRODUCTION_SNAPSHOT,
    build_comparison,
    read_local_catalog,
)


def complete_snapshot_from_local(local):
    """Create test-only snapshot rows from local values; never written to disk."""
    return {
        "source": "synthetic test fixture",
        "brands_complete": True,
        "products_complete": True,
        "categories_complete": True,
        "variants_complete": True,
        "reported_counts": {},
        "brands": [
            {"id": row["id"], "slug": row["slug"], "name": row["name"], "is_active": bool(row["is_active"])}
            for row in local["brands"]
        ],
        "categories": [
            {"id": row["id"], "slug": row["slug"], "is_active": bool(row["is_active"])}
            for row in local["categories"]
        ],
        "products": [
            {
                "id": row["id"],
                "slug": row["slug"],
                "brand_id": row["brand_id"],
                "category_id": row["category_id"],
                "name": row["name"],
                "description": row["description"],
                "image_url": row["image_url"],
                "base_price": row["base_price"],
                "is_active": bool(row["is_active"]),
            }
            for row in local["products"]
        ],
        "variants": [
            {
                "id": row["id"],
                "sku": row["sku"],
                "product_id": row["product_id"],
                "size": row["size"],
                "color": row["color"],
                "price": row["price"],
                "stock_quantity": row["stock_quantity"],
                "is_active": bool(row["is_active"]),
            }
            for row in local["product_variants"]
        ],
    }


class CatalogImportComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = read_local_catalog(LOCAL_DATABASE)
        cls.snapshot = complete_snapshot_from_local(cls.local)

    def test_exact_synthetic_snapshot_has_no_insert_proposals(self):
        report = build_comparison(self.local, deepcopy(self.snapshot))
        self.assertEqual(report["products_already_present_in_production"]["count"], 70)
        self.assertEqual(report["products_proposed_for_insertion"]["candidate_count_by_slug"], 0)
        self.assertEqual(report["variants_already_present_in_production"]["matched_count"], 402)
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 0)
        self.assertTrue(report["old_skool_classic_safety_check"]["brand_match"])

    def test_missing_sku_is_proposed_with_source_stock_only(self):
        snapshot = deepcopy(self.snapshot)
        missing = snapshot["variants"].pop()
        report = build_comparison(self.local, snapshot)
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 1)
        proposal = report["variants_proposed_for_insertion"]["items"][0]
        self.assertEqual(proposal["sku"], missing["sku"])
        self.assertEqual(proposal["stock_quantity"], missing["stock_quantity"])

    def test_existing_variant_difference_is_reported_but_not_replenished(self):
        snapshot = deepcopy(self.snapshot)
        snapshot["variants"][0]["stock_quantity"] += 1
        report = build_comparison(self.local, snapshot)
        self.assertTrue(any(item["field"] == "stock_quantity" for item in report["existing_variant_field_differences"]))
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 0)

    def test_existing_product_brand_mismatch_is_conflict_not_update(self):
        snapshot = deepcopy(self.snapshot)
        old_skool = next(row for row in snapshot["products"] if row["slug"] == "old-skool-classic")
        old_skool["brand_id"] = 1
        report = build_comparison(self.local, snapshot)
        self.assertTrue(any(item["slug"] == "old-skool-classic" for item in report["conflicting_product_slugs"]))
        self.assertFalse(report["old_skool_classic_safety_check"]["brand_match"])
        self.assertFalse(any(item["slug"] == "old-skool-classic" for item in report["products_proposed_for_insertion"]["items"]))

    def test_missing_product_slug_proposes_product_and_its_variants(self):
        snapshot = deepcopy(self.snapshot)
        removed = next(row for row in snapshot["products"] if row["slug"] == "old-skool-classic")
        snapshot["products"].remove(removed)
        snapshot["variants"] = [row for row in snapshot["variants"] if row["product_id"] != removed["id"]]
        report = build_comparison(self.local, snapshot)
        self.assertEqual(report["products_proposed_for_insertion"]["insert_ready_count"], 1)
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 3)

    def test_user_snapshot_matches_products_variants_and_reports_real_stock_difference(self):
        report = build_comparison(self.local, deepcopy(USER_PRODUCTION_SNAPSHOT))
        self.assertEqual(report["products_already_present_in_production"]["count"], 6)
        self.assertEqual(report["existing_product_field_differences"], [])
        self.assertEqual(report["variants_already_present_in_production"]["matched_count"], 18)
        self.assertEqual(report["variants_already_present_in_production"]["exact_match_count"], 17)
        self.assertEqual(report["variants_already_present_in_production"]["with_differences_count"], 1)
        self.assertEqual(report["existing_variant_field_differences"], [
            {"sku": "SZ-PUMA-RSX-08-ORG", "field": "stock_quantity", "local": 9, "production": 8}
        ])
        self.assertEqual(report["products_proposed_for_insertion"]["insert_ready_count"], 64)
        self.assertEqual(len(report["products_proposed_for_insertion"]["candidates_without_images"]), 64)
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 384)
        self.assertEqual(sum(x["mapped"] for x in report["local_brand_mappings_to_production"]), 7)
        self.assertEqual(sum(x["mapped"] for x in report["local_category_mappings_to_production"]), 4)
        self.assertTrue(report["old_skool_classic_safety_check"]["brand_match"])

    def test_duplicate_snapshot_identifiers_block_new_candidates(self):
        snapshot = deepcopy(USER_PRODUCTION_SNAPSHOT)
        snapshot["brands"].append(deepcopy(snapshot["brands"][0]))
        snapshot["categories"].append(deepcopy(snapshot["categories"][0]))
        snapshot["products"].append(deepcopy(snapshot["products"][0]))
        snapshot["variants"].append(deepcopy(snapshot["variants"][0]))
        report = build_comparison(self.local, snapshot)
        self.assertTrue(report["duplicate_production_identifiers"]["brand_slugs"])
        self.assertTrue(report["duplicate_production_identifiers"]["brand_ids"])
        self.assertTrue(report["duplicate_production_identifiers"]["category_slugs"])
        self.assertTrue(report["duplicate_production_identifiers"]["category_ids"])
        self.assertTrue(report["duplicate_production_identifiers"]["product_slugs"])
        self.assertTrue(report["duplicate_production_identifiers"]["product_ids"])
        self.assertTrue(report["duplicate_production_identifiers"]["variant_skus"])
        self.assertEqual(report["products_proposed_for_insertion"]["insert_ready_count"], 0)
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 0)

    def test_conflicting_existing_category_blocks_its_missing_variant(self):
        snapshot = deepcopy(USER_PRODUCTION_SNAPSHOT)
        snapshot["products"][0]["category_id"] = 3
        missing = snapshot["variants"].pop(0)
        report = build_comparison(self.local, snapshot)
        self.assertTrue(any(
            item["slug"] == "air-max-dn8" and "category" in item["reason"]
            for item in report["conflicting_product_slugs"]
        ))
        blocked = next(item for item in report["variants_proposed_for_insertion"]["blocked_items"] if item["sku"] == missing["sku"])
        self.assertFalse(blocked["insert_ready"])
        self.assertEqual(report["variants_proposed_for_insertion"]["count"], 384)

    def test_stock_difference_never_proposes_replacement(self):
        report = build_comparison(self.local, deepcopy(USER_PRODUCTION_SNAPSHOT))
        self.assertFalse(any(item["sku"] == "SZ-PUMA-RSX-08-ORG" for item in report["variants_proposed_for_insertion"]["items"]))
        matched = next(item for item in report["variants_already_present_in_production"]["items"] if item["sku"] == "SZ-PUMA-RSX-08-ORG")
        self.assertTrue(matched["will_remain_untouched"])
        stock = next(item for item in matched["comparisons"].values() if item.get("local") == 9)
        self.assertEqual(stock["production"], 8)

    def test_variant_sku_attached_to_wrong_product_is_conflict(self):
        snapshot = deepcopy(USER_PRODUCTION_SNAPSHOT)
        snapshot["variants"][0]["product_id"] = 2
        report = build_comparison(self.local, snapshot)
        self.assertTrue(any(
            item["sku"] == "SZ-NIKE-DN8-08-BLK" and item["reason"] == "SKU belongs to a different product"
            for item in report["duplicate_skus"]["ownership_or_data_conflicts"]
        ))


if __name__ == "__main__":
    unittest.main()
