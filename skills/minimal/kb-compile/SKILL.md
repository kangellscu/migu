---
title: kb-compile
version: 1.0
created: 2026-04-22
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
   - 提取实体：人物、地点、事件等
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
| person-template.md | 人物实体页面格式 |
| place-template.md | 地点实体页面格式 |
| event-template.md | 事件实体页面格式 |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_file.py | 根据路径读取文件 | 步骤 2：读取待编译文件内容 | 必须 |
| update_registry.py | 更新 raw-registry.md | 步骤 6：更新编译状态 | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
