# Phase 1: CLI Init + Rules Minimal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `migu init` CLI command that creates a minimal knowledge base skeleton.

**Architecture:** Single-command CLI using typer. Rules processing handles configuration merging and directory creation. TDD approach with pytest.

**Tech Stack:** Python 3.11+, typer, pathlib, pytest

---

### Task 0: Project Scaffolding

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/pyproject.toml`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/.python-version`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/__init__.py`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/tests/__init__.py`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/init/__init__.py`

- [ ] **Step 1: Create pyproject.toml with uv configuration**

```toml
[project]
name = "migu"
version = "0.1.0"
description = "CLI scaffolder for LLM-WIKI knowledge bases"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9",
    "rich>=13.0",
]

[project.scripts]
migu = "migu.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
]
```

- [ ] **Step 2: Create .python-version**

```
3.11
```

- [ ] **Step 3: Create migu/__init__.py**

```python
"""migu - LLM-WIKI knowledge base scaffolder."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Create empty test and init package files**

```python
# tests/__init__.py - empty file
# migu/init/__init__.py - empty file
```

- [ ] **Step 5: Install dependencies with uv**

Run: `uv sync`
Expected: Dependencies installed, .venv created

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .python-version migu/__init__.py tests/__init__.py migu/init/__init__.py
git commit -m "feat: initial project scaffolding with pyproject.toml and empty packages"
```

---

### Task 1: CLI App Structure

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/__main__.py`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/cli.py`
- Test: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_cli.py`

- [ ] **Step 1: Write the failing test for CLI app**

```python
# tests/test_cli.py
from typer.testing import CliRunner

def test_cli_app_exists():
    """Verify the CLI app can be imported and run."""
    from migu.cli import app
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "migu" in result.stdout.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'migu.cli'"

- [ ] **Step 3: Write the CLI app**

```python
# migu/__main__.py
from migu.cli import app

if __name__ == "__main__":
    app()
```

```python
# migu/cli.py
"""Migu CLI - LLM-WIKI knowledge base scaffolder."""

import typer

from migu import __version__

app = typer.Typer(
    name="migu",
    help="CLI scaffolder for LLM-WIKI knowledge bases",
    add_completion=False,
)

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"migu {__version__}")
        raise typer.Exit()

@app.callback()
def _main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    pass

@app.command()
def init(
    target_dir: str = typer.Argument(..., help="Target directory for the knowledge base"),
    rules: str = typer.Option("minimal", "--rules", help="Rules type (default: minimal)"),
) -> None:
    """Initialize a new knowledge base."""
    from migu.init.creator import create_kb
    
    create_kb(target_dir, rules)

if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_cli_app_exists -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add migu/__main__.py migu/cli.py tests/test_cli.py
git commit -m "feat: basic CLI app structure with version flag and init command"
```

---

### Task 2: Rules Configuration Files

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/rules/minimal/AGENTS.md`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/rules/minimal/structure.json`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/rules/minimal/skills.json`
- Test: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_rules.py`

- [ ] **Step 1: Write the failing test for rules loading**

```python
# tests/test_rules.py
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
    assert len(data["skills"]) >= 1
    
    # Each skill has name, source, version
    for skill in data["skills"]:
        assert "name" in skill
        assert "source" in skill
        assert "version" in skill
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_rules.py -v`
Expected: FAIL with file not found errors

- [ ] **Step 3: Create rules configuration files**

```markdown
<!-- Rules/minimal/AGENTS.md -->
---
version: "1.0"
---
# Knowledge Base Schema

## Directory Structure

- `raw/`: Raw source files (user managed, immutable)
- `raw/.extracted/`: Processed files from kb-ingest
- `wiki/`: LLM-generated structured documents
  - `entities/`: Person, place, organization pages
  - `concepts/`: Concept pages
  - `synthesis/`: Analysis and synthesis pages
- `output/`: User-generated derivative documents

## Naming Conventions

- Wiki pages: Title case, no file extension in wikilinks. E.g., `[[刘邦]]`
- Raw files: Preserve original naming structure. E.g., `raw/史记/本纪/高祖本纪.md`
- Extracted files: Mirror raw directory structure under `raw/.extracted/`

## Reference Format

Use Obsidian wikilinks: `[[Page Name]]`
For file references: `[[raw/path/to/file.md|display name]]`

source field in wiki documents:
```markdown
## 来源
- source: [[raw/path/to/file.md]]
```

## Operations

- kb-ingest: Scan raw/, preprocess, output to raw/.extracted/
- kb-compile: Read extracted files, extract entities, generate wiki pages
- kb-lint: Check wiki syntax and semantics
- kb-query: Search wiki with optional raw backtracking
- kb-archive: Write synthesis reports and integrate back into wiki
- kb-status: Show dashboard (parse index.md + raw-registry.md)
```

```json
{
  "directories": {
    "raw": {
      ".extracted": {}
    },
    "wiki": {
      "entities": {},
      "concepts": {},
      "synthesis": {}
    },
    "output": {}
  }
}
```

```json
{
  "skills": [
    {
      "name": "kb-ingest",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-compile",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-lint",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-query",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-archive",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-status",
      "source": "minimal",
      "version": "1.0"
    }
  ]
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_rules.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add "rules/minimal/AGENTS.md" "rules/minimal/structure.json" "rules/minimal/skills.json" tests/test_rules.py
git commit -m "feat: minimal rules configuration with structure and skills JSON"
```

---

### Task 3: Rules Processing Logic

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/init/rules.py`
- Test: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_rules_processing.py`

- [ ] **Step 1: Write the failing test for rules processing**

```python
# tests/test_rules_processing.py
import json
from pathlib import Path
from migu.init.rules import (
    resolve_rules,
    load_structure,
    load_skills,
)

def test_resolve_minimal_rules():
    """Verify minimal rules directory is found."""
    rules_path = resolve_rules("minimal")
    assert rules_path.exists()
    assert (rules_path / "skills.json").exists()

def test_resolve_invalid_rules():
    """Verify error for non-existent rules."""
    import pytest
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_rules_processing.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'migu.init.rules'"

- [ ] **Step 3: Write rules processing logic**

```python
# migu/init/rules.py
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


def load_skills(rules_name: str) -> list:
    """Load skills.json from rules directory.
    
    Args:
        rules_name: Name of the rules type
        
    Returns:
        List of skill definitions
        
    Raises:
        ValueError: If skills.json is missing
    """
    rules_dir = resolve_rules(rules_name)
    skills_file = rules_dir / "skills.json"
    
    return json.loads(skills_file.read_text())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_rules_processing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add migu/init/rules.py tests/test_rules_processing.py
git commit -m "feat: rules loading and resolution with fallback to minimal"
```

---

### Task 4: Directory Creation Logic

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/init/creator.py`
- Test: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_creator.py`

- [ ] **Step 1: Write the failing test for directory creation**

```python
# tests/test_creator.py
import pytest
from pathlib import Path
from migu.init.creator import ensure_directories

def test_ensure_nested_directories(tmp_path):
    """Verify nested directory structure is created."""
    structure = {
        "directories": {
            "wiki": {
                "entities": {},
                "concepts": {},
            },
            "raw": {".extracted": {}},
        }
    }
    
    ensure_directories(tmp_path, structure)
    
    assert (tmp_path / "wiki" / "entities").is_dir()
    assert (tmp_path / "wiki" / "concepts").is_dir()
    assert (tmp_path / "raw" / ".extracted").is_dir()

def test_ensure_directories_empty_structure(tmp_path):
    """Verify no error with empty directories dict."""
    structure = {"directories": {}}
    ensure_directories(tmp_path, structure)
    assert tmp_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_creator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'migu.init.creator'"

- [ ] **Step 3: Write directory creation logic**

```python
# migu/init/creator.py
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
    
    # Step 1: Check target directory does not exist
    if target_path.exists():
        raise ValueError(
            f"Target directory '{target_path}' already exists. "
            f"Choose a different path or remove it first."
        )
    
    # Step 3: Load configuration
    structure = load_structure(rules_name)
    skills = load_skills(rules_name)
    
    # Step 4: Create directory structure
    target_path.mkdir(parents=True)
    ensure_directories(target_path, structure)
    
    # Step 5: Placeholder for skill installation (Phase 2)
    _create_skills_placeholder(target_path, rules_name, skills)
    
    # Step 6: Create template files
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_creator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add migu/init/creator.py tests/test_creator.py
git commit -m "feat: knowledge base creation with directory structure and template files"
```

---

### Task 5: Integration Test for migu init

**Files:**
- Modify: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_cli.py`
- Modify: `/Users/23mofang/Documents/knowledge-bases/migu/migu/init/creator.py:45-60` (improve output)

- [ ] **Step 1: Write integration test for full init flow**

```python
# Add to tests/test_cli.py
from typer.testing import CliRunner
import json
from pathlib import Path

def test_init_creates_knowledge_base(tmp_path):
    """Verify migu init creates full knowledge base structure."""
    from migu.cli import app
    
    target = tmp_path / "test-kb"
    runner = CliRunner()
    result = runner.invoke(app, ["init", str(target)])
    
    assert result.exit_code == 0
    
    # Verify expected directories exist
    assert (target / "raw" / ".extracted").is_dir()
    assert (target / "wiki" / "entities").is_dir()
    assert (target / "wiki" / "concepts").is_dir()
    assert (target / "wiki" / "synthesis").is_dir()
    assert (target / "output").is_dir()
    assert (target / ".agents" / "skills").is_dir()
    
    # Verify expected files exist
    assert (target / "AGENTS.md").is_file()
    assert (target / "index.md").is_file()
    assert (target / "log.md").is_file()
    assert (target / "raw-registry.md").is_file()
    
    # Verify skills-lock.json
    lock_file = target / ".agents" / "skills-lock.json"
    assert lock_file.is_file()
    
    lock_data = json.loads(lock_file.read_text())
    assert lock_data["rules"] == "minimal"
    assert "skills" in lock_data

def test_init_fails_on_existing_directory(tmp_path):
    """Verify migu init fails if target directory exists."""
    from migu.cli import app
    
    target = tmp_path / "test-kb"
    target.mkdir()
    
    runner = CliRunner()
    result = runner.invoke(app, ["init", str(target)])
    
    assert result.exit_code != 0
    assert "already exists" in result.stdout.lower() or "already exists" in str(result.exception)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 3: Run full test suite**

Run: `uv run pytest -v`
Expected: ALL TESTS PASS

- [ ] **Step 4: Manual verification**

Run: `uv run migu init /tmp/test-migu-kb`
Expected: "Knowledge base created at: /tmp/test-migu-kb"

Verify structure:
```bash
ls -la /tmp/test-migu-kb/
ls -la /tmp/test-migu-kb/.agents/
cat /tmp/test-migu-kb/.agents/skills-lock.json
```

- [ ] **Step 5: Final commit**

```bash
git add tests/test_cli.py
git commit -m "feat: integration tests for migu init command"
```
