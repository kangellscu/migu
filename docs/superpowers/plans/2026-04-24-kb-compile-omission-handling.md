# kb-compile 遗漏处理实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 kb-compile 的遗漏处理能力，通过迭代收敛机制减少实体提取遗漏

**Architecture:** 仅修改 SKILL.md 文本和 raw-registry.md 模板，不新增 scripts 或 CLI 命令。通过意图识别让用户选择 compile 模式（默认/完整/补充/重新）

**Tech Stack:** SKILL.md (Markdown), raw-registry.md 模板

**Spec:** docs/superpowers/specs/2026-04-24-kb-compile-omission-handling-design.md

---

## Task 1: 修改 minimal 版本 kb-compile SKILL.md

**Files:**
- Modify: `skills/minimal/kb-compile/SKILL.md`

- [ ] **Step 1: 更新 frontmatter（version + description）**

修改 frontmatter：

```markdown
---
name: kb-compile
description: "Read files, extract entities and concepts with iterative omission handling. Use when user asks to compile knowledge base, extract information from sources, or when previous compile shows remaining omissions."
version: 2.0
---
```

- [ ] **Step 2: 新增意图识别 section**

在"职责"section 后，新增"意图识别"section：

```markdown
## 意图识别

| 用户意图 | 执行方式 |
|---------|---------|
| "compile" | 单轮提取 + 遗漏清单输出 |
| "完整 compile" | 迭代提取（最多 3 轮） |
| "补充 compile" | 读取 raw-registry.md 剩余遗漏 → 针对性提取 |
| "重新 compile" | 清空状态 → 执行完整 compile |

触发词示例：
- 默认："compile raw 文件"、"开始编译"
- 完整："完整 compile"、"穷尽提取"、"确保不遗漏"
- 补充："补充 compile"、"继续提取遗漏"
- 重新："重新 compile"、"重新编译 xxx 文件"
```

- [ ] **Step 3: 修改执行流程步骤 3**

将原有的"步骤 3: LLM 信息提取"改为分模式处理的迭代流程：

```markdown
3. **LLM 提取（根据意图）**：

   **默认模式**：
   - 单轮提取实体/概念
   - 输出提取清单 + 遗漏清单
   - 参考 templates 约束输出格式

   **完整模式**：
   - 第一轮：提取实体 → 输出提取清单 + 遗漏清单 A
   - 第二轮（遗漏清单 A 非空）：针对性补充 → 输出遗漏清单 B
   - 第三轮（遗漏清单 B 非空）：针对性补充 → 输出遗漏清单 C
   - 上限：3 轮
   - 收敛条件：连续两轮无新遗漏

   **补充模式**：
   - 读取 raw-registry.md 的"剩余遗漏"字段
   - 针对遗漏实体提取详情
   - 执行迭代检查新遗漏

   **重新模式**：
   - 清空该文件的编译状态
   - 执行完整模式
```

- [ ] **Step 4: 修改执行流程步骤 7**

将原有的"步骤 6: 更新 raw-registry.md"改为包含"剩余遗漏"字段：

```markdown
7. **更新 raw-registry.md**：调用 update_registry.py
   - 编译状态：已编译 / 部分编译
   - 剩余遗漏：空 / 实体1, 实体2, ...（逗号分隔）
   - 最近处理日期：当前日期
```

- [ ] **Step 5: 修改输出摘要 section**

替换原有的输出摘要：

```markdown
## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 wiki 文档（Y 实体，Z 概念）
2. **迭代信息**（完整/补充模式）：
   - 迭代次数：N 轮
   - 收敛状态：已收敛 / 未收敛（达到上限）
3. **剩余遗漏**（如有）：
   - 实体列表：A, B, C
   - 提示：可执行"补充 compile"继续提取
4. **下一步提示**：
   - 可运行 kb-lint 检查 wiki 格式
   - 如有剩余遗漏，可执行"补充 compile"

示例：
```
处理结果：生成 8 个 wiki 文档（5 实体，3 概念）
迭代信息：迭代 3 轮，已收敛
剩余遗漏：空
下一步提示：可运行 kb-lint 检查 wiki 格式
```

示例（未收敛）：
```
处理结果：生成 12 个 wiki 文档（8 实体，4 概念）
迭代信息：迭代 3 轮，未收敛（达到上限）
剩余遗漏：范增, 龙且, 钟离昧
下一步提示：可执行"补充 compile"补充遗漏实体
```
```

