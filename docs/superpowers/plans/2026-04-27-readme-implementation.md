# README.md Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create README.md and supporting documentation files for migu project.

**Architecture:** README.md (project root) provides quick start and basic information for knowledge base users. Supporting documentation files in docs/ directory provide detailed information for different roles.

**Tech Stack:** Markdown documentation files, CommonMark format, relative path links.

---

## File Structure

**Files to create:**
- `README.md` - Project root, 8 sections (250-350 lines)
- `docs/cli-reference.md` - Detailed CLI commands documentation
- `docs/knowledge-base-dev/constraints.md` - Detailed constraints documentation
- `docs/contributing/README.md` - Scaffold developer guide
- `docs/knowledge-base-dev/README.md` - Knowledge base developer guide

**Implementation order:**
1. Create directory structure and README files (docs/contributing/README.md, docs/knowledge-base-dev/README.md)
2. Create high-priority link files (docs/cli-reference.md, docs/knowledge-base-dev/constraints.md)
3. Create README.md (links to existing files)
4. Verify and commit

---

### Task 1: Create docs/contributing directory structure

**Files:**
- Create: `docs/contributing/README.md`

- [ ] **Step 1: Create docs/contributing directory**

```bash
mkdir -p docs/contributing
```

- [ ] **Step 2: Create docs/contributing/README.md**

```markdown
# Contributing to migu

This guide is for scaffold developers who want to contribute to the migu project.

## Development Setup

### Prerequisites

- Python 3.11+
- uv (package manager)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/migu.git
cd migu

# Install dependencies
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_init.py -v
```

### Running CLI

```bash
# Run migu init
uv run migu init my-kb

# Run migu skill commands
uv run migu skill list my-kb
```

## Architecture

See [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) for detailed architecture.

## Project Structure

```
migu/
├── migu/           # CLI code (typer commands)
├── skills/         # Knowledge base operation skills (minimal/history)
├── rules/          # Knowledge base rule definitions (minimal/history)
├── tests/          # pytest tests
└── docs/           # Documentation
```

## Key Concepts

- **rules**: Define knowledge base schema (directory structure, naming conventions)
- **skills**: Agent instructions for operating knowledge bases (ingest, compile, lint, query, archive, status)

## Coding Guidelines

See [AGENTS.md](../../AGENTS.md) for project-level coding guidelines.

## Development Workflow

1. Read spec documents in `docs/superpowers/specs/`
2. Write implementation plan in `docs/superpowers/plans/`
3. Implement features following plan
4. Run tests to verify
5. Commit changes with clear messages

## Testing

All features should have corresponding tests in `tests/` directory.

## Documentation

- Specs: `docs/superpowers/specs/`
- Plans: `docs/superpowers/plans/`
- README: Project root `README.md`
```

- [ ] **Step 3: Verify file created**

```bash
ls docs/contributing/README.md
```

Expected: File exists

- [ ] **Step 4: Commit**

```bash
git add docs/contributing/README.md
git commit -m "docs: add scaffold developer guide (docs/contributing/README.md)"
```

---

### Task 2: Create docs/knowledge-base-dev directory structure

**Files:**
- Create: `docs/knowledge-base-dev/README.md`

- [ ] **Step 1: Create docs/knowledge-base-dev directory**

```bash
mkdir -p docs/knowledge-base-dev
```

- [ ] **Step 2: Create docs/knowledge-base-dev/README.md**

```markdown
# Knowledge Base Developer Guide

This guide is for developers who want to customize knowledge bases or create new rules and skills.

## For Knowledge Base Users

If you are using migu to create and manage knowledge bases, see [README.md](../../README.md) for quick start.

## Customizing Knowledge Bases

### Modifying AGENTS.md

AGENTS.md is copied from rules during `migu init`. You can modify it to customize your knowledge base schema.

**Constraints**: See [constraints.md](constraints.md) for files you should not modify.

### Adding Custom Raw Files

Raw files in `raw/` directory are user-managed. You can add any files you need.

### Using Skills

Skills are agent instructions. Trigger skill name in your agent session (e.g., "kb-compile").

See [README.md](../../README.md) for skill descriptions.

