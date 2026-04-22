"""Skill installation operations (copy/remove/change detection)."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from migu.skill.manager import (
    get_bundled_skill_path,
    get_installed_skill_path,
    save_skills_lock,
)


def install_skill(skill_name: str, source: str, target_dir: Path, skills_lock: dict) -> None:
    """Install a skill from bundle to target directory.
    
    Args:
        skill_name: Name of the skill
        source: Source type (minimal, history)
        target_dir: Target knowledge base directory
        skills_lock: Current skills-lock.json data (modified in place)
    """
    bundled = get_bundled_skill_path(skill_name, source)
    installed = get_installed_skill_path(target_dir, skill_name)
    
    if not bundled.exists():
        raise ValueError(
            f"Skill '{skill_name}' not found in source '{source}' at {bundled}"
        )
    
    # Copy skill directory
    if installed.exists():
        shutil.rmtree(installed)
    shutil.copytree(bundled, installed)
    
    # Update skills-lock.json
    timestamp = datetime.now().isoformat()
    
    # Remove existing entry if present
    skills_lock["skills"] = [
        s for s in skills_lock["skills"] if s["name"] != skill_name
    ]
    
    # Add new entry
    skills_lock["skills"].append({
        "name": skill_name,
        "source": source,
        "version": "1.0",
        "installed_at": timestamp,
    })
    
    save_skills_lock(target_dir, skills_lock)


def uninstall_skill(skill_name: str, target_dir: Path, skills_lock: dict) -> None:
    """Uninstall a skill from target directory.
    
    Args:
        skill_name: Name of the skill to remove
        target_dir: Target knowledge base directory
        skills_lock: Current skills-lock.json data (modified in place)
    """
    installed = get_installed_skill_path(target_dir, skill_name)
    
    if not installed.exists():
        raise ValueError(f"Skill '{skill_name}' is not installed")
    
    shutil.rmtree(installed)
    
    # Remove from lock
    skills_lock["skills"] = [
        s for s in skills_lock["skills"] if s["name"] != skill_name
    ]
    
    save_skills_lock(target_dir, skills_lock)


def check_skill_changed(skill_name: str, target_dir: Path) -> bool:
    """Check if an installed skill differs from its bundled version.
    
    Args:
        skill_name: Name of the skill
        target_dir: Target knowledge base directory
        
    Returns:
        True if the skill has been modified from the bundled version
    """
    from migu.skill.manager import load_skills_lock
    
    skills_lock = load_skills_lock(target_dir)
    
    # Find source for this skill
    source = None
    for skill in skills_lock["skills"]:
        if skill["name"] == skill_name:
            source = skill["source"]
            break
    
    if source is None:
        return False
    
    bundled = get_bundled_skill_path(skill_name, source)
    installed = get_installed_skill_path(target_dir, skill_name)
    
    if not installed.exists():
        return False
    
    # Compare files via hash
    bundled_hash = _hash_directory(bundled)
    installed_hash = _hash_directory(installed)
    
    return bundled_hash != installed_hash


def _hash_directory(dir_path: Path) -> str:
    """Hash all files in a directory (recursively) for change detection."""
    hasher = hashlib.sha256()
    for file_path in sorted(dir_path.rglob("*")):
        if file_path.is_file():
            hasher.update(file_path.read_bytes())
    return hasher.hexdigest()
