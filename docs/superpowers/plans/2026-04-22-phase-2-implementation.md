# Phase 2: CLI Skill Commands + Full Skill Installation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `migu skill install/uninstall/reinstall/list` commands and complete `migu init` skill copy logic.

**Architecture:** Typer subcommand group + manager/installer modules. Follows existing patterns from Phase 1.

**Tech Stack:** Python 3.11+, typer, pathlib, shutil, hashlib, pytest

---

### Task 0: Skill Manager Logic

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/skill/__init__.py`
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/skill/manager.py`
- Test: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_skill.py`

- [ ] **Step 1: Write the failing test for skill manager**

```python
# tests/test_skill.py
import json
import pytest
from pathlib import Path
from migu.skill.manager import (
    load_skills_lock,
    save_skills_lock,
    validate_target_dir,
    get_bundled_skill_path,
    get_installed_skill_path,
)

TEST_KB = None  # Will use tmp_path fixture in tests

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_skill.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write skill manager logic**

```python
# migu/skill/__init__.py - empty

# mimu/skill/manager.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_skill.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add migu/skill/__init__.py migu/skill/manager.py tests/test_skill.py
git commit -m "feat: skill manager logic with lock file handling and path resolution"
```

---

### Task 1: Skill Installer Logic

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/skill/installer.py`
- Test: Add integration tests to `tests/test_skill.py`

- [ ] **Step 1: Write the failing test for skill installer**

```python
# Add to tests/test_skill.py
import shutil
import hashlib
from migu.skill.installer import (
    install_skill,
    uninstall_skill,
    check_skill_changed,
)

def test_install_skill(tmp_path):
    """Verify skill copies from bundle to target."""
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    
    from migu.skill.manager import load_skills_lock, save_skills_lock
    
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
    # First install
    from migu.skill.manager import load_skills_lock, save_skills_lock
    
    lock_file = tmp_path / ".agents" / "skills-lock.json"
    lock_file.parent.mkdir(parents=True)
    
    skills_lock = load_skills_lock(tmp_path)
    install_skill("kb-ingest", "minimal", tmp_path, skills_lock)
    
    # Then uninstall
    updated_lock = load_skills_lock(tmp_path)
    uninstall_skill("kb-ingest", tmp_path, updated_lock)
    
    skill_dir = tmp_path / ".agents" / "skills" / "kb-ingest"
    assert not skill_dir.exists(), "Skill directory not removed"
    
    updated_lock = load_skills_lock(tmp_path)
    skill_names = [s["name"] for s in updated_lock["skills"]]
    assert "kb-ingest" not in skill_names

def test_check_skill_changed(tmp_path):
    """Verify change detection against bundled version."""
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
    
    from migu.skill.manager import get_installed_skill_path, get_bundled_skill_path
    
    # Install skill fresh
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_skill.py::test_install_skill -v`
Expected: FAIL

- [ ] **Step 3: Write skill installer logic**

```python
# migu/skill/installer.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_skill.py -v`
Expected: PASS (8 tests total)

- [ ] **Step 5: Commit**

```bash
git add migu/skill/installer.py tests/test_skill.py
git commit -m "feat: skill installer with copy, remove, and change detection"
```

---

### Task 2: Skill CLI Commands

**Files:**
- Create: `/Users/23mofang/Documents/knowledge-bases/migu/migu/skill/cli.py`
- Test: Add CLI tests to `tests/test_skill.py`

- [ ] **Step 1: Write the failing test for skill CLI commands**

```python
# Add to tests/test_skill.py
from typer.testing import CliRunner

def test_skill_list_command(tmp_path):
    """Verify skill list shows installed skills."""
    from migu.skill.cli import skill_app
    
    # Setup a fake KB with skills-lock
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
    assert "kb-ingest" in result.stdout
    assert "minimal" in result.stdout

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
    
    # Install first
    from migu.skill.installer import install_skill
    install_skill("kb-ingest", "minimal", tmp_path, load_skills_lock(tmp_path))
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["uninstall", "kb-ingest", str(tmp_path)])
    
    assert result.exit_code == 0
    assert not (tmp_path / ".agents" / "skills" / "kb-ingest").exists()

def test_skill_reinstall_command(tmp_path):
    """Verify skill reinstall updates to latest."""
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
    
    install_skill("kb-ingest", "minimal", tmp_path, load_skills_lock(tmp_path))
    
    runner = CliRunner()
    result = runner.invoke(skill_app, ["reinstall", "kb-ingest", str(tmp_path)])
    
    assert result.exit_code == 0
    assert (tmp_path / ".agents" / "skills" / "kb-ingest").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_skill.py -k "cli" -v`
