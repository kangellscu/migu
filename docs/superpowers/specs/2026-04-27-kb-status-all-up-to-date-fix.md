---
title: kb-status "All up to date" 修复设计
created: 2026-04-27
type: spec
audience: migu skill 开发者
related_spec: skills/minimal/kb-status/SKILL.md
---

# kb-status "All up to date" 修复设计

## 背景

测评发现边界情况 3 处理不符合 spec：

- **spec 要求**: 无待处理文件时显示 "All up to date"
- **实际输出**: "Pending Ingest: 0 files"
- **grader 结论**: FAIL - 缺少 spec 要求的消息

## 修复目标

使 skill 输出符合 spec 定义：无待处理文件时显示 "All up to date" 消息。

## 设计方案

### 修改文件

| 文件 | 操作 | 内容 |
|------|------|------|
| `scripts/format_dashboard.py` | 修改 | 添加状态 box |

### 修改详情

**位置**: `format_dashboard.py` 第 54-55 行（Overview box 结束后）

**修改内容**: 添加条件判断，当 pending_ingest == 0 且 pending_compile == 0 时，显示状态 box：

```python
if pending_ingest == 0 and pending_compile == 0:
    print()
    print("┌─────────────────────────────────────────────────┐")
    print("│ Status                                            │")
    print("├─────────────────────────────────────────────────┤")
    print("│ All up to date                                    │")
    print("└─────────────────────────────────────────────────┘")
```

### 输出示例

**无待处理文件时**：

```
Knowledge Base Dashboard: test/

┌─────────────────────────────────────────────────┐
│ Overview                                         │
├─────────────────────────────────────────────────┤
│ Raw Files:         2 (markdown: 2)
│ Wiki Documents:    42 (entities: 36, concepts: 3, synthesis: 3)
│ Pending Ingest:    0 files
│ Pending Compile:   0 files
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Status                                            │
├─────────────────────────────────────────────────┤
│ All up to date                                    │
└─────────────────────────────────────────────────┘
```

**有待处理文件时**：

```
Knowledge Base Dashboard: test/

┌─────────────────────────────────────────────────┐
│ Overview                                         │
├─────────────────────────────────────────────────┤
│ Raw Files:         10 (markdown: 8, pdf: 2)
│ Wiki Documents:    5 (entities: 3, concepts: 2)
│ Pending Ingest:    3 files
│ Pending Compile:   2 files
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Pending Files                                     │
├─────────────────────────────────────────────────┤
│ raw/史记/列传/张良传.md         (未处理)          │
└─────────────────────────────────────────────────┘
```

## 测试验证

修复后重新测评：
- 测试用例 eval-0（无待处理文件）
- 断言：输出包含 "All up to date"
- 预期：100% PASS

## 不涉及内容

- 不修改 SKILL.md（spec 定义正确）
- 不修改 read_registry.py、read_index.py
- 不修改现有输出格式（保持 Overview box 结构不变）