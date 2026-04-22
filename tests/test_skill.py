import json
import pytest
from pathlib import Path
from migu.skill.manager import (
    load_skills_lock,
    save_skills_lock,
    validate_target_dir,
    get_bundled_skill_path,
    get_installed_skill_path,
)

def test_load_skills_lock(tmp_path):
    """Verify skills-lock.json loads correctly."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [
            {"name": "kb-ingest", "source": "minimal", "version": "1.0", "installed_at": "2026-04-22T10:00:00"}
        ],
    }
    lock_file.write_text(json.dumps(lock_data))
    
    result = load_skills_lock(tmp_path)
    assert result["rules"] == "minimal"
    assert len(result["skills"]) == 1

def test_validate_target_dir_valid(tmp_path):
    """Verify valid target directory passes validation."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_file.write_text("{}")
    
    validate_target_dir(tmp_path)  # Should not raise

def test_validate_target_dir_invalid(tmp_path):
    """Verify missing skills-lock.json raises error."""
    with pytest.raises(ValueError, match="skills-lock.json"):
        validate_target_dir(tmp_path)

def test_get_bundled_skill_path():
    """Verify bundled skill path resolves correctly."""
    path = get_bundled_skill_path("kb-ingest", "minimal")
    assert path.exists(), f"Skill directory not found: {path}"

def test_save_and_reload_skills_lock(tmp_path):
    """Verify save/load round-trip."""
    lock_data = {
        "rules": "test",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    
    save_skills_lock(tmp_path, lock_data)
    result = load_skills_lock(tmp_path)
    
    assert result == lock_data
