# Problems.md Issues Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 13 issues from problems.md to make migu init and skills work correctly.

**Architecture:** Three-phase fix: Phase 1 (core infrastructure), Phase 2 (architecture cleanup), Phase 3 (minimal AGENTS.md refactor). Each phase produces testable results.

**Tech Stack:** Python 3.11+, uv, pytest, typer

**Related Spec:** docs/superpowers/specs/2026-04-23-problems-fix-design.md

---

## File Structure

### Phase 1 Files
- Create: `rules/minimal/templates/index.md`
- Create: `rules/minimal/templates/log.md`
- Create: `rules/minimal/templates/raw-registry.md`
- Modify: `skills/minimal/kb-ingest/SKILL.md` (verify parameter docs)
- Modify: `skills/minimal/kb-compile/scripts/update_registry.py` (fix column matching)
- Modify: `skills/minimal/kb-lint/scripts/syntax.py` (fix kb_dir parameter)
- Modify: `skills/minimal/kb-status/scripts/read_registry.py` (fix separator parsing)

### Phase 2 Files
- Rename: `skills/minimal/kb-lint/scripts/syntax.py` → `_syntax.py`
- Rename: `skills/minimal/kb-lint/scripts/semantic.py` → `_semantic.py`
- Modify: `skills/minimal/kb-lint/scripts/lint.py` (import instead of subprocess)
- Modify: `skills/minimal/kb-compile/references/templates/*.md` (add frontmatter)
- Modify: `rules/minimal/AGENTS.md` (wikilink format)
- Modify: `rules/history/AGENTS.md` (wikilink format)

### Phase 3 Files
- Modify: `rules/minimal/structure.json` (add synthesis/)
- Rewrite: `rules/minimal/AGENTS.md` (minimal as generic base)
- Modify: `rules/history/AGENTS.md` (inherit minimal + domain definitions)
- Modify: `skills/minimal/kb-archive/SKILL.md` (clarify synthesis pages)

---

## Phase 1: Core Infrastructure

### Task 1: Create templates directory

**Files:**
- Create: `rules/minimal/templates/index.md`
- Create: `rules/minimal/templates/log.md`
- Create: `rules/minimal/templates/raw-registry.md`

- [ ] **Step 1: Create templates directory**

```bash
mkdir -p rules/minimal/templates
```

- [ ] **Step 2: Create index.md template**

Write to `rules/minimal/templates/index.md`:
```markdown
---
version: 1.0
---
# Wiki Index

<!-- 
entry format: - [[Page Name]] | brief summary | updated: YYYY-MM-DD
Page types: entity pages, concept pages, synthesis, summaries, comparisons, overview
-->

<!-- Sections added by kb-compile and kb-archive -->
```

- [ ] **Step 3: Create log.md template**

Write to `rules/minimal/templates/log.md`:
```markdown
---
version: 1.0
---
# Knowledge Base Log

<!-- 
entry format: ## [YYYY-MM-DD] operation | details
operation: ingest | compile | archive | lint
query and status not logged
-->

<!-- Log entries appended by kb-ingest/compile/archive/lint -->
```

- [ ] **Step 4: Create raw-registry.md template**

Write to `rules/minimal/templates/raw-registry.md`:
```markdown
---
version: 1.0
---
# Raw File Registry

<!-- 
entry format: | File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed |
-->

| File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed |
|------|------|------|-----------|---------|---------|-------------|
```

- [ ] **Step 5: Verify templates directory exists**

```bash
ls -la rules/minimal/templates/
```

Expected: three files exist (index.md, log.md, raw-registry.md)

- [ ] **Step 6: Commit**

```bash
git add rules/minimal/templates/
git commit -m "feat: add minimal templates (index, log, raw-registry)"
```

---

### Task 2: Fix update_registry.py column matching

**Files:**
- Modify: `skills/minimal/kb-compile/scripts/update_registry.py`

**Current issue:** Uses fixed column index (cells[5], cells[6]) - breaks if columns shift.

- [ ] **Step 1: Read current update_registry.py**

```bash
cat skills/minimal/kb-compile/scripts/update_registry.py
```

- [ ] **Step 2: Rewrite with column name matching**