## Creating New Rules

### Rules Structure

Each rules directory contains:
- `AGENTS.md` - Knowledge base schema (required)
- `skills.json` - Skills selection (required)
- `structure.json` - Directory structure (optional, inherits minimal)
- `templates/*.md` - Initial file templates (optional, inherits minimal)

### Steps to Create New Rules

1. Create directory: `rules/<rules-name>/`
2. Create `AGENTS.md` - Define knowledge base schema
3. Create `skills.json` - Select needed skills
4. (Optional) Create `structure.json` - Define directory structure
5. (Optional) Create `templates/*.md` - Customize initial files
6. Test: `migu init test-kb --rules <rules-name>`

### Example: Creating legal rules

```
rules/legal/
├── AGENTS.md       # Legal knowledge base schema
├── skills.json     # Select skills for legal knowledge base
├── structure.json  # (Optional) Legal-specific directory structure
└── templates/
    └── index.md    # (Optional) Customized index format
```

### Skills.json Format

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
    }
  ]
}
```

**Note**: Each rules must provide `skills.json` independently (no inheritance).

## Creating New Skills

### Skills Structure

Each skill contains:
- `SKILL.md` - Agent instructions (required)
- `scripts/` - Helper scripts (optional)
- `references/` - Reference documents, templates (optional)

### Skill Naming

- Skill directory: `<skill-name>` (no type suffix)
- Location: `skills/<source>/<skill-name>/`

### Example: Creating kb-validate skill

```
skills/minimal/kb-validate/
├── SKILL.md        # Agent instructions for validation
├── scripts/
│   └ validate.py   # Validation script
└── references/
    └── rules.md    # Validation rules
```

## Architecture Reference

See [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) for detailed architecture.

## Constraints Reference

See [constraints.md](constraints.md) for files you should not modify.
```

- [ ] **Step 3: Verify file created**

```bash
ls docs/knowledge-base-dev/README.md
```

Expected: File exists

- [ ] **Step 4: Commit**

```bash
git add docs/knowledge-base-dev/README.md
git commit -m "docs: add knowledge base developer guide (docs/knowledge-base-dev/README.md)"
```

---

### Task 3: Create docs/cli-reference.md

**Files:**
- Create: `docs/cli-reference.md`

- [ ] **Step 1: Create docs/cli-reference.md**

```markdown
# CLI Reference

Detailed documentation for migu CLI commands.

## Global Options

```bash
migu --version        # Show version
migu --help           # Show help
```

---

## migu init

Create a new knowledge base with specified rules.

### Usage

```bash
migu init <target-dir> [--rules <rules-name>]
```

### Arguments

- `<target-dir>`: Knowledge base target directory (required)
- `--rules`: Rules name (minimal, history), default minimal

### Examples

```bash
# Create minimal knowledge base
migu init my-kb

# Create history knowledge base
migu init my-history-kb --rules history

# Create custom rules knowledge base
migu init my-legal-kb --rules legal
```

### Execution Flow

1. Check if `<target-dir>` exists (error if exists)
2. Validate rules configuration
3. Create directory structure (from structure.json)
4. Install skills (from skills.json)
5. Create skills-lock.json
6. Copy template files (index.md, log.md, raw-registry.md)
7. Copy AGENTS.md

### Error Handling

- **Directory exists**: Error, suggest other path
- **Rules not found**: Error, suggest valid rules names
- **Missing skills.json**: Error, rules must have skills.json

---

## migu skill

Manage skills in knowledge bases.

### migu skill list

List installed skills and versions.

#### Usage

```bash
migu skill list <target-dir>
```

#### Output

```
Installed skills:
kb-ingest   minimal  1.0  ✓ latest
kb-compile  history  1.0  ⚠ outdated (migu has 1.1)
kb-lint     minimal  1.0  ✓ latest
kb-query    minimal  1.0  ✓ latest
kb-archive  minimal  1.0  ✓ latest
kb-status   minimal  1.0  ✓ latest
```

#### Version Status

- `✓ latest`: Installed version matches migu bundled version
- `⚠ outdated`: Installed version older than migu bundled version

### migu skill install

Install skill to knowledge base.

#### Usage

```bash
migu skill install <skill-name> <target-dir> [--source <source>] [--version <version>]
```

#### Arguments

- `<skill-name>`: Skill name (kb-ingest, kb-compile, etc.)
- `<target-dir>`: Knowledge base directory
- `--source`: Skill source (minimal, history), default from skills-lock.json
- `--version`: Skill version, default latest

#### Examples

```bash
# Install skill from minimal source
migu skill install kb-lint my-kb --source minimal

