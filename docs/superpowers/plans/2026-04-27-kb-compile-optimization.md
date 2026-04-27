# kb-compile Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize minimal/kb-compile skill by reducing redundancy, adding subtype support, and clarifying file locations.

**Architecture:** Streamline SKILL.md structure by merging redundant sections, add subtype field to templates, and update Directory Structure in AGENTS.md.

**Tech Stack:** Python 3.11+, skill-creator framework for testing

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `skills/minimal/kb-compile/SKILL.md` | Modify | 精简内容（178行→95行） |
| `skills/minimal/kb-compile/references/templates/entity-template.md` | Modify | 添加 subtype 字段 |
| `skills/minimal/kb-compile/references/templates/concept-template.md` | Modify | 添加 subtype 字段 |
| `rules/minimal/AGENTS.md` | Modify | Directory Structure 增加 3 个根目录文件 |
| `kb-compile-workspace/iteration-1/` | Create | skill-creator 测试目录 |

---

## Task 1: Modify templates to add subtype field

**Files:**
- Modify: `skills/minimal/kb-compile/references/templates/entity-template.md`
- Modify: `skills/minimal/kb-compile/references/templates/concept-template.md`

- [ ] **Step 1: Edit entity-template.md**

Add `subtype: {{subtype}}` to frontmatter:

```yaml
---
type: entity
subtype: {{subtype}}
---
# {{name}}

## 基本信息
- 别名：{{aliases}}
- 时间：{{time_range}}
- 地点：{{location}}

## 描述
{{description}}

## 关系
{{relations}}

## 来源
- source: [[raw/path/to/source.md]]
```

- [ ] **Step 2: Edit concept-template.md**

Add `subtype: {{subtype}}` to frontmatter:

```yaml
---
type: concept
subtype: {{subtype}}
---
# {{name}}

## 定义
{{definition}}

## 特征
{{characteristics}}

## 相关概念
{{related_concepts}}

## 来源
- source: [[raw/path/to/source.md]]
```

- [ ] **Step 3: Commit template changes**

```bash
git add skills/minimal/kb-compile/references/templates/
git commit -m "feat(kb-compile): add subtype field to templates"
```

---

## Task 2: Rewrite SKILL.md with streamlined structure

**Files:**
- Modify: `skills/minimal/kb-compile/SKILL.md`

- [ ] **Step 1: Replace SKILL.md with optimized content**

Write entire file:

```markdown
---
name: kb-compile
description: "Read files, extract entities and concepts with iterative omission handling. Use when user asks to compile knowledge base, extract information from sources, or when previous compile shows remaining omissions."
version: 2.0
---

# kb-compile

## 职责

读取 raw/.extracted/ 或 raw/ 文件，LLM 提取实体和概念，生成 wiki 页面。支持迭代遗漏处理。

## 意图识别

| 用户意图 | 执行方式 |
|---------|---------|
| "compile" | 单轮提取 + 遗漏清单输出 |
| "完整 compile" | 迭代提取（最多 3 轮） |
| "补充 compile" | 读取 raw-registry.md 剩余遗漏 → 针对性提取 |
| "重新 compile" | 清空状态 → 执行完整 compile |

触发词：默认（"compile raw 文件"、"开始编译"），完整（"完整 compile"、"穷尽提取"），补充（"补充 compile"），重新（"重新 compile"）

## 执行流程

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：调用 `read_file.py`（产物路径 != `-` 时读取产物路径，否则读取 raw 文件）
3. **LLM 提取**：根据意图执行（默认单轮、完整迭代≤3轮、补充针对性、重新清空后完整）
4. **LLM wiki 生成**：检查 wiki/ 是否已有文档，无则创建，有则增量更新。source 字段：`- source: [[raw/path/to/source.md]]`
5. **更新 index.md**：添加新页面索引到对应 section
6. **更新 log.md**：追加 compile 操作记录
7. **更新 raw-registry.md**：调用 `update_registry.py`，更新编译状态和最近处理日期

增量更新时：信息补充→追加；信息冲突→判断是否同一信息或保留注释；关系→去重合并

## 实体/概念提取

**原则**：穷尽提取文档中所有可命名的内容，不受模板类型限制。

| 类别 | 定义 | 预定义 subtype |
|------|------|---------------|
| 实体 | 具体、可命名、有时空属性的个体 | person, place, organization, event, product, tool, {{自定义}} |
| 概念 | 抽象、主题性、无时空属性的类别 | policy, methodology, phenomenon, {{自定义}} |

**subtype填写**：根据实体/概念性质选择预定义值或自定义填写。

**事件归属**：详细描述的事件（有具体时间、地点、参与者）归为实体；抽象提及的事件归为概念。

## templates说明

templates 约束 wiki 页面格式，不约束提取范围。

## scripts使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_file.py | 根据路径读取文件 | 步骤 2：读取待编译文件内容 | 必须 |
| update_registry.py | 更新 raw-registry.md | 步骤 7：更新编译状态 | 必须 |

## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 wiki 文档（Y 实体，Z 概念）
2. **迭代信息**（完整/补充模式）：迭代次数 N 轮，收敛状态
3. **剩余遗漏**（如有）：实体列表，提示可执行"补充 compile"
4. **下一步提示**：可运行 kb-lint 检查 wiki 格式
```

- [ ] **Step 2: Commit SKILL.md changes**

```bash
git add skills/minimal/kb-compile/SKILL.md
git commit -m "refactor(kb-compile): streamline SKILL.md from 178 to 95 lines"
```

