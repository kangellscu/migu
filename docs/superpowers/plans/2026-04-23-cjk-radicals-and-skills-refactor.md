# CJK Radicals and Skills Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add CJK radicals conversion to normalize_markdown.py and refactor all skills to conform to skill-creator specification (frontmatter + output summary).

**Architecture:** Hardcode ~340 CJK radical mappings in normalize_markdown.py. Batch update 7 SKILL.md files with proper frontmatter (name + description) and add output summary section to each workflow.

**Tech Stack:** Python 3.11, pytest, typer

---

## File Structure

| File | Responsibility |
|------|---------------|
| `skills/minimal/kb-ingest/scripts/normalize_markdown.py` | CJK radicals conversion logic |
| `tests/skills/test_kb_ingest.py` | Test CJK radicals conversion |
| `skills/minimal/kb-status/SKILL.md` | kb-status skill specification |
| `skills/minimal/kb-ingest/SKILL.md` | kb-ingest skill specification |
| `skills/minimal/kb-compile/SKILL.md` | kb-compile skill specification |
| `skills/minimal/kb-lint/SKILL.md` | kb-lint skill specification |
| `skills/minimal/kb-query/SKILL.md` | kb-query skill specification |
| `skills/minimal/kb-archive/SKILL.md` | kb-archive skill specification |
| `skills/history/kb-compile/SKILL.md` | history kb-compile skill specification |

---

## Task 1: CJK Radicals Mapping

**Files:**
- Modify: `skills/minimal/kb-ingest/scripts/normalize_markdown.py`
- Test: `tests/skills/test_kb_ingest.py`

- [ ] **Step 1: Write the failing test**

Add test case to `tests/skills/test_kb_ingest.py`:

```python
def test_normalize_cjk_radical(tmp_path):
    """CJK radical converts to unified ideograph."""
    import subprocess
    from pathlib import Path
    
    kb_ingest_dir = Path(__file__).parent.parent / "skills" / "minimal" / "kb-ingest"
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    # Kangxi RADICAL ONE (U+2F00) + normal char
    content = "\u2f00\u4e00\u4e28"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        ["python", str(kb_ingest_dir / "scripts" / "normalize_markdown.py"),
         str(input_file), str(output_file)],
        capture_output=True,
        cwd=str(kb_ingest_dir),
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert "\u2f00" not in output
    assert output == "\u4e00\u4e00\u4e28"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/skills/test_kb_ingest.py::test_normalize_cjk_radical -v`
Expected: FAIL - `convert_cjk_radicals` function not called

- [ ] **Step 3: Add CJK radicals mapping dictionary**

Add to `skills/minimal/kb-ingest/scripts/normalize_markdown.py` (before `main()` function):

