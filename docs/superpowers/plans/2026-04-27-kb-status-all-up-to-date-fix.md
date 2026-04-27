# kb-status "All up to date" 修复实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 kb-status skill，在无待处理文件时显示 "All up to date" 状态 box

**Architecture:** 在 format_dashboard.py 添加条件判断，当 pending_ingest == 0 且 pending_compile == 0 时，输出独立的 Status box

**Tech Stack:** Python 3.11+

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `skills/minimal/kb-status/scripts/format_dashboard.py` | 修改 | 添加状态 box 输出逻辑 |

---

### Task 1: 添加状态 box 输出

**Files:**
- Modify: `skills/minimal/kb-status/scripts/format_dashboard.py:54-55`

- [ ] **Step 1: 编辑 format_dashboard.py，添加状态 box**

在第 54 行（Overview box 结束后）添加：

```python
    print("└─────────────────────────────────────────────────┘")
    
    if pending_ingest == 0 and pending_compile == 0:
        print()
        print("┌─────────────────────────────────────────────────┐")
        print("│ Status                                            │")
        print("├─────────────────────────────────────────────────┤")
        print("│ All up to date                                    │")
        print("└─────────────────────────────────────────────────┘")
    
    if pending_files:
```

注意：原有的 `if pending_files:` 块保持不变，新代码插入在 Overview box 和 Pending Files box 之间。

- [ ] **Step 2: 测试修改**

运行测试脚本：

```bash
cd /Users/23mofang/Documents/knowledge-bases/migu/skills/minimal/kb-status/scripts
echo "kb_dir:/Users/23mofang/Documents/knowledge-bases/test
raw_total:2
raw_types:markdown:2
pending_ingest:0
pending_compile:0
wiki_total:42
wiki_sections:entities:36,concepts:3,synthesis:3" | python format_dashboard.py
```

预期输出包含：
```
┌─────────────────────────────────────────────────┐
│ Status                                            │
├─────────────────────────────────────────────────┤
│ All up to date                                    │
└─────────────────────────────────────────────────┘
```

- [ ] **Step 3: 测试有待处理文件场景**

```bash
echo "kb_dir:/tmp/test
raw_total:10
raw_types:markdown:8,pdf:2
pending_ingest:3
pending_compile:2
pending:raw/test.md|未处理|
wiki_total:5
wiki_sections:entities:3,concepts:2" | python format_dashboard.py
```

预期输出**不包含** Status box（有待处理文件）

- [ ] **Step 4: Commit**

```bash
git add skills/minimal/kb-status/scripts/format_dashboard.py
git commit -m "fix: add 'All up to date' status box when no pending files"
```

---

## Self-Review

**1. Spec coverage:**
- spec 要求"无待处理文件时显示 'All up to date'" → Task 1 Step 1 实现 ✅

**2. Placeholder scan:**
- 无 TBD、TODO、未完成步骤 ✅
- 所有代码完整 ✅

**3. Type consistency:**
- 变量名 pending_ingest、pending_compile 与现有代码一致 ✅

---

## 执行选项

Plan complete and saved to `docs/superpowers/plans/2026-04-27-kb-status-all-up-to-date-fix.md`.

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**