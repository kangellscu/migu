---
title: Problems.md Issues Fix Design
created: 2026-04-23
type: spec
status: draft
version: 1.0
related: problems.md
---

# Problems.md Issues Fix Design

> 本设计文档修复 problems.md 中列出的 13 个问题。
> 
> 参考 Karpathy LLM-WIKI gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## 1. 问题总览

| 类别 | 问题数 | 说明 |
|------|--------|------|
| 脚本 bug | 4 | scan_raw.py, update_registry.py, syntax.py, read_registry.py |
| 缺失交付物 | 3 | templates 目录, wiki frontmatter, entities 结构说明 |
| 架构问题 | 3 | lint 脚本设计, wikilink 格式, minimal AGENTS.md 假设历史类 |
| Registry 格式 | 2 | update_registry 列匹配, read_registry 分隔符解析 |

---

## 2. 修复策略

**三阶段修复**：
- Phase 1: 核心基础设施（阻塞问题）
- Phase 2: 架构清理（重要问题）
- Phase 3: 文档与结构修正（minimal 重构）

**验证方式**：实际测试 - 使用 `migu init` 创建知识库验证修复。

---

## 3. Phase 1: 核心基础设施

### 3.1 创建缺失 templates

**问题**：rules/minimal/templates/ 不存在，migu init 无法复制模板。

**修复**：创建 templates 目录及三个模板文件。

**目录结构**：
```
rules/minimal/templates/
  index.md         # Wiki 索引模板
  log.md           # 操作日志模板
  raw-registry.md  # Raw 文件注册表模板
```

**模板内容**（参考 scaffold-design spec §4.1）：

**index.md**：
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

**log.md**：
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

**raw-registry.md**：
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

### 3.2 scan_raw.py 参数

**问题**：调用时返回 Usage 报错。

**分析**：
- 脚本正确：接收 kb_dir 参数
- 问题可能在于 SKILL.md 未明确指定参数

**修复**：验证 kb-ingest SKILL.md 明确指定 `<kb_dir>` 参数。

### 3.3 update_registry.py 修复

**问题**：
1. 传入 4 个参数返回 Usage 报错（脚本只接受 3 个）
2. 破坏 registry 格式 - 按固定列索引更新，未识别列名语义

**修复**：

**参数问题**：移除日期参数，脚本内部获取日期。

**列匹配问题**：改用列名匹配而非固定索引。

**修正后逻辑**：
```python
def main(kb_dir: str, file_path: str, status: str):
    # 解析 header 行，获取列名索引
    # 根据 "编译状态" 列名定位，而非 cells[5]
    # 根据 "最近处理日期" 列名定位，而非 cells[6]
```

### 3.4 syntax.py 范围修正

**问题**：直接调用扫描 `.agents/` 目录。

**原因**：脚本接收 wiki_dir，但 agent 可能传入 kb_dir。

**修复**：
- 参数改为 kb_dir
- 内部提取 wiki/ 子目录
- 增加 `.agents/` 目录过滤

### 3.5 read_registry.py 分隔符解析

**问题**：输出 total:0 - 分隔符格式不匹配。

**原因**：脚本只匹配 `|------|` 格式，不支持 `| -------- |` 格式。

**修复**：匹配两种分隔符格式。

```python
# 当前：只匹配 |------|
if line.startswith("|------"):
    in_table = True

# 修正：匹配两种格式
if line.startswith("|") and ("---" in line or "------" in line):
    in_table = True
```

---

## 4. Phase 2: 架构清理

### 4.1 Lint 脚本架构

**问题**：syntax.py/semantic.py 可独立运行但不应独立调用。

**修复方案**：**Internal 模块方案**（保持测试性）

1. Rename: syntax.py → _syntax.py, semantic.py → _semantic.py
2. Update lint.py: import modules instead of subprocess
3. Add header: "Internal module - called by lint.py only"

**lint.py 修正**：
```python
from . import _syntax, _semantic

# 调用内部模块而非 subprocess
issues = _syntax.check(wiki_dir)
issues.extend(_semantic.check(kb_dir))
```

### 4.2 Wiki Frontmatter

**问题**：生成的 wiki 文档无 YAML frontmatter。

**修复**：模板添加 frontmatter，仅 `type` 字段。

**Frontmatter 格式**：
```yaml
---
type: person
---
```

**说明**：
- source 信息在正文 `## 来源` section（完整多来源列表）
- frontmatter 不记录 source，避免重复和主次判断复杂度

