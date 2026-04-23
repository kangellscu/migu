# CJK 部首处理与 Skills 规范重构

## 背景

两项工作需要处理：
1. kb-ingest 处理古籍中的 CJK 部首字符（康熙部首、CJK Radicals Supplement、CJK Strokes）
2. 所有生成的 skills 不符合 skill-creator 规范（frontmatter 缺少 `description`）

## 目标

- CJK 部首字符转换为普通汉字（便于搜索和显示）
- Skills frontmatter 符合 skill-creator 规范（name + description）
- 每个 skill workflow 增加 output summary（处理结果 + 下一步提示）

---

## Part 1: CJK 部首映射

### 映射范围

| Unicode 区块 | 范围 | 数量 | 说明 |
|-------------|------|------|------|
| CJK Radicals Supplement | U+2E80-U+2EEF | ~112 | 简化部首变体 |
| Kangxi Radicals | U+2F00-U+2FD5 | 214 | 康熙部首（标准） |
| CJK Strokes | U+31C6, U+31CF-U+31E1 | ~14 | 笔画（仅包含有等效汉字映射的部分） |
| **总计** | - | **~340** | - |

### 数据源

- EquivalentUnifiedIdeograph.txt (Unicode 13.0.0)
- CJKRadicals.txt (Unicode 13.0.0)

### 实现方案

**硬编码映射字典**（无外部依赖，script 自包含）：

```python
_CJK_RADICALS_TO_UNICODE = {
    # CJK Radicals Supplement (2E80-2EEF)
    '\u2e81': '\u5382',  # CJK RADICAL CLIFF → 厂
    '\u2e85': '\u4ebb',  # CJK RADICAL PERSON → 亻
    '\u2e86': '\u5182',  # CJK RADICAL BOX → 冂
    # ... ~112 个
    
    # Kangxi Radicals (2F00-2FD5)
    '\u2f00': '\u4e00',  # KANGXI RADICAL ONE → 一
    '\u2f01': '\u4e28',  # KANGXI RADICAL LINE → 丨
    '\u2f08': '\u4eba',  # KANGXI RADICAL MAN → 人
    # ... 214 个
    
    # CJK Strokes (31C6, 31CF-31E1, 仅包含有等效汉字映射的部分)
    '\u31d0': '\u4e00',  # CJK STROKE H → 一
    '\u31d1': '\u4e28',  # CJK STROKE S → 丨
    # ... ~14 个
}

def convert_cjk_radicals(text: str) -> str:
    """Convert CJK radicals to equivalent unified ideographs."""
    return ''.join(_CJK_RADICALS_TO_UNICODE.get(c, c) for c in text)
```

**集成位置：**

`skills/minimal/kb-ingest/scripts/normalize_markdown.py` 的 `main()` 函数中：

```python
def main(input_file: str, output_file: str):
    src = Path(input_file)
    dst = Path(output_file)
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    content = src.read_text(encoding="utf-8")
    content = convert_cjk_radicals(content)  # 新增：CJK 部首转换
    
    # ... 现有逻辑（BOM 移除等）
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

### 性能分析

| 指标 | 评估 |
|------|------|
| 字典大小 | ~340 个映射，内存占用 ~2KB |
| 查找复杂度 | O(1)（Python dict） |
| 计算负担 | 对无部首文本：O(n) 遍历 + O(1) 查找，开销 < 1% |
| I/O 影响 | 相对文件读写，计算开销可忽略 |

**结论：负担很小，可忽略。**

---

## Part 2: Skills Frontmatter 重构

### 当前问题

| 字段 | 当前格式 | skill-creator 规范 | 问题 |
|------|---------|-------------------|------|
| name | ❌ 使用 `title` | ✅ 必须使用 `name` | 字段名错误 |
| description | ❌ 缺失 | ✅ 必须包含（触发条件） | **主要问题** |
| created | ❌ 非标准 | ❌ 可选 | 可删除 |

### 目标格式

```yaml
---
name: <skill-name>
description: "<职责描述>. Use when user asks to <触发条件1>, <触发条件2>, or <触发条件3>."
version: 1.0
---
```

**description 设计原则：**
- 包含职责描述（简洁）
- 包含触发条件（"pushy" - 防止 undertriggering）
- 多个触发条件用 `or` 连接

### 修改文件列表

| # | 文件 | 当前 | 目标 |
|---|------|------|------|
| 1 | `skills/minimal/kb-status/SKILL.md` | title: kb-status | name + description |
| 2 | `skills/minimal/kb-ingest/SKILL.md` | title: kb-ingest | name + description |
| 3 | `skills/minimal/kb-compile/SKILL.md` | title: kb-compile | name + description |
| 4 | `skills/minimal/kb-lint/SKILL.md` | title: kb-lint | name + description |
| 5 | `skills/minimal/kb-query/SKILL.md` | title: kb-query | name + description |
| 6 | `skills/minimal/kb-archive/SKILL.md` | title: kb-archive | name + description |
| 7 | `skills/history/kb-compile/SKILL.md` | title: kb-compile | name + description |

### 各 skill description 内容

| Skill | description |
|-------|-------------|
| kb-status | "Show knowledge base dashboard with file counts and processing status. Use when user asks to check KB status, see statistics, view dashboard, or wants overview of raw files and wiki pages." |
| kb-ingest | "Scan raw/ directory, preprocess files (normalize markdown, convert PDF, fix CJK radicals), output to raw/.extracted/, and update raw-registry.md. Use when user asks to ingest files, process raw sources, or prepare files for compilation." |
| kb-compile | "Read extracted files, extract entities (person/place/event), generate wiki pages, update index.md and raw-registry.md. Use when user asks to compile knowledge base, generate wiki pages, or extract entities from sources." |
| kb-compile (history) | "Read extracted files, extract entities (person/place/event) and concepts (institution/official/thought), generate wiki pages, update index.md and raw-registry.md. Use when user asks to compile history knowledge base, generate wiki pages, or extract historical entities and concepts from sources." |
| kb-lint | "Check wiki pages for syntax errors (wikilink format, frontmatter) and semantic issues (orphan pages, missing sources). Use when user asks to lint wiki, check format, fix errors, or verify knowledge base quality." |
| kb-query | "Search wiki pages with optional raw source backtracking. Use when user asks to query knowledge base, search entities, find information, or look up historical figures/events." |
| kb-archive | "Write synthesis reports and integrate findings back into wiki entity pages. Use when user asks to archive findings, write synthesis, summarize research, or integrate analysis into knowledge base." |

---

## Part 3: Workflow 输出摘要

### 标准格式

每个 skill 的 workflow 最后一步：

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：<summary 格式>
2. **下一步提示**：可运行 kb-<skill> 进行下一步操作

示例：
```
处理结果：已处理 5 个文件
下一步提示：可运行 kb-compile 开始编译
```
```

