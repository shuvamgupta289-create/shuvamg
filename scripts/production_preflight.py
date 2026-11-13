"""Read-only production migration preflight for STEPZONE.

This module never loads dotenv or imports the Flask application.  It only
connects after an operator explicitly supplies both execution switches.
"""

import argparse
import json
import os
from urllib.parse import urlsplit


EXPECTED_HEAD = "f8a1c2d3e4f5"
POSTGRES_SCHEMES = {"postgres", "postgresql", "postgresql+psycopg"}


def _validate_postgres_url(database_url):
    parsed = urlsplit(database_url)
    if parsed.scheme not in POSTGRES_SCHEMES or not parsed.hostname:
        raise ValueError("The supplied environment variable must contain a PostgreSQL URL.")


def inspect_database(database_url):
    """Return migration and negative-stock facts from one read-only transaction."""
    import psycopg

    with psycopg.connect(database_url, autocommit=True) as connection:
        with connection.transaction():
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '10s'")
            revisions = [
                row[0]
                for row in connection.execute(
                    "SELECT version_num FROM alembic_version ORDER BY version_num"
                )
            ]
            negative_count, lowest_stock = connection.execute(
                "SELECT COUNT(*), MIN(stock_quantity) "
                "FROM product_variants WHERE stock_quantity < 0"
            ).fetchone()
            reservation_columns = {
                row[0]
                for row in connection.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = current_schema() AND table_name = 'orders' "
                    "AND column_name IN ('stock_reserved', 'stock_deducted')"
                )
            }
            stock_constraint_present = connection.execute(
                "SELECT EXISTS ("
                "SELECT 1 FROM pg_constraint AS con "
                "JOIN pg_class AS rel ON rel.oid = con.conrelid "
                "JOIN pg_namespace AS ns ON ns.oid = rel.relnamespace "
                "WHERE ns.nspname = current_schema() "
                "AND rel.relname = 'product_variants' "
                "AND con.conname = 'ck_product_variants_stock_nonnegative' "
                "AND con.contype = 'c'"
                ")"
            ).fetchone()[0]
    return {
        "migration_revisions": revisions,
        "expected_head": EXPECTED_HEAD,
        "at_expected_head": revisions == [EXPECTED_HEAD],
        "negative_stock_count": negative_count,
        "lowest_negative_stock": lowest_stock,
        "reservation_columns_present": sorted(reservation_columns),
        "reservation_flags_present": reservation_columns
        == {"stock_reserved", "stock_deducted"},
        "stock_constraint_present": stock_constraint_present,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only STEPZONE production preflight")
    parser.add_argument(
        "--database-url-env",
        default="DATABASE_URL",
        help="Environment-variable name that holds the PostgreSQL URL; its value is never printed.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Allow the read-only checks to connect to the database.",
    )
    parser.add_argument(
        "--confirm-read-only-production",
        action="store_true",
        help="Confirm that this is an authorized production read-only preflight.",
    )
    args = parser.parse_args(argv)

    if not (args.execute and args.confirm_read_only_production):
        print(
            json.dumps(
                {
                    "status": "not_executed",
                    "reason": "Requires --execute and --confirm-read-only-production.",
                    "checks": ["alembic revision", "negative product-variant stock"],
                }
            )
        )
        return 0

    database_url = os.environ.get(args.database_url_env)
    if not database_url:
        print(json.dumps({"status": "blocked", "reason": "Required database URL environment variable is absent."}))
        return 2
    try:
        _validate_postgres_url(database_url)
        result = inspect_database(database_url)
    except Exception:
        print(json.dumps({"status": "blocked", "reason": "Read-only preflight could not complete."}))
        return 2

    result["status"] = "passed" if result["negative_stock_count"] == 0 else "blocked"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