```python
_CJK_RADICALS_TO_UNICODE = {
    # CJK Radicals Supplement (2E80-2EEF) - ~112 mappings
    '\u2e81': '\u5382', '\u2e82': '\u4e5b', '\u2e83': '\u4e5a', '\u2e84': '\u4e59',
    '\u2e85': '\u4ebb', '\u2e86': '\u5182', '\u2e87': '\ud841\udd28',
    '\u2e88': '\u5200', '\u2e89': '\u5202', '\u2e8a': '\u535c',
    '\u2e8b': '\ud84b\udf3e', '\u2e8c': '\u5c0f', '\u2e8d': '\u5c0f',
    '\u2e8e': '\u5140', '\u2e8f': '\u5c23', '\u2e90': '\u5c22',
    '\u2e91': '\ud846\udf42', '\u2e92': '\u5df3', '\u2e93': '\u5e7a',
    '\u2e94': '\u5f51', '\u2e95': '\u5f50', '\u2e96': '\u5fc4',
    '\u2e97': '\u5fc3', '\u2e98': '\u624c', '\u2e99': '\u6535',
    '\u2e9b': '\u65e1', '\u2e9c': '\u65e5', '\u2e9d': '\u6708',
    '\u2e9e': '\u6b7a', '\u2e9f': '\u6bcd', '\u2ea0': '\u6c11',
    '\u2ea1': '\u6c35', '\u2ea2': '\u6c3a', '\u2ea3': '\u706c',
    '\u2ea4': '\u722b', '\u2ea5': '\u722b', '\u2ea6': '\u4e2c',
    '\u2ea7': '\u725b', '\u2ea8': '\u72ad', '\u2ea9': '\u738b',
    '\u2eaa': '\ud850\udf14', '\u2eab': '\u76ee', '\u2eac': '\u793a',
    '\u2ead': '\u793b', '\u2eae': '\ud856\uded7', '\u2eaf': '\u7cf9',
    '\u2eb0': '\u7e9f', '\u2eb1': '\u7f53', '\u2eb2': '\u7f52',
    '\u2eb3': '\ud84c\udfc1', '\u2eb4': '\u5197', '\u2eb5': '\ud858\ude6b',
    '\u2eb6': '\u7f8a', '\u2eb7': '\ud859\ude8c', '\u2eb8': '\ud859\ude8b',
    '\u2eb9': '\u8002', '\u2eba': '\u8080', '\u2ebb': '\u807f',
    '\u2ebc': '\u8089', '\u2ebd': '\ud85a\ude51', '\u2ebe': '\u8279',
    '\u2ebf': '\u8279', '\u2ec0': '\u8279', '\u2ec1': '\u864e',
    '\u2ec2': '\u8864', '\u2ec3': '\u8980', '\u2ec4': '\u897f',
    '\u2ec5': '\u89c1', '\u2ec6': '\u89d2', '\u2ec7': '\ud862\udf32',
    '\u2ec8': '\u8ba0', '\u2ec9': '\u8d1d', '\u2eca': '\ud87f\udfb7',
    '\u2ecb': '\u8f66', '\u2ecc': '\u8fb6', '\u2ecd': '\u8fb6',
    '\u2ece': '\u8fb6', '\u2ecf': '\u9091', '\u2ed0': '\u9485',
    '\u2ed1': '\u9577', '\u2ed2': '\u9578', '\u2ed3': '\u957f',
    '\u2ed4': '\u95e8', '\u2ed5': '\ud86e\ude0f', '\u2ed6': '\u961d',
    '\u2ed7': '\u96e8', '\u2ed8': '\u9752', '\u2ed9': '\u97e6',
    '\u2eda': '\u9875', '\u2edb': '\u98ce', '\u2edc': '\u98de',
    '\u2edd': '\u98df', '\u2ede': '\ud866\ude7f', '\u2edf': '\u98e0',
    '\u2ee0': '\u9963', '\u2ee1': '\ud861\ude10', '\u2ee2': '\u9a6c',
    '\u2ee3': '\u9aa8', '\u2ee4': '\u9b3c', '\u2ee5': '\u9c7c',
    '\u2ee6': '\u9e1f', '\u2ee7': '\u5364', '\u2ee8': '\u9ea6',
    '\u2ee9': '\u9ec4', '\u2eea': '\u9efe', '\u2eeb': '\u6589',
    '\u2eec': '\u9f50', '\u2eed': '\u6b6f', '\u2eee': '\u9f7f',
    '\u2eef': '\u7adc', '\u2ef0': '\u9f99', '\u2ef1': '\u9f9c',
    '\u2ef2': '\u4e80', '\u2ef3': '\u9f9f',
    
    # Kangxi Radicals (2F00-2FD5) - 214 mappings
    '\u2f00': '\u4e00', '\u2f01': '\u4e28', '\u2f02': '\u4e36',
    '\u2f03': '\u4e3f', '\u2f04': '\u4e59', '\u2f05': '\u4e85',
    '\u2f06': '\u4e8c', '\u2f07': '\u4ea0', '\u2f08': '\u4eba',
    '\u2f09': '\u513f', '\u2f0a': '\u5165', '\u2f0b': '\u516b',
    '\u2f0c': '\u5182', '\u2f0d': '\u5196', '\u2f0e': '\u51ab',
    '\u2f0f': '\u51e0', '\u2f10': '\u51f5', '\u2f11': '\u5200',
    '\u2f12': '\u529b', '\u2f13': '\u52f9', '\u2f14': '\u5315',
    '\u2f15': '\u531a', '\u2f16': '\u5338', '\u2f17': '\u5341',
    '\u2f18': '\u535c', '\u2f19': '\u5369', '\u2f1a': '\u5382',
    '\u2f1b': '\u53b6', '\u2f1c': '\u53c8', '\u2f1d': '\u53e3',
    '\u2f1e': '\u56d7', '\u2f1f': '\u571f', '\u2f20': '\u58eb',
    '\u2f21': '\u5902', '\u2f22': '\u590a', '\u2f23': '\u5915',
    '\u2f24': '\u5927', '\u2f25': '\u5973', '\u2f26': '\u5b50',
    '\u2f27': '\u5b80', '\u2f28': '\u5bf8', '\u2f29': '\u5c0f',
    '\u2f2a': '\u5c22', '\u2f2b': '\u5c38', '\u2f2c': '\u5c6e',
    '\u2f2d': '\u5c71', '\u2f2e': '\u5ddb', '\u2f2f': '\u5de5',
    '\u2f30': '\u5df1', '\u2f31': '\u5dfe', '\u2f32': '\u5e72',
    '\u2f33': '\u5e7a', '\u2f34': '\u5e7f', '\u2f35': '\u5ef4',
    '\u2f36': '\u5efe', '\u2f37': '\u5f0b', '\u2f38': '\u5f13',
    '\u2f39': '\u5f50', '\u2f3a': '\u5f61', '\u2f3b': '\u5f73',
    '\u2f3c': '\u5fc3', '\u2f3d': '\u6208', '\u2f3e': '\u6236',
    '\u2f3f': '\u624b', '\u2f40': '\u652f', '\u2f41': '\u6534',
    '\u2f42': '\u6587', '\u2f43': '\u6597', '\u2f44': '\u65a4',
    '\u2f45': '\u65b9', '\u2f46': '\u65e0', '\u2f47': '\u65e5',
    '\u2f48': '\u66f0', '\u2f49': '\u6708', '\u2f4a': '\u6728',
    '\u2f4b': '\u6b20', '\u2f4c': '\u6b62', '\u2f4d': '\u6b79',
    '\u2f4e': '\u6bb3', '\u2f4f': '\u6bcb', '\u2f50': '\u6bd4',
    '\u2f51': '\u6bdb', '\u2f52': '\u6c0f', '\u2f53': '\u6c14',
    '\u2f54': '\u6c34', '\u2f55': '\u706b', '\u2f56': '\u722a',
    '\u2f57': '\u7236', '\u2f58': '\u723b', '\u2f59': '\u723f',
    '\u2f5a': '\u7247', '\u2f5b': '\u7259', '\u2f5c': '\u725b',
    '\u2f5d': '\u72ac', '\u2f5e': '\u7384', '\u2f5f': '\u7389',
    '\u2f60': '\u74dc', '\u2f61': '\u74e6', '\u2f62': '\u7518',
    '\u2f63': '\u751f', '\u2f64': '\u7528', '\u2f65': '\u7530',
    '\u2f66': '\u758b', '\u2f67': '\u7592', '\u2f68': '\u7676',
    '\u2f69': '\u767d', '\u2f6a': '\u76ae', '\u2f6b': '\u76bf',
    '\u2f6c': '\u76ee', '\u2f6d': '\u77db', '\u2f6e': '\u77e2',
    '\u2f6f': '\u77f3', '\u2f70': '\u793a', '\u2f71': '\u79b8',
    '\u2f72': '\u79be', '\u2f73': '\u7a74', '\u2f74': '\u7acb',
    '\u2f75': '\u7af9', '\u2f76': '\u7c73', '\u2f77': '\u7cf8',
    '\u2f78': '\u7f36', '\u2f79': '\u7f51', '\u2f7a': '\u7f8a',
    '\u2f7b': '\u7fbd', '\u2f7c': '\u8001', '\u2f7d': '\u800c',
    '\u2f7e': '\u8012', '\u2f7f': '\u8033', '\u2f80': '\u807f',
    '\u2f81': '\u8089', '\u2f82': '\u81e3', '\u2f83': '\u81ea',
    '\u2f84': '\u81f3', '\u2f85': '\u81fc', '\u2f86': '\u820c',
    '\u2f87': '\u821b', '\u2f88': '\u821f', '\u2f89': '\u826e',
    '\u2f8a': '\u8272', '\u2f8b': '\u8278', '\u2f8c': '\u864d',
    '\u2f8d': '\u866b', '\u2f8e': '\u8840', '\u2f8f': '\u884c',
    '\u2f90': '\u8863', '\u2f91': '\u897e', '\u2f92': '\u898b',
    '\u2f93': '\u89d2', '\u2f94': '\u8a00', '\u2f95': '\u8c37',
    '\u2f96': '\u8c46', '\u2f97': '\u8c55', '\u2f98': '\u8c78',
    '\u2f99': '\u8c9d', '\u2f9a': '\u8d64', '\u2f9b': '\u8d70',
    '\u2f9c': '\u8db3', '\u2f9d': '\u8eab', '\u2f9e': '\u8eca',
    '\u2f9f': '\u8f9b', '\u2fa0': '\u8fb0', '\u2fa1': '\u8fb5',
    '\u2fa2': '\u9091', '\u2fa3': '\u9149', '\u2fa4': '\u91c6',
    '\u2fa5': '\u91cc', '\u2fa6': '\u91d1', '\u2fa7': '\u9577',
    '\u2fa8': '\u9580', '\u2fa9': '\u961c', '\u2faa': '\u96b6',
    '\u2fab': '\u96b9', '\u2fac': '\u96e8', '\u2fad': '\u9751',
    '\u2fae': '\u975e', '\u2faf': '\u9762', '\u2fb0': '\u9769',
    '\u2fb1': '\u97cb', '\u2fb2': '\u97ed', '\u2fb3': '\u97f3',
    '\u2fb4': '\u9801', '\u2fb5': '\u98a8', '\u2fb6': '\u98db',
    '\u2fb7': '\u98df', '\u2fb8': '\u9996', '\u2fb9': '\u9999',
    '\u2fba': '\u99ac', '\u2fbb': '\u9aa8', '\u2fbc': '\u9ad8',
    '\u2fbd': '\u9adf', '\u2fbe': '\u9b25', '\u2fbf': '\u9b2f',
    '\u2fc0': '\u9b32', '\u2fc1': '\u9b3c', '\u2fc2': '\u9b5a',
    '\u2fc3': '\u9ce5', '\u2fc4': '\u9e75', '\u2fc5': '\u9e7f',
    '\u2fc6': '\u9ea5', '\u2fc7': '\u9ebb', '\u2fc8': '\u9ec3',
    '\u2fc9': '\u9ecd', '\u2fca': '\u9ed1', '\u2fcb': '\u9ef9',
    '\u2fcc': '\u9efd', '\u2fcd': '\u9f0e', '\u2fce': '\u9f13',
    '\u2fcf': '\u9f20', '\u2fd0': '\u9f3b', '\u2fd1': '\u9f4a',
    '\u2fd2': '\u9f52', '\u2fd3': '\u9f8d', '\u2fd4': '\u9f9c',
    '\u2fd5': '\u9fa0',
    
    # CJK Strokes (31C6, 31CF-31E1) - ~14 mappings
    '\u31c6': '\ud840\udccc', '\u31cf': '\u4e40', '\u31d0': '\u4e00',
    '\u31d1': '\u4e28', '\u31d2': '\u4e3f', '\u31d3': '\u4e3f',
    '\u31d4': '\u4e36', '\u31d5': '\ud840\udccd', '\u31d6': '\u4e5b',
    '\u31d7': '\ud840\udcca', '\u31d8': '\ud840\udcce', '\u31d9': '\ud840\udf0c',
    '\u31da': '\u4e85', '\u31db': '\ud87f\udfe8', '\u31dc': '\ud840\udccb',
    '\u31dd': '\u4e40', '\u31de': '\ud840\udcd1', '\u31df': '\u4e5a',
    '\u31e0': '\u4e59', '\u31e1': '\ud840\udf0e',
}


def convert_cjk_radicals(text: str) -> str:
    """Convert CJK radicals and Kangxi radicals to equivalent unified ideographs."""
    return ''.join(_CJK_RADICALS_TO_UNICODE.get(c, c) for c in text)
```

