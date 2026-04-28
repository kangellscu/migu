"""Knowledge base creation logic."""

import json
from datetime import datetime
from pathlib import Path

from migu.init.rules import load_structure, load_skills, resolve_rules


def _resolve_template_file(filename: str, rules_name: str) -> Path:
    """Resolve template file with inheritance fallback.
    
    Args:
        filename: Template filename (e.g., 'index.md', 'kb-README.md')
        rules_name: Rules name (e.g., 'minimal', 'history')
        
    Returns:
        Path to template file
        
    Raises:
        ValueError: If template not found in rules or minimal
    """
    rules_dir = resolve_rules(rules_name)
    rules_template = rules_dir / "templates" / filename
    
    if rules_template.exists():
        return rules_template
    
    # Fallback to minimal
    minimal_dir = resolve_rules("minimal")
    minimal_template = minimal_dir / "templates" / filename
    
    if minimal_template.exists():
        return minimal_template
    
    raise ValueError(
        f"Template '{filename}' not found in {rules_name} or minimal templates"
    )


def _generate_index_sections(structure: dict) -> str:
    """Generate index.md sections from structure.json wiki directories.
    
    Args:
        structure: Dictionary from structure.json
        
    Returns:
        Sections content string
    """
    wiki_dirs = structure.get("directories", {}).get("wiki", {})
    sections = []
    
    for section_name in wiki_dirs.keys():
        sections.append(f"\n## {section_name}")
        sections.append("<!-- entry: - [[Page Name]] | brief summary | updated: YYYY-MM-DD -->")
    
    return "\n".join(sections)


def ensure_directories(base_path: Path, structure: dict) -> None:
    """Create directory structure from structure.json definition.
    
    Args:
        base_path: Root path where directories should be created
        structure: Dictionary with 'directories' key containing nested structure
    """
    directories = structure.get("directories", {})
    _create_directories_recursive(base_path, directories)


def _create_directories_recursive(base_path: Path, dirs: dict) -> None:
    """Recursively create directories from nested dictionary."""
    for dir_name, children in dirs.items():
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        if children:
            _create_directories_recursive(dir_path, children)


def create_kb(target_dir: str, rules_name: str) -> None:
    """Create a new knowledge base.
    
    Args:
        target_dir: Path where the knowledge base should be created
        rules_name: Name of the rules type to use
        
    Raises:
        ValueError: If target directory already exists
    """
    target_path = Path(target_dir).resolve()
    
    # Check target directory does not exist
    if target_path.exists():
        raise ValueError(
            f"Target directory '{target_path}' already exists. "
            f"Choose a different path or remove it first."
        )
    
    # Load configuration
    structure = load_structure(rules_name)
    skills = load_skills(rules_name)
    
    # Create directory structure
    target_path.mkdir(parents=True)
    ensure_directories(target_path, structure)
    
    # Install skills from bundle
    _create_skills(target_path, skills, rules_name)
    
    # Create template files
    _create_template_files(target_path, rules_name)
    
    print(f"Knowledge base created at: {target_path}")
    print(f"Using rules: {rules_name}")


def _create_skills(target_path: Path, skills: dict, rules_name: str) -> None:
    """Install all skills from bundle to target directory."""
    from migu.skill.installer import install_skill
    from migu.skill.manager import save_skills_lock
    
    skills_dir = target_path / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    lock_data = {
        "rules": rules_name,
        "installed_at": datetime.now().isoformat(),
        "migu_version": "0.1.0",
        "skills": [],
    }
    
    for skill_entry in skills.get("skills", []):
        install_skill(
            skill_entry["name"],
            skill_entry["source"],
            target_path,
            lock_data,
        )


def _create_template_files(target_path: Path, rules_name: str) -> None:
    """Create initial knowledge base files from templates.
    
    Copies templates from rules/*/templates/ to knowledge base root.
    Implements inheritance: fallback to minimal if rules has no templates.
    Dynamically generates index.md sections from structure.json.
    """
    # Load structure for index.md dynamic generation
    structure = load_structure(rules_name)
    
    # Get list of template files from minimal (base templates)
    minimal_dir = resolve_rules("minimal")
    minimal_templates_dir = minimal_dir / "templates"
    
    if not minimal_templates_dir.exists():
        raise ValueError("minimal templates directory not found")
    
    template_files = [f.name for f in minimal_templates_dir.iterdir() if f.is_file()]
    
    # Copy each template file
    for filename in template_files:
        # Resolve template with inheritance
        template_source = _resolve_template_file(filename, rules_name)
        template_content = template_source.read_text()
        
        # Special handling for index.md: add dynamic sections
        if filename == "index.md":
            sections_content = _generate_index_sections(structure)
            template_content = template_content + sections_content
        
        # Write to knowledge base root
        (target_path / filename).write_text(template_content)
    
    # Copy AGENTS.md (not in templates/, separate inheritance logic)
    rules_dir = resolve_rules(rules_name)
    agents_source = rules_dir / "AGENTS.md"
    if not agents_source.exists():
        minimal_dir = resolve_rules("minimal")
        agents_source = minimal_dir / "AGENTS.md"
    (target_path / "AGENTS.md").write_text(agents_source.read_text())
