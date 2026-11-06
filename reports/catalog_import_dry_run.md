# STEPZONE production catalog comparison (dry run)

Generated: `2026-11-05T12:04:33.654409+00:00`

**Status:** `manual_review_required`

**Production snapshot source:** User-provided verified sanitized production snapshot; offline only

## Safety

- Local SQLite was opened read-only.
- The production data is the user-provided sanitized snapshot; no live database was queried.
- No environment variables, migration, seed, or production write was used.
- Existing production rows, stock, images, descriptions, prices, and relationships remain untouched.
- Production execution is unsupported by this tool.

## Local catalog

- Brands: 7
- Products: 70
- Variants: 402
- Products with images: 6
- Products without images: 64
- Local duplicate product slugs: 0
- Local duplicate SKUs: 0
- Local foreign-key issues: 0

## Brand and category mappings

- Local brands mapped to active production brands: 7/7.
- Local categories mapped to active production categories: 4/4.
- Product candidates are insert-ready only when their active brand and category mappings and relationships validate.

## Existing products compared

| Slug | Result | Production brand | Compared fields |
| --- | --- | --- | --- |
| `574-core-trainer` | match | `new-balance` (ID 3) | brand_slug=match, name=match, base_price=match, category_slug=match |
| `air-max-dn8` | match | `nike` (ID 1) | brand_slug=match, name=match, base_price=match, category_slug=match |
| `club-c-revenge` | match | `reebok` (ID 5) | brand_slug=match, name=match, base_price=match, category_slug=match |
| `forum-low-classic` | match | `adidas` (ID 2) | brand_slug=match, name=match, base_price=match, category_slug=match |
| `old-skool-classic` | match | `vans` (ID 6) | brand_slug=match, name=match, base_price=match, category_slug=match |
| `rs-x-heritage` | match | `puma` (ID 4) | brand_slug=match, name=match, base_price=match, category_slug=match |

- Supplied production products matched by slug: **6**.
- Product field differences: **0**.
- Product names, brand/category assignments, and base prices are compared. Description/image values were not supplied.

## New products

- Local slugs absent from the production snapshot: **64**.
- Validated product proposals: **64**.
- Blocked product candidates: **0**.
- Candidates without local image URLs: **64**; none were invented.

## Variants

- Production variants matched by SKU: **18**.
- Existing variant field or relationship differences: **1**.
- Local variant candidates absent from the production SKU snapshot: **384**.
- Validated variant proposals: **384**.
- Blocked variant candidates: **0**.
- Stock differences require manual review; no existing stock value is proposed for replacement.

## Conflicts and manual review

- Identifier, mapping, or foreign-key conflicts: **0**.
- Existing product/variant field differences: **1**.
Review the detailed JSON conflict and difference entries. Existing records remain unchanged.
- 64 new-product candidates have no local image URL; review fallback presentation before any future import.
- Review every reported existing-record difference or key conflict; existing values must remain untouched.

## Old Skool Classic

- Production relationship matches Vans brand ID 6: **True**.
- Existing variants matched by SKU: **3**.
- Existing product data and stock remain untouched.


## User-approved local decisions

- GEL-Quantum 360 VIII category correction was applied locally to Unisex Sneakers (ID 3). Production remains unchanged.
- Zig Kinetica 2.5 is on HOLD_MODEL_IDENTITY_UNVERIFIED and excluded from insertion proposals.
- Remaining 63 candidates are not import-ready; image permission, descriptions, exact editions/colorways and other field checks remain unresolved.