# Install specific version
migu skill install kb-compile my-kb --source history --version 1.0
```

### migu skill uninstall

Remove skill from knowledge base.

#### Usage

```bash
migu skill uninstall <skill-name> <target-dir>
```

#### Examples

```bash
migu skill uninstall kb-lint my-kb
```

### migu skill reinstall

Reinstall skill (update or restore).

#### Usage

```bash
migu skill reinstall <skill-name> <target-dir>
```

#### Execution Flow

1. Read skill source from skills-lock.json
2. Compare installed skill with migu bundled version
3. If user modified, show diff and ask confirmation
4. Copy latest version
5. Update skills-lock.json

#### Examples

```bash
# Update outdated skill
migu skill reinstall kb-compile my-kb

# Restore skill after accidental modification
migu skill reinstall kb-ingest my-kb
```

---

## migu rules

Check rules configuration versions.

### migu rules list

List rules configuration files and version status.

#### Usage

```bash
migu rules list <target-dir>
```

#### Output

```
Rules: history
Configuration files:
AGENTS.md            1.0  ⚠ outdated (migu has 1.1)
templates/index.md   1.0  ✓ latest
templates/log.md     1.0  ✓ latest
```

#### Manual Update

Rules configuration files are user-managed. To update:
1. Compare with migu bundled rules (shown in output)
2. Manually merge changes
3. Update version in frontmatter

---

## Knowledge Base Skills

Skills are agent instructions, not CLI commands. Trigger skill name in your agent session.

### Available Skills

| Skill | Description | Trigger |
|-------|-------------|---------|
| `kb-ingest` | Preprocess raw files | "kb-ingest" in agent |
| `kb-compile` | Extract entities, generate wiki pages | "kb-compile" in agent |
| `kb-lint` | Check wiki consistency | "kb-lint" in agent |
| `kb-query` | Query wiki and generate reports | "kb-query" in agent |
| `kb-archive` | Synthesize reports, write back to wiki | "kb-archive" in agent |
| `kb-status` | Show knowledge base dashboard | "kb-status" in agent |

### Skill Execution

Skills are triggered in agent session (Claude Code, similar tools):
1. Navigate to knowledge base directory
2. Trigger skill name (e.g., "kb-compile")
3. Agent loads SKILL.md and executes instructions
4. Agent may call scripts in skill's `scripts/` directory

### Skill Dependencies

| Dependency Type | Example | Execution |
|----------------|---------|-----------|
| Data dependency | kb-ingest → kb-compile | User orchestrates execution order |
| Session dependency | kb-query report → kb-archive | Must be same agent session |

See [docs/superpowers/specs/2026-04-21-skills-implementation-guide.md](superpowers/specs/2026-04-21-skills-implementation-guide.md) for detailed skill workflows.
```

- [ ] **Step 2: Verify file created**

```bash
ls docs/cli-reference.md
```

Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add docs/cli-reference.md
git commit -m "docs: add detailed CLI reference (docs/cli-reference.md)"
```

---

### Task 4: Create docs/knowledge-base-dev/constraints.md

**Files:**
- Create: `docs/knowledge-base-dev/constraints.md`

- [ ] **Step 1: Create docs/knowledge-base-dev/constraints.md**

```markdown
# Knowledge Base Constraints

Files in knowledge bases have different management policies. This document explains what you can and cannot modify.

---

## Immutable Files (User Managed)

These files are managed by users. Skills never modify them.

### raw/ directory

**Policy**: User-managed, immutable by skills

**Contents**: Source files (markdown, PDF, images)

**Management**:
- Add files: User copies files to `raw/`
- Remove files: User deletes files from `raw/`
- Modify files: User edits files in `raw/`

