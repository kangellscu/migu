import pytest
from pathlib import Path
from migu.init.creator import ensure_directories, create_kb


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


def test_init_copies_actual_skills(tmp_path):
    """Verify migu init copies actual skills from bundle."""
    target = tmp_path / "test-kb"
    create_kb(str(target), "minimal")
    
    ingest_dir = target / ".agents" / "skills" / "kb-ingest"
    assert ingest_dir.exists(), "kb-ingest skill not copied"
    assert (ingest_dir / "SKILL.md").exists(), "SKILL.md not copied"


def test_init_copies_all_skills(tmp_path):
    """Verify all 6 skills are copied."""
    target = tmp_path / "test-kb"
    create_kb(str(target), "minimal")
    
    expected_skills = ["kb-ingest", "kb-compile", "kb-lint", "kb-query", "kb-archive", "kb-status"]
    for skill in expected_skills:
        skill_dir = target / ".agents" / "skills" / skill
        assert skill_dir.exists(), f"Skill '{skill}' not copied"
