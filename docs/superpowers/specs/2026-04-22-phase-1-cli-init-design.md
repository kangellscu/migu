---
title: Phase 1 - CLI Init + Rules Minimal
created: 2026-04-22
type: spec
status: approved
version: 1.0
related_specs:
  - docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
  - docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# Phase 1 Design: CLI Init + Rules Minimal

## Scope

**Goal:** `migu init my-kb` creates knowledge base skeleton, independently verifiable.

**Deliverables:**
1. `pyproject.toml` - Project configuration
2. `migu/` package - CLI base + `migu init` command
3. `rules/minimal/` - Base rules configuration
4. Basic tests

**Out of scope (later phases):**
- `migu skill` command (Phase 2)
- Full skills implementation (Phase 3)
- history rules (Phase 4)

## Key Decisions

| Decision | Approach | Notes |
|----------|----------|-------|
| `migu init` skills installation | Placeholder logic | Phase 1: create `.agents/skills/` dirs and generate `skills-lock.json`; full copy logic in Phase 2 |
| Three-party consistency | Basic check | Validate rules directory structure; skip kb-compile SKILL.md validation (skills not implemented yet) |
| Template files | Inline in code | Phase 1: template content hardcoded; migrate to `rules/minimal/templates/` later |
| Error handling | Fail-fast | Invalid args, existing dirs, missing configs → exit with error |

## File List

```
pyproject.toml                           # New
.python-version                          # New
migu/__init__.py                         # New
migu/__main__.py                         # New
migu/cli.py                              # New (typer app)
migu/init/__init__.py                    # New
migu/init/creator.py                     # New (KB creation logic)
migu/init/rules.py                       # New (rules processing)
rules/minimal/AGENTS.md                  # New
rules/minimal/structure.json             # New
rules/minimal/skills.json                # New
tests/test_init.py                       # New
tests/test_cli.py                        # New
```

## Implementation Flow (per spec §3.2)

1. Check `<target-dir>` exists → error if exists
2. Validate three-party consistency (basic)
3. Merge configuration (inherit minimal + override specified rules)
4. Create directory structure (from merged structure.json)
5. Install skills (placeholder): create dirs + skills-lock.json
6. Copy template files (with frontmatter preserved)

## Verification

```bash
uv sync
uv run pytest
uv run migu init my-kb
ls my-kb/  # Shows: AGENTS.md, index.md, log.md, raw-registry.md, raw/, wiki/, output/, .agents/
```
