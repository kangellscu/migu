---
title: kb-lint 分层修复设计
created: 2026-04-24
type: spec
status: draft
related_spec: docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# kb-lint 分层修复设计

> 本文档定义 kb-lint 的分层检测和分级修复机制，解决当前 scripts 检测分散、修复能力有限的问题。

---

## 1. 问题定义

### 1.1 当前架构问题

| 问题 | 当前状态 | 影响 |
|------|---------|------|
| 检测分散 | 4 个独立 scripts，各自输出 | 无统一报告 |
| 修复能力有限 | 只能修复 wikilink 不平衡、缺失 source placeholder | orphan/broken links 无法修复 |
| 术语技术化 | "Level 1/2/3" 不直观 | 用户不理解 |
| 无分级报告 | 所有问题混杂输出 | 不便于优先级排序 |

### 1.2 设计目标

- 分层检测（确定性 vs 不确定性）
- 分级报告（格式/结构/内容问题）
- 分级修复（自动/建议/人工）
- 表意式命名（直观易理解）

---

## 2. 核心概念

### 2.1 问题分类

| 问题类型 | 确定性程度 | 检测方式 | 修复方式 |
|---------|-----------|---------|---------|
| **格式问题** | 高（纯格式） | scripts | 自动修复 |
| **结构问题** | 中（可推断但需确认） | scripts | 输出建议 |
| **内容问题** | 低（需语义判断） | LLM | 仅提示 |

### 2.2 术语对照

| 技术术语 | 表意术语 | 说明 |
|---------|---------|------|
| Level 1 | **格式问题** | wikilink 不平衡、缺失 source |
| Level 2 | **结构问题** | orphan pages、broken wikilinks、缺失 title |
| Level 3 | **内容问题** | 内容冲突、语义问题 |

---

## 3. 检测分级

### 3.1 格式问题检测（scripts，自动修复）

| 问题 | 检测逻辑 | 当前实现 | 改进 |
|------|---------|---------|------|
| wikilink 不平衡 | `[[` vs `]]` 数量 | ✓ `_syntax.py` | 不改动 |
| 缺失 source 字段 | 检查 `## 来源` + `- source:` | ✓ `_syntax.py` | 改进：推断真实路径 |

### 3.2 结构问题检测（scripts，建议修复）

| 问题 | 检测逻辑 | 当前实现 | 改进 |
|------|---------|---------|------|
| orphan pages | wiki/ vs index.md | ✓ `_orphans.py` | 新增：路径推断 suggest_section |
| broken wikilinks | wikilink 目标是否存在 | ✓ `_broken_links.py` | 已改进：按文档分组输出 |
| 缺失 title heading | 检查 `# ` | ✓ `_semantic.py` | 新增：从文件名推断 |

### 3.3 内容问题检测（LLM，仅提示）

| 问题 | 检测逻辑 | 当前实现 | 改进 |
|------|---------|---------|------|
| 内容冲突 | 语义判断 | ✗ 无 | 新增：LLM 检测 |
| 模板结构不完整 | section + 内容判断 | 部分 `_semantic.py` | 改进：LLM 判断 |

---

## 4. 报告格式

### 4.1 问题概览（摘要）

默认模式（"lint wiki"）仅输出摘要：

```
kb-lint Summary

- 格式问题: 5 个（可自动修复）
  - wikilink 不平衡: 0
  - 缺失 source: 5
  
- 结构问题: 51 个（建议修复）
  - orphan pages: 18
  - broken wikilinks: 33
  
- 内容问题: 0 个（需人工修复）

Next: "lint 详细" 查看完整报告，或 "lint 并修复" 自动修复格式问题
```

### 4.2 完整报告

详细模式（"lint 详细"）输出完整报告：

