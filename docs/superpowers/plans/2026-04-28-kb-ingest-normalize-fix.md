# kb-ingest normalize_markdown.py 输出逻辑修正实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正 normalize_markdown.py 输出逻辑，使其仅在有修复时才创建产物，并返回 JSON 状态供 agent 解析。

**Architecture:** normalize_markdown.py 检测 BOM 和 CJK 部首问题，有修复时才输出到 `.extracted/` 目录，返回 JSON 状态（status、output_path、issues）。kb-ingest agent 根据状态更新 raw-registry.md。

**Tech Stack:** Python 3.11+, pytest

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `skills/minimal/kb-ingest/scripts/normalize_markdown.py` | Modify | 检测问题、有修复才输出、返回 JSON |
| `skills/minimal/kb-ingest/SKILL.md` | Modify | 更新流程描述、补充 JSON 返回说明 |
| `tests/skills/test_normalize_markdown.py` | Create | 测试 normalize_markdown.py 行为 |

---

### Task 1: 创建 normalize_markdown.py 测试

**Files:**
- Create: `tests/skills/test_normalize_markdown.py`

- [ ] **Step 1: Write failing tests for skipped status**

```python
"""Tests for normalize_markdown.py output logic."""

import json
import subprocess
import tempfile
from pathlib import Path


def test_no_bom_no_radicals_returns_skipped():
    """文件无 BOM 无康熙部首，返回 skipped 状态，不创建产物。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("正常内容", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "skipped"
        assert output["output_path"] is None
        assert output["issues"] == []
        
        extracted_dir = raw_dir / ".extracted"
        assert not extracted_dir.exists()


def test_bom_only_returns_processed():
    """文件有 BOM，返回 processed 状态，创建产物。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("\ufeff有BOM内容", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "processed"
        assert output["output_path"] == ".extracted/test.md"
        assert output["issues"] == ["bom"]
        
        extracted_file = raw_dir / ".extracted" / "test.md"
        assert extracted_file.exists()
        content = extracted_file.read_text(encoding="utf-8")
        assert not content.startswith("\ufeff")


def test_radicals_only_returns_processed():
    """文件有康熙部首，返回 processed 状态，创建产物。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        # 康熙部首 ⼈ (U+2F08) 应转换为 人 (U+4EBA)
        src_file.write_text("康熙部首⼈", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "processed"
        assert output["output_path"] == ".extracted/test.md"
        assert output["issues"] == ["radicals"]
        
        extracted_file = raw_dir / ".extracted" / "test.md"
        assert extracted_file.exists()
        content = extracted_file.read_text(encoding="utf-8")
        assert content == "康熙部首人"


def test_both_bom_and_radicals_returns_processed():
    """文件有 BOM 和康熙部首，返回 processed 状态，issues 包含两者。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        src_file = raw_dir / "test.md"
        src_file.write_text("\ufeff康熙部首⼈", encoding="utf-8")
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/normalize_markdown.py",
             str(src_file), str(raw_dir)],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert output["status"] == "processed"
        assert output["output_path"] == ".extracted/test.md"
        assert "bom" in output["issues"]
        assert "radicals" in output["issues"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/23mofang/Documents/knowledge-bases/migu && uv run pytest tests/skills/test_normalize_markdown.py -v`

Expected: FAIL（normalize_markdown.py 当前不返回 JSON）

- [ ] **Step 3: Commit test file**

```bash
git add tests/skills/test_normalize_markdown.py
git commit -m "test: add normalize_markdown.py output logic tests (expect fail)"
```

---

### Task 2: 修改 normalize_markdown.py 实现逻辑

**Files:**
- Modify: `skills/minimal/kb-ingest/scripts/normalize_markdown.py`

- [ ] **Step 1: Rewrite normalize_markdown.py to match new design**

```python
"""Normalize markdown file (encoding fix, CJK radicals conversion).

Returns JSON status:
- status: "processed" or "skipped"
- output_path: path to extracted file (if processed) or null (if skipped)
- issues: list of detected issue types (e.g., ["bom"], ["radicals"])
"""

import json
import sys
from pathlib import Path

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


def main(input_file: str, output_dir: str):
    src = Path(input_file)
    raw_dir = Path(output_dir)
    
    content = src.read_text(encoding="utf-8")
    original = content
    issues = []
    
    if content.startswith('\ufeff'):
        content = content[1:]
        issues.append("bom")
    
    converted = convert_cjk_radicals(content)
    if converted != content:
        issues.append("radicals")
        content = converted
    
    needs_fix = len(issues) > 0
    
    if needs_fix:
        extracted_dir = raw_dir / ".extracted"
        rel_path = src.relative_to(raw_dir)
        dst = extracted_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        
        result = {
            "status": "processed",
            "output_path": f".extracted/{rel_path}",
            "issues": issues
        }
        print(f"FIXED: {input_file} -> {dst}", file=sys.stderr)
    else:
        result = {
            "status": "skipped",
            "output_path": None,
            "issues": []
        }
        print(f"OK: {input_file}", file=sys.stderr)
    
    print(json.dumps(result))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: normalize_markdown.py <input_file> <raw_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd /Users/23mofang/Documents/knowledge-bases/migu && uv run pytest tests/skills/test_normalize_markdown.py -v`

