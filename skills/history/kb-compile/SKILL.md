---
name: kb-compile
description: "Read extracted files, extract entities (person/place/event) and concepts (institution/official/thought), generate wiki pages, update index.md and raw-registry.md. Use when user asks to compile history knowledge base, generate wiki pages, or extract historical entities and concepts from sources."
version: 1.0
---

# kb-compile

## 职责

读取 raw/.extracted/ 或 raw/ 文件，LLM 提取实体，生成 wiki 页面。

## 执行流程

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：
   - 产物路径 != `-`：调用 `read_file.py` 读取产物路径对应文件
   - 产物路径 == `-`：调用 `read_file.py` 读取 raw 文件本身
3. **LLM 实体提取**：
   - 阅读文档内容
   - 提取实体：人物、地点、事件、制度、官职、思想
   - 识别关系、消歧别名
   - 参考 references/templates/ 约束输出格式
4. **LLM wiki 生成**：
   - 检查 wiki/ 是否已有对应实体文档
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

## templates 说明

| template | 用途 |
|----------|------|
| person-template.md | 历史人物页面格式 |
| place-template.md | 历史地点页面格式 |
| event-template.md | 历史事件页面格式 |
| institution-template.md | 制度页面格式 |
| official-template.md | 官职页面格式 |
| thought-template.md | 思想页面格式 |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_file.py | 根据路径读取文件 | 步骤 2：读取待编译文件内容 | 必须 |
| update_registry.py | 更新 raw-registry.md | 步骤 6：更新编译状态 | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script

## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 wiki 文档（Y 人物，Z 地点，W 事件，U 制度，V 官职，T 思想）
2. **下一步提示**：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库

示例：
```
处理结果：生成 15 个 wiki 文档（5 人物，3 地点，2 事件，2 制度，2 官职，1 思想）
下一步提示：可运行 kb-lint 检查 wiki 格式，或运行 kb-query 查询知识库
```
