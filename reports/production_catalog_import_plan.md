# STEPZONE — Production Catalogue Import Preparation

Generated: 2026-11-06T17:43:38.1126953Z

## Decision status

**Preparation only; awaiting explicit approval.** No live database was contacted and no production write was executed. The guarded writer is implemented but was not invoked. This report uses the user's sanitized production snapshot and the existing read-only local audit artifacts.

## Current snapshot counts

- Supplied production snapshot: 7 brands, 4 categories, 6 products, 18 variants.
- Local catalogue audit: 7 brands, 4 categories, 70 products, 402 variants.
- Brand/category mappings in the supplied snapshot: 7/7 and 4/4.
- Existing products: 6 match by slug; product name, brand, category, and price comparisons show no differences.
- Existing variants: 18 matched by SKU; 17 exact and 1 with a reported stock discrepancy.

| Existing product | Slug | Brand | Local price | Local variants | Action |
| --- | --- | --- | ---: | ---: | --- |
| 574 Core Trainer | `574-core-trainer` | `new-balance` | 8999.00 | 3 | Preserve unchanged |
| Air Max Dn8 | `air-max-dn8` | `nike` | 14995.00 | 3 | Preserve unchanged |
| Club C Revenge | `club-c-revenge` | `reebok` | 9799.00 | 3 | Preserve unchanged |
| Forum Low Classic | `forum-low-classic` | `adidas` | 10499.00 | 3 | Preserve unchanged |
| Old Skool Classic | `old-skool-classic` | `vans` | 7499.00 | 3 | Preserve unchanged |
| RS-X Heritage | `rs-x-heritage` | `puma` | 11499.00 | 3 | Preserve unchanged |

All six production products, all 18 production variants, and every existing stock value remain unchanged.

## Proposed scope (not approved for execution)

- 63 missing products are candidates for a future approval review.
- 378 variants belong to those 63 products.
- **Currently approved inserts: 0 products and 0 variants.** Product descriptions remain drafts, 64 additional products lack verified image assets/usage permission, and exact edition/colorway links remain unresolved.
- Reebok Zig Kinetica 2.5 (`zig-kinetica-25`) is held. Its six local variants are excluded with it.
- If all 63 candidate products are later approved and imported, the conditional count would be 69 products and 396 variants. This is not an execution recommendation or approval.

## Category correction

The approved GEL-Quantum 360 VIII correction is reflected as local category `unisex-sneakers` (ID 3). No production category change is proposed or performed.

## Manual review

- **Descriptions:** 63 drafts await wording approval.
- **Images:** 64 additional products have no verified local image and no confirmed image reuse permission. Keep the existing fallback.
- **Model editions and colorways:** exact style code, edition, and manufacturer colorway are not fully linked to local SKUs. Broad local labels such as “Black/Silver” are not proof of manufacturer colorway.
- **Reebok:** maintain hold until exact identity is verified from a reliable official source; exclude product and variants.
- **Puma stock:** `SZ-PUMA-RSX-08-ORG` is local stock 9 versus supplied production snapshot stock 8. Preserve production stock; investigate manually.

## Reconciliation of existing artifacts

The older dry-run JSON/Markdown disagree internally: it reports 63 candidates and zero ready by count, while candidate item flags say `insert_ready=true`; the Markdown also describes 64 products/384 variants. Its GEL-Quantum row still says Men's/category ID 1, while the approved verification manifest says Unisex/category ID 3. This plan resolves those discrepancies for the final approval view and keeps every candidate blocked pending review.

## Safe future execution and rollback

The separate writer now requires a product approval manifest with approved wording, image/fallback decision, and edition/colorway review for every candidate. It re-reads production by brand/category slug, product slug, and SKU; validates foreign keys; inserts only missing rows; and aborts on any collision or mismatch. Dry-run is the default and does not connect to a database. Production execution additionally requires an explicit CLI switch, a typed confirmation phrase, and a Supabase PostgreSQL target. Before commit, any error must roll back the transaction. After commit, recovery should use a reviewed backup/restore or separately approved compensating change; this plan does not authorize deleting records as a rollback shortcut.


## Writer implementation status

- Guarded writer: `scripts/import_catalog_production.py`.
- Dry-run is the default and performs no database connection.
- Every proposed product requires explicit approval of the product, description, image or fallback decision, and edition/colorway review in `reports/catalog_import_approvals.json`.
- Reebok Zig Kinetica 2.5, the six snapshot-matched product slugs, and all 18 snapshot SKUs are protected from insertion.
- Execution requires `--execute-production`, the exact confirmation phrase `STEPZONE PRODUCTION IMPORT CONFIRMED`, and a PostgreSQL Supabase host. A transaction wraps all inserts; any failure rolls back.
- The public import function validates each approval and cross-checks product fields, variant SKUs, sizes, colors, prices, and stock against the reviewed plan and read-only local catalog. Existing values are compared and preserved; any other conflict aborts. The Puma stock difference is reported and production stock is retained.
- Writer status: implemented; not invoked. Database connection and production writes: none.
- Offline preview command: `venv\\Scripts\\python.exe scripts\\import_catalog_production.py` (reports pending approvals; no DB connection).
- The approval JSON must be keyed by candidate slug and include `product_approved`, `description_approved`, approved `description`, `image_decision_approved`, `image_url` or `image_fallback_approved`, and `edition_colorway_reviewed`.
- Exact execution phrase: `STEPZONE PRODUCTION IMPORT CONFIRMED`.
## Safety confirmation

No Supabase connection, environment read, migration, seed execution, production SQL, production write, commit, push, or deployment occurred. Existing production records and customer/order/cart/wishlist/payment data were not accessed or modified. The six matched products and 18 variants are preservation-only.
## Validation

- Python syntax, Jinja parsing, and JavaScript syntax checks passed. The venv Python 3.14.2 differs from the project 3.12 pin; no 3.12 interpreter was installed.
- The writer's default offline dry-run reported 63 candidates, 378 variants, zero approvals, zero writes, and no database connection; it also reported the Puma stock difference.
- Full pytest suite: **76 passed**. SQLAlchemy uses its bundled pure-Python fallback because Windows Application Control blocked the optional Cython DLLs in this virtual environment.
