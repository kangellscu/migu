import json
from pathlib import Path

def test_minimal_rules_exist():
    """Verify minimal rules directory contains required files."""
    rules_dir = Path(__file__).parent.parent / "rules" / "minimal"
    
    assert (rules_dir / "AGENTS.md").exists(), "AGENTS.md not found"
    assert (rules_dir / "structure.json").exists(), "structure.json not found"
    assert (rules_dir / "skills.json").exists(), "skills.json not found"

def test_structure_json_format():
    """Verify structure.json has valid directory definitions."""
    structure_file = Path(__file__).parent.parent / "rules" / "minimal" / "structure.json"
    
    data = json.loads(structure_file.read_text())
    assert "directories" in data
    assert "raw" in data["directories"]
    assert "wiki" in data["directories"]
    assert "output" in data["directories"]
    
    # Verify wiki subdirectories
    wiki_dirs = data["directories"]["wiki"]
    assert "entities" in wiki_dirs
    assert "concepts" in wiki_dirs
    assert "synthesis" in wiki_dirs

def test_skills_json_format():
    """Verify skills.json has valid skills list."""
    skills_file = Path(__file__).parent.parent / "rules" / "minimal" / "skills.json"
    
    data = json.loads(skills_file.read_text())
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert len(data["skills"]) == 6
    
    # Each skill has name, source, version
    for skill in data["skills"]:
        assert "name" in skill
        assert "source" in skill
        assert "version" in skill