- [ ] **Step 4: Integrate conversion into main()**

Modify `skills/minimal/kb-ingest/scripts/normalize_markdown.py` main() function:

```python
def main(input_file: str, output_file: str):
    src = Path(input_file)
    dst = Path(output_file)
    dst.parent.mkdir(parents=True, exist_ok=True)

    content = src.read_text(encoding="utf-8")
    content = convert_cjk_radicals(content)  # NEW: convert CJK radicals
    
    needs_fix = False

    if content.startswith('\ufeff'):
        content = content[1:]
        needs_fix = True

    dst.write_text(content, encoding="utf-8")

    if needs_fix:
        print(f"FIXED: {input_file} -> {output_file}")
    else:
        print(f"OK: {input_file}")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/skills/test_kb_ingest.py::test_normalize_cjk_radical -v`
Expected: PASS

- [ ] **Step 6: Add test for multiple CJK radicals**

Add to `tests/skills/test_kb_ingest.py`:

```python
def test_normalize_cjk_radical_multiple(tmp_path):
    """Multiple CJK radicals convert correctly."""
    import subprocess
    from pathlib import Path
    
    kb_ingest_dir = Path(__file__).parent.parent / "skills" / "minimal" / "kb-ingest"
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    # Mix of CJK Radicals Supplement + Kangxi + Strokes + normal chars
    content = "\u2e85\u2f08\u31d0\u4e00\u4eba"  # 亻 + 人 + 一 + 一 + 人
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        ["python", str(kb_ingest_dir / "scripts" / "normalize_markdown.py"),
         str(input_file), str(output_file)],
        capture_output=True,
        cwd=str(kb_ingest_dir),
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert "\u2e85" not in output
    assert "\u2f08" not in output
    assert "\u31d0" not in output
    assert output == "\u4ebb\u4eba\u4e00\u4e00\u4eba"
```

