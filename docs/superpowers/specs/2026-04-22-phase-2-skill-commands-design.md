---
title: Phase 2 - CLI Skill Commands + Full Skill Installation
created: 2026-04-22
type: spec
status: approved
version: 1.0
related_specs:
  - docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
  - docs/superpowers/specs/2026-04-22-phase-1-cli-init-design.md
---

# Phase 2 Design: CLI Skill Commands + Full Skill Installation

## Scope

**Goal:** Implement `migu skill install/uninstall/reinstall/list` commands and complete `migu init` skill installation logic.

**Deliverables:**
1. `migu skill list <target-dir>` - List installed skills with version status
2. `migu skill install <skill-name> <target-dir>` - Install a new skill
3. `migu skill uninstall <skill-name> <target-dir>` - Remove a skill
4. `migu skill reinstall <skill-name> <target-dir>` - Reinstall with change detection
5. Fix `migu init` step 5: full skill copy from `skills/<source>/<skill>` → `.agents/skills/<skill>`

**Out of scope (later phases):**
- `migu rules` command
- history rules implementation
- Skills implementation (Phase 3)

## Key Decisions

| Decision | Approach | Notes |
|----------|----------|-------|
| Skill copy | `shutil.copytree` with overwrite | Skills are programmatic files, safe to replace |
| Change detection (reinstall) | Compare file contents via hash | Simple but effective; alert user if changed |
| Error handling | Fail-fast with clear messages | Invalid target-dir, missing skills-lock, unknown skill |
| Typer group | Use `app.command()` with subcommands | typer's native subcommand pattern |

## File Structure

```
migu/skill/__init__.py              # New (empty)
migu/skill/cli.py                   # New (typer subcommand group)
migu/skill/manager.py               # New (skill management logic)
migu/skill/installer.py             # New (copy/remove operations)
tests/test_skill.py                 # New
migu/init/creator.py                # Modify (fix step 5)
tests/test_creator.py               # Add test for full skill copy
```

## Implementation Flow

### `migu skill list <target-dir>`
1. Validate target-dir has `.agents/skills-lock.json`
2. Read skills-lock.json
3. Compare each skill's version with bundled version in `skills/<source>/<skill>`
4. Output: name, source, version, status (✓ latest / ⚠ outdated)

### `migu skill install <skill-name> <target-dir>`
1. Validate target-dir has skills-lock.json
2. Check skill not already installed
3. Copy from `skills/minimal/<skill-name>` (default source)
4. Update skills-lock.json

### `migu skill uninstall <skill-name> <target-dir>`
1. Validate target-dir and skill is installed
2. Remove `.agents/skills/<skill-name>/`
3. Update skills-lock.json

### `migu skill reinstall <skill-name> <target-dir>`
1. Validate target-dir and skill is installed
2. Check for user changes (hash comparison)
3. If changed: warn and ask for confirmation
4. Copy latest from source, update skills-lock.json

## Verification

```bash
uv run pytest -v                      # All tests pass
uv run migu init /tmp/test-kb         # Creates KB with actual skills copied
uv run migu skill list /tmp/test-kb   # Shows 6 skills with ✓ latest
```
