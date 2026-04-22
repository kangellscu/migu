"""Rules configuration loading and merge logic."""

import json
from pathlib import Path

RULES_ROOT = Path(__file__).parent.parent.parent / "rules"


def resolve_rules(rules_name: str) -> Path:
    """Resolve rules name to directory path.
    
    Args:
        rules_name: Name of the rules type (e.g., 'minimal', 'history')
        
    Returns:
        Path to the rules directory
        
    Raises:
        ValueError: If rules directory does not exist
    """
    rules_dir = RULES_ROOT / rules_name
    
    if not rules_dir.exists():
        raise ValueError(
            f"Rules '{rules_name}' not found at {rules_dir}. "
            f"Available rules: {', '.join(d.name for d in RULES_ROOT.iterdir() if d.is_dir())}"
        )
    
    if not (rules_dir / "skills.json").exists():
        raise ValueError(
            f"Rules '{rules_name}' is missing skills.json. "
            f"Check rules configuration at {rules_dir}"
        )
    
    return rules_dir


def load_structure(rules_name: str) -> dict:
    """Load structure.json from rules directory.
    
    Falls back to minimal if structure.json does not exist in specified rules.
    
    Args:
        rules_name: Name of the rules type
        
    Returns:
        Dictionary with directory structure definition
    """
    rules_dir = resolve_rules(rules_name)
    structure_file = rules_dir / "structure.json"
    
    if not structure_file.exists():
        # Fall back to minimal
        minimal_dir = resolve_rules("minimal")
        structure_file = minimal_dir / "structure.json"
    
    return json.loads(structure_file.read_text())


def load_skills(rules_name: str) -> dict:
    """Load skills.json from rules directory.
    
    Args:
        rules_name: Name of the rules type
        
    Returns:
        Dictionary with skills list
    """
    rules_dir = resolve_rules(rules_name)
    skills_file = rules_dir / "skills.json"
    
    return json.loads(skills_file.read_text())