- [ ] **Step 7: Run multiple radicals test**

Run: `uv run pytest tests/skills/test_kb_ingest.py::test_normalize_cjk_radical_multiple -v`
Expected: PASS

- [ ] **Step 8: Add test for normal chars unchanged**

Add to `tests/skills/test_kb_ingest.py`:

```python
def test_normalize_preserves_normal_chars(tmp_path):
    """Normal Chinese characters are unchanged."""
    import subprocess
    from pathlib import Path
    
    kb_ingest_dir = Path(__file__).parent.parent / "skills" / "minimal" / "kb-ingest"
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    content = "刘邦项羽张良韩信"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        ["python", str(kb_ingest_dir / "scripts" / "normalize_markdown.py"),
         str(input_file), str(output_file)],
        capture_output=True,
        cwd=str(kb_ingest_dir),
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert output == content
```

- [ ] **Step 9: Run normal chars test**

Run: `uv run pytest tests/skills/test_kb_ingest.py::test_normalize_preserves_normal_chars -v`
Expected: PASS

- [ ] **Step 10: Run all kb_ingest tests**

Run: `uv run pytest tests/skills/test_kb_ingest.py -v`
Expected: All tests PASS (now 8 tests)

- [ ] **Step 11: Commit CJK radicals implementation**