Write to `skills/minimal/kb-compile/scripts/update_registry.py`:
```python
"""Update compilation status in raw-registry.md using column name matching."""

import sys
from pathlib import Path
from datetime import datetime


def main(kb_dir: str, file_path: str, status: str):
    registry = Path(kb_dir) / "raw-registry.md"
    if not registry.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = registry.read_text()
    lines = content.split("\n")
    today = datetime.now().strftime("%Y-%m-%d")
    
    header_line = None
    for i, line in enumerate(lines):
        if line.startswith("| 文件"):
            header_line = i
            break
    
    if header_line is None:
        print("ERROR: Header row not found", file=sys.stderr)
        sys.exit(1)
    
    header_cells = [c.strip() for c in lines[header_line].split("|")[1:-1]]
    
    try:
        compile_status_idx = header_cells.index("编译状态")
        last_processed_idx = header_cells.index("最近处理日期")
    except ValueError as e:
        print(f"ERROR: Column not found: {e}", file=sys.stderr)
        sys.exit(1)
    
    updated = False
    for i, line in enumerate(lines):
        if i <= header_line + 1:
            continue
        if file_path in line:
            cells = line.split("|")
            if len(cells) > max(compile_status_idx, last_processed_idx) + 1:
                cells[compile_status_idx + 1] = f" {status} "
                cells[last_processed_idx + 1] = f" {today} "
                lines[i] = "|".join(cells)
                updated = True
                break
    
    if updated:
        registry.write_text("\n".join(lines))
        print(f"Updated: {file_path} -> {status}")
    else:
        print(f"WARNING: Entry not found for {file_path}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: update_registry.py <kb_dir> <file_path> <status>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
```

- [ ] **Step 3: Test update_registry.py with sample registry**

Create test registry:
```bash
cat > /tmp/test-registry.md << 'EOF'
---
version: 1.0
---
# Raw File Registry

| File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/test.md|test]] | markdown | Test file | 已处理 | - | 未编译 | 2026-04-20 |
EOF
```

Run script:
```bash
python skills/minimal/kb-compile/scripts/update_registry.py /tmp raw/test.md 已编译
```

Expected output: "Updated: raw/test.md -> 已编译"

Verify:
```bash
cat /tmp/test-registry.md
```

Expected: "编译状态" column shows "已编译", date updated to today.

- [ ] **Step 4: Commit**

```bash
git add skills/minimal/kb-compile/scripts/update_registry.py
git commit -m "fix: update_registry.py uses column name matching"
```

---

### Task 3: Fix syntax.py kb_dir parameter

**Files:**
- Modify: `skills/minimal/kb-lint/scripts/syntax.py`

**Current issue:** Receives wiki_dir but may be called with kb_dir.

- [ ] **Step 1: Read current syntax.py**

```bash
cat skills/minimal/kb-lint/scripts/syntax.py
```

- [ ] **Step 2: Rewrite with kb_dir parameter**

Write to `skills/minimal/kb-lint/scripts/syntax.py`:
```python
"""Syntax check: markdown format, wikilink validity, source field."""

import sys
from pathlib import Path


def main(kb_dir: str):
    kb = Path(kb_dir)
    if not kb.exists():
        print(f"ERROR: Knowledge base directory not found", file=sys.stderr)
        sys.exit(1)
    
    wiki = kb / "wiki"
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    agents_dir = kb / ".agents"
    
    issues = []
    for md_file in sorted(wiki.rglob("*.md")):
        if agents_dir.exists() and str(md_file).startswith(str(agents_dir)):
            continue
        
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)

        if "## 来源" not in content and "- source:" not in content:
            issues.append(f"{rel}: missing '## 来源' section with source field")

        open_count = content.count("[[")
        close_count = content.count("]]")
        if open_count != close_count:
            issues.append(f"{rel}: unbalanced wikilinks ({open_count} [[ vs {close_count} ]])")

    if issues:
        print("SYNTAX ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("SYNTAX OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: syntax.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 3: Test syntax.py**

Create test KB structure:
```bash
mkdir -p /tmp/test-kb/wiki
cat > /tmp/test-kb/wiki/test.md << 'EOF'
# Test Page