### 各 skill 输出摘要设计

| Skill | 处理结果 summary | 下一步提示 |
|-------|-----------------|-----------|
| kb-status | "状态：X 个 raw 文件（Y 待处理），Z 个 wiki 文档" | "可运行 kb-ingest 处理 raw 文件，或运行 kb-compile 开始编译" |
| kb-ingest | "处理结果：已处理 X 个文件，Y 个需转换" | "可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度" |
| kb-compile | "处理结果：生成 X 个 wiki 文档（Y 人物，Z 地点，W 事件...）" | "可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库" |
| kb-compile (history) | "处理结果：生成 X 个 wiki 文档（Y 人物，Z 地点，W 事件，U 制度，V 官职，T 思想）" | "可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库" |
| kb-lint | "检查结果：X 个问题，Y 个已修复" | "可运行 kb-query 查询知识库，或运行 kb-archive 进行综合分析" |
| kb-query | "查询结果：找到 X 个相关文档" | "可运行 kb-archive 进行综合分析，或继续查询其他内容" |
| kb-archive | "处理结果：生成 X 个 synthesis 报告，更新 Y 个实体页面" | "可运行 kb-status 查看知识库状态，或运行 kb-lint 检查健康度" |

### 输出位置

- **stdout**（推荐）：符合现有项目结构，便于追溯
- 不写入 log.md（避免持久化简单摘要）

---

## Part 4: 测试策略

### 新增测试用例

**文件：** `tests/skills/test_kb_ingest.py`

```python
def test_normalize_cjk_radical(tmp_path):
    """CJK 部首转换为普通汉字"""
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    # CJK Radicals Supplement "厂" (U+2E81) + Kangxi "人" (U+2F08)
    content = "\u2e81\u2f08\u4eba"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run(
        ["python", "scripts/normalize_markdown.py", str(input_file), str(output_file)],
        capture_output=True,
        cwd=Path(__file__).parent.parent / "skills" / "minimal" / "kb-ingest",
    )
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert "\u2e81" not in output
    assert "\u2f08" not in output
    assert "\u5382\u4eba\u4eba" in output

def test_normalize_cjk_radical_multiple(tmp_path):
    """多个 CJK 部首同时转换"""
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    # 测试 5 个不同类型的部首
    content = "\u2f00\u2f08\u2e85\u31d0\u4e00"  # 康熙"一"+康熙"人"+CJK"亻"+笔画"一"+普通"一"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run([...])
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    # 所有部首已转换
    assert "\u2f00" not in output
    assert "\u2f08" not in output
    assert "\u2e85" not in output
    assert "\u31d0" not in output

def test_normalize_cjk_radical_preserves_normal_chars(tmp_path):
    """普通汉字不受影响"""
    input_file = tmp_path / "test.md"
    output_file = tmp_path / "output.md"
    
    content = "刘邦项羽张良韩信"
    input_file.write_text(content, encoding="utf-8")
    
    result = subprocess.run([...])
    
    assert result.returncode == 0
    output = output_file.read_text(encoding="utf-8")
    assert output == content  # 内容不变
```

---

## 文件修改清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `skills/minimal/kb-ingest/scripts/normalize_markdown.py` | 修改 | `_CJK_RADICALS_TO_UNICODE` 映射 + `convert_cjk_radicals()` 函数 |
| `tests/skills/test_kb_ingest.py` | 修改 | 新增 3 个测试用例 |
| `skills/minimal/kb-status/SKILL.md` | 修改 | frontmatter + 输出摘要 |
| `skills/minimal/kb-ingest/SKILL.md` | 修改 | frontmatter + 输出摘要 |
| `skills/minimal/kb-compile/SKILL.md` | 修改 | frontmatter + 输出摘要 |
| `skills/minimal/kb-lint/SKILL.md` | 修改 | frontmatter + 输出摘要 |
| `skills/minimal/kb-query/SKILL.md` | 修改 | frontmatter + 输出摘要 |
| `skills/minimal/kb-archive/SKILL.md` | 修改 | frontmatter + 输出摘要 |
| `skills/history/kb-compile/SKILL.md` | 修改 | frontmatter + 输出摘要 |

---

## 验证命令

```bash
uv run pytest -v
# 应有 56+ tests passing（新增 3 个）

uv run migu init test-kb --rules minimal
# 验证 skills 安装正确
```

---

## 参考

- skill-creator skill: skill 规范和 frontmatter 要求
- EquivalentUnifiedIdeograph.txt: Unicode 部首映射数据源
- CJKRadicals.txt: 康熙部首编号对照表