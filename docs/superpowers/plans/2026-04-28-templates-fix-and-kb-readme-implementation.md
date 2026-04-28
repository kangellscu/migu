# templates 复制机制修复与知识库 README 模板实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix templates copying mechanism to match spec, and create knowledge base README template for users.

**Architecture:** Replace hardcoded templates in creator.py with file-based copying from rules/*/templates/, implement inheritance (fallback to minimal), and dynamically generate index.md sections from structure.json.

**Tech Stack:** Python 3.11+, pytest, pathlib

---

## File Structure

**Files to modify:**
- `migu/init/creator.py` - Replace `_create_template_files` with templates copying + inheritance + index.md dynamic generation
- `docs/cli-reference.md` - Update execution flow to match spec

**Files to create:**
- `rules/minimal/templates/kb-README.md` - Knowledge base README template (Chinese, ~120 lines)
- `tests/test_templates.py` - Test templates copying and inheritance

**Files to read (reference):**
- `migu/init/rules.py` - Use `resolve_rules()` for template path resolution
- `rules/minimal/structure.json` - Use wiki subdirectories for index.md sections
- `rules/minimal/templates/*.md` - Template files to copy

---

## Task 1: Write tests for templates copying mechanism

**Files:**
- Create: `tests/test_templates.py`

- [ ] **Step 1: Write test for templates copying from minimal**

```python
"""Tests for templates copying mechanism."""
import tempfile
from pathlib import Path

from migu.init.creator import create_kb


def test_templates_copying_from_minimal():
    """Test templates copied from minimal/templates/ to knowledge base root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Check templates copied
        assert (kb_path / "index.md").exists()
        assert (kb_path / "log.md").exists()
        assert (kb_path / "raw-registry.md").exists()
        assert (kb_path / "AGENTS.md").exists()
```

- [ ] **Step 2: Write test for templates inheritance (history fallback to minimal)**

```python
def test_templates_inheritance_history():
    """Test history inherits templates from minimal (history has no templates dir)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-history"
        
        create_kb(str(kb_path), "history")
        
        # Check templates inherited from minimal
        assert (kb_path / "index.md").exists()
        assert (kb_path / "log.md").exists()
        assert (kb_path / "raw-registry.md").exists()
```

- [ ] **Step 3: Write test for index.md dynamic generation**

```python
def test_index_md_dynamic_sections():
    """Test index.md sections generated from structure.json wiki directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Read index.md content
        index_content = (kb_path / "index.md").read_text()
        
        # Check sections match structure.json wiki directories
        assert "## entities" in index_content
        assert "## concepts" in index_content
        assert "## synthesis" in index_content
        
        # Check section format
        assert "<!-- entry: - [[Page Name]] | brief summary | updated: YYYY-MM-DD -->" in index_content
```

- [ ] **Step 4: Write test for frontmatter preservation**

```python
def test_templates_frontmatter_preserved():
    """Test templates frontmatter (version) preserved when copied."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Check frontmatter preserved
        index_content = (kb_path / "index.md").read_text()
        assert "---" in index_content
        assert "version:" in index_content
```

- [ ] **Step 5: Run tests to verify they fail**

Run: `uv run pytest tests/test_templates.py -v`

Expected: Tests fail because `_create_template_files` still uses hardcoded content

- [ ] **Step 6: Commit test file**

```bash
git add tests/test_templates.py
git commit -m "test: add templates copying and inheritance tests"
```

---

## Task 2: Implement templates copying mechanism

**Files:**
- Modify: `migu/init/creator.py`

- [ ] **Step 1: Add helper function to resolve template file with inheritance**

In `creator.py`, add after imports:

```python
def _resolve_template_file(filename: str, rules_name: str) -> Path:
    """Resolve template file with inheritance fallback.
    
    Args:
        filename: Template filename (e.g., 'index.md', 'kb-README.md')
        rules_name: Rules name (e.g., 'minimal', 'history')
        
    Returns:
        Path to template file
        
    Raises:
        ValueError: If template not found in rules or minimal
    """
    rules_dir = resolve_rules(rules_name)
    rules_template = rules_dir / "templates" / filename
    
    if rules_template.exists():
        return rules_template
    
    # Fallback to minimal
    minimal_dir = resolve_rules("minimal")
    minimal_template = minimal_dir / "templates" / filename
    
    if minimal_template.exists():
        return minimal_template
    
    raise ValueError(
        f"Template '{filename}' not found in {rules_name} or minimal templates"
    )
```

- [ ] **Step 2: Add helper function to generate index.md sections**

In `creator.py`, add after `_resolve_template_file`:

```python
def _generate_index_sections(structure: dict) -> str:
    """Generate index.md sections from structure.json wiki directories.
    
    Args:
        structure: Dictionary from structure.json
        
    Returns:
        Sections content string
    """
    wiki_dirs = structure.get("directories", {}).get("wiki", {})
    sections = []
    
    for section_name in wiki_dirs.keys():
        sections.append(f"\n## {section_name}")
        sections.append("<!-- entry: - [[Page Name]] | brief summary | updated: YYYY-MM-DD -->")
    
    return "\n".join(sections)
```

- [ ] **Step 3: Replace `_create_template_files` with templates copying logic**

Replace entire `_create_template_files` function (Line 92-153):

```python
def _create_template_files(target_path: Path, rules_name: str) -> None:
    """Create initial knowledge base files from templates.
    
    Copies templates from rules/*/templates/ to knowledge base root.
    Implements inheritance: fallback to minimal if rules has no templates.
    Dynamically generates index.md sections from structure.json.
    """
    # Load structure for index.md dynamic generation
    structure = load_structure(rules_name)
    
    # Get list of template files from minimal (base templates)
    minimal_dir = resolve_rules("minimal")
    minimal_templates_dir = minimal_dir / "templates"
    
    if not minimal_templates_dir.exists():
        raise ValueError("minimal templates directory not found")
    
    template_files = [f.name for f in minimal_templates_dir.iterdir() if f.is_file()]
    
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
    
    # Copy AGENTS.md (not in templates/, separate inheritance logic)
    rules_dir = resolve_rules(rules_name)
    agents_source = rules_dir / "AGENTS.md"
    if not agents_source.exists():
        minimal_dir = resolve_rules("minimal")
        agents_source = minimal_dir / "AGENTS.md"
    (target_path / "AGENTS.md").write_text(agents_source.read_text())
```

- [ ] **Step 4: Run tests to verify implementation**

Run: `uv run pytest tests/test_templates.py -v`

Expected: Tests pass

- [ ] **Step 5: Run all tests to verify no regression**

Run: `uv run pytest`

Expected: All tests pass (58 tests)

- [ ] **Step 6: Commit creator.py changes**

```bash
git add migu/init/creator.py
git commit -m "fix: implement templates copying with inheritance and index.md dynamic generation"
```

---

## Task 3: Create knowledge base README template

**Files:**
- Create: `rules/minimal/templates/kb-README.md`

- [ ] **Step 1: Create kb-README.md template file**

Create file at `rules/minimal/templates/kb-README.md`:

```markdown
---
version: 1.0
---
# 知识库使用指南

## 知识库是什么

本知识库基于三层架构：

| 层级 | 目录 | 说明 |
|------|------|------|
| **Raw sources** | `raw/` | 你添加的源文件，不可变 |
| **Wiki** | `wiki/` | LLM 生成的结构化文档，可累积 |
| **Schema** | `AGENTS.md` | 告诉 LLM 如何结构化 wiki |

核心理念：wiki 是**持久化可累积产物**——每次 compile 添加新内容，知识库逐渐丰富。

## 目录结构

```
.
├── raw/                # 源文件（你管理）
│   ├── .extracted/     # 预处理产物（自动生成）
│   └── ...             # 你的文件
├── wiki/               # 结构化文档（LLM 生成）
│   ├── entities/       # 实体页面
│   ├── concepts/       # 概念页面
│   └── synthesis/      # 分析页面
├── output/             # 衍生文档（你管理）
├── raw-registry.md     # 文件注册表（自动维护）
├── index.md            # 文档索引（自动维护）
├── log.md              # 操作日志（自动维护）
└── AGENTS.md           # 知识库 schema（可定制）
```

## 快速上手

**Step 1: 添加源文件**

```bash
# 将你的文件放入 raw/ 目录
cp ~/documents/史记-项羽本纪.md raw/
mkdir raw/史记
cp ~/documents/史记-高祖本纪.md raw/史记/
```

**Step 2: 预处理（kb-ingest）**

在知识库目录，触发 skill：
```
kb-ingest
```

Agent 会扫描 raw/，预处理文件，更新 raw-registry.md。

**Step 3: 提取内容（kb-compile）**

触发 skill：
```
kb-compile
```

Agent 会读取文件，提取实体/概念，生成 wiki 页面。

**Step 4: 查看状态**

触发 skill：
```
kb-status
```

查看知识库仪表盘。

## Skills 工作流程

| Skill | 作用 | 触发时机 |
|-------|------|---------|
| **kb-ingest** | 预处理 raw 文件 | 添加新文件后 |
| **kb-compile** | 提取实体/概念，生成 wiki | ingest 后 |
| **kb-lint** | 检查 wiki 语法/语义 | compile 后 |
| **kb-query** | 搜索 wiki，生成报告 | 需要查询时 |
| **kb-archive** | 生成分析页面，回写 wiki | query 后 |
| **kb-status** | 显示知识库状态 | 需要查看时 |

**典型工作流程**：
```
添加 raw 文件 → kb-ingest → kb-compile → kb-lint → kb-query → kb-archive
```

**Skills 使用方式**：Skills 是 agent 指令。在 Claude Code 或类似工具中，直接触发 skill 名称（如 "kb-compile"），agent 会加载指令并执行。

## 使用约束

**✓ 可以修改**：
- `raw/` - 添加、删除你的源文件
- `output/` - 创建衍生文档
- `AGENTS.md` - 定制知识库 schema

**✗ 不要修改**：
- `raw/.extracted/` - kb-ingest 自动维护
- `wiki/` - kb-compile 自动生成
- `raw-registry.md` - skills 自动更新
- `index.md` - skills 自动更新
- `log.md` - skills 自动追加

**违反约束**：可能导致 skills 功能异常。重新运行对应 skill 可恢复。

## 示例：完整流程

```bash
# 1. 添加 raw 文件
mkdir raw/史记
cp ~/documents/史记-项羽本纪.md raw/史记/
cp ~/documents/史记-高祖本纪.md raw/史记/

# 2. 在知识库目录，触发 skills（agent session 中）
kb-ingest      # 预处理
kb-compile     # 提取实体（项羽、刘邦、萧何等）
kb-lint        # 检查 wiki
kb-status      # 查看状态

# 3. 查询知识库
kb-query "刘邦的主要功绩有哪些？"

# 4. 生成分析页面
kb-archive     # 将 query 报告整合到 wiki
```
```

- [ ] **Step 2: Verify file created**

Run: `ls rules/minimal/templates/kb-README.md`

Expected: File exists

- [ ] **Step 3: Commit kb-README.md**

```bash
git add rules/minimal/templates/kb-README.md
git commit -m "docs: add knowledge base README template (kb-README.md)"
```

---

## Task 4: Test complete workflow

**Files:**
- Test: Knowledge base creation

- [ ] **Step 1: Test minimal knowledge base creation**

Run: `uv run migu init test-minimal-kb --rules minimal`

Expected: Knowledge base created with README.md

- [ ] **Step 2: Verify README.md copied**

Run: `ls test-minimal-kb/README.md`

Expected: File exists

- [ ] **Step 3: Verify index.md has dynamic sections**

Run: `cat test-minimal-kb/index.md`

Expected: Sections match structure.json (entities, concepts, synthesis)

- [ ] **Step 4: Test history knowledge base creation**

Run: `uv run migu init test-history-kb --rules history`

Expected: Knowledge base created with inherited templates

- [ ] **Step 5: Verify history inherited minimal templates**

Run: `cat test-history-kb/README.md`

Expected: README.md content matches minimal kb-README.md

- [ ] **Step 6: Clean up test directories**

Run: `rm -rf test-minimal-kb test-history-kb`

- [ ] **Step 7: Run all tests**

Run: `uv run pytest`

Expected: All tests pass

---

## Task 5: Update docs/cli-reference.md

**Files:**
- Modify: `docs/cli-reference.md`

- [ ] **Step 1: Update execution flow (Line 42-50)**

Replace Lines 42-50:

```markdown
### Execution Flow

1. Check if `<target-dir>` exists (error if exists)
2. Validate three-party consistency
3. Merge configuration (inherit minimal + override specified rules)
4. Create directory structure (from structure.json)
5. Install skills (from skills.json)
6. Create skills-lock.json
7. Copy template files (preserve frontmatter, dynamic index.md sections)
```

- [ ] **Step 2: Commit docs/cli-reference.md**

```bash
git add docs/cli-reference.md
git commit -m "docs: update cli-reference execution flow to match spec"
```

---

## Self-Review Checklist

After completing all tasks:

- [ ] All tests pass (uv run pytest)
- [ ] README.md copied to knowledge base root (migu init creates README.md)
- [ ] index.md sections dynamic (match structure.json)
- [ ] templates inheritance works (history inherits minimal)
- [ ] docs/cli-reference.md matches spec

---

## Notes

**Templates copying logic design:**
- List template files from minimal/templates/ (base templates)
- For each file, resolve with inheritance (fallback to minimal if rules has no templates dir)
- Special handling for index.md: append dynamic sections from structure.json
- Copy AGENTS.md separately (not in templates/, has its own inheritance logic)

**index.md dynamic generation:**
- Read structure.json wiki subdirectories
- Generate sections for each wiki subdirectory
- Append sections to template content (preserving frontmatter and header)

**kb-README.md inheritance:**
- history has no templates/ dir, inherits minimal/templates/kb-README.md
- minimal/templates/kb-README.md copied to knowledge base root as README.md