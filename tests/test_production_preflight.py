import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "production_preflight.py"
SPEC = importlib.util.spec_from_file_location("production_preflight", SCRIPT_PATH)
production_preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(production_preflight)


def test_preflight_does_not_connect_without_both_execution_switches(monkeypatch, capsys):
    monkeypatch.setattr(production_preflight, "inspect_database", lambda _: (_ for _ in ()).throw(AssertionError()))
    assert production_preflight.main([]) == 0
    assert '"status": "not_executed"' in capsys.readouterr().out


def test_preflight_rejects_non_postgres_urls():
    try:
        production_preflight._validate_postgres_url("sqlite:///stepzone.sqlite3")
    except ValueError:
        pass
    else:
        raise AssertionError("SQLite URL unexpectedly accepted")
