"""Skill management logic (read/validate/locate skills)."""

import json
from pathlib import Path

SKILLS_ROOT = Path(__file__).parent.parent.parent / "skills"


def load_skills_lock(target_dir: Path) -> dict:
    """Load skills-lock.json from target directory."""
    lock_file = target_dir / ".agents" / "skills-lock.json"
    return json.loads(lock_file.read_text())


def save_skills_lock(target_dir: Path, data: dict) -> None:
    """Save skills-lock.json to target directory."""
    lock_file = target_dir / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(data, indent=2) + "\n")


def validate_target_dir(target_dir: Path) -> None:
    """Validate that target_dir is a valid knowledge base.
    
    Raises:
        ValueError: If skills-lock.json is missing
    """
    lock_file = target_dir / ".agents" / "skills-lock.json"
    if not lock_file.exists():
        raise ValueError(
            f"Not a valid knowledge base: '{target_dir}' is missing .agents/skills-lock.json. "
            f"Run 'migu init' first."
        )


def get_bundled_skill_path(skill_name: str, source: str) -> Path:
    """Get path to a bundled skill in the migu repository.
    
    Args:
        skill_name: Name of the skill (e.g., 'kb-ingest')
        source: Source of the skill (e.g., 'minimal', 'history')
    """
    return SKILLS_ROOT / source / skill_name


def get_installed_skill_path(target_dir: Path, skill_name: str) -> Path:
    """Get path to an installed skill in target directory."""
    return target_dir / ".agents" / "skills" / skill_name
