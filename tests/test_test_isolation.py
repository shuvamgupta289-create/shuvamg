import os
import unittest


class TestIsolationTests(unittest.TestCase):
    def test_pytest_forces_in_memory_sqlite_before_application_imports(self):
        self.assertEqual(os.environ.get("DATABASE_URL"), "sqlite:///:memory:")
        self.assertEqual(os.environ.get("APP_ENV"), "testing")


if __name__ == "__main__":
    unittest.main()