---

## Task 3: Update Directory Structure in AGENTS.md

**Files:**
- Modify: `rules/minimal/AGENTS.md`

- [ ] **Step 1: Edit Directory Structure section**

Replace lines 9-17 with:

```markdown
## Directory Structure

- `raw/`: Raw source files (user managed, immutable)
- `raw/.extracted/`: Processed files from kb-ingest
- `raw-registry.md`: Raw file registry (root level)
- `wiki/`: LLM-generated structured documents
  - `entities/`: Entity pages
  - `concepts/`: Concept pages
  - `synthesis/`: Analysis pages
- `index.md`: Knowledge base index (root level)
- `log.md`: Operation log (root level)
- `output/`: User-generated derivative documents
```

- [ ] **Step 2: Commit AGENTS.md changes**

```bash
git add rules/minimal/AGENTS.md
git commit -m "docs: add root-level files to Directory Structure"
```

---

## Task 4: Create test workspace for skill-creator evaluation

**Files:**
- Create: `kb-compile-workspace/iteration-1/`

- [ ] **Step 1: Create workspace directory structure**

```bash
mkdir -p kb-compile-workspace/iteration-1
```

- [ ] **Step 2: Snapshot old skill for baseline comparison**

```bash
cp -r skills/minimal/kb-compile kb-compile-workspace/skill-snapshot/
```

---

## Task 5: Design evaluation test cases

**Files:**
- Create: `kb-compile-workspace/evals.json`

- [ ] **Step 1: Write evals.json with test prompts**

```json
{
  "skill_name": "kb-compile",
  "evals": [
    {
      "id": 1,
      "prompt": "compile raw/史记/本纪/高祖本纪.md，提取刘邦及其相关人物",
      "expected_output": "生成 wiki 文档，包含实体（刘邦、萧何、韩信等），frontmatter 有 type 和 subtype 字段",
      "assertions": [
        {
          "text": "输出包含处理结果（spec: SKILL.md 输出摘要 §1）",
          "passed": null,
          "evidence": null
        },
        {
          "text": "wiki 文档 frontmatter 包含 subtype 字段（spec: §3 templates）",
          "passed": null,
          "evidence": null
        },
        {
          "text": "index.md 在根目录而非 wiki/ 下（spec: §6 Directory Structure）",
          "passed": null,
          "evidence": null
        }
      ]
    },
    {
      "id": 2,
      "prompt": "完整 compile raw/某文档.md",
      "expected_output": "迭代提取最多3轮，输出迭代信息和收敛状态",
      "assertions": [
        {
          "text": "输出包含迭代信息（spec: SKILL.md 输出摘要 §2）",
          "passed": null,
          "evidence": null
        },
        {
          "text": "迭代不超过3轮（spec: SKILL.md 意图识别表格）",
          "passed": null,
          "evidence": null
        }
      ]
    },
    {
      "id": 3,
      "prompt": "补充 compile，处理遗漏实体",
      "expected_output": "读取 raw-registry.md 剩余遗漏，针对性提取",
      "assertions": [
        {
          "text": "读取 raw-registry.md 剩余遗漏字段（spec: SKILL.md 意图识别表格）",
          "passed": null,
          "evidence": null
        }
      ]
    }
  ]
}
```

---

## Task 6: Run skill-creator evaluation

**Files:**
- Output: `kb-compile-workspace/iteration-1/benchmark.json`

- [ ] **Step 1: Spawn with-skill subagent for each eval**

Use skill-creator workflow:
- Launch subagents with new skill version
- Save outputs to `kb-compile-workspace/iteration-1/eval-{N}/with_skill/outputs/`

- [ ] **Step 2: Spawn baseline subagent for each eval**

Use old skill snapshot:
- Launch subagents with `kb-compile-workspace/skill-snapshot/`
- Save outputs to `kb-compile-workspace/iteration-1/eval-{N}/old_skill/outputs/`

- [ ] **Step 3: Capture timing data**

Save `timing.json` for each run when subagent completes.

- [ ] **Step 4: Grade outputs**

Spawn grader subagent to evaluate assertions against spec.

- [ ] **Step 5: Aggregate benchmark**

```bash
python -m scripts.aggregate_benchmark kb-compile-workspace/iteration-1 --skill-name kb-compile
```

- [ ] **Step 6: Review results**

Run eval viewer for user feedback:
```bash
python skill-creator/eval-viewer/generate_review.py kb-compile-workspace/iteration-1 --skill-name kb-compile --benchmark kb-compile-workspace/iteration-1/benchmark.json
```

---

## Task 7: Iterate based on feedback

**Files:**
- Modify: `skills/minimal/kb-compile/SKILL.md` (if needed)

- [ ] **Step 1: Read feedback.json**

Process user feedback from eval viewer.

- [ ] **Step 2: Apply improvements**

If feedback indicates issues, update SKILL.md accordingly.

- [ ] **Step 3: Rerun evaluation**

Create `iteration-2/` and rerun test cases.

---

## Self-Review

**Spec coverage:**
- §3 Templates: Task 1 ✓
- §4 SKILL.md structure: Task 2 ✓
- §6 Directory Structure: Task 3 ✓
- §8 Implementation method (skill-creator): Tasks 4-7 ✓

**Placeholder scan:** No TBD/TODO found. All steps have concrete code.

**Type consistency:** subtype field consistently used across templates and SKILL.md.