**Note**: Skills read raw files but never write to `raw/`.

### output/ directory

**Policy**: User-managed

**Contents**: Derived documents (slides, Excel, exports)

**Management**:
- Create files: User creates derived documents
- Structure: User-defined subdirectories
- migu tracking: Not tracked by migu (not in raw-registry.md)

---

## Auto-Maintained Files (Do Not Edit)

These files are automatically maintained by skills. Do not edit them manually.

### raw/.extracted/ directory

**Policy**: kb-ingest auto-maintained

**Contents**: Preprocessed files (normalized markdown, PDF conversions)

**Management**:
- Created by: kb-ingest
- Updated by: kb-ingest (when raw files change)
- Deleted by: kb-ingest (when raw files removed)

**Violation**: Manual modification may cause kb-compile to use wrong data.

**Recovery**: Re-run kb-ingest to restore.

### raw-registry.md

**Policy**: kb-ingest/kb-compile auto-maintained

**Contents**: Raw file registry (tracking processing status)

**Management**:
- Updated by: kb-ingest (adds files, updates preprocessing status)
- Updated by: kb-compile (updates compilation status)
- Read by: kb-status (shows dashboard)

**Violation**: Manual modification may cause kb-status to show incorrect status.

**Recovery**: Re-run kb-ingest to restore registry.

### skills-lock.json

**Policy**: migu auto-maintained

**Contents**: Installed skills version records

**Management**:
- Created by: migu init
- Updated by: migu skill install/uninstall/reinstall
- Read by: migu skill list (version detection)

**Violation**: Manual modification may cause skill version detection to fail.

**Recovery**: Use migu skill reinstall to restore.

### index.md

**Policy**: kb-compile/kb-archive auto-maintained

**Contents**: Wiki document index

**Management**:
- Created by: migu init (initial template)
- Updated by: kb-compile (adds wiki page entries)
- Updated by: kb-archive (adds synthesis entries)

**Violation**: Manual modification may cause duplicate entries or broken wikilinks.

**Recovery**: 
- For wiki entries: Re-run kb-compile
- For synthesis entries: Re-run kb-archive

### log.md

**Policy**: Skills auto-maintained

**Contents**: Operation log

**Management**:
- Appended by: kb-ingest, kb-compile, kb-archive, kb-lint
- Not appended by: kb-query, kb-status

**Violation**: Manual modification may cause operation history confusion.

**Recovery**: Not recoverable (history is lost).

---

## Editable Files (User Customizable)

These files can be modified by users.

### AGENTS.md

**Policy**: User-customizable

**Contents**: Knowledge base schema

**Management**:
- Created by: migu init (copied from rules)
- Modified by: User (customize schema)
- Version: tracked in frontmatter

**Note**: AGENTS.md defines how wiki is structured. Modifying it affects kb-compile behavior.

### wiki/ directory

**Policy**: LLM-generated, user can verify

**Contents**: Wiki pages (entities, concepts, synthesis)

**Management**:
- Created by: kb-compile (LLM-driven)
- Modified by: kb-lint (fix issues)
- User role: Verify content accuracy

**Note**: Wiki pages are generated by LLM. User should verify content but not manually create wiki pages.

---

## Violation Effects and Recovery

| Violated File | Effect | Recovery |
|---------------|--------|----------|
| `raw/.extracted/` | kb-compile uses wrong data | Re-run kb-ingest |
| `raw-registry.md` | kb-status shows incorrect status | Re-run kb-ingest |
| `skills-lock.json` | skill version detection fails | migu skill reinstall |
| `index.md` | Duplicate/broken entries | Re-run kb-compile/kb-archive |
| `log.md` | History confusion | Not recoverable |

---

## Best Practices

1. **Add raw files**: Use `cp` or file management tools, not skills
2. **Check status**: Use kb-status before running skills
3. **Recovery**: Re-run corresponding skill to restore auto-maintained files
4. **Customize schema**: Modify AGENTS.md to customize knowledge base structure
5. **Verify wiki**: Check wiki content accuracy, fix with kb-lint if needed

---

## Related Documentation