```bash
git add skills/minimal/kb-ingest/scripts/normalize_markdown.py tests/skills/test_kb_ingest.py
git commit -m "feat(kb-ingest): add CJK radicals conversion (~340 mappings)"
```

---

## Task 2: Refactor kb-status SKILL.md

**Files:**
- Modify: `skills/minimal/kb-status/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/minimal/kb-status/SKILL.md`:

```yaml
---
name: kb-status
description: "Show knowledge base dashboard with file counts and processing status. Use when user asks to check KB status, see statistics, view dashboard, or wants overview of raw files and wiki pages."
version: 1.0
---
```

- [ ] **Step 2: Add output summary section**

Append to `skills/minimal/kb-status/SKILL.md` after the scripts section:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：状态：X 个 raw 文件（Y 待处理），Z 个 wiki 文档
2. **下一步提示**：可运行 kb-ingest 处理 raw 文件，或运行 kb-compile 开始编译

示例：
```
处理结果：状态：10 个 raw 文件（5 待处理），8 个 wiki 文档
下一步提示：可运行 kb-ingest 处理 raw 文件，或运行 kb-compile 开始编译
```
```

- [ ] **Step 3: Commit kb-status refactor**

```bash
git add skills/minimal/kb-status/SKILL.md
git commit -m "refactor(kb-status): update frontmatter + add output summary"
```

---

## Task 3: Refactor kb-ingest SKILL.md

**Files:**
- Modify: `skills/minimal/kb-ingest/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/minimal/kb-ingest/SKILL.md`:

```yaml
---
name: kb-ingest
description: "Scan raw/ directory, preprocess files (normalize markdown, convert PDF, fix CJK radicals), output to raw/.extracted/, and update raw-registry.md. Use when user asks to ingest files, process raw sources, or prepare files for compilation."
version: 1.0
---
```

- [ ] **Step 2: Update workflow to mention CJK radicals**

Modify step 3 in `skills/minimal/kb-ingest/SKILL.md` workflow:

```markdown
3. **处理文件**：
   - **markdown**：调用 `normalize_markdown.py` 检查编码、转换 CJK 部首，输出到 raw/.extracted/（如有修复）
   - **PDF**：调用 `convert_pdf.py` 转换为 markdown，输出到 raw/.extracted/
   - **image**：无需处理，直接引用
