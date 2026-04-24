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

触发词示例：
- 默认："compile raw 文件"、"开始编译"
- 完整："完整 compile"、"穷尽提取"、"确保不遗漏"
- 补充："补充 compile"、"继续提取遗漏"
- 重新："重新 compile"、"重新编译 xxx 文件"

## 执行流程

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：
   - 产物路径 != `-`：调用 `read_file.py` 读取产物路径对应文件
   - 产物路径 == `-`：调用 `read_file.py` 读取 raw 文件本身
3. **LLM 提取（根据意图）**：

   **默认模式**：
   - 单轮提取实体/概念
   - 输出提取清单 + 遗漏清单
   - 参考 templates 约束输出格式

   **完整模式**：
   - 第一轮：提取实体 → 输出提取清单 + 遗漏清单 A
   - 第二轮（遗漏清单 A 非空）：针对性补充 → 输出遗漏清单 B
   - 第三轮（遗漏清单 B 非空）：针对性补充 → 输出遗漏清单 C
   - 上限：3 轮
   - 收敛条件：连续两轮无新遗漏

   **补充模式**：
   - 读取 raw-registry.md 的"剩余遗漏"字段
   - 针对遗漏实体提取详情
   - 执行迭代检查新遗漏

   **重新模式**：
   - 清空该文件的编译状态
   - 执行完整模式
4. **LLM wiki 生成**：
   - 检查 wiki/ 是否已有对应文档
   - 无：根据 templates 创建新文档
   - 有：阅读现有内容，合并新信息（增量更新）
   - wiki 文档 source 字段：`- source: [[raw/path/to/source.md]]`
5. **更新 index.md**：添加新页面索引到对应 section
6. **更新 raw-registry.md**：调用 `update_registry.py`
   - 编译状态：已编译 / 部分编译
   - 剩余遗漏：空 / 实体1, 实体2, ...（逗号分隔）
   - 最近处理日期：当前日期

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
2. **迭代信息**（完整/补充模式）：
   - 迭代次数：N 轮
   - 收敛状态：已收敛 / 未收敛（达到上限）
3. **剩余遗漏**（如有）：
   - 实体列表：A, B, C
   - 提示：可执行"补充 compile"继续提取
4. **下一步提示**：
   - 可运行 kb-lint 检查 wiki 格式
   - 如有剩余遗漏，可执行"补充 compile"

示例（已收敛）：
```
处理结果：生成 8 个 wiki 文档（5 实体，3 概念）
迭代信息：迭代 3 轮，已收敛
剩余遗漏：空
下一步提示：可运行 kb-lint 检查 wiki 格式
```

示例（未收敛）：
```
处理结果：生成 12 个 wiki 文档（8 实体，4 概念）
迭代信息：迭代 3 轮，未收敛（达到上限）
剩余遗漏：范增, 龙且, 钟离昧
下一步提示：可执行"补充 compile"补充遗漏实体
```