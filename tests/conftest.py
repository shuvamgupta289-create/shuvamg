"""Global test isolation: never let test imports inherit a real database URL."""

import os

# This runs before pytest imports test modules (and therefore before they import
# config.py or the Flask application). Keep this unconditional so a developer's
# shell, .env file, or CI secret can never direct the test suite at a real DB.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["APP_ENV"] = "testing"
os.environ["FLASK_ENV"] = "testing"
os.environ["PYTHON_DOTENV_DISABLED"] = "true"

