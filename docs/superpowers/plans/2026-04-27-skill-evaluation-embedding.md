# Skill 测评规范嵌入实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 skill 测评约束嵌入 AGENTS.md，建立项目级测评规范

**Architecture:** 在 AGENTS.md "Spec 文档" 章节后添加精简版测评规范章节，引用完整 spec 作为详细文档

**Tech Stack:** Markdown 文档编辑

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `AGENTS.md` | 修改 | 添加 "Skill 测评规范" 章节（精简版） |
| `docs/superpowers/specs/2026-04-27-skill-evaluation-constraints.md` | 已存在 | 完整 spec（引用源） |

---

### Task 1: 在 AGENTS.md 添加测评规范章节

**Files:**
- Modify: `AGENTS.md:91`（在 "Spec 文档" 章节后插入）

- [ ] **Step 1: 编辑 AGENTS.md，添加测评规范章节**

在第 91 行（Spec 文档章节后）插入以下内容：

```markdown

## Skill 测评规范

使用 skill-creator 测评 migu skills 时遵循以下约束：

### 断言设计
- 所有断言必须引用 skill spec（SKILL.md）作为基准
- 仅验证行为断言（是否符合 spec），不验证主观风格
- 断言文本包含 spec 引用（如 "spec: SKILL.md 边界情况表格"）

### 边界测试覆盖
- 必须覆盖 SKILL.md 定义的所有边界情况
- 每个边界情况至少 1 个测试用例
- 测试用例验证 spec 定义的预期处理方式

### 数据采集
- timing 数据来自 subagent notification（真实运行数据）
- grading 使用独立 grader agent（避免主观偏见）
- grading.json 使用 text/passed/evidence 字段

**详细规范**: `docs/superpowers/specs/2026-04-27-skill-evaluation-constraints.md`
```

- [ ] **Step 2: 验证文档格式**

运行: `cat AGENTS.md`
预期: 新章节出现在 "Spec 文档" 之后，格式正确

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add skill evaluation constraints to AGENTS.md"
```

---

## Self-Review

**1. Spec coverage:**
- §1 断言设计 → Task 1 "断言设计" 章节
- §2 边界测试 → Task 1 "边界测试覆盖" 章节
- §3 数据采集 → Task 1 "数据采集" 章节
- 所有 spec 核心约束已覆盖

**2. Placeholder scan:**
- 无 TBD、TODO、未完成步骤
- 所有代码/内容完整

**3. Type consistency:**
- 无类型定义（文档任务）

---

## 执行选项

Plan complete and saved to `docs/superpowers/plans/2026-04-27-skill-evaluation-embedding.md`.

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**