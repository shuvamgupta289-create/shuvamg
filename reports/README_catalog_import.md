# STEPZONE offline catalog comparison

## Purpose and safety

`../scripts/prepare_catalog_import.py` compares the dedicated local SQLite sneaker catalog against a sanitized production snapshot stored in the script. The supplied production rows are labeled as user-provided verified snapshots; the tool does not independently verify them against a live database.

The script is standard-library-only. It opens only `local_test_data/stepzone_catalog_test.sqlite3` in SQLite read-only mode. It does not import Flask configuration, read `.env` or environment variables, connect to PostgreSQL/Supabase, read customer/order/cart/wishlist/payment data, or perform writes. Production execution is not implemented.

## Current report

Run the offline comparison and regenerate both reports:

```powershell
.\venv\Scripts\python.exe scripts\prepare_catalog_import.py
```

Outputs:

- `reports/catalog_import_dry_run.json` — field-level matches, differences, candidates, conflicts, and relationship checks.
- `reports/catalog_import_dry_run.md` — readable summary of the same comparison.

The checked-in snapshot constants contain 7 brands, 4 categories, 6 existing products, and 18 existing variants from the user's sanitized snapshot. The current local database contains 70 products and 402 variants. The generated report identifies 64 new product slugs and their 384 local variant rows, and only marks them insert-ready when the production brand/category mappings and product relationships validate. “Insert-ready” is a comparison result only; it is not authorization or an execution facility.

For the supplied snapshot, all 6 existing products match the local catalog on slug, name, brand, category, and base price. All 18 production variant SKUs match; 17 match all compared fields. One manual-review difference is reported for `SZ-PUMA-RSX-08-ORG`: local stock is 9 and snapshot stock is 8. No update or stock replacement is proposed. All 7 local brand slugs and all 4 local category slugs map to active snapshot rows, so the 64 new product and 384 variant candidates have validated mappings and parent relationships. Those 64 new product records have no local image URL; the report flags this, and no image is invented.

Existing rows are matched by brand/category slug, product slug, and variant SKU. Product names, brand and category assignments, and product prices are compared. Variant product ownership, size, color, price, and stock are compared. A difference in existing stock is reported for manual review and never creates a replacement or replenishment proposal. Existing descriptions and image URLs are not in the supplied production product snapshot and are not inferred.

## Optional offline snapshot file

The script also accepts a sanitized JSON snapshot for local-only comparison:

```powershell
.\venv\Scripts\python.exe scripts\prepare_catalog_import.py --production-snapshot C:\path\to\sanitized_catalog_snapshot.json
```

The JSON snapshot must contain arrays named `brands`, `categories`, `products`, and `variants`, plus boolean completeness flags. It must not contain credentials, environment data, customer details, or order/payment data.

| Array | Fields needed for a complete comparison |
| --- | --- |
| `brands` | `id`, `slug`, `name`, `is_active` |
| `categories` | `id`, `slug`, `name`, `is_active` |
| `products` | `id`, `slug`, `name`, `brand_id`, `category_id`, `base_price` |
| `variants` | `product_id`, `sku`, `size`, `color`, `price`, `stock_quantity` |

Set `brands_complete`, `categories_complete`, `products_complete`, and `variants_complete` to `true` only if the corresponding arrays are complete. Each existing product and variant is comparison-only: differences never produce updates. Duplicate slugs/SKUs, duplicate IDs, unresolved or inactive mappings, and mismatched variant ownership are surfaced and can block related new-row candidates.

## Import execution is not supported

This workflow only generates reports. It has no production writer, migration, seed operation, or database connection path. Do not interpret its proposals as approval to alter production. Any future import would require a separately reviewed implementation and separate explicit approval.

The existing `scripts/seed_data.py` is not modified or invoked by this workflow.