```
kb-lint Report

## 问题概览
- 格式问题: 5 个（可自动修复）
- 结构问题: 51 个（建议修复）
- 内容问题: 0 个

## 格式问题详情
（无格式问题）

## 结构问题详情

### Orphan Pages (18)
  entities/人物/:
    - 刘邦.md (建议: 添加到 "人物" section)
    - 韩信.md (建议: 添加到 "人物" section)
  entities/地点/:
    - 长安.md (建议: 添加到 "地点" section)
  concepts/:
    - 商鞅变法.md (建议: 添加到 "concepts" section)

### Broken Wikilinks (33)
  entities/卫鞅.md:
    [[秦惠文君]] (建议: 创建页面或删除链接)
  concepts/商鞅变法.md:
    [[甘龙]], [[杜挚]] (建议: 创建页面或删除链接)

## 内容问题详情
（无内容问题）

## 下一步
- 格式问题: 执行 "lint 并修复" 自动修复
- 结构问题: 执行 "lint 建议" 查看修复建议
- 内容问题: 需人工判断处理
```

---

## 5. 修复策略

### 5.1 格式问题修复（自动）

| 问题 | 修复逻辑 | 当前实现 | 改进 |
|------|---------|---------|------|
| wikilink 不平衡 | 移除孤立 `[[`/`]]` | ✓ fix.py | 不改动 |
| 缺失 source | 添加 placeholder | ✓ fix.py | 改进：从 raw-registry 推断真实路径 |

### 5.2 结构问题建议

| 问题 | 建议内容 |
|------|---------|
| orphan pages | 建议添加到哪个 section（基于路径推断） |
| broken wikilinks | 建议创建缺失页面或删除链接 |

**suggest_section 推断逻辑**：

```python
def infer_section(file_path, wiki_dir):
    rel_path = file_path.relative_to(wiki_dir)
    parts = rel_path.parts
    
    # minimal: wiki/entities/foo.md → entities
    # history: wiki/entities/人物/刘邦.md → 人物
    
    if len(parts) >= 2:
        return parts[1] if parts[1] != parts[0] else parts[0]
    else:
        return parts[0]
```

---

## 6. Skill 意图识别

| 用户意图 | 执行方式 | 输出内容 |
|---------|---------|---------|
| "lint wiki" | 检测所有问题 | 仅摘要 |
| "lint 详细" | 检测所有问题 | 完整报告 |
| "lint 建议" | 检测所有问题 | 摘要 + 结构问题建议 |
| "lint 并修复" | 检测 + 自动修复格式问题 | 摘要 + 修复结果 |

触发词示例：
- 默认："lint wiki"、"检查 wiki"
- 详细："lint 详细"、"完整检查"
- 建议："lint 建议"、"检查建议"
- 修复："lint 并修复"、"检查并修复"

---

## 7. 实现方案

### 7.1 改动清单

| 文件 | 改动内容 | 优先级 |
|------|---------|-------|
| `SKILL.md` | 新增意图识别 + 执行流程改进 | 高 |
| `lint.py` | 改为分级调用 + 输出结构化报告 | 高 |
| `_orphans.py` | 新增 suggest_section（路径推断） | 高 |
| `fix.py` | 新增 source 路径推断 | 高 |
| `_report.py` | 新增：结构化报告生成 | 高 |
| `_semantic.py` | 新增 title heading 推断 | 中 |

### 7.2 实现顺序

1. 新增 `_report.py`（结构化报告生成）
2. 改进 `lint.py`（分级调用 + 报告输出）
3. 改进 `_orphans.py`（路径推断）
4. 改进 `fix.py`（source 路径推断）
5. 改进 `SKILL.md`（意图识别）
6. 改进 `_semantic.py`（title heading 推断）

---

## 8. 实施规则

### 规则 1：使用 skill-creator skill 进行实际优化工作

在实施阶段，应使用 skill-creator skill 对 kb-lint 进行实际优化：
- 创建 evals.json（测试意图识别 + 报告格式）
- 运行 eval-viewer 进行用户审阅
- 根据反馈迭代改进

### 规则 2：渐进式实施

实施顺序：
1. 先完成 scripts 改进（_report.py + lint.py + _orphans.py + fix.py）
2. 测试验证 scripts 行为
3. 最后更新 SKILL.md（意图识别）

---

## 9. 审阅记录

- 创建日期：2026-04-24
- 审阅状态：待审阅
- 审阅人：用户