```

- [ ] **Step 3: Add output summary section**

Append to `skills/minimal/kb-ingest/SKILL.md`:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：已处理 X 个文件，Y 个需转换
2. **下一步提示**：可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度

示例：
```
处理结果：已处理 5 个文件，2 个需转换
下一步提示：可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度
```
```

- [ ] **Step 4: Commit kb-ingest refactor**

```bash
git add skills/minimal/kb-ingest/SKILL.md
git commit -m "refactor(kb-ingest): update frontmatter + workflow + output summary"
```

---

## Task 4: Refactor kb-compile SKILL.md (minimal)

**Files:**
- Modify: `skills/minimal/kb-compile/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/minimal/kb-compile/SKILL.md`:

```yaml
---
name: kb-compile
description: "Read extracted files, extract entities (person/place/event), generate wiki pages, update index.md and raw-registry.md. Use when user asks to compile knowledge base, generate wiki pages, or extract entities from sources."
version: 1.0
---
```

- [ ] **Step 2: Add output summary section**

Append to `skills/minimal/kb-compile/SKILL.md`:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 wiki 文档（Y 人物，Z 地点，W 事件）
2. **下一步提示**：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库

示例：
```
处理结果：生成 12 个 wiki 文档（5 人物，4 地点，3 事件）
下一步提示：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库
```
```

- [ ] **Step 3: Commit kb-compile refactor**

```bash
git add skills/minimal/kb-compile/SKILL.md
git commit -m "refactor(kb-compile): update frontmatter + add output summary"
```

---

## Task 5: Refactor kb-lint SKILL.md

**Files:**
- Modify: `skills/minimal/kb-lint/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/minimal/kb-lint/SKILL.md`:

```yaml
---
name: kb-lint
description: "Check wiki pages for syntax errors (wikilink format, frontmatter) and semantic issues (orphan pages, missing sources). Use when user asks to lint wiki, check format, fix errors, or verify knowledge base quality."
version: 1.0
---
```

- [ ] **Step 2: Add output summary section**

Append to `skills/minimal/kb-lint/SKILL.md`:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：X 个问题，Y 个已修复
2. **下一步提示**：可运行 kb-query 查询知识库，或运行 kb-archive 进行综合分析

示例：
```
处理结果：3 个问题，2 个已修复
下一步提示：可运行 kb-query 查询知识库，或运行 kb-archive 进行综合分析
```
```

- [ ] **Step 3: Commit kb-lint refactor**

```bash
git add skills/minimal/kb-lint/SKILL.md
git commit -m "refactor(kb-lint): update frontmatter + add output summary"
```

---

## Task 6: Refactor kb-query SKILL.md

**Files:**
- Modify: `skills/minimal/kb-query/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/minimal/kb-query/SKILL.md`:

