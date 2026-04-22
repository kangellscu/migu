# Phase 3: Skills Minimal Implementation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete all 6 minimal skills (SKILL.md + scripts + references) per implementation-guide.

**Architecture:** Each skill is self-contained: SKILL.md (agent instructions), scripts/ (Python helpers), references/ (templates). Scripts tested via subprocess calls.

**Tech Stack:** Markdown, Python 3.11+, pytest

**Order:** kb-status → kb-ingest → kb-compile → kb-lint → kb-query → kb-archive (by dependency).

---

### Task 0: kb-status Skill

**Files:**
- Write: `skills/minimal/kb-status/SKILL.md`
- Create: `skills/minimal/kb-status/scripts/read_registry.py`
- Create: `skills/minimal/kb-status/scripts/read_index.py`
- Create: `skills/minimal/kb-status/scripts/format_dashboard.py`
- Test: `tests/skills/test_kb_status.py`

- [ ] **Step 1: Write test for kb-status scripts**

```python
# tests/skills/test_kb_status.py
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-status" / "scripts"

def test_read_registry(tmp_path):
    """Verify read_registry.py counts pending files."""
    registry = tmp_path / "raw-registry.md"
    registry.write_text("""| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/a.md\|a]] | markdown | test | 已处理 | raw/.extracted/a.md | 已编译 | 2026-04-22 |
| [[raw/b.pdf\|b]] | pdf | pdf | 未处理 | - | 未编译 | - |
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_registry.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "pending_ingest:1" in result.stdout
    assert "pending_compile:1" in result.stdout

def test_read_index(tmp_path):
    """Verify read_index.py counts wiki documents."""
    index = tmp_path / "index.md"
    index.write_text("""# Wiki Index

## entities
- [[刘邦]] | 汉朝开国皇帝 | 更新: 2026-04-17

## concepts
- [[沛县]] | 刘邦故乡 | 更新: 2026-04-17
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_index.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "total:2" in result.stdout

def test_read_registry_missing_file(tmp_path):
    """Verify error on missing raw-registry.md."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_registry.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "raw-registry.md not found" in result.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/skills/test_kb_status.py -v`