Expected: FAIL

- [ ] **Step 3: Write skill CLI commands**

```python
# migu/skill/cli.py
"""Skill CLI commands (install, uninstall, reinstall, list)."""

import typer

from pathlib import Path

from migu.skill.manager import (
    load_skills_lock,
    validate_target_dir,
    get_bundled_skill_path,
)
from migu.skill.installer import (
    install_skill,
    uninstall_skill,
    check_skill_changed,
)

skill_app = typer.Typer(name="skill", help="Manage knowledge base skills")


@skill_app.command("list")
def list_skills(target_dir: str = typer.Argument(..., help="Knowledge base directory")) -> None:
    """List installed skills with version status."""
    target_path = Path(target_dir).resolve()
    validate_target_dir(target_path)
    
    lock_data = load_skills_lock(target_path)
    print(f"Skills in {target_path}:")
    print()
    
    for skill in lock_data["skills"]:
        bundled = get_bundled_skill_path(skill["name"], skill["source"])
        
        # Check version status
        is_latest = bundled.exists()  # Simplified: exists = latest
        
        status = "✓ latest" if is_latest else "⚠ outdated"
        print(f"  {skill['name']}  source: {skill['source']}  version: {skill['version']}  {status}")
    
    print()


@skill_app.command("install")
def install_skill_cmd(
    skill_name: str = typer.Argument(..., help="Skill name (e.g., kb-ingest)"),
    target_dir: str = typer.Argument(..., help="Knowledge base directory"),
    source: str = typer.Option("minimal", "--source", help="Skill source (default: minimal)"),
) -> None:
    """Install a skill into a knowledge base."""
    target_path = Path(target_dir).resolve()
    validate_target_dir(target_path)
    
    lock_data = load_skills_lock(target_path)
    
    # Check if already installed
    for skill in lock_data["skills"]:
        if skill["name"] == skill_name:
            typer.echo(f"Skill '{skill_name}' is already installed. Use 'reinstall' to update.")
            raise typer.Exit(code=1)
    
    install_skill(skill_name, source, target_path, lock_data)
    typer.echo(f"Skill '{skill_name}' installed from source '{source}'.")


@skill_app.command("uninstall")
def uninstall_skill_cmd(
    skill_name: str = typer.Argument(..., help="Skill name"),
    target_dir: str = typer.Argument(..., help="Knowledge base directory"),
) -> None:
    """Uninstall a skill from a knowledge base."""
    target_path = Path(target_dir).resolve()
    validate_target_dir(target_path)
    
    lock_data = load_skills_lock(target_path)
    uninstall_skill(skill_name, target_path, lock_data)
    
    typer.echo(f"Skill '{skill_name}' uninstalled.")


@skill_app.command("reinstall")
def reinstall_skill_cmd(
    skill_name: str = typer.Argument(..., help="Skill name"),
    target_dir: str = typer.Argument(..., help="Knowledge base directory"),
) -> None:
    """Reinstall a skill (updates to latest version)."""
    target_path = Path(target_dir).resolve()
    validate_target_dir(target_path)
    
    lock_data = load_skills_lock(target_path)
    
    # Find skill source
    source = None
    for skill in lock_data["skills"]:
        if skill["name"] == skill_name:
            source = skill["source"]
            break
    
    if source is None:
        typer.echo(f"Skill '{skill_name}' is not installed. Use 'install' first.")
        raise typer.Exit(code=1)
    
    # Check for user changes
    if check_skill_changed(skill_name, target_path):
        typer.echo(f"⚠ Skill '{skill_name}' has been modified.")
        confirm = typer.confirm("Changes will be overwritten. Continue?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit()
    
    install_skill(skill_name, source, target_path, lock_data)
    typer.echo(f"Skill '{skill_name}' reinstalled from source '{source}'.")
```

- [ ] **Step 4: Integrate with main CLI app**

