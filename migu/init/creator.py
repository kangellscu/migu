"""Knowledge base creation logic."""

import json
from datetime import datetime
from pathlib import Path

from migu.init.rules import load_structure, load_skills, resolve_rules


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
    
    # Create skill directories (placeholder for Phase 2)
    _create_skills_placeholder(target_path, rules_name, skills)
    
    # Create template files
    _create_template_files(target_path, rules_name)
    
    print(f"Knowledge base created at: {target_path}")
    print(f"Using rules: {rules_name}")


def _create_skills_placeholder(target_path: Path, rules_name: str, skills: dict) -> None:
    """Create skill directories and skills-lock.json (placeholder for Phase 2)."""
    skills_dir = target_path / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    lock_data = {
        "rules": rules_name,
        "installed_at": datetime.now().isoformat(),
        "migu_version": "0.1.0",
        "skills": skills.get("skills", []),
    }
    
    (target_path / ".agents" / "skills-lock.json").write_text(
        json.dumps(lock_data, indent=2) + "\n"
    )


def _create_template_files(target_path: Path, rules_name: str) -> None:
    """Create initial knowledge base files."""
    # index.md template
    index_content = """---
version: "1.0"
---
# Wiki Index

<!-- 
entry format: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD
sections correspond to structure.json wiki directory structure
-->

## entities
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->

## concepts
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->

## synthesis
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->
"""
    (target_path / "index.md").write_text(index_content)
    
    # log.md template
    log_content = """---
version: "1.0"
---
# Knowledge Base Log

<!-- 
entry format: ## [YYYY-MM-DD] operation | details
operation: ingest | compile | archive | lint
query and status not recorded
-->

<!-- Operation log appended by kb-ingest/compile/archive/lint -->
"""
    (target_path / "log.md").write_text(log_content)
    
    # raw-registry.md template
    registry_content = """---
version: "1.0"
---
# Raw File Registry

<!-- 
entry format: | 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
-->

| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
"""
    (target_path / "raw-registry.md").write_text(registry_content)
    
    # AGENTS.md from rules
    rules_dir = resolve_rules(rules_name)
    agents_source = rules_dir / "AGENTS.md"
    (target_path / "AGENTS.md").write_text(agents_source.read_text())