- [ ] **Step 6: Commit minimal 版本改动**

```bash
git add skills/minimal/kb-compile/SKILL.md
git commit -m "feat(kb-compile): add iterative omission handling for minimal version"
```

---

## Task 2: 修改 history 版本 kb-compile SKILL.md

**Files:**
- Modify: `skills/history/kb-compile/SKILL.md`

- [ ] **Step 1: 更新 frontmatter**

同 minimal 版本：

```markdown
---
name: kb-compile
description: "Read files, extract entities and concepts with iterative omission handling. Use when user asks to compile knowledge base, extract information from sources, or when previous compile shows remaining omissions."
version: 2.0
---
```

- [ ] **Step 2: 新增意图识别 section**

同 minimal 版本。

- [ ] **Step 3: 修改执行流程步骤 3**

同 minimal 版本（history 版本实体类型为：人物、地点、事件、制度、官职、思想）。

- [ ] **Step 4: 修改执行流程步骤 7**

同 minimal 版本。

- [ ] **Step 5: 修改输出摘要 section**

同 minimal 版本（输出示例调整为 history 实体类型）：

```markdown
示例：
```
处理结果：生成 15 个 wiki 文档（5 人物，3 地点，2 事件，2 制度，2 官职，1 思想）
迭代信息：迭代 3 轮，已收敛
剩余遗漏：空
下一步提示：可运行 kb-lint 检查 wiki 格式
```
```

- [ ] **Step 6: Commit history 版本改动**

```bash
git add skills/history/kb-compile/SKILL.md
git commit -m "feat(kb-compile): add iterative omission handling for history version"
```

---

## Task 3: 修改 minimal 版本 raw-registry template

**Files:**
- Modify: `rules/minimal/templates/raw-registry-template.md`

- [ ] **Step 1: 查找当前 template 内容**

先读取当前文件确认结构。

- [ ] **Step 2: 新增"剩余遗漏"字段到表头**

在表头行新增字段：

```markdown
| 文件路径 | 类型 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 | 剩余遗漏 |
```

- [ ] **Step 3: 新增示例行展示字段用法**

在示例 section 新增带"剩余遗漏"字段的示例：

```markdown
| raw/史记/高祖本纪.md | markdown | 已处理 | - | 已编译 | 2026-04-24 | 空 |
| raw/史记/项羽本纪.md | markdown | 已处理 | - | 部分编译 | 2026-04-24 | 范增, 龙且 |
| raw/汉书/高帝纪.md | pdf | 已处理 | raw/.extracted/汉书/高帝纪.md | 未编译 | - | - |
```

- [ ] **Step 4: 新增字段约定说明**

在 template 说明 section 新增：

```markdown
## 剩余遗漏字段约定

- `空`：已收敛，无遗漏
- `实体1, 实体2, ...`：剩余遗漏实体清单（逗号分隔）
- `-`：未编译，字段不适用
```

- [ ] **Step 5: Commit minimal template 改动**

```bash
git add rules/minimal/templates/raw-registry-template.md
git commit -m "feat(raw-registry): add 剩余遗漏 field for minimal version"
```

---

## Task 4: 修改 history 版本 raw-registry template

**Files:**
- Modify: `rules/history/templates/raw-registry-template.md`

- [ ] **Step 1: 同 minimal 版本改动**

新增表头字段 + 示例行 + 字段约定说明。

- [ ] **Step 2: Commit history template 改动**