Modify `migu/cli.py` to add the skill subcommand group:

```python
# migu/cli.py - add this import and registration
from migu.skill.cli import skill_app

app.add_typer(skill_app, name="skill")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_skill.py -v`
Expected: PASS (13 tests total)

- [ ] **Step 6: Commit**

```bash
git add migu/skill/cli.py migu/cli.py tests/test_skill.py
git commit -m "feat: skill CLI commands with install/uninstall/reinstall/list"
```

---

### Task 3: Fix migu init Full Skill Copy

**Files:**
- Modify: `/Users/23mofang/Documents/knowledge-bases/migu/migu/init/creator.py` (fix `_create_skills_placeholder`)
- Modify: `/Users/23mofang/Documents/knowledge-bases/migu/tests/test_creator.py` (add test for actual skill copy)

- [ ] **Step 1: Write the failing test for full skill copy in init**

```python
# Add to tests/test_creator.py
from migu.init.creator import create_kb

def test_init_copies_actual_skills(tmp_path):
    """Verify migu init copies actual skills from bundle."""
    target = tmp_path / "test-kb"
    
    create_kb(str(target), "minimal")
    
    # Verify at least one skill was copied
    ingest_dir = target / ".agents" / "skills" / "kb-ingest"
    assert ingest_dir.exists(), "kb-ingest skill not copied"
    assert (ingest_dir / "SKILL.md").exists(), "SKILL.md not copied"

def test_init_copies_all_skills(tmp_path):
    """Verify all 6 skills are copied."""
    target = tmp_path / "test-kb"
    
    create_kb(str(target), "minimal")
    
    expected_skills = ["kb-ingest", "kb-compile", "kb-lint", "kb-query", "kb-archive", "kb-status"]
    for skill in expected_skills:
        skill_dir = target / ".agents" / "skills" / skill
        assert skill_dir.exists(), f"Skill '{skill}' not copied"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_creator.py -v`
Expected: FAIL (skills not actually copied - just placeholder)

- [ ] **Step 3: Fix create_kb to copy actual skills**

Replace `_create_skills_placeholder` with actual installation:

```python
# migu/init/creator.py - replace _create_skills_placeholder

def _create_skills(target_path: Path, skills: dict) -> None:
    """Install all skills from bundle to target directory."""
    from migu.skill.installer import install_skill
    from migu.skill.manager import load_skills_lock
    
    skills_dir = target_path / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    lock_data = {
        "rules": "minimal",  # Will be overridden by caller
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
    
    # Ensure rules field is correct
    lock_data["rules"] = "minimal"  # Will be set by caller
    save_skills_lock(target_path, lock_data)
```

Update `create_kb` to call `_create_skills` with the correct rules_name:

```python
# In create_kb, replace _create_skills_placeholder call:
# Old:
# _create_skills_placeholder(target_path, rules_name, skills)
# New:
_create_skills(target_path, skills, rules_name)
```

Update `_create_skills` signature:

```python
def _create_skills(target_path: Path, skills: dict, rules_name: str) -> None:
    ...
    lock_data["rules"] = rules_name
    ...
```

Add import:
```python
from migu.skill.manager import save_skills_lock
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_creator.py -v`
Expected: PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: ALL TESTS PASS

- [ ] **Step 6: Commit**

```bash
git add migu/init/creator.py tests/test_creator.py
git commit -m "feat: migu init now copies actual skills from bundle"
```

---

### Task 4: Manual Verification + Final Commit

- [ ] **Step 1: Manual end-to-end test**

Run: `uv run migu init /tmp/test-kb-phase2`
Run: `uv run migu skill list /tmp/test-kb-phase2`
Run: `uv run migu skill reinstall kb-ingest /tmp/test-kb-phase2` (should ask for confirmation if no changes)

Expected output:
- `init`: "Knowledge base created at: /tmp/test-kb-phase2"
- `list`: Shows 6 skills with ✓ status
- `reinstall`: Skill reinstalled message

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass

- [ ] **Step 3: Manual cleanup**

```bash
rm -rf /tmp/test-kb-phase2 /tmp/test-kb /tmp/test-migu-kb /tmp/test-migu-review-kb
```

- [ ] **Step 4: Final commit (if any changes needed)**
