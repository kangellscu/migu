---
name: kb-compile
description: "Read files, extract entities and concepts (dynamic classification), generate wiki pages. Use when user asks to compile knowledge base or extract information from sources."
version: 1.0
---

# kb-compile

## 职责

读取 raw/.extracted/ 或 raw/ 文件，LLM 提取实体和概念，生成 wiki 页面。

## 执行流程

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：
   - 产物路径 != `-`：调用 `read_file.py` 读取产物路径对应文件
   - 产物路径 == `-`：调用 `read_file.py` 读取 raw 文件本身
3. **LLM 信息提取**：
   - 阅读文档内容
   - 提取信息片段
   - 动态判断类型：
     - **实体**：具体、可命名、有时空属性（人物、地点、组织、物品等）
     - **概念**：抽象、主题性、无时空属性（思想、制度、文化等）
   - 识别关系、消歧别名
   - 参考 templates 约束输出格式
4. **LLM wiki 生成**：
   - 检查 wiki/ 是否已有对应文档
   - 无：根据 templates 创建新文档
   - 有：阅读现有内容，合并新信息（增量更新）
   - wiki 文档 source 字段：`- source: [[raw/path/to/source.md]]`
5. **更新 index.md**：添加新页面索引到对应 section
6. **更新 raw-registry.md**：调用 `update_registry.py` 更新编译状态

## 增量更新逻辑

| 场景 | LLM 处理方式 |
|------|-------------|
| 信息补充 | 追加新字段或补充现有字段内容 |
| 信息冲突 | 判断是否同一信息的不同表述，或保留冲突注释 |
| 关系去重 | 判断两个关系是否重复，合并 |
| 结构调整 | 根据信息量调整页面结构 |

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

## templates 说明

| template | 用途 |
|----------|------|
| entity-template.md | 实体页面格式 |
| concept-template.md | 概念页面格式 |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_file.py | 根据路径读取文件 | 步骤 2：读取待编译文件内容 | 必须 |
| update_registry.py | 更新 raw-registry.md | 步骤 6：更新编译状态 | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script

## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 wiki 文档（Y 实体，Z 概念）
2. **下一步提示**：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库

示例：
```
处理结果：生成 8 个 wiki 文档（5 实体，3 概念）
下一步提示：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库
```