## 来源
- source: [[raw/test.md]]
EOF
```

Run script:
```bash
python skills/minimal/kb-lint/scripts/syntax.py /tmp/test-kb
```

Expected output: "SYNTAX OK"

- [ ] **Step 4: Commit**

```bash
git add skills/minimal/kb-lint/scripts/syntax.py
git commit -m "fix: syntax.py uses kb_dir parameter, filters .agents/"
```

---

### Task 4: Fix read_registry.py separator parsing

**Files:**
- Modify: `skills/minimal/kb-status/scripts/read_registry.py`

**Current issue:** Only matches `|------|` separator, fails with `| -------- |`.

- [ ] **Step 1: Read current read_registry.py**

```bash
cat skills/minimal/kb-status/scripts/read_registry.py
```

- [ ] **Step 2: Rewrite with flexible separator matching**

Write to `skills/minimal/kb-status/scripts/read_registry.py`:
```python
"""Parse raw-registry.md and return statistics."""

import sys
from pathlib import Path


def main(kb_dir: str):
    registry_file = Path(kb_dir) / "raw-registry.md"
    if not registry_file.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = registry_file.read_text()
    lines = content.strip().split("\n")
    
    data_lines = []
    in_table = False
    for line in lines:
        if line.startswith("|") and ("---" in line or "------" in line):
            in_table = True
            continue
        if in_table and line.strip() and line.startswith("|"):
            data_lines.append(line)
    
    entries = []
    for line in data_lines:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) >= 7:
            entries.append({
                "file": cells[0],
                "type": cells[1],
                "summary": cells[2],
                "preprocess_status": cells[3],
                "product_path": cells[4],
                "compile_status": cells[5],
                "last_processed": cells[6],
            })
    
    type_counts = {}
    status_counts = {"未处理": 0, "已处理": 0, "无需处理": 0}
    compile_counts = {"未编译": 0, "已编译": 0, "部分编译": 0, "已引用": 0, "": 0}
    
    for entry in entries:
        t = entry["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
        ps = entry["preprocess_status"]
        if ps in status_counts:
            status_counts[ps] += 1
        cs = entry["compile_status"]
        if cs in compile_counts:
            compile_counts[cs] += 1
    
    pending_ingest = status_counts["未处理"]
    pending_compile = compile_counts["未编译"] + compile_counts["部分编译"]
    
    print(f"total:{len(entries)}")
    print(f"types:{','.join(f'{k}:{v}' for k, v in type_counts.items())}")
    print(f"pending_ingest:{pending_ingest}")
    print(f"pending_compile:{pending_compile}")
    for entry in entries:
        if entry["preprocess_status"] == "未处理" or entry["compile_status"] in ("未编译", "部分编译"):
            print(f"pending:{entry['file']}|{entry['preprocess_status']}|{entry['compile_status']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_registry.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 3: Test read_registry.py with both separator formats**

Test with `|------|` format:
```bash
cat > /tmp/test-registry1.md << 'EOF'
| File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/test.md|test]] | markdown | Test | 已处理 | - | 未编译 | 2026-04-20 |
EOF
mkdir -p /tmp/test-kb1
mv /tmp/test-registry1.md /tmp/test-kb1/raw-registry.md
python skills/minimal/kb-status/scripts/read_registry.py /tmp/test-kb1
```

Expected output: "total:1"

Test with `| -------- |` format:
```bash
cat > /tmp/test-registry2.md << 'EOF'
| File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed |
| -------- | -------- | -------- | ----------- | --------- | --------- | ------------- |
| [[raw/test.md|test]] | markdown | Test | 已处理 | - | 未编译 | 2026-04-20 |
EOF
mkdir -p /tmp/test-kb2
mv /tmp/test-registry2.md /tmp/test-kb2/raw-registry.md
python skills/minimal/kb-status/scripts/read_registry.py /tmp/test-kb2
```

Expected output: "total:1"

- [ ] **Step 4: Commit**

```bash
git add skills/minimal/kb-status/scripts/read_registry.py
git commit -m "fix: read_registry.py handles both separator formats"
```

---

### Task 5: Verify kb-ingest SKILL.md parameter docs

**Files:**
- Check: `skills/minimal/kb-ingest/SKILL.md`

- [ ] **Step 1: Read kb-ingest SKILL.md**

```bash
cat skills/minimal/kb-ingest/SKILL.md
```

- [ ] **Step 2: Verify scan_raw.py parameter is documented**

Check that SKILL.md specifies `<kb_dir>` parameter for scan_raw.py.

If missing, update scripts usage table to include:
```
| scan_raw.py | Scan raw/ directory | Step 1 | <kb_dir> |
```

- [ ] **Step 3: Commit if modified**

```bash
git add skills/minimal/kb-ingest/SKILL.md
git commit -m "docs: clarify scan_raw.py kb_dir parameter"
```

---

### Task 6: Test Phase 1 with migu init

- [ ] **Step 1: Run migu init with minimal rules**

```bash
uv run migu init /tmp/test-minimal-kb --rules minimal
```

Expected: KB created with templates copied.

- [ ] **Step 2: Verify templates exist**

```bash
ls -la /tmp/test-minimal-kb/
```

Expected: index.md, log.md, raw-registry.md exist with frontmatter.

- [ ] **Step 3: Clean up test KB**

```bash
rm -rf /tmp/test-minimal-kb
```

- [ ] **Step 4: Phase 1 checkpoint commit**

```bash
git add -A
git commit -m "feat(phase1): core infrastructure fixes complete"
```

---

## Phase 2: Architecture Cleanup

### Task 7: Rename lint scripts to internal modules

**Files:**
- Rename: `skills/minimal/kb-lint/scripts/syntax.py` → `_syntax.py`
- Rename: `skills/minimal/kb-lint/scripts/semantic.py` → `_semantic.py`

- [ ] **Step 1: Rename syntax.py to _syntax.py**

```bash
git mv skills/minimal/kb-lint/scripts/syntax.py skills/minimal/kb-lint/scripts/_syntax.py
```

- [ ] **Step 2: Add internal module header to _syntax.py**

Add at top of file:
```python
"""Internal module - syntax check for wiki pages. Called by lint.py only."""
```

- [ ] **Step 3: Rename semantic.py to _semantic.py**

```bash
git mv skills/minimal/kb-lint/scripts/semantic.py skills/minimal/kb-lint/scripts/_semantic.py
```

- [ ] **Step 4: Add internal module header to _semantic.py**

Add at top of file:
```python
"""Internal module - semantic check for wiki pages. Called by lint.py only."""
```

---

### Task 8: Update lint.py to import internal modules

**Files:**
- Modify: `skills/minimal/kb-lint/scripts/lint.py`

- [ ] **Step 1: Read current lint.py**

```bash
cat skills/minimal/kb-lint/scripts/lint.py
```

- [ ] **Step 2: Rewrite lint.py with imports**

Write to `skills/minimal/kb-lint/scripts/lint.py`:
```python
"""Orchestrate lint checks by importing internal modules."""

import sys
from pathlib import Path
import importlib.util


def load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(kb_dir: str):
    scripts_dir = Path(__file__).parent
    kb = Path(kb_dir)
    
    if not kb.exists():
        print(f"ERROR: Knowledge base not found: {kb_dir}", file=sys.stderr)
        sys.exit(1)
    
    syntax_module = load_module(scripts_dir / "_syntax.py")
    semantic_module = load_module(scripts_dir / "_semantic.py")
    
    print("Running syntax check...")
    syntax_module.main(kb_dir)
    
    print("Running semantic check...")
    semantic_module.main(kb_dir)
    
    print("\nAll checks passed ✓")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: lint.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 3: Test lint.py**

```bash
mkdir -p /tmp/test-kb/wiki
cat > /tmp/test-kb/wiki/test.md << 'EOF'
---
type: entity
---
# Test

## 来源
- source: [[raw/test.md]]
EOF

python skills/minimal/kb-lint/scripts/lint.py /tmp/test-kb
```

Expected: "All checks passed ✓"

- [ ] **Step 4: Commit**

```bash
git add skills/minimal/kb-lint/scripts/
git commit -m "refactor: lint scripts as internal modules, lint.py imports them"
```

---

### Task 9: Add frontmatter to entity templates

**Files:**
- Modify: `skills/minimal/kb-compile/references/templates/person-template.md`
- Modify: `skills/minimal/kb-compile/references/templates/place-template.md`
- Modify: `skills/minimal/kb-compile/references/templates/event-template.md`
- Modify: `skills/history/kb-compile/references/templates/*.md` (similar)

- [ ] **Step 1: Check minimal templates**

```bash
ls skills/minimal/kb-compile/references/templates/
```

- [ ] **Step 2: Add frontmatter to person-template.md**

Prepend frontmatter:
```markdown
---
type: person
---

# <Entity Name>
...
```

- [ ] **Step 3: Add frontmatter to other templates**

Repeat for place-template.md, event-template.md:
```markdown
---
type: place
---
---
type: event
---
```

- [ ] **Step 4: Check history templates**

```bash
ls skills/history/kb-compile/references/templates/
```

Add frontmatter similarly.

- [ ] **Step 5: Commit**

```bash
git add skills/*/kb-compile/references/templates/*.md
git commit -m "feat: add frontmatter to entity templates (type field)"
```

---

### Task 10: Fix wikilink format in AGENTS.md

**Files:**
- Modify: `rules/minimal/AGENTS.md`
- Modify: `rules/history/AGENTS.md`

- [ ] **Step 1: Update minimal AGENTS.md wikilink section**

Replace wikilink example with code block format:
```markdown
## Reference Format

Use Obsidian wikilinks:
```
[[PageName]]
```

For file references:
```
[[raw/<your-path>\|<display-name>]]
```
```

- [ ] **Step 2: Update history AGENTS.md similarly**

- [ ] **Step 3: Commit**

```bash
git add rules/*/AGENTS.md
git commit -m "fix: wikilink examples use code blocks to prevent parsing"
```

---

### Task 11: Phase 2 checkpoint

- [ ] **Step 1: Test lint with updated scripts**

```bash
mkdir -p /tmp/test-kb/wiki/entities
cat > /tmp/test-kb/wiki/entities/test.md << 'EOF'
---
type: person
---
# Test Person

## 来源
- source: [[raw/test.md]]
EOF

python skills/minimal/kb-lint/scripts/lint.py /tmp/test-kb
```

Expected: "All checks passed ✓"

- [ ] **Step 2: Commit Phase 2**

```bash
git add -A
git commit -m "feat(phase2): architecture cleanup complete"
```

---

## Phase 3: Minimal AGENTS.md Refactor

### Task 12: Update minimal structure.json

**Files:**
- Modify: `rules/minimal/structure.json`

- [ ] **Step 1: Read current structure.json**

```bash
cat rules/minimal/structure.json
```

- [ ] **Step 2: Update structure.json with synthesis**

Write to `rules/minimal/structure.json`:
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

- [ ] **Step 3: Commit**

```bash
git add rules/minimal/structure.json
git commit -m "feat: minimal structure includes synthesis directory"
```

---

### Task 13: Rewrite minimal AGENTS.md

**Files:**
- Rewrite: `rules/minimal/AGENTS.md`

- [ ] **Step 1: Write new minimal AGENTS.md**

Write to `rules/minimal/AGENTS.md`:
```markdown
---
version: "1.0"
---
# Knowledge Base Schema (Minimal)

Generic knowledge base schema per Karpathy LLM-WIKI pattern.
Domain-specific types defined in derived rules (history, legal, etc.).

## Directory Structure

- `raw/`: Raw source files (user managed, immutable)
- `raw/.extracted/`: Processed files from kb-ingest
- `wiki/`: LLM-generated structured documents
  - `entities/`: Entity pages (persons, places, organizations, etc.)
  - `concepts/`: Concept pages and summaries
  - `synthesis/`: Analysis pages (synthesis, comparisons, overview)
- `output/`: User-generated derivative documents

## Wiki Page Types

Per Karpathy LLM-WIKI, wiki contains:
- **Primary pages** (kb-compile): entity pages, concept pages, summaries
- **Analysis pages** (kb-archive): synthesis, comparisons, overview

Entity/concept types are domain-specific. Minimal provides base structure.
Analysis pages stored in wiki/synthesis/, distinguished by frontmatter type:
```
---
type: synthesis | comparison | overview
---
```

kb-archive writes analysis pages directly to wiki/synthesis/.

## Naming Conventions

- Wiki pages: Title case, no file extension in wikilinks. E.g., `[[EntityName]]`
- Raw files: Preserve original naming. E.g., `raw/path/to/file.md`
- Extracted files: Mirror raw structure under `raw/.extracted/`

## Reference Format

Use Obsidian wikilinks:
```
[[PageName]]
```

For file references:
```
[[raw/<your-path>\|<display-name>]]
```

Wiki pages must include source field:
```
## 来源
- source: [[raw/path/to/source.md]]
```

## Operations

- kb-ingest: Scan raw/, preprocess, output to raw/.extracted/
- kb-compile: Read files, extract entities/concepts, generate wiki pages
- kb-lint: Check wiki syntax and semantics
- kb-query: Search wiki with optional raw backtracking
- kb-archive: Generate synthesis/comparison/overview, integrate into wiki
- kb-status: Show dashboard
```

- [ ] **Step 2: Commit**

```bash
git add rules/minimal/AGENTS.md
git commit -m "refactor: minimal AGENTS.md as generic base per Karpathy"
```

---

### Task 14: Update history AGENTS.md

**Files:**
- Modify: `rules/history/AGENTS.md`

- [ ] **Step 1: Read current history AGENTS.md**

```bash
cat rules/history/AGENTS.md
```

- [ ] **Step 2: Ensure history inherits minimal**

Verify history AGENTS.md:
- Inherits minimal structure (entities/concepts/synthesis)
- Adds history-specific entity types
- Keeps wikilink format from minimal

If missing, add entity types section:
```markdown
## Entity Types (History Domain)

- `person`: Historical figures
- `place`: Geographic locations
- `event`: Historical events
- `institution`: Organizations, dynasties

## Concept Types (History Domain)

- `dynasty`: Dynastic periods
- `policy`: Policies and reforms
- `culture`: Cultural phenomena
```

- [ ] **Step 3: Commit**

```bash
git add rules/history/AGENTS.md
git commit -m "docs: history AGENTS.md inherits minimal + domain types"
```

---

### Task 15: Update kb-archive SKILL.md

**Files:**
- Modify: `skills/minimal/kb-archive/SKILL.md`

- [ ] **Step 1: Read kb-archive SKILL.md**

```bash
cat skills/minimal/kb-archive/SKILL.md
```

- [ ] **Step 2: Add synthesis page clarification**

Update output section:
```markdown
## Output

Analysis pages written to wiki/synthesis/:
- synthesis: Comprehensive analysis (e.g., relation networks)
- comparison: Entity comparisons (e.g., figure comparisons)
- overview: Topic summaries

All use frontmatter type field to distinguish:
```
---
type: synthesis
---
```
```

- [ ] **Step 3: Commit**

```bash
git add skills/minimal/kb-archive/SKILL.md
git commit -m "docs: kb-archive SKILL.md clarifies synthesis page types"
```

---

### Task 16: Final verification

- [ ] **Step 1: Run migu init minimal**

```bash
uv run migu init /tmp/final-test-minimal --rules minimal
```

Expected: KB created with correct structure.

- [ ] **Step 2: Verify directory structure**

```bash
ls -la /tmp/final-test-minimal/wiki/
```

Expected: entities/, concepts/, synthesis/ directories exist.

- [ ] **Step 3: Verify AGENTS.md**

```bash
cat /tmp/final-test-minimal/AGENTS.md | head -30
```

Expected: Generic minimal schema, no history-specific types.

- [ ] **Step 4: Run migu init history**

```bash
uv run migu init /tmp/final-test-history --rules history
```

Expected: KB created with history structure.

- [ ] **Step 5: Verify history AGENTS.md**

```bash
cat /tmp/final-test-history/AGENTS.md | grep -A 5 "Entity Types"
```

Expected: History-specific entity types defined.

- [ ] **Step 6: Clean up**

```bash
rm -rf /tmp/final-test-minimal /tmp/final-test-history
```

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat(phase3): minimal AGENTS.md refactor complete"
```

---

## Self-Review Checklist

After completing all tasks, verify:

1. **Spec coverage**: All 13 issues from problems.md addressed?
2. **Placeholder scan**: No TBD/TODO in implementation?
3. **Type consistency**: frontmatter type field used consistently?
4. **Test results**: All scripts tested with expected output?