```bash
git add rules/history/templates/raw-registry-template.md
git commit -m "feat(raw-registry): add 剩余遗漏 field for history version"
```

---

## Task 5: 使用 skill-creator 进行测试和迭代

**Files:**
- Create: `.agents/skills/kb-compile-workspace/evals/evals.json`

- [ ] **Step 1: 创建测试用例 JSON**

```json
{
  "skill_name": "kb-compile",
  "evals": [
    {
      "id": 1,
      "eval_name": "default-compile-mode",
      "prompt": "请 compile raw/史记/高祖本纪.md",
      "expected_output": "生成 wiki 页面，输出遗漏清单，更新 raw-registry.md",
      "assertions": [
        {
          "name": "outputs-extraction-list",
          "description": "输出提取清单（实体/概念列表）"
        },
        {
          "name": "outputs-omission-list",
          "description": "输出遗漏清单"
        },
        {
          "name": "updates-raw-registry",
          "description": "更新 raw-registry.md（编译状态 + 剩余遗漏）"
        }
      ]
    },
    {
      "id": 2,
      "eval_name": "complete-compile-mode",
      "prompt": "请完整 compile raw/史记/项羽本纪.md，确保不遗漏任何实体",
      "expected_output": "迭代提取（最多3轮），输出迭代信息和收敛状态",
      "assertions": [
        {
          "name": "executes-iteration",
          "description": "执行迭代提取（至少2轮）"
        },
        {
          "name": "outputs-iteration-info",
          "description": "输出迭代次数和收敛状态"
        },
        {
          "name": "updates-remaining-omissions",
          "description": "更新 raw-registry.md 的剩余遗漏字段"
        }
      ]
    },
    {
      "id": 3,
      "eval_name": "supplement-compile-mode",
      "prompt": "请补充 compile raw/史记/项羽本纪.md，之前编译后剩余遗漏：范增, 龙且",
      "expected_output": "针对性提取范增、龙且的详情，检查新遗漏",
      "assertions": [
        {
          "name": "reads-remaining-omissions",
          "description": "读取 raw-registry.md 的剩余遗漏字段"
        },
        {
          "name": "targeted-extraction",
          "description": "针对遗漏实体提取详情"
        },
        {
          "name": "checks-new-omissions",
          "description": "执行迭代检查新遗漏"
        }
      ]
    },
    {
      "id": 4,
      "eval_name": "re-compile-mode",
      "prompt": "请重新 compile raw/史记/高祖本纪.md",
      "expected_output": "清空状态，执行完整模式",
      "assertions": [
        {
          "name": "clears-status",
          "description": "清空编译状态"
        },
        {
          "name": "executes-complete-mode",
          "description": "执行完整模式（迭代提取）"
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: 运行 skill-creator 测试流程**

按照 skill-creator skill 的指导：
1. Spawn with-skill + baseline subagents
2. Draft assertions
3. Grade and aggregate
4. Launch eval-viewer

- [ ] **Step 3: 根据反馈迭代改进**

读取 `feedback.json`，根据用户反馈修改 SKILL.md。

---

## Self-Review

**1. Spec coverage:**

| Spec Requirement | Task Coverage |
|-----------------|---------------|
| §4.1 意图识别 | Task 1 Step 2, Task 2 Step 2 |
| §4.1 流程改进 | Task 1 Step 3-4, Task 2 Step 3-4 |
| §4.1 输出摘要 | Task 1 Step 5, Task 2 Step 5 |
| §4.2 剩余遗漏字段 | Task 3, Task 4 |
| §11 规则 1 (skill-creator) | Task 5 |
| §11 规则 2 (渐进式实施) | Task 1 → Task 2 → Task 3 → Task 4 |
| §11 规则 3 (向后兼容) | 默认模式保持原有行为 |

**2. Placeholder scan:** 无 TBD、TODO、"add validation"等占位符。

**3. Type consistency:** 所有步骤使用统一的"剩余遗漏"字段名称。

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-24-kb-compile-omission-handling.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?