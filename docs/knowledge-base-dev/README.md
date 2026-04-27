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

### skills.json Format

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
│   └── validate.py # Validation script
└── references/
    └── rules.md    # Validation rules
```

## Architecture Reference

See [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](../superpowers/specs/2026-04-17-migu-scaffold-design.md) for detailed architecture.

## Constraints Reference

See [constraints.md](constraints.md) for files you should not modify.