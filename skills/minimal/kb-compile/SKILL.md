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