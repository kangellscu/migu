import pytest
from pathlib import Path
from migu.init.creator import ensure_directories


def test_ensure_nested_directories(tmp_path):
    """Verify nested directory structure is created."""
    structure = {
        "directories": {
            "wiki": {
                "entities": {},
                "concepts": {},
            },
            "raw": {".extracted": {}},
        }
    }

    ensure_directories(tmp_path, structure)

    assert (tmp_path / "wiki" / "entities").is_dir()
    assert (tmp_path / "wiki" / "concepts").is_dir()
    assert (tmp_path / "raw" / ".extracted").is_dir()


def test_ensure_directories_empty_structure(tmp_path):
    """Verify no error with empty directories dict."""
    structure = {"directories": {}}
    ensure_directories(tmp_path, structure)
    assert tmp_path.exists()
