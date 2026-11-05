import os
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_local_preview import LOCAL_DATABASE_PATH, create_local_preview_app


class LocalPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict(
            os.environ,
            {
                "PYTHON_DOTENV_DISABLED": "",
                "DATABASE_URL": "postgresql://preview-isolation.invalid/catalog",
                "APP_ENV": "production",
                "FLASK_ENV": "production",
                "VERCEL": "1",
                "STEPZONE_ALLOW_REMOTE_SEED": "1",
            },
        ):
            cls.app = create_local_preview_app()
        cls.app.config.update(TESTING=True)

    def test_preview_uses_local_catalog_and_all_shopping_routes(self):
        self.assertTrue(LOCAL_DATABASE_PATH.is_file())
        before_mtime = LOCAL_DATABASE_PATH.stat().st_mtime_ns
        with sqlite3.connect(LOCAL_DATABASE_PATH) as connection:
            before_counts = connection.execute(
                "select (select count(*) from brands), (select count(*) from products), "
                "(select count(*) from product_variants), (select count(*) from orders)"
            ).fetchone()
        self.assertEqual(before_counts, (7, 70, 402, 0))

        client = self.app.test_client()
        homepage = client.get("/")
        self.assertEqual(homepage.status_code, 200)
        home_text = homepage.get_data(as_text=True)
        self.assertIn("/static/images/brands/nike.svg", home_text)
        self.assertIn("/brands/asics", home_text)

        for brand_slug in ("adidas", "asics", "new-balance", "nike", "puma", "reebok", "vans"):
            response = client.get(f"/brands/{brand_slug}")
            self.assertEqual(response.status_code, 200, brand_slug)
            self.assertIn("available product", response.get_data(as_text=True), brand_slug)

        search = client.get("/search?q=GEL-Kayano")
        self.assertEqual(search.status_code, 200)
        self.assertIn("GEL-Kayano 31", search.get_data(as_text=True))

        detail = client.get("/product/gel-kayano-31")
        self.assertEqual(detail.status_code, 200)
        self.assertIn("GEL-Kayano 31", detail.get_data(as_text=True))

        filtered = client.get("/brands/nike?size=8&min_price=6000&sort=price_asc")
        self.assertEqual(filtered.status_code, 200)
        self.assertIn("Air Force 1", filtered.get_data(as_text=True))

        page_one = client.get("/brands/nike?page=1").get_data(as_text=True)
        page_two = client.get("/brands/nike?page=2").get_data(as_text=True)
        self.assertEqual(page_one.count('class="product-card brand-product-card"'), 9)
        self.assertEqual(page_two.count('class="product-card brand-product-card"'), 1)

        with sqlite3.connect(LOCAL_DATABASE_PATH) as connection:
            after_counts = connection.execute(
                "select (select count(*) from brands), (select count(*) from products), "
                "(select count(*) from product_variants), (select count(*) from orders)"
            ).fetchone()
        self.assertEqual(after_counts, before_counts)
        self.assertEqual(LOCAL_DATABASE_PATH.stat().st_mtime_ns, before_mtime)


if __name__ == "__main__":
    unittest.main()
