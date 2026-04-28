---
title: templates 复制机制修复与知识库 README 模板设计
created: 2026-04-28
type: spec
status: draft
version: 1.0
last_updated: 2026-04-28
changes: Initial design
---

# templates 复制机制修复与知识库 README 模板设计

> **受众声明**：本 spec 服务于脚手架开发者，修复 templates 复制机制并创建知识库 README 模板。
>
> **背景**：用户创建知识库后，需要一份 README.md 文档介绍如何使用知识库。发现当前实现与 spec 定义不一致（templates 硬编码而非从 templates/ 复制）。

---

## 1. 问题分析

### 1.1 当前实现与 Spec 差异

| 文件 | Spec 定义 | 当前实现 | 问题 |
|------|-----------|---------|------|
| templates 来源 | rules/*/templates/*.md | creator.py 硬编码 | **不一致** |
| templates 继承 | 同名覆盖，不存在继承 minimal | 无继承机制 | **不一致** |
| index.md sections | 根据 structure.json 动态生成 | 硬编码 entities/concepts/synthesis | **不一致** |
| AGENTS.md | 存在覆盖，不存在继承 | 有 fallback | **一致** |

### 1.2 Spec 定义回顾

**§3.1 继承规则**：
- templates/*.md：同名文件覆盖，不存在则继承 minimal/templates/ 对应文件

**§4.1 index.md 生成方式**：
- migu init：根据 structure.json wiki 目录动态生成 sections

---

## 2. 设计目标

### 2.1 templates 复制机制修复

**目标**：使 creator.py 与 spec 定义一致

**设计约束**：
- templates 文件从 rules/*/templates/ 目录复制到知识库根目录
- 继承机制：rules_name/templates/ 无文件时，fallback 到 minimal/templates/
- index.md sections 根据 structure.json wiki 目录动态生成
- 保留 frontmatter（版本信息）

**不改变的内容**：
- 执行流程步骤顺序不变
- AGENTS.md 继承机制已正确实现

### 2.2 知识库 README 模板创建

**目标**：为知识库使用者提供一份简洁完备的使用指南

**目标受众**：知识库使用者（无背景知识，读完立刻使用）

**设计约束**：
- 语言：中文
- 长度：约 120 行（简洁）
- 结构：6 部分（知识库是什么、目录结构、快速上手、Skills 工作流程、使用约束、示例）
- 内容：三层架构简要说明（不引用 Karpathy）、表格概览（不详细展开）、完整示例（包含具体命令）

**文件位置**：
- 模板文件：rules/minimal/templates/kb-README.md
- 复制位置：知识库根目录 README.md（migu init 复制并重命名）

**继承设计**：
- history 规则继承 minimal/templates/kb-README.md（差异小，无需覆盖）

---

## 3. 知识库 README 模板内容设计

### 3.1 文档结构

```
# 知识库使用指南

## 知识库是什么
[三层架构表格：Raw/Wiki/Schema]

## 目录结构
[知识库目录树]

## 快速上手
[4-step 示例：添加文件、预处理、提取、查看状态]

## Skills 工作流程
[表格：skill 名称、作用、触发时机]
[典型工作流程]
[Skills 使用方式]

## 使用约束
[分类：可以修改 vs 不要修改]
[违反约束的恢复方式]

## 示例：完整流程
[完整流程示例：kb-ingest → kb-compile → kb-lint → kb-query → kb-archive]
```

### 3.2 内容要点

**知识库是什么**：
- 三层架构表格（不引用 Karpathy 名称）
- 核心理念：wiki 是持久化可累积产物

**快速上手**：
- Step 1: 添加源文件（具体命令）
- Step 2: 预处理（触发 skill）
- Step 3: 提取内容
- Step 4: 查看状态

**Skills 工作流程**：
- 表格概览（不详细展开每个 skill）
- 典型工作流程图
- Skills 使用方式说明（agent 指令，触发方式）

**使用约束**：
- 可以修改：raw/, output/, AGENTS.md
- 不要修改：raw/.extracted/, wiki/, raw-registry.md, index.md, log.md

---

## 4. docs/cli-reference.md 一致化设计

### 4.1 问题

docs/cli-reference.md 执行流程与 spec 定义不一致：

| docs/cli-reference.md | spec §3.2 | 问题 |
|----------------------|-----------|------|
| 2. Validate rules configuration | 2. 验证三方一致性 | **不一致** |
| **缺失** | 3. 合并配置 | **缺失** |
| 7. Copy AGENTS.md | 未单独列出 | **不一致** |

### 4.2 设计约束

**目标**：使 docs/cli-reference.md 执行流程与 spec 一致

**修改内容**：
- Line 44：改为 "Validate three-party consistency"
- Line 45：改为 "Merge configuration (inherit minimal + override)"
- Line 49-50：合并为 "Copy template files (preserve frontmatter)"

**修改后执行流程**：
1. Check if `<target-dir>` exists (error if exists)
2. Validate three-party consistency
3. Merge configuration (inherit minimal + override specified rules)
4. Create directory structure (from structure.json)
5. Install skills (from skills.json)
6. Create skills-lock.json
7. Copy template files (preserve frontmatter)

---

## 5. 实现任务

### Task 1: 修复 creator.py templates 复制逻辑

**修改文件**：migu/init/creator.py

**修改内容**：
- 实现 templates 复制逻辑
- 实现 templates 继承逻辑
- 实现 index.md 动态生成

### Task 2: 创建知识库 README 模板

**创建文件**：rules/minimal/templates/kb-README.md

**内容**：中文，约 120 行，6 部分

### Task 3: 测试完整流程

**验证**：
- migu init test-kb --rules minimal
- migu init test-history --rules history
- templates 继承正常

### Task 4: docs/cli-reference.md 一致化

**修改文件**：docs/cli-reference.md

**修改内容**：执行流程与 spec 一致

---

## 6. 实现约束

**不改变的内容**：
- AGENTS.md 继承机制（已正确实现）
- 执行流程步骤顺序不变
- spec 文件不需要修改（设计意图已正确）

**需要修改的内容**：
- creator.py 实现（使其与 spec 一致）
- 创建 kb-README.md 模板文件
- docs/cli-reference.md（使其与 spec 一致）

---

## 附录：设计决策

### A.1 为什么 history 继承 minimal/templates/kb-README.md？

理由：
- README.md 核心内容相同（工作流程、使用约束）
- 差异只在示例（用户可理解）
- 简化维护（只需维护 minimal/templates/kb-README.md）
- 未来可扩展（history 按需覆盖）

### A.2 为什么不详细展开每个 skill？

理由：
- README.md 目标是简洁完备（无背景知识读完立刻使用）
- 详细 skill 说明在 SKILL.md 中
- 表格概览足够让用户理解工作流程

### A.3 为什么使用中文？

理由：
- 知识库使用者可能不是开发者
- 中文更友好
- minimal 规则面向通用知识库（中文用户为主）