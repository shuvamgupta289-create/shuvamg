from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _migration_script_directory():
    config = Config()
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    return ScriptDirectory.from_config(config)


def test_migration_graph_has_one_merge_head():
    script = _migration_script_directory()
    assert script.get_heads() == ["f8a1c2d3e4f5"]

    merge_revision = script.get_revision("f8a1c2d3e4f5")
    assert set(merge_revision._versioned_down_revisions) == {
        "7ac2d937e08b",
        "c72a9321f0de",
    }
