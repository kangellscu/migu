"""Tests for Phase 4: history rules."""

import json
from pathlib import Path

import pytest

from migu.init.rules import resolve_rules
from migu.init.creator import create_kb


@pytest.fixture
def temp_kb(tmp_path):
    """Temporary knowledge base directory."""
    return str(tmp_path / "my-kb")


def test_history_rules_directory_exists():
    """History rules directory should exist."""
    rules_dir = resolve_rules("history")
    assert rules_dir.exists()
    assert (rules_dir / "skills.json").exists()


def test_history_skills_json():
    """skills.json should reference history kb-compile."""
    rules_dir = resolve_rules("history")
    skills_data = json.loads((rules_dir / "skills.json").read_text())
    
    compile_skill = None
    for skill in skills_data["skills"]:
        if skill["name"] == "kb-compile":
            compile_skill = skill
            break
    
    assert compile_skill is not None
    assert compile_skill["source"] == "history"
    assert compile_skill["version"] == "1.0"


def test_history_kb_compile_skill_exists():
    """History kb-compile skill should exist."""
    skill_path = Path(__file__).parent.parent / "skills" / "history" / "kb-compile"
    assert skill_path.exists()
    assert (skill_path / "SKILL.md").exists()


def test_history_kb_compile_scripts_exist():
    """History kb-compile scripts should exist."""
    scripts_dir = (
        Path(__file__).parent.parent / "skills" / "history" / "kb-compile" / "scripts"
    )
    assert (scripts_dir / "read_file.py").exists()
    assert (scripts_dir / "update_registry.py").exists()


def test_history_kb_compile_templates_exist():
    """History kb-compile should have 6 templates."""
    templates_dir = (
        Path(__file__).parent.parent
        / "skills"
        / "history"
        / "kb-compile"
        / "references"
        / "templates"
    )
    expected_templates = [
        "person-template.md",
        "place-template.md",
        "event-template.md",
        "institution-template.md",
        "official-template.md",
        "thought-template.md",
    ]
    for template_name in expected_templates:
        assert (templates_dir / template_name).exists()


def test_history_templates_have_content():
    """All history templates should have meaningful content."""
    templates_dir = (
        Path(__file__).parent.parent
        / "skills"
        / "history"
        / "kb-compile"
        / "references"
        / "templates"
    )
    for template_file in templates_dir.glob("*.md"):
        content = template_file.read_text()
        assert len(content) > 50, f"{template_file.name} is too short"
        assert "# {{" in content, f"{template_file.name} missing title"
        assert "## " in content, f"{template_file.name} missing sections"


def test_migu_init_with_rules_history(temp_kb):
    """migu init --rules history should create knowledge base."""
    create_kb(temp_kb, "history")
    
    kb_path = Path(temp_kb)
    assert kb_path.exists()
    assert (kb_path / "wiki").exists()
    assert (kb_path / "raw").exists()
    assert (kb_path / "output").exists()
    assert (kb_path / "AGENTS.md").exists()
    assert (kb_path / "index.md").exists()
    assert (kb_path / "index.md").exists()
