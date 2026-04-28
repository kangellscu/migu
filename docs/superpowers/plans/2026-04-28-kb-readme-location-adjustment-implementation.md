# kb-README.md 位置调整实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move kb-README.md from templates/ to rules/ root directory and update copying logic.

**Architecture:** kb-README.md becomes a standalone user-customizable file (like AGENTS.md), copied separately from templates/ with same inheritance logic.

**Tech Stack:** Python 3.11+, pytest, git mv

---

## File Structure

**Files to modify:**
- `migu/init/creator.py` - Update copying logic (remove templates kb-README.md handling, add standalone copying)

**Files to move:**
- `rules/minimal/templates/kb-README.md` → `rules/minimal/kb-README.md` - Git move to preserve history

**Files to update:**
- `tests/test_templates.py` - Add test for kb-README.md standalone copying

---

## Task 1: Move kb-README.md file

**Files:**
- Move: `rules/minimal/templates/kb-README.md` → `rules/minimal/kb-README.md`

- [ ] **Step 1: Use git mv to move file (preserve history)**

```bash
git mv rules/minimal/templates/kb-README.md rules/minimal/kb-README.md
```

- [ ] **Step 2: Verify file moved**

```bash
ls rules/minimal/kb-README.md
ls rules/minimal/templates/kb-README.md 2>/dev/null || echo "File no longer in templates/"
```

Expected: kb-README.md exists in rules/minimal/, not in templates/

- [ ] **Step 3: Commit file move**

```bash
git add rules/minimal/kb-README.md
git commit -m "refactor: move kb-README.md from templates/ to rules/ root directory"
```

---

## Task 2: Update creator.py copying logic

**Files:**
- Modify: `migu/init/creator.py`

- [ ] **Step 1: Remove kb-README.md handling from templates loop (Line 173-174)**

Current code (Line 163-177):
```python
# Copy each template file
for filename in template_files:
    # Resolve template with inheritance
    template_source = _resolve_template_file(filename, rules_name)
    template_content = template_source.read_text()
    
    # Special handling for index.md: add dynamic sections
    if filename == "index.md":
        sections_content = _generate_index_sections(structure)
        template_content = template_content + sections_content
    
    # Rename kb-README.md to README.md
    target_filename = "README.md" if filename == "kb-README.md" else filename
    
    # Write to knowledge base root
    (target_path / target_filename).write_text(template_content)
```

Replace with:
```python
# Copy each template file
for filename in template_files:
    # Resolve template with inheritance
    template_source = _resolve_template_file(filename, rules_name)
    template_content = template_source.read_text()
    
    # Special handling for index.md: add dynamic sections
    if filename == "index.md":
        sections_content = _generate_index_sections(structure)
        template_content = template_content + sections_content
    
    # Write to knowledge base root
    (target_path / filename).write_text(template_content)
```

- [ ] **Step 2: Add kb-README.md standalone copying (after AGENTS.md, Line 179-185)**

Add after Line 185 (after AGENTS.md copying):
```python
# Copy kb-README.md (not in templates/, standalone user file)
kb_readme_source = rules_dir / "kb-README.md"
if not kb_readme_source.exists():
    minimal_dir = resolve_rules("minimal")
    kb_readme_source = minimal_dir / "kb-README.md"
(target_path / "README.md").write_text(kb_readme_source.read_text())
```

- [ ] **Step 3: Run tests to verify changes**

```bash
uv run pytest tests/test_templates.py -v
```

Expected: All tests pass (templates tests still work because kb-README.md no longer in templates/)

- [ ] **Step 4: Run all tests**

```bash
uv run pytest
```

Expected: All 62 tests pass

- [ ] **Step 5: Commit creator.py changes**

```bash
git add migu/init/creator.py
git commit -m "fix: update kb-README.md copying logic (standalone from rules/ root)"
```

---

## Task 3: Update tests for kb-README.md standalone copying

**Files:**
- Modify: `tests/test_templates.py`

- [ ] **Step 1: Add test for kb-README.md standalone copying**

Add new test to `tests/test_templates.py`:
```python
def test_kb_readme_standalone_copying():
    """Test kb-README.md copied from rules/ root (not templates/)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Check README.md exists (copied from kb-README.md)
        assert (kb_path / "README.md").exists()
        
        # Check README.md content matches kb-README.md
        readme_content = (kb_path / "README.md").read_text()
        kb_readme_path = Path(__file__).parent.parent / "rules" / "minimal" / "kb-README.md"
        kb_readme_content = kb_readme_path.read_text()
        
        # README.md should have kb-README.md content (frontmatter + sections)
        assert kb_readme_content in readme_content
```

- [ ] **Step 2: Add test for kb-README.md inheritance**

Add new test to `tests/test_templates.py`:
```python
def test_kb_readme_inheritance():
    """Test kb-README.md inheritance (history inherits minimal)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-history"
        
        create_kb(str(kb_path), "history")
        
        # Check README.md exists (inherited from minimal kb-README.md)
        assert (kb_path / "README.md").exists()
        
        # Check README.md content matches minimal kb-README.md
        readme_content = (kb_path / "README.md").read_text()
        kb_readme_path = Path(__file__).parent.parent / "rules" / "minimal" / "kb-README.md"
        kb_readme_content = kb_readme_path.read_text()
        
        assert kb_readme_content in readme_content
```

- [ ] **Step 3: Run tests to verify**

```bash
uv run pytest tests/test_templates.py -v
```

Expected: All 6 tests pass (4 original + 2 new)

- [ ] **Step 4: Commit test updates**

```bash
git add tests/test_templates.py
git commit -m "test: add kb-README.md standalone copying and inheritance tests"
```

---

## Task 4: Verify complete workflow

**Files:**
- Test: Knowledge base creation

- [ ] **Step 1: Test minimal knowledge base**

```bash
uv run migu init test-minimal-kb --rules minimal
```

- [ ] **Step 2: Verify README.md created from kb-README.md**

```bash
ls test-minimal-kb/README.md
cat test-minimal-kb/README.md
```

Expected: README.md exists, content matches rules/minimal/kb-README.md

- [ ] **Step 3: Test history knowledge base**

```bash
uv run migu init test-history-kb --rules history
```

- [ ] **Step 4: Verify README.md inherited**

```bash
cat test-history-kb/README.md
```

Expected: README.md content matches minimal kb-README.md (history inherited)

- [ ] **Step 5: Clean up test directories**

```bash
rm -rf test-minimal-kb test-history-kb
```

- [ ] **Step 6: Run all tests**

```bash
uv run pytest
```

Expected: All tests pass

---

## Self-Review Checklist

After completing all tasks:

- [ ] kb-README.md moved to rules/minimal/ (not in templates/)
- [ ] creator.py updated (no templates kb-README.md handling, standalone copying added)
- [ ] Tests added for kb-README.md standalone copying and inheritance
- [ ] All tests pass
- [ ] migu init creates README.md from kb-README.md (rules/ root)

---

## Notes

**kb-README.md copying logic design:**
- Standalone copying (like AGENTS.md)
- Inheritance: rules_dir / "kb-README.md" → fallback to minimal_dir / "kb-README.md"
- Rename: kb-README.md → README.md (when copied to KB root)

**templates/ loop changes:**
- Remove kb-README.md handling (Line 173-174 removed)
- No longer checks for kb-README.md in templates/

**history inheritance:**
- history has no kb-README.md → inherits minimal kb-README.md
- Same pattern as AGENTS.md inheritance