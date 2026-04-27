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