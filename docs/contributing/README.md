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