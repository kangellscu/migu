---
title: Minimal kb-compile Generic Architecture Fix
created: 2026-04-24
type: spec
status: draft
version: 1.0
related: problems.md (architecture inconsistency)
---

# Minimal kb-compile Generic Architecture Fix

> 修复 minimal kb-compile 与 minimal AGENTS.md 架构不一致问题。
> 
> minimal AGENTS.md 声明通用基础，但 minimal kb-compile 预设历史类模板（person/place/event）。

---

## 1. 问题分析

### 1.1 架构不一致

| 组件 | 当前状态 | 应该是 |
|------|---------|--------|
| minimal AGENTS.md | 通用基础，domain-specific types defined in derived rules | ✓ 正确 |
| minimal kb-compile SKILL.md | "提取实体：人物、地点、事件等" | ✗ 预设历史类 |
| minimal templates | person-template, place-template, event-template | ✗ 预设历史类 |

### 1.2 Scope 分离

| Scope | 负责内容 | 不应涉及 |
|-------|---------|---------|
| 脚手架 | rules 继承、skills.json、migu CLI | skills 内部逻辑 |
| 知识库 | skills 执行、wiki 生成 | 脚手架机制 |

minimal kb-compile 是知识库 scope，不应提及"领域定制"（脚手架层概念）。

---

## 2. 修复方案

### 2.1 Templates 变更

**删除历史类模板**：
```
skills/minimal/kb-compile/references/templates/
  删除: person-template.md
  删除: place-template.md  
  删除: event-template.md
```

**创建通用模板**：

**entity-template.md**：
```markdown
---
type: entity
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

**concept-template.md**：
```markdown
---
type: concept
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

### 2.2 SKILL.md 变更

**文件**: `skills/minimal/kb-compile/SKILL.md`

**变更点**：

#### 2.2.1 description (line 3)

旧：
```markdown
description: "Read extracted files, extract entities (person/place/event), generate wiki pages..."
```

新：
```markdown
description: "Read files, extract entities and concepts (dynamic classification), generate wiki pages. Use when user asks to compile knowledge base or extract information from sources."
```

#### 2.2.2 步骤 3 LLM 信息提取 (line 19-23)

旧：
```markdown
3. **LLM 实体提取**：
   - 阅读文档内容
   - 提取实体：人物、地点、事件等
   - 识别关系、消歧别名
   - 参考 references/templates/ 约束输出格式
```

新：
```markdown
3. **LLM 信息提取**：
   - 阅读文档内容
   - 提取信息片段
   - 动态判断类型：
     - **实体**：具体、可命名、有时空属性（人物、地点、组织、物品等）
     - **概念**：抽象、主题性、无时空属性（思想、制度、文化等）
   - 识别关系、消歧别名
   - 参考 templates 约束输出格式
```

#### 2.2.3 新增识别逻辑 section

在 "增量更新逻辑" 之后添加：

```markdown
## 实体 vs 概念识别

LLM 根据内容特征动态判断：

| 特征 | 实体倾向 | 概念倾向 |
|------|---------|---------|
| 时间属性 | 有具体时间（生卒、成立时间） | 无具体时间 |
| 地点属性 | 有具体地点（出生地、所在地） | 无具体地点 |
| 可命名性 | 具体个体（可指认） | 抽象类别（无法指认） |
| 参与者 | 通常有参与者 | 无参与者概念 |

**输出对应目录**：
- `type: entity` → wiki/entities/
- `type: concept` → wiki/concepts/
```

#### 2.2.4 templates 说明 (line 41-47)

旧：
```markdown
| template | 用途 |
|----------|------|
| person-template.md | 人物实体页面格式 |
| place-template.md | 地点实体页面格式 |
| event-template.md | 事件实体页面格式 |
```

新：
```markdown
| template | 用途 |
|----------|------|
| entity-template.md | 实体页面格式 |
| concept-template.md | 概念页面格式 |
```

#### 2.2.5 输出摘要示例 (line 59-63)

旧：
```markdown
处理结果：生成 12 个 wiki 文档（5 人物，4 地点，3 事件）
```

新：
```markdown
处理结果：生成 8 个 wiki 文档（5 实体，3 概念）
```

---

## 3. 不修改文件

### 3.1 history kb-compile

history kb-compile 已正确设计：
- templates: person/place/event/institution/official/thought（历史类）
- SKILL.md: 明确历史类提取
- history skills.json 选择 `source: history`

**无需修改**。

### 3.2 minimal AGENTS.md

minimal AGENTS.md 已正确声明：
> "Entity/concept types are domain-specific. Minimal provides base structure."

**无需修改**。

---

## 4. 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `skills/minimal/kb-compile/references/templates/person-template.md` | 删除 | 预设历史类 |
| `skills/minimal/kb-compile/references/templates/place-template.md` | 删除 | 预设历史类 |
| `skills/minimal/kb-compile/references/templates/event-template.md` | 删除 | 预设历史类 |
| `skills/minimal/kb-compile/references/templates/entity-template.md` | 创建 | 通用实体模板 |
| `skills/minimal/kb-compile/references/templates/concept-template.md` | 创建 | 通用概念模板 |
| `skills/minimal/kb-compile/SKILL.md` | 修改 | 通用提取 + 识别逻辑 |

---

## 5. 验证计划

1. 删除历史类模板，创建通用模板
2. 更新 minimal kb-compile SKILL.md
3. 测试：migu init minimal → 检查 templates 安装
4. 验证：minimal kb-compile SKILL.md 不含"人物、地点、事件"等历史类词汇
5. 验证：history kb-compile 保持历史类设计