---
title: kb-compile Optimization Design
created: 2026-04-27
type: spec
audience: migu skill 开发者
related_spec: docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# kb-compile Optimization Design

> 本 spec 定义 minimal/kb-compile skill 的优化方案，解决两个问题：
> 1. 内部冗余内容（178行过长）
> 2. entity/concept 缺乏 subtype 区分具体类型

---

## 1. 问题分析

### 1.1 冗余问题

minimal/kb-compile/SKILL.md 当前 178 行，存在以下冗余：

| 冗余点 | 位置 | 问题 |
|-------|------|------|
| 意图识别 vs 执行流程 | 两节重复描述 4 种模式 | 同一信息说两遍 |
| templates 说明 | 多处重复"约束格式不约束范围" | 重复 3 次 |
| 实体类型 vs 遗漏检查 | 高度重叠的内容 | 检查项即类型本身 |
| 提取原则 | 单独一节 | 已隐含在类型定义中 |

### 1.2 subtype 问题

当前 templates frontmatter：
```yaml
type: entity  # 无法区分 person/place/event 等
```

LLM 提取时能识别不同类型（person、place、event），但模板无法记录这种区分。

---

## 2. 设计决策

### 2.1 精简目标

- 删除冗余内容
- 改善结构清晰度
- 预期精简至 ~95 行（减少 47%）

### 2.2 subtype 设计

**方案**：预定义常见类型 + 允许扩展

| 类别 | 预定义 subtype |
|------|---------------|
| 实体 | person, place, organization, event, product, tool, {{自定义}} |
| 概念 | policy, methodology, phenomenon, {{自定义}} |

**理由**：
- 预定义给 LLM 提供引导，减少歧义
- "允许扩展" 保留灵活性
- 后续 kb-query/filter 可按 subtype 筛选

### 2.3 history 版本

history 保持不变（已有 6 个细分模板，frontmatter 使用 `type: person` 等具体类型）。

---

## 3. Templates 改动

### 3.1 entity-template.md

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

改动：仅添加 `subtype: {{subtype}}` 字段。

### 3.2 concept-template.md

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

改动：仅添加 `subtype: {{subtype}}` 字段。

---

## 4. SKILL.md 结构调整

### 4.1 新结构

```markdown
## 职责
（一句话）

## 意图识别
（表格 + 触发词示例）

## 执行流程
（7 步流程，合并增量更新逻辑）

## 实体/概念提取
（新节：类型定义 + subtype 预定义 + 事件归属说明）

## templates说明
（一句话）

## scripts使用说明
（表格不变）

## 输出摘要
（不变）
```

### 4.2 删除的节

- "增量更新逻辑"（合并到执行流程步骤 4）
- "遗漏清单检查指导"（删除，检查项即类型本身）
- "提取原则"（删除，已隐含在实体/概念提取节）

---

## 5. 精简版 SKILL.md 内容

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

**行数**：约 95 行（从 178 行精简 47%）

---

---

## 6. Directory Structure 补充

### 6.1 问题

kb-compile 和 kb-archive 都会更新 index.md、log.md，但 LLM 经常误将它们创建在 wiki/ 下而非根目录。原因是 Directory Structure 只定义了目录，未定义根目录文件。

### 6.2 解决方案

在 rules/minimal/AGENTS.md Directory Structure 增加：

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

### 6.3 文件位置说明

| 文件 | 位置 | 用途 | 创建时机 |
|------|------|------|---------|
| raw-registry.md | 根目录 | raw 文件状态注册表 | kb-ingest |
| index.md | 根目录 | wiki 文档索引 | kb-compile |
| log.md | 根目录 | 操作日志 | kb-compile/kb-archive |

---

## 7. 实施范围

| 文件 | 改动 |
|------|------|
| minimal/kb-compile/SKILL.md | 精简内容 + 新结构 |
| minimal/kb-compile/references/templates/entity-template.md | 添加 subtype 字段 |
| minimal/kb-compile/references/templates/concept-template.md | 添加 subtype 字段 |
| rules/minimal/AGENTS.md | Directory Structure 增加 3 个根目录文件 |
| history/kb-compile/* | 不改动 |

---

## 8. 实施方法

使用 skill-creator skill 对 kb-compile 进行实际优化工作：
- 创建测试用例验证优化效果
- 运行 with-skill 和 baseline 对比
- 根据评测结果迭代改进