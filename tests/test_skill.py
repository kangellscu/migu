import hashlib
import json
import shutil

import pytest
from pathlib import Path
from migu.skill.manager import (
    load_skills_lock,
    save_skills_lock,
    validate_target_dir,
    get_bundled_skill_path,
    get_installed_skill_path,
)
from migu.skill.installer import (
    install_skill,
    uninstall_skill,
    check_skill_changed,
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

def test_install_skill(tmp_path):
    """Verify skill copies from bundle to target."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    lock_file.write_text(json.dumps(lock_data))

    skills_lock = load_skills_lock(tmp_path)

    install_skill("kb-ingest", "minimal", tmp_path, skills_lock)

    skill_dir = tmp_path / ".agents" / "skills" / "kb-ingest"
    assert skill_dir.exists(), "Skill directory not created"
    assert (skill_dir / "SKILL.md").exists(), "SKILL.md not copied"

    # Check lock file updated
    updated_lock = load_skills_lock(tmp_path)
    skill_names = [s["name"] for s in updated_lock["skills"]]
    assert "kb-ingest" in skill_names

def test_uninstall_skill(tmp_path):
    """Verify skill removes from target and updates lock."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    (tmp_path / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    lock_file.write_text(json.dumps(lock_data))

    skills_lock = load_skills_lock(tmp_path)
    install_skill("kb-ingest", "minimal", tmp_path, skills_lock)

    # Then uninstall
    uninstall_skill("kb-ingest", tmp_path, skills_lock)

    skill_dir = tmp_path / ".agents" / "skills" / "kb-ingest"
    assert not skill_dir.exists(), "Skill directory not removed"

    updated_lock = load_skills_lock(tmp_path)
    skill_names = [s["name"] for s in updated_lock["skills"]]
    assert "kb-ingest" not in skill_names

def test_check_skill_changed(tmp_path):
    """Verify change detection against bundled version."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    (tmp_path / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [
            {"name": "kb-ingest", "source": "minimal", "version": "1.0", "installed_at": "2026-04-22T10:00:00"}
        ],
    }
    lock_file.write_text(json.dumps(lock_data))

    install_skill("kb-ingest", "minimal", tmp_path, load_skills_lock(tmp_path))

    # Should not be changed right after install
    assert not check_skill_changed("kb-ingest", tmp_path)

    # Modify a file
    skill_file = get_installed_skill_path(tmp_path, "kb-ingest") / "SKILL.md"
    original = skill_file.read_text()
    skill_file.write_text("# Modified\n")

    # Should now be detected as changed
    assert check_skill_changed("kb-ingest", tmp_path)

    # Restore
    skill_file.write_text(original)

def test_install_skill_nonexistent_raises(tmp_path):
    """Verify installing nonexistent skill raises ValueError."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    lock_file.write_text(json.dumps(lock_data))

    skills_lock = load_skills_lock(tmp_path)

    with pytest.raises(ValueError, match="not found"):
        install_skill("nonexistent", "minimal", tmp_path, skills_lock)

def test_uninstall_skill_not_installed_raises(tmp_path):
    """Verify uninstalling non-installed skill raises ValueError."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    lock_file.write_text(json.dumps(lock_data))

    skills_lock = load_skills_lock(tmp_path)

    with pytest.raises(ValueError, match="not installed"):
        uninstall_skill("kb-ingest", tmp_path, skills_lock)

def test_install_skill_reinstall_overwrites(tmp_path):
    """Verify reinstalling a skill overwrites existing copy."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    lock_file.write_text(json.dumps(lock_data))

    skills_lock = load_skills_lock(tmp_path)

    install_skill("kb-ingest", "minimal", tmp_path, skills_lock)

    # Modify the installed file
    skill_file = get_installed_skill_path(tmp_path, "kb-ingest") / "SKILL.md"
    skill_file.write_text("# Modified\n")

    # Reinstall should overwrite
    install_skill("kb-ingest", "minimal", tmp_path, load_skills_lock(tmp_path))

    bundled_file = get_bundled_skill_path("kb-ingest", "minimal") / "SKILL.md"
    assert skill_file.read_text() == bundled_file.read_text()


# CLI tests for skill commands

from typer.testing import CliRunner


def test_skill_list_command(tmp_path):
    """Verify skill list shows installed skills."""
    from migu.skill.cli import skill_app
    
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
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["list", str(tmp_path)])
    
    assert result.exit_code == 0
    assert "kb-ingest" in result.output
    assert "minimal" in result.output


def test_skill_install_command(tmp_path):
    """Verify skill install copies skill to target."""
    from migu.skill.cli import skill_app
    
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    lock_data = {
        "rules": "minimal",
        "installed_at": "2026-04-22T10:00:00",
        "migu_version": "0.1.0",
        "skills": [],
    }
    lock_file.write_text(json.dumps(lock_data))
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["install", "kb-ingest", str(tmp_path)])
    
    assert result.exit_code == 0
    assert (tmp_path / ".agents" / "skills" / "kb-ingest").exists()


def test_skill_list_invalid_target(tmp_path):
    """Verify error for non-knowledge-base directory."""
    from migu.skill.cli import skill_app
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["list", str(tmp_path)])
    
    assert result.exit_code != 0
    assert "skills-lock.json" in result.output


def test_skill_uninstall_command(tmp_path):
    """Verify skill uninstall removes skill."""
    from migu.skill.cli import skill_app
    from migu.skill.manager import load_skills_lock
    from migu.skill.installer import install_skill
    
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
    (tmp_path / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    
    install_skill("kb-ingest", "minimal", tmp_path, load_skills_lock(tmp_path))
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["uninstall", "kb-ingest", str(tmp_path)])
    
    assert result.exit_code == 0
    assert not (tmp_path / ".agents" / "skills" / "kb-ingest").exists()


def test_skill_reinstall_command(tmp_path):
    """Verify skill reinstalls successfully."""
    from migu.skill.cli import skill_app
    from migu.skill.manager import load_skills_lock
    from migu.skill.installer import install_skill
    
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
    (tmp_path / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    
    install_skill("kb-ingest", "minimal", tmp_path, load_skills_lock(tmp_path))
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["reinstall", "kb-ingest", str(tmp_path)], input="y\n")
    
    assert result.exit_code == 0
    assert (tmp_path / ".agents" / "skills" / "kb-ingest").exists()
