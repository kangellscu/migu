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
| `migu init <dir> [--rules <name>]` | Create knowledge base (default rules: minimal) |
| `migu skill list <dir>` | List installed skills and versions |
| `migu skill install <name> <dir>` | Install skill to knowledge base |
| `migu skill uninstall <name> <dir>` | Remove skill from knowledge base |
| `migu skill reinstall <name> <dir>` | Reinstall skill (update or restore) |
| `migu rules list <dir>` | Check rules configuration versions *(未实现)* |
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