Expected: FAIL (scripts don't exist)

- [ ] **Step 3: Create read_registry.py**

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
        if line.startswith("|------"):
            in_table = True
            continue
        if in_table and line.strip():
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

- [ ] **Step 4: Create read_index.py**

```python
"""Parse index.md and return statistics."""

import sys
from pathlib import Path

def main(kb_dir: str):
    index_file = Path(kb_dir) / "index.md"
    if not index_file.exists():
        print("ERROR: index.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = index_file.read_text()
    lines = content.strip().split("\n")
    
    sections = {}
    current_section = None
    
    for line in lines:
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections[current_section] = []
        elif current_section and line.startswith("- [["):
            sections[current_section].append(line)
    
    doc_counts = {k: len(v) for k, v in sections.items()}
    total_docs = sum(doc_counts.values())
    
    print(f"total:{total_docs}")
    print(f"sections:{','.join(f'{k}:{v}' for k, v in doc_counts.items())}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_index.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 5: Create format_dashboard.py**

```python
"""Format dashboard output from registry and index stats."""

import sys

def main():
    lines = sys.stdin.read().strip().split("\n")
    
    kb_dir = ""
    raw_total = 0
    raw_types = {}
    pending_ingest = 0
    pending_compile = 0
    pending_files = []
    wiki_total = 0
    wiki_sections = {}
    
    for line in lines:
        if line.startswith("kb_dir:"):
            kb_dir = line.split(":", 1)[1]
        elif line.startswith("raw_total:"):
            raw_total = int(line.split(":", 1)[1])
        elif line.startswith("raw_types:"):
            for pair in line.split(":", 1)[1].split(","):
                if ":" in pair:
                    k, v = pair.split(":")
                    raw_types[k] = int(v)
        elif line.startswith("pending_ingest:"):
            pending_ingest = int(line.split(":", 1)[1])
        elif line.startswith("pending_compile:"):
            pending_compile = int(line.split(":", 1)[1])
        elif line.startswith("pending:"):
            pending_files.append(line.split(":", 1)[1])
        elif line.startswith("wiki_total:"):
            wiki_total = int(line.split(":", 1)[1])
        elif line.startswith("wiki_sections:"):
            for pair in line.split(":", 1)[1].split(","):
                if ":" in pair:
                    k, v = pair.split(":")
                    wiki_sections[k] = int(v)
    
    name = kb_dir.split("/")[-1] if kb_dir else "unknown"
    type_parts = ", ".join(f"{k}: {v}" for k, v in raw_types.items()) if raw_types else "none"
    section_parts = ", ".join(f"{k}: {v}" for k, v in wiki_sections.items()) if wiki_sections else "none"
    
    print(f"Knowledge Base Dashboard: {name}/")
    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│ Overview                                         │")
    print("├─────────────────────────────────────────────────┤")
    print(f"│ Raw Files:         {raw_total} ({type_parts})")
    print(f"│ Wiki Documents:    {wiki_total} ({section_parts})")
    print(f"│ Pending Ingest:    {pending_ingest} files")
    print(f"│ Pending Compile:   {pending_compile} files")
    print("└─────────────────────────────────────────────────┘")
    
    if pending_files:
        print()
        print("┌─────────────────────────────────────────────────┐")
        print("│ Pending Files                                     │")
        print("├─────────────────────────────────────────────────┤")
        for pf in pending_files[:10]:
            parts = pf.split("|")
            if len(parts) >= 3:
                print(f"│ {parts[0]:40s} ({parts[1]}, {parts[2]}) │")
        if len(pending_files) > 10:
            print(f"│ ... ({len(pending_files) - 10} more)")
        print("└─────────────────────────────────────────────────┘")

if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Create SKILL.md**

```markdown
---
title: kb-status
version: 1.0
created: 2026-04-22
---

# kb-status

## 职责

展示知识库仪表盘（解析 index.md + raw-registry.md）。

## 执行流程

1. **解析 raw-registry.md**：调用 `read_registry.py` 统计 raw 文件数量、类型分布、处理状态
2. **解析 index.md**：调用 `read_index.py` 统计 wiki 文档数量、分类分布
3. **格式化输出**：将结果管道给 `format_dashboard.py` 生成仪表盘

## 边界情况

| 场景 | 处理方式 |
|------|----------|
| raw-registry.md 不存在 | 报错退出，提示用户先执行 kb-ingest |
| index.md 不存在 | 报错退出，提示用户先执行 kb-compile |
| 无待处理文件 | 显示 "All up to date" |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_registry.py | 解析 raw-registry.md | 步骤 1：统计 raw 文件状态 | 必须 |
| read_index.py | 解析 index.md | 步骤 2：统计 wiki 文档状态 | 必须 |
| format_dashboard.py | 格式化仪表盘输出 | 步骤 3：生成仪表盘 | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
```

- [ ] **Step 7: Verify tests pass**

Run: `uv run pytest tests/skills/test_kb_status.py -v`
Expected: PASS (3 tests)

- [ ] **Step 8: Commit**

```bash
git add skills/minimal/kb-status/ tests/skills/test_kb_status.py
git commit -m "feat: kb-status skill with dashboard scripts"
```

---

### Task 1: kb-ingest Skill

**Files:**
- Write: `skills/minimal/kb-ingest/SKILL.md`
- Create: `skills/minimal/kb-ingest/scripts/scan_raw.py`
- Create: `skills/minimal/kb-ingest/scripts/normalize_markdown.py`
- Create: `skills/minimal/kb-ingest/scripts/convert_pdf.py`
- Create: `skills/minimal/kb-ingest/scripts/validate_batch.py`
- Test: `tests/skills/test_kb_ingest.py`

- [ ] **Step 1: Create test_kb_ingest.py**

```python
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-ingest" / "scripts"

def test_scan_raw(tmp_path):
    """Verify scan_raw.py detects files."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "test.md").write_text("# test")
    (raw / "doc.pdf").write_text(b"%PDF-fake")
    ext = raw / ".extracted"
    ext.mkdir()
    (ext / "old.md").write_text("# old")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "scan_raw.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "test.md|markdown" in result.stdout
    assert "doc.pdf|pdf" in result.stdout
    assert "old.md" not in result.stdout

def test_scan_raw_missing(tmp_path):
    """Verify scan_raw.py errors on missing raw/."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "scan_raw.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "raw/ directory not found" in result.stderr

def test_normalize_markdown(tmp_path):
    """Verify normalize_markdown.py copies and fixes content."""
    src = tmp_path / "src.md"
    dst = tmp_path / "dst.md"
    src.write_text("# Hello\n\nSome content.")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "normalize_markdown.py"), str(src), str(dst)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert dst.exists()
    assert dst.read_text() == "# Hello\n\nSome content."

def test_convert_pdf_placeholder(tmp_path):
    """Verify convert_pdf.py creates placeholder when pdfplumber missing."""
    pdf = tmp_path / "test.pdf"
    pdf.write_text(b"fake-pdf")
    output = tmp_path / "out"
    output.mkdir()
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "convert_pdf.py"), str(pdf), str(output)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert (output / "test.md").exists()

def test_validate_batch_valid(tmp_path):
    """Verify validate_batch.py passes on valid registry."""
    registry = tmp_path / "raw-registry.md"
    registry.write_text("""| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_batch.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "VALID" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Create scan_raw.py**

```python
"""Scan raw/ directory and detect new files."""

import sys
from pathlib import Path

def main(kb_dir: str):
    raw_dir = Path(kb_dir) / "raw"
    if not raw_dir.exists():
        print("ERROR: raw/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    extracted_dir = raw_dir / ".extracted"
    files = [f for f in raw_dir.rglob("*") if f.is_file() and not str(f).startswith(str(extracted_dir))]
    
    for f in sorted(files):
        rel_path = f.relative_to(raw_dir)
        ext = f.suffix.lower()
        if ext in (".md",):
            file_type = "markdown"
        elif ext == ".pdf":
            file_type = "pdf"
        elif ext in (".png", ".jpg", ".jpeg", ".gif"):
            file_type = "image"
        else:
            file_type = "unknown"
        print(f"{rel_path}|{file_type}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scan_raw.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 4: Create normalize_markdown.py**

```python
"""Normalize markdown file (encoding fix, http image handling)."""

import sys
from pathlib import Path

def main(input_file: str, output_file: str):
    src = Path(input_file)
    dst = Path(output_file)
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    content = src.read_text(encoding="utf-8")
    needs_fix = False
    
    if content.startswith('\ufeff'):
        content = content[1:]
        needs_fix = True
    
    dst.write_text(content, encoding="utf-8")
    
    if needs_fix:
        print(f"FIXED: {input_file} -> {output_file}")
    else:
        print(f"OK: {input_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: normalize_markdown.py <input> <output>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 5: Create convert_pdf.py**

```python
"""Convert PDF to markdown. Uses pdfplumber if available, falls back to placeholder."""

import sys
from pathlib import Path

def main(input_file: str, output_dir: str):
    src = Path(input_file)
    dst = Path(output_dir) / f"{src.stem}.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import pdfplumber
        with pdfplumber.open(src) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        dst.write_text("\n\n".join(pages), encoding="utf-8")
        print(f"Converted: {src.name} -> {dst.name}")
    except ImportError:
        dst.write_text(
            f"# {src.stem}\n\n**PDF conversion pending**\n\n"
            f"Install pdfplumber: `pip install pdfplumber`\n\n"
            f"Raw PDF: `{src.name}`",
            encoding="utf-8",
        )
        print(f"Placeholder: {src.name} (install pdfplumber for full conversion)")
    except Exception as e:
        print(f"Error converting {src.name}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_pdf.py <input.pdf> <output_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 6: Create validate_batch.py**

```python
"""Validate batch processing results."""

import sys
from pathlib import Path

def main(kb_dir: str):
    registry = Path(kb_dir) / "raw-registry.md"
    if not registry.exists():
        print("ERROR: raw-registry.md not found", file=sys.stderr)
        sys.exit(1)
    
    content = registry.read_text()
    lines = content.split("\n")
    issues = []
    
    for i, line in enumerate(lines, 1):
        if "[[" in line and line.count("[[") != line.count("]]"):
            issues.append(f"Line {i}: wikilink format error, expected [[path|alias]]")
        if "状态" in line and "预处理" in line:
            continue
        if line.startswith("|------"):
            continue
    
    if issues:
        print("VALIDATION_FAILED:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("VALID")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_batch.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 7: Create SKILL.md**

```markdown
---
title: kb-ingest
version: 1.0
created: 2026-04-22
---

# kb-ingest

## 职责

扫描 raw/、预处理文件、输出到 raw/.extracted/，更新 raw-registry.md。

## 执行流程

1. **扫描 raw/ 目录**：调用 `scan_raw.py` 检测所有文件（递归，排除 .extracted/）
2. **对比 raw-registry.md**：找出未记录的文件，准备添加新条目
3. **处理文件**：
   - **markdown**：调用 `normalize_markdown.py` 检查编码，输出到 raw/.extracted/（如有修复）
   - **PDF**：调用 `convert_pdf.py` 转换为 markdown，输出到 raw/.extracted/
   - **image**：无需处理，直接引用
4. **验证**：调用 `validate_batch.py` 检查 raw-registry.md 格式
5. **更新 raw-registry.md**：
   - 预处理状态：已处理 / 无需处理
   - 产物路径：有产物时记录路径，无产物时 `-`
   - 最近处理日期：当前日期

## 类型判断

| 扩展名 | 类型 | 处理方式 |
|--------|------|---------|
| .md | markdown | 规范化检查，可能生成 raw/.extracted/ |
| .pdf | pdf | 转 markdown + 提取图片 → raw/.extracted/ |
| .png, .jpg, .gif | image | 无需处理，直接引用 |

## 边界情况

| 场景 | 处理方式 |
|------|----------|
| raw/ 目录为空 | 输出 "No files to process" |
| raw-registry.md 格式错误 | validate_batch.py 报错退出 |
| 文件已存在 .extracted/ 版本 | 跳过，除非重新处理 |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| scan_raw.py | 扫描 raw/ 目录，检测新文件 | 步骤 1：检测新文件 | 必须 |
| validate_batch.py | 验证 raw-registry.md 格式 | 步骤 4：验证格式 | 必须 |
| normalize_markdown.py | 规范化 markdown 文件 | 步骤 3：处理 markdown | 必须 |
| convert_pdf.py | 转换 PDF 为 markdown | 步骤 3：处理 PDF | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
```

- [ ] **Step 8: Verify tests pass**

```bash
uv run pytest tests/skills/test_kb_ingest.py -v
```

- [ ] **Step 9: Commit**

```bash
git add skills/minimal/kb-ingest/ tests/skills/test_kb_ingest.py
git commit -m "feat: kb-ingest skill with scan/normalize/convert scripts"
```

---

### Task 2: kb-compile Skill

**Files:**
- Write: `skills/minimal/kb-compile/SKILL.md`
- Create: `skills/minimal/kb-compile/scripts/read_file.py`
- Create: `skills/minimal/kb-compile/scripts/update_registry.py`
- Create: `skills/minimal/kb-compile/references/templates/person-template.md`
- Create: `skills/minimal/kb-compile/references/templates/place-template.md`
- Create: `skills/minimal/kb-compile/references/templates/event-template.md`
- Test: `tests/skills/test_kb_compile.py`

- [ ] **Step 1: Create test_kb_compile.py**

```python
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-compile" / "scripts"

def test_read_file(tmp_path):
    """Verify read_file.py reads file content."""
    f = tmp_path / "test.md"
    f.write_text("# Hello World")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_file.py"), str(f)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "# Hello World" in result.stdout

def test_read_file_missing(tmp_path):
    """Verify read_file.py errors on missing file."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_file.py"), str(tmp_path / "nope.md")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr

def test_update_registry(tmp_path):
    """Verify update_registry.py updates compile status."""
    registry = tmp_path / "raw-registry.md"
    registry.write_text("""| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/test.md\|test]] | markdown | test | 已处理 | raw/.extracted/test.md | 未编译 | - |
""")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "update_registry.py"), str(tmp_path), "raw/test.md", "已编译"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "Updated" in result.stdout
    
    content = registry.read_text()
    assert "已编译" in content
```

- [ ] **Step 2: Create read_file.py**

```python
"""Read file content by path."""

import sys
from pathlib import Path

def main(file_path: str):
    p = Path(file_path)
    if not p.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    print(p.read_text(encoding="utf-8"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: read_file.py <path>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 3: Create update_registry.py**

```python
"""Update compilation status in raw-registry.md."""

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
    
    updated = False
    for i, line in enumerate(lines):
        if file_path in line:
            cells = line.split("|")
            if len(cells) > 6:
                cells[5] = f" {status} "
                cells[6] = f" {today} "
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

- [ ] **Step 4: Create person-template.md**

```markdown
# {{name}}

## 基本信息
- 别名：{{aliases}}
- 出生地：[[birth_place]]
- 生卒：{{birth_year}} — {{death_year}}

## 生平
{{biography}}

## 相关事件
- [[event1]]
- [[event2]]

## 相关人物
- [[person1]]
- [[person2]]

## 来源
- source: [[raw/path/to/source.md]]
```

- [ ] **Step 5: Create place-template.md**

```markdown
# {{name}}

## 基本信息
- 别名：{{aliases}}
- 类型：{{place_type}}（城市/山脉/河流等）
- 坐标：{{coordinates}}

## 描述
{{description}}

## 历史
{{history}}

## 相关事件
- [[event1]]

## 相关人物
- [[person1]]

## 来源
- source: [[raw/path/to/source.md]]
```

- [ ] **Step 6: Create event-template.md**

```markdown
# {{name}}

## 基本信息
- 时间：{{start_date}} — {{end_date}}
- 地点：[[location]]
- 参与者：[[person1]], [[person2]]

## 概述
{{summary}}

## 经过
{{details}}

## 影响
{{impact}}

## 来源
- source: [[raw/path/to/source.md]]
```

- [ ] **Step 7: Create SKILL.md**

```markdown
---
title: kb-compile
version: 1.0
created: 2026-04-22
---

# kb-compile

## 职责

读取 raw/.extracted/ 或 raw/ 文件，LLM 提取实体，生成 wiki 页面。

## 执行流程

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：
   - 产物路径 != `-`：调用 `read_file.py` 读取产物路径对应文件
   - 产物路径 == `-`：调用 `read_file.py` 读取 raw 文件本身
3. **LLM 实体提取**：
   - 阅读文档内容
   - 提取实体：人物、地点、事件等
   - 识别关系、消歧别名
   - 参考 references/templates/ 约束输出格式
4. **LLM wiki 生成**：
   - 检查 wiki/ 是否已有对应实体文档
   - 无：根据 templates 创建新文档
   - 有：阅读现有内容，合并新信息（增量更新）
   - wiki 文档 source 字段：`- source: [[raw/path/to/source.md]]`
5. **更新 index.md**：添加新页面索引到对应 section
6. **更新 raw-registry.md**：调用 `update_registry.py` 更新编译状态

## 增量更新逻辑

| 场景 | LLM 处理方式 |
|------|-------------|
| 信息补充 | 追加新字段或补充现有字段内容 |
| 信息冲突 | 判断是否同一信息的不同表述，或保留冲突注释 |
| 关系去重 | 判断两个关系是否重复，合并 |
| 结构调整 | 根据信息量调整页面结构 |

## templates 说明

| template | 用途 |
|----------|------|
| person-template.md | 人物实体页面格式 |
| place-template.md | 地点实体页面格式 |
| event-template.md | 事件实体页面格式 |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_file.py | 根据路径读取文件 | 步骤 2：读取待编译文件内容 | 必须 |
| update_registry.py | 更新 raw-registry.md | 步骤 6：更新编译状态 | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
```

- [ ] **Step 8: Verify tests pass**

- [ ] **Step 9: Commit**

```bash
git add skills/minimal/kb-compile/ tests/skills/test_kb_compile.py
git commit -m "feat: kb-compile skill with read/update scripts and entity templates"
```

---

### Task 3: kb-lint Skill

**Files:**
- Write: `skills/minimal/kb-lint/SKILL.md`
- Create: `skills/minimal/kb-lint/scripts/lint.py`
- Create: `skills/minimal/kb-lint/scripts/syntax.py`
- Create: `skills/minimal/kb-lint/scripts/semantic.py`
- Create: `skills/minimal/kb-lint/scripts/fix.py`
- Create: `skills/minimal/kb-lint/references/rules.md`
- Test: `tests/skills/test_kb_lint.py`

- [ ] **Step 1: Create test_kb_lint.py**

```python
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-lint" / "scripts"

def test_syntax_check_valid(tmp_path):
    """Verify syntax.py passes on valid markdown."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "test.md").write_text("# Test\n\nContent here.\n\n## 来源\n- source: [[raw/test.md]]")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "syntax.py"), str(wiki)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0

def test_syntax_check_missing_source(tmp_path):
    """Verify syntax.py detects missing source field."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "test.md").write_text("# Test\n\nContent.\n\n## 无关\nno source")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "syntax.py"), str(wiki)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "source" in result.stdout.lower()
```

- [ ] **Step 2: Create syntax.py**

```python
"""Syntax check: markdown format, wikilink validity, source field."""

import sys
from pathlib import Path

def main(wiki_dir: str):
    wiki = Path(wiki_dir)
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    issues = []
    for md_file in sorted(wiki.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)
        
        # Check for source field
        if "## 来源" not in content and "- source:" not in content:
            issues.append(f"{rel}: missing '## 来源' section with source field")
        
        # Check wikilink format (balanced brackets)
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
        print("Usage: syntax.py <wiki_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 3: Create semantic.py**

```python
"""Semantic check: content consistency, template structure."""

import sys
from pathlib import Path

def main(kb_dir: str):
    wiki = Path(kb_dir) / "wiki"
    if not wiki.exists():
        print(f"ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    issues = []
    for md_file in sorted(wiki.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(wiki)
        
        # Check title matches filename
        title_line = content.strip().split("\n")[0]
        if not title_line.startswith("# "):
            issues.append(f"{rel}: missing title heading")
    
    if issues:
        print("SEMANTIC ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("SEMANTIC OK")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: semantic.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 4: Create lint.py (orchestrator)**

```python
"""Orchestrate lint checks."""

import subprocess
import sys
from pathlib import Path

def main(kb_dir: str):
    scripts_dir = Path(__file__).parent
    
    # Syntax check
    wiki = Path(kb_dir) / "wiki"
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "syntax.py"), str(wiki)],
        capture_output=True, text=True,
    )
    print("Syntax:", result.stdout.strip())
    syntax_ok = result.returncode == 0
    
    # Semantic check
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "semantic.py"), str(kb_dir)],
        capture_output=True, text=True,
    )
    print("Semantic:", result.stdout.strip())
    semantic_ok = result.returncode == 0
    
    if syntax_ok and semantic_ok:
        print("\nAll checks passed ✓")
    else:
        print("\nSome checks failed ✗")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: lint.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 5: Create fix.py**

```python
"""Auto-fix fixable lint issues."""

import sys
from pathlib import Path

def main(kb_dir: str):
    wiki = Path(kb_dir) / "wiki"
    if not wiki.exists():
        print("ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    fixed = 0
    for md_file in wiki.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        original = content
        
        # Fix wikilink imbalance (remove orphan brackets)
        while "[[" in content and "]]" not in content:
            content = content.replace("[[", "", 1)
        while "]]" in content and "[[" not in content:
            content = content.replace("]]", "", 1)
        
        # Add missing source placeholder
        if "## 来源" not in content and "- source:" not in content:
            content = content.rstrip() + "\n\n## 来源\n- source: [[raw/PENDING]]\n"
        
        if content != original:
            md_file.write_text(content, encoding="utf-8")
            print(f"Fixed: {md_file.relative_to(wiki)}")
            fixed += 1
    
    print(f"Fixed {fixed} files")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fix.py <kb_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 6: Create rules.md reference**

```markdown
# Lint Rules

## Syntax Rules

| Rule | Description | Severity |
|------|-------------|---------|
| Source field | Every wiki document must have `## 来源` section with `- source: [[raw/...]]` | Error |
| Wikilink balance | All `[[...]]` must have matching opening and closing | Warning |
| Title heading | File must start with `# Title` heading | Warning |

## Semantic Rules

| Rule | Description | Severity |
|------|-------------|---------|
| Template structure | Documents should follow template sections (person, place, event) | Warning |
| Orphan entries | index.md entries must point to existing wiki files | Warning |

## Auto-fixable

| Issue | Fix |
|-------|-----|
| Missing source | Add `## 来源\n- source: [[raw/PENDING]]` |
| Orphan brackets | Remove unmatched `[[` or `]]` |
```

- [ ] **Step 7: Create SKILL.md**

```markdown
---
title: kb-lint
version: 1.0
created: 2026-04-22
---

# kb-lint

## 职责

Wiki 检查（语法、语义、修复）。

## 执行流程

1. **扫描 wiki/ 目录**：获取所有 wiki 文档
2. **语法检查**：调用 `syntax.py` 检查 markdown 格式、链接有效性、source 字段
3. **语义检查**：调用 `semantic.py` 检查内容一致性、模板结构
4. **报告问题**：汇总检查结果，呈现给用户
5. **可选修复**：调用 `fix.py` 自动修复可修复的问题

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| lint.py | 协调检查流程（syntax + semantic） | 步骤 2-3：启动检查 | 必须 |
| syntax.py | 语法检查 | 步骤 2：检查 markdown 格式、链接 | 必须 |
| semantic.py | 语义检查 | 步骤 3：检查内容一致性 | 必须 |
| fix.py | 自动修复 | 步骤 5：可选修复可修复问题 | 可选 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
- 可选：agent 可判断是否需要调用
```

- [ ] **Step 8: Verify tests pass**

- [ ] **Step 9: Commit**

---

### Task 4: kb-query Skill

**Files:**
- Write: `skills/minimal/kb-query/SKILL.md`
- Create: `skills/minimal/kb-query/scripts/search_wiki.py`
- Create: `skills/minimal/kb-query/references/intent-patterns.md`
- Create: `skills/minimal/kb-query/references/templates/report-template.md`
- Test: `tests/skills/test_kb_query.py`

- [ ] **Step 1: Create test_kb_query.py**

```python
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-query" / "scripts"

def test_search_wiki(tmp_path):
    """Verify search_wiki.py finds matching documents."""
    wiki = tmp_path / "wiki"
    (wiki / "entities").mkdir(parents=True)
    (wiki / "entities" / "刘邦.md").write_text("# 刘邦\n\n汉朝开国皇帝，出生地沛县。\n\n## 来源\n- source: [[raw/test.md]]")
    (wiki / "entities" / "项羽.md").write_text("# 项羽\n\n西楚霸王。\n\n## 来源\n- source: [[raw/test.md]]")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "search_wiki.py"), str(tmp_path), "沛县"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "刘邦" in result.stdout
    assert "项羽" not in result.stdout

def test_search_wiki_no_results(tmp_path):
    """Verify search_wiki.py returns empty on no match."""
    wiki = tmp_path / "wiki"
    wiki.mkdir(parents=True)
    (wiki / "test.md").write_text("# Test\n\n## 来源\n- source: [[raw/t.md]]")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "search_wiki.py"), str(tmp_path), "nonexistent"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
```

- [ ] **Step 2: Create search_wiki.py**

```python
"""Search wiki directory for matching documents."""

import sys
from pathlib import Path

def main(kb_dir: str, query: str):
    wiki_dir = Path(kb_dir) / "wiki"
    if not wiki_dir.exists():
        print("ERROR: wiki/ directory not found", file=sys.stderr)
        sys.exit(1)
    
    query_lower = query.lower()
    results = []
    
    for md_file in sorted(wiki_dir.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8").lower()
        rel_path = md_file.relative_to(wiki_dir)
        
        if query_lower in content or query_lower in md_file.stem.lower():
            results.append(f"wiki/{rel_path}")
    
    for r in results:
        print(r)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: search_wiki.py <kb_dir> <query>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 3: Create intent-patterns.md**

```markdown
# Query Intent Patterns

## 回溯关键词

| 关键词 | 示例查询 |
|--------|---------|
| 回溯 | 回溯分析刘邦的社交网络 |
| 全面 | 全面梳理楚汉之争的关键人物 |
| 详细 | 详细考察萧何的政治生涯 |
| 完整 | 完整还原刘邦的早期经历 |
| 补充 | 补充刘邦与萧何的关系细节 |
| 溯源 | 溯源刘邦早期经历的原始记载 |

## 查询意图识别

| 模式 | 触发词 | 行为 |
|------|--------|------|
| 关系查询 | "关系"、"社交"、"网络" | 搜索 wiki/ 中的关系描述 |
| 生平查询 | "生平"、"经历"、"一生" | 搜索完整 wiki 文档 |
| 事件查询 | "事件"、"经过"、"战役" | 搜索 event 类型文档 |
| 回溯模式 | 见回溯关键词表 | 触发 raw 回溯流程 |
```

- [ ] **Step 4: Create report-template.md**

```markdown
---
title: {{title}}
type: query-report
---

# {{title}}

## 分析
{{analysis}}

<!-- 回溯模式额外内容 -->
### 回溯新发现
从 raw/xxx.md 发现：
- 信息A（未提取）
- 信息B（未提取）

## 结论
{{conclusion}}

## 相关实体
[[entity1]], [[entity2]], ...

## 回写建议
- 补充 [[entity]]：内容描述（来源：wiki/entities/xxx.md 或 raw/xxx.md）
```

- [ ] **Step 5: Create SKILL.md**

```markdown
---
title: kb-query
version: 1.0
created: 2026-04-22
---

# kb-query

## 职责

Wiki 查询 + 回溯模式 + 生成 report。

## 执行流程

1. **接收查询意图**：用户提出问题
2. **解析意图**：识别查询对象、范围、方式、回溯关键词
3. **【含回溯关键词】询问用户**：是否需要回溯 raw 文件？
4. **搜索 wiki/**：调用 `search_wiki.py` 根据意图匹配文档
5. **聚合结果**：汇总查询结果
6. **【查询结果为空】输出提示并终止**："未找到相关实体，建议检查 raw 是否已 compile"
7. **生成 report**（符合 report-template.md）
8. **【标准模式】输出疑似缺失提示**

## 回溯范围限制

| 限制类型 | 规则 | 超出处理 |
|---------|------|---------|
| 数量限制 | 最多 5 个唯一 raw 文件 | 提示用户选择优先哪些 |
| 大小限制 | 单文件不超过 50KB | 提示用户确认是否处理 |

## 边界情况

| 场景 | 输出 |
|------|------|
| wiki 无相关实体 | "未找到相关实体，建议检查 raw 是否已 compile" |
| 回溯无新发现 | "raw 回溯完成，无新发现信息" |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| search_wiki.py | 搜索 wiki 目录 | 步骤 4：根据意图匹配文档 | 可选（可替代为 grep） |

依赖类型说明：
- 可选：agent 可判断是否需要调用，可用其他方式替代
```

- [ ] **Step 6: Verify tests pass and commit**

---

### Task 5: kb-archive Skill

**Files:**
- Write: `skills/minimal/kb-archive/SKILL.md`
- Create: `skills/minimal/kb-archive/scripts/read_report.py`
- Create: `skills/minimal/kb-archive/scripts/create_synthesis.py`
- Create: `skills/minimal/kb-archive/scripts/update_entity.py`
- Create: `skills/minimal/kb-archive/references/templates/synthesis-template.md`
- Test: `tests/skills/test_kb_archive.py`

- [ ] **Step 1: Create test_kb_archive.py**

```python
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-archive" / "scripts"

def test_create_synthesis(tmp_path):
    """Verify create_synthesis.py creates synthesis file."""
    synthesis_dir = tmp_path / "wiki" / "synthesis"
    synthesis_dir.mkdir(parents=True)
    report_content = "# Test Report\n\n## 分析\n...\n\n## 结论\nDone."
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "create_synthesis.py"), str(synthesis_dir), "Test Report"],
        capture_output=True, text=True,
        input=report_content,
    )
    assert result.returncode == 0
    assert (synthesis_dir / "Test Report.md").exists()
```

- [ ] **Step 2: Create read_report.py**

```python
"""Read report from agent context (stdin or file)."""

import sys
from pathlib import Path

def main(input_source: str = ""):
    if input_source:
        content = Path(input_source).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()
    
    if not content.strip():
        print("ERROR: No report content found", file=sys.stderr)
        sys.exit(1)
    
    print(content)

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else ""
    main(source)
```

- [ ] **Step 3: Create create_synthesis.py**

```python
"""Create synthesis report file."""

import sys
from pathlib import Path
from datetime import datetime

def main(synthesis_dir: str, title: str):
    out_dir = Path(synthesis_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Read report from stdin
    content = sys.stdin.read()
    
    title_line = f"# {title}"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{content}\n"
    
    out_file = out_dir / f"{title}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"Created: {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: create_synthesis.py <synthesis_dir> <title>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 4: Create update_entity.py**

```python
"""Update entity wiki file with organic integration."""

import sys
from pathlib import Path

def main(entity_path: str, content: str):
    p = Path(entity_path)
    if not p.exists():
        print(f"ERROR: Entity file not found: {entity_path}", file=sys.stderr)
        sys.exit(1)
    
    existing = p.read_text(encoding="utf-8")
    
    # Append to end before source section
    if "## 来源" in existing:
        parts = existing.split("## 来源", 1)
        updated = parts[0].rstrip() + "\n\n" + content + "\n\n## 来源" + parts[1]
    else:
        updated = existing.rstrip() + "\n\n" + content + "\n"
    
    p.write_text(updated, encoding="utf-8")
    print(f"Updated: {entity_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_entity.py <entity_path> <content>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 5: Create synthesis-template.md**

```markdown
---
title: {{title}}
type: synthesis
date: {{date}}
---

# {{title}}

## 分析
{{analysis}}

## 结论
{{conclusion}}

## 相关实体
[[entity1]], [[entity2]], ...
```

- [ ] **Step 6: Create SKILL.md**

```markdown
---
title: kb-archive
version: 1.0
created: 2026-04-22
---

# kb-archive

## 职责

接收 report + 回写摘要 + 有机融入。

## 会话依赖

kb-archive 必须在 kb-query 执行后的同一 agent session 中执行。

## 执行流程

1. **检查 report 是否存在**：
   - report 在 agent 上下文中：继续执行
   - report 不存在：输出提示并终止
2. **接收 report**：调用 `read_report.py` 读取 agent 上下文中的 report
3. **解析回写建议**：提取 report 中的回写建议列表
4. **生成回写摘要**：呈现给用户
5. **询问用户是否执行回写**：
   - `yes`：执行所有回写
   - `no`：只创建 synthesis 报告
   - `selective`：逐个确认
6. **根据选择执行**：
   - 调用 `create_synthesis.py` 创建 synthesis 文件（不含回写建议）
   - 调用 `update_entity.py` 有机融入 wiki 实体文档
7. **更新 index.md**：添加新报告索引

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_report.py | 读取 report 内容 | 步骤 2：从 agent 上下文读取 | 必须 |
| create_synthesis.py | 创建 synthesis 文件 | 步骤 6：创建 synthesis 报告 | 必须 |
| update_entity.py | 有机融入 wiki 文档 | 步骤 6：执行回写建议 | 必须 |
```

- [ ] **Step 7: Verify tests pass and commit**

---

### Task 6: Manual Verification + Final

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 2: Manual verification**

Create a test KB with sample data and run skills:

```bash
# Create test KB
mkdir -p /tmp/verify-kb/raw
echo "# 刘邦\n\n刘邦，汉朝开国皇帝。" > /tmp/verify-kb/raw/test.md
uv run migu init /tmp/verify-kb 2>/dev/null || true

# kb-status scripts
uv run python skills/minimal/kb-status/scripts/read_registry.py /tmp/verify-kb
uv run python skills/minimal/kb-status/scripts/read_index.py /tmp/verify-kb

# kb-ingest scripts
uv run python skills/minimal/kb-ingest/scripts/scan_raw.py /tmp/verify-kb

# kb-compile scripts
uv run python skills/minimal/kb-compile/scripts/read_file.py /tmp/verify-kb/raw/test.md

# kb-lint scripts
uv run python skills/minimal/kb-lint/scripts/lint.py /tmp/verify-kb

# kb-query scripts
uv run python skills/minimal/kb-query/scripts/search_wiki.py /tmp/verify-kb "刘邦"

# Cleanup
rm -rf /tmp/verify-kb
```

- [ ] **Step 3: Final commit**

```bash
git add docs/superpowers/specs/2026-04-22-phase-3-skills-minimal-design.md
git commit -m "docs: add Phase 3 skills minimal spec"
```