**应用范围**：
- skills/minimal/kb-compile/references/templates/*.md
- skills/history/kb-compile/references/templates/*.md

### 4.3 Wikilink 示例格式

**问题**：AGENTS.md wikilink 示例被 Obsidian 解析，创建占位文件。

**修复**：使用三引号代码块（完全防止解析）。

**修正格式**：
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

使用 `<your-path>` 占位符，避免真实路径被解析创建。

---

## 5. Phase 3: Minimal AGENTS.md 重构

### 5.1 核心问题

**当前问题**：minimal AGENTS.md 假设历史类知识库（entities/: Person, place, organization）。

**Karpathy 参考**：
> "The schema tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow."
> "The exact directory structure... will depend on your domain."

**minimal 应是通用基础**，不预设领域特定结构。

### 5.2 Wiki 页面分类

**参考 Karpathy wiki 内容**：
- entity pages
- concept pages
- summaries
- synthesis
- comparisons
- overview

**分类**：

| 类别 | 页面类型 | 来源 kb | 性质 |
|------|---------|---------|------|
| **基础页** | entities, concepts, summaries | kb-compile | 从 raw 提取 |
| **分析页** | synthesis, comparisons, overview | kb-archive | 综合分析 |

### 5.3 Minimal 目录结构

**minimal structure.json**：
```json
{
  "directories": {
    "raw": { ".extracted": {} },
    "wiki": {
      "entities": {},
      "concepts": {},
      "synthesis": {}
    },
    "output": {}
  }
}
```

**说明**：
- entities/, concepts/ 是基础页（kb-compile 输出）
- synthesis/ 是分析页（kb-archive 输出），预创建简化实现
- 所有分析页（synthesis/comparison/overview）存放在 synthesis/
- frontmatter type 区分页面类型：synthesis | comparison | overview

### 5.4 Minimal AGENTS.md 修正

**修正内容**：

```markdown
---
version: "1.0"
---
# Knowledge Base Schema (Minimal)

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
Analysis pages stored in wiki/synthesis/ (pre-created), distinguished by frontmatter type:
```
---
type: synthesis | comparison | overview
---
```

kb-archive writes analysis pages directly to wiki/synthesis/.

## Naming Conventions

- Wiki pages: Title case, no file extension in wikilinks. E.g., `[[EntityName]]`
- Raw files: Preserve original naming. E.g., `raw/史记/本纪/高祖本纪.md`
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

## Operations

- kb-ingest: Scan raw/, preprocess, output to raw/.extracted/
- kb-compile: Read files, extract entities/concepts, generate wiki pages
- kb-lint: Check wiki syntax and semantics
- kb-query: Search wiki with optional raw backtracking
- kb-archive: Generate synthesis/comparison/overview, integrate into wiki
- kb-status: Show dashboard
```

### 5.5 History Rules 继承

**history structure.json**（覆盖 minimal）：
```json
{
  "directories": {
    "raw": { ".extracted": {} },
    "wiki": {
      "entities": {},
      "concepts": {},
      "synthesis": {}
    },
    "output": {}
  }
}
```

**说明**：
- history 与 minimal 结构一致（继承 minimal）
- history 的实体类型定义：person, place, event, institution
- history 的概念类型定义：dynasty, policy, culture

**history AGENTS.md**：
- 继承 minimal AGENTS.md 结构和格式
- 添加历史领域特定定义：
  - Entity types section: person, place, event, institution
  - Concept types section: dynasty, policy, culture
  - Synthesis examples: relation network, timeline analysis

---

## 6. 文件修改清单

| Phase | 文件 | 操作 |
|-------|------|------|
| 1 | rules/minimal/templates/index.md | 创建 |
| 1 | rules/minimal/templates/log.md | 创建 |
| 1 | rules/minimal/templates/raw-registry.md | 创建 |
| 1 | skills/minimal/kb-ingest/SKILL.md | 验证参数说明 |
| 1 | skills/minimal/kb-compile/scripts/update_registry.py | 修正列匹配 |
| 1 | skills/minimal/kb-lint/scripts/syntax.py | 修正参数 kb_dir |
| 1 | skills/minimal/kb-status/scripts/read_registry.py | 修正分隔符匹配 |
| 2 | skills/minimal/kb-lint/scripts/syntax.py | rename → _syntax.py |
| 2 | skills/minimal/kb-lint/scripts/semantic.py | rename → _semantic.py |
| 2 | skills/minimal/kb-lint/scripts/lint.py | 修正 import |
| 2 | skills/*/kb-compile/references/templates/*.md | 添加 frontmatter |
| 2 | rules/minimal/AGENTS.md | wikilink 转义 |
| 2 | rules/history/AGENTS.md | wikilink 转义 |
| 3 | rules/minimal/structure.json | 修正 wiki 结构 |
| 3 | rules/minimal/AGENTS.md | 重构为通用基础 |
| 3 | rules/history/structure.json | 添加 synthesis/ |
| 3 | rules/history/AGENTS.md | 继承 minimal + 领域定义 |

---

## 7. 验证计划

**验证步骤**：

1. Phase 1 完成 → `migu init test-kb` → 验证 templates 复制
2. Phase 2 完成 → 测试 kb-lint、检查 frontmatter
3. Phase 3 完成 → 验证 minimal/history 结构差异

**验证命令**：
```bash
uv run migu init test-kb --rules minimal
uv run migu init test-history-kb --rules history
# 检查目录结构、AGENTS.md 内容
```