```yaml
---
name: kb-query
description: "Search wiki pages with optional raw source backtracking. Use when user asks to query knowledge base, search entities, find information, or look up historical figures/events."
version: 1.0
---
```

- [ ] **Step 2: Add output summary section**

Append to `skills/minimal/kb-query/SKILL.md`:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：找到 X 个相关文档
2. **下一步提示**：可运行 kb-archive 进行综合分析，或继续查询其他内容

示例：
```
处理结果：找到 5 个相关文档
下一步提示：可运行 kb-archive 进行综合分析，或继续查询其他内容
```
```

- [ ] **Step 3: Commit kb-query refactor**

```bash
git add skills/minimal/kb-query/SKILL.md
git commit -m "refactor(kb-query): update frontmatter + add output summary"
```

---

## Task 7: Refactor kb-archive SKILL.md

**Files:**
- Modify: `skills/minimal/kb-archive/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/minimal/kb-archive/SKILL.md`:

```yaml
---
name: kb-archive
description: "Write synthesis reports and integrate findings back into wiki entity pages. Use when user asks to archive findings, write synthesis, summarize research, or integrate analysis into knowledge base."
version: 1.0
---
```

- [ ] **Step 2: Add output summary section**

Append to `skills/minimal/kb-archive/SKILL.md`:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 synthesis 报告，更新 Y 个实体页面
2. **下一步提示**：可运行 kb-status 查看知识库状态，或运行 kb-lint 检查健康度

示例：
```
处理结果：生成 2 个 synthesis 报告，更新 3 个实体页面
下一步提示：可运行 kb-status 查看知识库状态，或运行 kb-lint 检查健康度
```
```

- [ ] **Step 3: Commit kb-archive refactor**

```bash
git add skills/minimal/kb-archive/SKILL.md
git commit -m "refactor(kb-archive): update frontmatter + add output summary"
```

---

## Task 8: Refactor kb-compile SKILL.md (history)

**Files:**
- Modify: `skills/history/kb-compile/SKILL.md`

- [ ] **Step 1: Update frontmatter**

Replace frontmatter in `skills/history/kb-compile/SKILL.md`:

```yaml
---
name: kb-compile
description: "Read extracted files, extract entities (person/place/event) and concepts (institution/official/thought), generate wiki pages, update index.md and raw-registry.md. Use when user asks to compile history knowledge base, generate wiki pages, or extract historical entities and concepts from sources."
version: 1.0
---
```

- [ ] **Step 2: Add output summary section**

Append to `skills/history/kb-compile/SKILL.md`:

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 wiki 文档（Y 人物，Z 地点，W 事件，U 制度，V 官职，T 思想）
2. **下一步提示**：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库

示例：
```
处理结果：生成 15 个 wiki 文档（5 人物，3 地点，2 事件，2 制度，2 官职，1 思想）
下一步提示：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库
```
```

- [ ] **Step 3: Commit history kb-compile refactor**

```bash
git add skills/history/kb-compile/SKILL.md
git commit -m "refactor(kb-compile history): update frontmatter + add output summary"
```

---

## Task 9: Final Verification

**Files:**
- None

- [ ] **Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: 56+ tests PASS (53 existing + 3 new CJK tests)

- [ ] **Step 2: Verify test count**

Check output for test count summary. Should show ~56 tests.

- [ ] **Step 3: Verify migu init works**

Run: `uv run migu init test-kb --rules minimal`
Expected: Knowledge base created successfully

Run: `ls test-kb/.agents/skills/`
Expected: 6 skills installed

- [ ] **Step 4: Cleanup test knowledge base**

Run: `rm -rf test-kb`

- [ ] **Step 5: Final commit message**

```bash
git add docs/superpowers/plans/2026-04-23-cjk-radicals-and-skills-refactor.md
git commit -m "docs: add implementation plan for CJK radicals and skills refactor"
```

---

## Self-Review Checklist

- [x] Spec coverage: All requirements from spec covered
- [x] Placeholder scan: No TBD/TODO/similar-to patterns
- [x] Type consistency: Function names consistent across tasks
- [x] Test coverage: 3 new tests for CJK radicals
- [x] All 7 SKILL.md files covered
- [x] Exact file paths in every step
- [x] Complete code in every code step