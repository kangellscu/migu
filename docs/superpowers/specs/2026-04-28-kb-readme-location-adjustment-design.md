---
title: kb-README.md 位置调整设计
created: 2026-04-28
type: spec
status: draft
version: 1.0
last_updated: 2026-04-28
changes: Initial design
---

# kb-README.md 位置调整设计

> **受众声明**：本 spec 服务于脚手架开发者，调整 kb-README.md 文件位置。
>
> **背景**：kb-README.md 当前位于 templates/ 目录下，但其性质与 templates/ 其他文件不同（静态用户文档 vs 自动维护模板）。应移到 rules/ 根目录，与 AGENTS.md 同级。

---

## 1. 问题分析

### 1.1 当前状态

| 文件 | 位置 | 性质 | 维护方 |
|------|------|------|--------|
| kb-README.md | templates/ | 静态用户文档 | 用户可定制 |
| index.md | templates/ | 文档索引 | kb-compile/kb-archive 自动更新 |
| log.md | templates/ | 操作日志 | skills 自动追加 |
| raw-registry.md | templates/ | 文件注册表 | kb-ingest/kb-compile 自动更新 |
| AGENTS.md | rules/ 根目录 | 知识库 schema | 用户可定制 |

### 1.2 问题

- kb-README.md 与 templates/ 其他文件职责不一致（静态 vs 自动维护）
- kb-README.md 与 AGENTS.md 性质相似（都是用户可定制文件），但位置不同
- templates/ 目录职责不清晰

---

## 2. 设计意图

**目标**：将 kb-README.md 从 templates/ 移到 rules/ 根目录，与 AGENTS.md 同级

**意图**：
- 聃责分离：templates/ 只放自动维护模板，rules/ 根目录放用户可定制文件
- 概念一致：kb-README.md 与 AGENTS.md 都是用户可定制文件，位置一致
- 继承自然：kb-README.md 与 AGENTS.md 共享相同的继承逻辑

---

## 3. 设计约束

### 3.1 文件位置约束

- kb-README.md 必须位于 `rules/*/` 根目录（与 AGENTS.md 同级）
- templates/ 目录只包含自动维护模板（index.md, log.md, raw-registry.md）
- templates/ 目录不包含静态用户文档

### 3.2 继承约束

- kb-README.md 继承规则与 AGENTS.md 相同：存在覆盖，不存在继承 minimal
- history 无 kb-README.md → 自动继承 minimal kb-README.md
- 用户可按需覆盖 kb-README.md（如 history 提供历史知识库专属使用指南）

### 3.3 复制约束

- kb-README.md 复制到知识库根目录时重命名为 README.md
- kb-README.md 复制逻辑独立于 templates/ 复制逻辑（类似 AGENTS.md）
- templates/ 复制逻辑不处理 kb-README.md（因为不在 templates/ 目录）

---

## 4. 文件位置对比

### 4.1 调整前

```
rules/minimal/
├── AGENTS.md
├── skills.json
├── structure.json
└── templates/
    ├── index.md
    ├── kb-README.md  ← 当前位置
    ├── log.md
    └── raw-registry.md
```

### 4.2 调整后

```
rules/minimal/
├── AGENTS.md
├── kb-README.md  ← 新位置（与 AGENTS.md 同级）
├── skills.json
├── structure.json
└ templates/
    ├── index.md
    ├── log.md
    └ raw-registry.md
```

---

## 5. 聃责定义

### 5.1 templates/ 聃责

**意图**：存放知识库运行所需的初始模板

**约束**：
- 模板会被 skills 自动维护更新
- 用户不应手动修改（违反约束会导致 skills 功能异常）
- 包含文件：index.md, log.md, raw-registry.md
- 不包含静态用户文档

### 5.2 rules/ 根目录职责

**意图**：存放规则定义和用户可定制文件

**约束**：
- 用户可定制文件可以被用户修改覆盖
- 包含文件：
  - AGENTS.md（知识库 schema）
  - kb-README.md（知识库使用指南）
  - skills.json（Skills 选择，独立配置）
  - structure.json（目录结构，可继承）

---

## 6. 实现任务

### Task 1: 移动 kb-README.md 文件

**目标**：移动文件位置

**约束**：
- 从 `rules/minimal/templates/kb-README.md` 移到 `rules/minimal/kb-README.md`
- Git 操作应保留文件历史（使用 git mv）

### Task 2: 修改 creator.py 复制逻辑

**目标**：实现新的复制逻辑

**约束**：
- 添加 kb-README.md 单独复制逻辑（类似 AGENTS.md）
- 从 templates/ 复制逻辑中移除 kb-README.md 处理（移除重命名逻辑）
- kb-README.md 复制时重命名为 README.md

### Task 3: 更新测试

**目标**：验证新的复制逻辑

**约束**：
- 测试 kb-README.md 从 rules/ 根目录复制
- 测试 kb-README.md 继承（history 继承 minimal）
- 测试知识库根目录生成 README.md（从 kb-README.md）

---

## 附录：设计决策

### A.1 为什么 kb-README.md 继承规则与 AGENTS.md 相同？

理由：
- kb-README.md 与 AGENTS.md 性质相似（都是用户可定制文件）
- 共享继承逻辑简化实现（使用相同的 fallback 模式）
- 用户可按需覆盖（如 history 提供历史知识库专属使用指南）

### A.2 为什么不放在 templates/ 目录？

理由：
- templates/ 目录职责是"自动维护模板"
- kb-README.md 是静态用户文档（skills 不更新）
- 聃责分离避免混淆（templates/ 只放运行所需模板）

### A.3 为什么复制时重命名为 README.md？

理由：
- 知识库根目录需要 README.md（GitHub 标准惯例）
- 模板文件名 kb-README.md 避免与知识库 README.md 混淆
- 复制时重命名清晰表达意图（模板 → 实际使用文件）