- [README.md](../../README.md) - Quick start and basic constraints
- [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) - Detailed architecture
```

- [ ] **Step 2: Verify file created**

```bash
ls docs/knowledge-base-dev/constraints.md
```

Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add docs/knowledge-base-dev/constraints.md
git commit -m "docs: add detailed constraints documentation (docs/knowledge-base-dev/constraints.md)"
```

---

### Task 5: Create README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# migu

CLI scaffolder for LLM-WIKI knowledge bases.

## Installation

Install with uv or pipx:

```bash
# uv (recommended)
uv tool install migu

# pipx
pipx install migu
```

Verify installation:

```bash
migu --version
```

## Quick Start

Create a knowledge base and add raw files:

```bash
# Create knowledge base
migu init my-kb --rules minimal

# Add raw files (user managed)
cp ~/documents/史记-项羽本纪.md my-kb/raw/
mkdir my-kb/raw/史记
cp ~/documents/史记-高祖本纪.md my-kb/raw/史记/

# View installed skills
cd my-kb
migu skill list
```

Use skills to process your knowledge base:

```bash
# In knowledge base directory, trigger skills:
# kb-ingest   - Preprocess raw files
# kb-compile  - Extract entities, generate wiki pages
# kb-lint     - Check wiki consistency
# kb-query    - Query wiki and generate reports
# kb-archive  - Synthesize reports back to wiki
# kb-status   - Show knowledge base dashboard
```

**Note**: Skills are agent instructions. Trigger skill name in your agent session (e.g., "kb-compile" in Claude Code or similar tools).

## What is migu?

migu is a CLI scaffolder for creating LLM-WIKI knowledge bases. It provides:

- **Rules**: Define knowledge base schema (directory structure, naming conventions)
- **Skills**: Agent instructions for operating knowledge bases (ingest, compile, lint, query, archive, status)

**Key distinction**:

- migu is the scaffolder (produces tools), not the knowledge base (consumes tools)
- Knowledge bases are created with `migu init`, then managed by users

**Architecture** (Karpathy LLM-WIKI):

| Layer | migu Correspondence | Description |
|-------|--------------------|-------------|
| Raw sources | `raw/` directory | User-managed source files, immutable |
| Wiki | `wiki/` directory | LLM-generated structured documents |
| Schema | `AGENTS.md` + Skills | Instructions for LLM to structure wiki |

**Available rules**:

- `minimal`: Basic structure for general knowledge bases
- `history`: Customized for historical document knowledge bases

**See detailed architecture**: [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](docs/superpowers/specs/2026-04-17-migu-scaffold-design.md)

## Commands Overview

### migu CLI commands

| Command | Description |
|---------|-------------|
| `migu init <dir> [--rules <name>]` | Create knowledge base with specified rules |
| `migu skill list <dir>` | List installed skills and versions |
| `migu skill install <name> <dir>` | Install skill to knowledge base |
| `migu skill uninstall <name> <dir>` | Remove skill from knowledge base |
| `migu skill reinstall <name> <dir>` | Reinstall skill (update or restore) |
| `migu rules list <dir>` | Check rules configuration versions |
| `migu --version` | Show version |
| `migu --help` | Show help |

### Knowledge base skills

| Skill | Description |
|-------|-------------|
| `kb-ingest` | Preprocess raw files (scan, normalize, convert PDF) |
| `kb-compile` | Extract entities, generate wiki pages (LLM-driven) |
| `kb-lint` | Check wiki consistency (syntax, semantic, fix) |
| `kb-query` | Query wiki and generate reports (standard + backtrack mode) |
| `kb-archive` | Synthesize reports, write back to wiki |
| `kb-status` | Show knowledge base dashboard |

**See detailed commands**: [docs/cli-reference.md](docs/cli-reference.md)

## Constraints

Knowledge base users should follow these constraints:

**Immutable (user managed)**:
- `raw/` directory: Source files, never modified by skills
- `output/` directory: Derived documents, user-managed

**Auto-maintained (do not edit)**:
- `raw/.extracted/` directory: kb-ingest preprocessing outputs
- `raw-registry.md`: Raw file registry (kb-ingest/kb-compile update)
- `skills-lock.json`: Skill version records