Expected: PASS（4 tests）

- [ ] **Step 3: Commit normalize_markdown.py changes**

```bash
git add skills/minimal/kb-ingest/scripts/normalize_markdown.py
git commit -m "fix: normalize_markdown.py only outputs when fix needed, returns JSON status"
```

---

### Task 3: 更新 SKILL.md 流程描述

**Files:**
- Modify: `skills/minimal/kb-ingest/SKILL.md`

- [ ] **Step 1: Update step 3 description and scripts table**

修改第 18-19 行：
```markdown
3. **处理文件**：
   - **markdown**：调用 `normalize_markdown.py` 检查 BOM 和康熙部首/CJK 部首。有修复时输出到 `raw/.extracted/`，返回 JSON 状态（status、output_path、issues）；无修复时不输出，返回 status: skipped。
   - **PDF**：调用 `convert_pdf.py` 转换为 markdown，输出到 `raw/.extracted/`
   - **image**：无需处理，直接引用
```

修改第 46-51 行表格：
```markdown
| script | 用途 | 调用时机 | 参数 | 依赖类型 | 返回值 |
|--------|------|---------|------|---------|--------|
| scan_raw.py | 扫描 raw/ 目录，检测新文件 | 步骤 1：检测新文件 | <kb_dir> | 必须 | stdout: 文件路径|类型 |
| validate_batch.py | 验证 raw-registry.md 格式 | 步骤 4：验证格式 | - | 必须 | 无 |
| normalize_markdown.py | 规范化 markdown 文件 | 步骤 3：处理 markdown | <input_file> <raw_dir> | 必须 | stdout: JSON 状态，stderr: 日志 |
| convert_pdf.py | 转换 PDF 为 markdown | 步骤 3：处理 PDF | - | 必须 | 无 |
```

- [ ] **Step 2: Add JSON status format section**

在 scripts 使用说明后添加：
```markdown
## normalize_markdown.py 返回值格式

stdout 输出 JSON：
```json
{
  "status": "processed" | "skipped",
  "output_path": ".extracted/path/to/file.md" | null,
  "issues": ["bom"] | ["radicals"] | ["bom", "radicals"] | []
}
```

stderr 输出日志：
- 有修复：`FIXED: <input> -> <output>`
- 无修复：`OK: <input>`
```

- [ ] **Step 3: Commit SKILL.md changes**

```bash
git add skills/minimal/kb-ingest/SKILL.md
git commit -m "docs: update kb-ingest SKILL.md with JSON return format"
```

---

### Task 4: 验证整体流程

- [ ] **Step 1: Test with real files in test2**

在 test2 知识库中添加测试文件：
```bash
mkdir -p /Users/23mofang/Documents/knowledge-bases/test2/raw/史记/本纪
echo "正常内容" > /Users/23mofang/Documents/knowledge-bases/test2/raw/史记/本纪/秦本纪.md
printf '\ufeff有BOM' > /Users/23mofang/Documents/knowledge-bases/test2/raw/史记/本纪/项羽本纪.md
echo "康熙部首⼈" > /Users/23mofang/Documents/knowledge-bases/test2/raw/史记/本纪/高祖本纪.md
```

- [ ] **Step 2: Run normalize_markdown.py on each file**

```bash
cd /Users/23mofang/Documents/knowledge-bases/migu
python skills/minimal/kb-ingest/scripts/normalize_markdown.py \
  /Users/23mofang/Documents/knowledge-bases/test2/raw/史记/本纪/秦本纪.md \
  /Users/23mofang/Documents/knowledge-bases/test2/raw
```

Expected: stdout JSON with status: "skipped", stderr: "OK: ..."

- [ ] **Step 3: Check extracted directory**

```bash
ls -la /Users/23mofang/Documents/knowledge-bases/test2/raw/.extracted/
```

Expected: 无秦本纪.md 产物（因为无修复），有项羽本纪.md 和高祖本纪.md 产物

---

## Self-Review

**1. Spec coverage:**
- 判断条件（BOM + CJK 部首） → Task 2 实现
- 输出行为（有修复才输出） → Task 2 实现，Task 1 测试
- 返回格式（JSON） → Task 2 实现，Task 1 测试
- registry 记录 → Task 3 SKILL.md 更新（agent 负责调用）
- SKILL.md 更新 → Task 3

**2. Placeholder scan:** 无 TBD、TODO 等占位符

**3. Type consistency:** 
- JSON 字段名：status、output_path、issues（Task 1 测试、Task 2 实现一致）
- output_path 格式：`.extracted/...`（一致）