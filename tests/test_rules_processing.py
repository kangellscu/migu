import pytest
from migu.init.rules import resolve_rules, load_structure, load_skills

def test_resolve_minimal_rules():
    """Verify minimal rules directory is found."""
    rules_path = resolve_rules("minimal")
    assert rules_path.exists()
    assert (rules_path / "skills.json").exists()

def test_resolve_invalid_rules():
    """Verify error for non-existent rules."""
    with pytest.raises(ValueError, match="Rules.*not found"):
        resolve_rules("nonexistent")

def test_load_structure():
    """Verify structure.json loads correctly."""
    structure = load_structure("minimal")
    assert "directories" in structure
    assert "wiki" in structure["directories"]

def test_load_skills():
    """Verify skills.json loads correctly."""
    skills = load_skills("minimal")
    assert "skills" in skills
    assert len(skills["skills"]) >= 1