**Editable (user customizable)**:
- `AGENTS.md`: Knowledge base schema (copied from rules, can modify)

**Note**: Violating constraints may cause migu skills to malfunction. Re-run corresponding skill to restore.

**See detailed constraints**: [docs/knowledge-base-dev/constraints.md](docs/knowledge-base-dev/constraints.md)

## Documentation

**For knowledge base users** (this README covers basics):
- [docs/knowledge-base-dev/](docs/knowledge-base-dev/) - Customizing knowledge bases
- [docs/cli-reference.md](docs/cli-reference.md) - Detailed CLI commands

**For scaffold developers**:
- [docs/contributing/](docs/contributing/) - Contributing to migu

**For knowledge base developers**:
- [docs/knowledge-base-dev/](docs/knowledge-base-dev/) - Creating rules and skills

**Technical specs**:
- [docs/superpowers/specs/](docs/superpowers/specs/) - Design documents

## Contributing

Interested in contributing to migu? See:

- [docs/contributing/](docs/contributing/) - Development guide, architecture, testing
```

- [ ] **Step 2: Verify file created**

```bash
ls README.md
```

Expected: File exists

- [ ] **Step 3: Verify file content**

```bash
wc -l README.md
```

Expected: 143-153 lines (as spec predicted)

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README.md for knowledge base users"
```

---

### Task 6: Verify all links

**Files:**
- Verify: All documentation files

- [ ] **Step 1: Verify README.md links**

Check all links in README.md point to existing files:
- [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](docs/superpowers/specs/2026-04-17-migu-scaffold-design.md) - Should exist
- [docs/cli-reference.md](docs/cli-reference.md) - Should exist (created in Task 3)
- [docs/knowledge-base-dev/constraints.md](docs/knowledge-base-dev/constraints.md) - Should exist (created in Task 4)
- [docs/contributing/](docs/contributing/) - Should exist (created in Task 1)
- [docs/knowledge-base-dev/](docs/knowledge-base-dev/) - Should exist (created in Task 2)

```bash
ls docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
ls docs/cli-reference.md
ls docs/knowledge-base-dev/constraints.md
ls docs/contributing/
ls docs/knowledge-base-dev/
```

Expected: All paths exist

- [ ] **Step 2: Verify docs/cli-reference.md links**

Check links in docs/cli-reference.md:
- [superpowers/specs/2026-04-21-skills-implementation-guide.md](superpowers/specs/2026-04-21-skills-implementation-guide.md) - Should exist

```bash
ls docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
```

Expected: File exists

- [ ] **Step 3: Verify docs/contributing/README.md links**

Check links in docs/contributing/README.md:
- [../superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) - Should exist
- [../../AGENTS.md](../../AGENTS.md) - Should exist

```bash
ls docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
ls AGENTS.md
```

Expected: All paths exist

- [ ] **Step 4: Verify docs/knowledge-base-dev/README.md links**

Check links in docs/knowledge-base-dev/README.md:
- [../../README.md](../../README.md) - Should exist
- [constraints.md](constraints.md) - Should exist
- [../superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) - Should exist

```bash
ls README.md
ls docs/knowledge-base-dev/constraints.md
ls docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
```

Expected: All paths exist

- [ ] **Step 5: Verify docs/knowledge-base-dev/constraints.md links**

Check links in docs/knowledge-base-dev/constraints.md:
- [../../README.md](../../README.md) - Should exist
- [../superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) - Should exist

```bash
ls README.md
ls docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
```

Expected: All paths exist

---

## Self-Review Checklist

After completing all tasks, verify:

- [ ] README.md exists and has 143-153 lines (250-350 lines with whitespace)
- [ ] All links in README.md point to existing files
- [ ] docs/cli-reference.md exists and covers all CLI commands
- [ ] docs/knowledge-base-dev/constraints.md exists and covers all constraints
- [ ] docs/contributing/README.md exists and covers scaffold developer guide
- [ ] docs/knowledge-base-dev/README.md exists and covers knowledge base developer guide
- [ ] All commits have clear messages