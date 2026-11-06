"""Run STEPZONE against the isolated local catalog SQLite database only."""

import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATABASE_PATH = PROJECT_ROOT / "local_test_data" / "stepzone_catalog_test.sqlite3"


def create_local_preview_app():
    # Do this before importing config or the Flask app. Local preview never
    # reads .env and never accepts a DATABASE_URL or deployment environment.
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    for variable in ("DATABASE_URL", "APP_ENV", "FLASK_ENV", "VERCEL", "STEPZONE_ALLOW_REMOTE_SEED"):
        os.environ.pop(variable, None)

    import dotenv

    def prevent_dotenv_loading(*args, **kwargs):
        return False

    dotenv.load_dotenv = prevent_dotenv_loading

    sys.path.insert(0, str(PROJECT_ROOT))
    from config import config_by_name

    local_database_url = f"sqlite:///{LOCAL_DATABASE_PATH.as_posix()}"
    config_by_name["catalog_preview_local_only"] = type(
        "LocalCatalogPreviewConfig",
        (),
        {
            "SECRET_KEY": "local-stepzone-preview-only",
            "SQLALCHEMY_DATABASE_URI": local_database_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SAMESITE": "Lax",
            "SESSION_COOKIE_SECURE": False,
            "DEBUG": False,
        },
    )

    from app import create_app
    from app.extensions import db

    app = create_app("catalog_preview_local_only")
    with app.app_context():
        engine = db.engine
        if engine.url.get_backend_name() != "sqlite":
            raise RuntimeError("Local preview safety check failed: database engine is not SQLite.")
        actual_path = Path(engine.url.database).resolve()
        if actual_path != LOCAL_DATABASE_PATH.resolve():
            raise RuntimeError("Local preview safety check failed: database file path does not match the dedicated catalog file.")
        if "DATABASE_URL" in os.environ or os.getenv("PYTHON_DOTENV_DISABLED") != "1":
            raise RuntimeError("Local preview safety check failed: remote database environment is not isolated.")
        if not actual_path.is_file():
            raise RuntimeError(f"Local catalog database is missing: {actual_path}")
    return app


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run STEPZONE locally with the dedicated SQLite catalog database.")
    parser.add_argument("--port", type=int, default=5000, help="Local preview port (default: 5000).")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")

    app = create_local_preview_app()
    print(f"STEPZONE local preview: http://127.0.0.1:{args.port}")
    print(f"SQLite database: {LOCAL_DATABASE_PATH.resolve()}")
    print("Listening on loopback only. Press Ctrl+C to stop.", flush=True)
    app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
