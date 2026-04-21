---
title: Skills Implementation Guide
created: 2026-04-21
type: guide
audience: 知识库开发者（Skills SKILL.md 编写者）
related_spec: docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
---

# Skills Implementation Guide

> 本文档是 Skills 流程设计指导文档，帮助知识库开发者编写 SKILL.md。
>
> 最终实现结果写入 `skills/<type>/<skill-name>/SKILL.md`。

---

## 与 Karpathy LLM-WIKI Operations 的对应关系

| Karpathy Operation | migu Skill | 说明 |
|--------------------|------------|------|
| Ingest | kb-ingest | 预处理 raw 文件，输出到 raw/.extracted/ |
| Ingest（编译部分） | kb-compile | 读取文件、提取实体、生成 wiki 页面 |
| Query | kb-query | Wiki 查询 + 回溯模式 + 生成 report |
| Query（回写部分） | kb-archive | 接收 report + 有机融入回写 |
| Lint | kb-lint | Wiki 检查（语法、语义、模板一致性） |
| - | kb-status | 仪表盘展示（migu 特有） |

## 附录：SKILL.md 编写模板

### 基本结构

```markdown
---
title: <skill-name>
version: 1.0
created: YYYY-MM-DD
---

# <skill-name>

## 职责

<一句话描述该 skill 的职责>

## 执行流程

<按步骤描述执行流程，包含意图识别、条件分支、边界处理>

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| <script-name> | <用途描述> | <调用时机> | 必须/可选 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
- 可选：agent 可判断是否需要调用，可用其他方式替代

## references 说明

| reference | 用途 |
|-----------|------|
| <reference-name> | <用途描述> |

## 输入输出

**输入**：
- <输入项>

**输出**：
- <输出项>

## 边界情况

| 场景 | 处理方式 |
|------|----------|
| <场景描述> | <处理方式> |
```

### 注意事项

1. **完全 LLM 的 skill**（如 kb-compile）：流程步骤直接写 LLM 操作，不写具体算法
2. **含 scripts 的 skill**：流程步骤写"调用 xxx.py"，scripts 使用说明表格详细描述
3. **有会话依赖的 skill**（如 kb-archive）：明确声明会话依赖，说明同一 agent session 的要求
4. **有条件分支的 skill**：使用意图识别表格，明确各分支的触发条件和执行方式

---

## 1. kb-ingest 流程设计

**职责**：扫描 raw/、预处理文件、输出到 raw/.extracted/。

**适用范围**：见 scaffold-design §4.2 按类型分组。

### 1.1 流程步骤

1. **扫描 raw/ 目录**：检测所有文件（递归）
2. **对比 raw-registry.md**：找出未记录的文件，添加新条目（预处理状态：未处理）
3. **处理文件**：
   - markdown：
     - 无需预处理：标记为"已处理"，产物路径 `-`
     - 需预处理（编码修复/图片下载）：调用 normalize_markdown.py → 输出到 `raw/.extracted/`，记录产物路径
   - pdf：调用 convert_pdf.py → 输出 markdown + 图片到 `raw/.extracted/`，记录产物路径
   - image：标记为"无需处理"，产物路径 `-`
4. **更新 raw-registry.md**：
   - 预处理状态：已处理 / 无需处理
   - 产物路径：有产物时记录路径，无产物时 `-`
   - 最近处理日期：当前日期

### 1.2 类型判断

根据文件扩展名：

| 扩展名 | 类型 | 处理方式 |
|--------|------|---------|
| .md | markdown | 规范化检查 → 可能生成 raw/.extracted/（编码修复/图片下载时） |
| .pdf | pdf | 转 markdown + 提取图片 → raw/.extracted/ |
| .png, .jpg, .gif | image | 无需处理，直接引用 |

### 1.3 markdown 预处理场景

| 场景 | 产物路径 | 说明 |
|------|---------|------|
| 无需预处理 | `-` | 文件格式规范，编码正常，无 http 图片 |
| 编码修复 | raw/.extracted/... | 文件名或内容含特殊编码，规范化后输出 |
| 图片下载 | raw/.extracted/... | 含 http 图片，下载到本地，更新链接后输出 |

### 1.4 scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| scan_raw.py | 扫描 raw/ 目录，检测新文件 | 步骤 1：检测 raw/ 目录中的新文件 | 必须 |
| validate_batch.py | 验证批次处理逻辑 | 步骤 2：对比 raw-registry.md 时验证 | 可选 |
| normalize_markdown.py | 规范化 markdown 文件 | 步骤 3：处理需预处理的 markdown | 必须 |
| convert_pdf.py | 转换 PDF 为 markdown | 步骤 3：处理 PDF 文件 | 必须 |

---

## 2. kb-compile 流程设计

**职责**：读取文件、提取实体、生成 wiki 页面（完全 LLM）。

**适用范围**：见 scaffold-design §4.2 按类型分组。

### 2.1 minimal 版本流程

kb-compile 采用完全 LLM 方案：实体提取和 wiki 生成均由 agent（LLM）完成。

#### 流程步骤

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：
   - 产物路径 != `-`：读取产物路径对应文件
   - 产物路径 == `-`：读取 raw 文件本身
3. **LLM 实体提取**：
   - 阅读 document 内容
   - 提取实体：人物、地点、事件、制度等
   - 识别关系、消歧别名
   - 参考 references/templates/ 约束输出格式
4. **LLM wiki 生成**：
   - 检查 wiki/ 是否已有对应实体文档
   - 无：根据 templates 创建新文档
   - 有：阅读现有内容，合并新信息（增量更新）
   - wiki 文档 source 字段指向 raw 文件
5. **更新 index.md**：添加新页面索引
6. **更新 raw-registry.md**：
   - 编译状态：已编译 / 部分编译
   - 最近处理日期：当前日期

#### 增量更新逻辑

当 wiki/ 已存在同名实体文档时：

| 场景 | LLM 处理方式 |
|------|-------------|
| 信息补充 | 追加新字段或补充现有字段内容 |
| 信息冲突 | 判断是否同一信息的不同表述，或保留冲突注释 |
| 关系去重 | 判断两个关系是否重复，合并 |
| 结构调整 | 根据信息量调整页面结构 |

#### 重新编译意图识别

SKILL.md 包含意图分支逻辑：

| 用户意图 | 执行方式 |
|---------|---------|
| 默认编译 | 篮选"已处理但未编译"的文件 |
| 重新编译（指定文件） | 直接编译指定文件，忽略编译状态 |
| 重新编译（表达意图） | 如用户说"重新编译刘邦"，识别后强制执行 |

#### minimal 版本 templates

| template | 用途 |
|----------|------|
| person-template.md | 人物实体页面格式 |
| place-template.md | 地点实体页面格式 |
| event-template.md | 事件实体页面格式 |

### 2.1.5 scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_file.py | 根据产物路径读取文件 | 步骤 2：读取待编译文件内容 | 必须 |
| update_registry.py | 更新 raw-registry.md | 步骤 6：更新编译状态和日期 | 必须 |

### 2.2 history 版本流程（继承 minimal + 差异）

history 版本继承 minimal 流程，差异点：

#### 差异的 templates

| template | 用途 |
|----------|------|
| person-template.md | 历史人物实体页面格式（定制） |
| place-template.md | 历史地点实体页面格式（定制） |
| event-template.md | 历史事件实体页面格式（定制） |
| institution-template.md | 机构实体页面格式（history 特有） |
| synthesis-template.md | synthesis 报告格式（定制） |

#### entity-patterns.md

history 特有文件，定义历史文档的实体识别模式：
- 历史人物识别规则（别名、谥号、庙号）
- 历史地点识别规则（古地名 vs 现地名）
- 历史事件识别规则（年号、纪年转换）
- 机构识别规则（官职、机构名称）

注：history 版本 scripts 与 minimal 版本相同，scripts 使用说明见 §2.1.5。

---

## 3. kb-lint 流程设计

**职责**：Wiki 检查（语法、语义、修复）。

**适用范围**：见 scaffold-design §4.2 按类型分组。

### 3.1 流程步骤

1. **扫描 wiki/ 目录**：获取所有 wiki 文档
2. **语法检查**：调用 syntax.py 检查 markdown 格式、链接有效性
3. **语义检查**：调用 semantic.py 检查内容一致性、引用完整性
4. **模板一致性检查**：调用 semantic.py 检查 wiki 文档是否符合 kb-compile templates 定义的结构
5. **报告问题**：汇总检查结果，呈现给用户
6. **可选修复**：调用 fix.py 自动修复可修复的问题

### 3.2 模板一致性检查规则

| 检查项 | 规则 | 问题级别 |
|--------|------|----------|
| section 结构 | wiki 文档的 sections 是否符合 templates 定义的 section 列表 | 告警 |
| 必填字段 | templates 定义为必填的字段是否存在 | 告警 |
| wikilink 格式 | 引用是否使用正确的 wikilink 格式 `[[文档名]]` | 告警 |
| source 字段 | 是否包含 `source: [[raw/...]]` 字段 | 错误 |

### 3.3 orphan entries 检查

kb-lint 可检测 orphan entries（index.md entries 指向的 wiki 文件所在目录不在 structure.json 定义中）。

检测机制（SKILL.md 定义）：
- 解析 index.md entries
- 检查每个 entry 指向的 wiki 文件目录是否存在于 structure.json wiki 子目录中
- 输出告警，建议用户手动处理

### 3.4 scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| lint.py | 协调检查流程 | 步骤 1：扫描 wiki/ 后启动 | 必须 |
| syntax.py | 语法检查 | 步骤 2：检查 markdown 格式、链接 | 必须 |
| semantic.py | 语义检查 | 步骤 3-4：检查内容一致性、模板一致性 | 必须 |
| fix.py | 自动修复 | 步骤 6：可选修复可修复问题 | 可选 |

---

## 4. kb-query 流程设计

**职责**：Wiki 查询 + 回溯模式 + 生成 report。

**适用范围**：见 scaffold-design §4.2 按类型分组。

### 4.1 流程步骤

1. **接收查询意图**：用户提出问题（如"刘邦的社交关系网络"）

2. **解析意图**：
   - 查询对象：实体类型（人物、地点、事件、关系）
   - 查询范围：单实体、多实体、全库、时间限定
   - 查询方式：关键词匹配、语义搜索、关系遍历
   - 输出格式：文档列表、关系图、时间线、对比表格
   - 检测回溯关键词（见下文）

3. **【含回溯关键词】询问用户**：
   ```
   检测到回溯关键词，是否需要回溯 raw 文件？
   (yes → 回溯模式 / no → 标准模式)
   ```

4. **搜索 wiki/ 目录**：根据意图选择搜索策略，匹配相关文档

5. **聚合结果**：汇总查询结果

6. **【查询结果为空】输出提示并终止**：
   ```
   未找到相关实体，建议检查 raw 是否已 compile
   ```

7. **根据模式执行**：

   **标准模式**：
   - 检测疑似缺失（关系不对称、信息稀疏）

   **回溯模式**：
   - 识别相关 raw（通过 entities 的 source 字段）
   - 检查回溯范围限制：
     - 数量限制：最多 5 个 raw 文件
     - 大小限制：单文件超过 50KB 提示用户确认
   - 回溯 raw 文件
   - LLM 提取未提取信息

8. **生成 report**（符合 report-template.md）

9. **【标准模式】输出疑似缺失提示**：
   ```
   疑似缺失提示：
   - [[萧何]] 信息稀疏，建议重新 compile raw/史记/本纪/高祖本纪.md
   
   是否立即重新 compile？(yes/no)
   ```

10. **呈现 report**

### 4.2 回溯关键词

| 关键词 | 示例查询 |
|--------|---------|
| 回溯 | 回溯分析刘邦的社交网络 |
| 全面 | 全面梳理楚汉之争的关键人物 |
| 详细 | 详细考察萧何的政治生涯 |
| 完整 | 完整还原刘邦的早期经历 |
| 补充 | 补充刘邦与萧何的关系细节 |
| 溯源 | 溯源刘邦早期经历的原始记载 |

### 4.3 回溯范围限制

| 限制类型 | 规则 | 超出处理 |
|---------|------|---------|
| 数量限制 | 最多回溯 5 个 **唯一** raw 文件 | 提示用户选择优先回溯哪些 |
| 大小限制 | 单文件不超过 50KB | 提示用户确认是否处理 |

唯一文件计算方式：
- 按 **唯一 raw 文件路径** 计数，同一文件只计入 1 次
- 通过 entities 的 `source` 字段收集所有引用的 raw 文件
- 去重后计算总数，不超过 5 个

### 4.4 report 输出格式

report 符合 report-template.md 结构：

```markdown
# {{title}}

## 分析
{{analysis}}

【回溯模式额外】
### 回溯新发现
从 raw/xxx.md 发现：
- 信息A（未提取）
- 信息B（未提取）

## 结论
{{conclusion}}

## 相关实体
[[entity1]], [[entity2]], ...

## 回写建议
- 补充 [[entity]]：内容描述（来源：wiki/entities/xxx.md 或 raw/xxx.md）
```

### 4.5 边界情况处理

| 场景 | 输出 |
|------|------|
| wiki 无相关实体 | "未找到相关实体，建议检查 raw 是否已 compile" |
| 回溯无新发现 | "raw 回溯完成，无新发现信息" |

### 4.6 scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| search_wiki.py | 搜索 wiki 目录 | 步骤 4：根据意图搜索相关文档 | 可选（可替代为 grep） |

---

## 5. kb-archive 流程设计

**职责**：接收 report + 回写摘要 + 有机融入。

**适用范围**：见 scaffold-design §4.2 按类型分组。

**会话依赖**：kb-archive 必须在 kb-query 执行后的同一 agent session 中执行。

### 5.1 report 接收机制

kb-archive 通过 **agent 上下文** 接收 report：
- kb-archive 在同一 agent session 中执行，读取上下文中的 report 内容
- 用户在同一次对话中依次触发 kb-query 和 kb-archive
- 若 report 不在上下文中（如单独调用 kb-archive），kb-archive 输出提示："未找到 report，请先执行 kb-query"

### 5.2 流程步骤

1. **检查 report 是否存在**：
   - report 在 agent 上下文中：继续执行
   - report 不存在：输出提示并终止

2. **接收 report**：读取 agent 上下文中的 report 内容

3. **解析回写建议**：提取 report 中的回写建议列表

4. **生成回写摘要**：
   ```
   ## 回写摘要
   
   ### 补充 [[萧何]]
   位置：相关人物 section
   内容：添加"推荐刘邦担任亭长"
   ---
   原文：萧何与刘邦关系密切
   更新后：萧何与刘邦关系密切，曾向沛公推荐刘邦担任亭长
   
   是否执行回写？(yes/no/selective)
   ```

5. **询问用户是否执行回写**：
   - `yes`：执行所有回写建议
   - `no`：只创建 synthesis 报告，不执行回写
   - `selective`：逐个确认每条回写建议

6. **根据用户选择执行**：
   - 创建 synthesis/*.md（写入 report，不含回写建议）
   - 执行回写建议：有机融入 wiki 实体文档

7. **更新 index.md**：添加新报告索引

### 5.3 有机融入逻辑

回写采用有机融入，而非简单追加：

| 场景 | 简单追加（错误） | 有机融入（正确） |
|------|-----------------|-----------------|
| 补充关系 | 文末追加"推荐刘邦" | 在"相关人物"section 融入萧何→刘邦关系 |
| 补充事件 | 文末追加事件描述 | 在"生平"section 按时间顺序插入 |
| 补充属性 | 文末追加"出生地：沛县" | 在"基本信息"section 补充或确认出生地字段 |

有机融入由 LLM 执行：
- 阅读现有 wiki 文档内容和结构
- 阅读回写建议中的新内容
- LLM 判断：新内容应融入哪个 section
- 融合写入：补充、合并、或插入到合适位置

### 5.4 synthesis 报告格式

synthesis 报告符合 synthesis-template.md 结构：

```markdown
# {{title}}

## 分析
{{analysis}}

## 结论
{{conclusion}}

## 相关实体
[[entity1]], [[entity2]], ...
```

注：synthesis 报告不含"回写建议"section（回写建议已由 kb-archive 执行）。

### 5.5 scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_report.py | 读取 report 内容 | 步骤 2：从 agent 上下文读取 report | 必须 |
| create_synthesis.py | 创建 synthesis 文件 | 步骤 6：创建 synthesis 报告 | 必须 |
| update_entity.py | 有机融入 wiki 文档 | 步骤 6：执行回写建议 | 必须 |

---

## 6. kb-status 流程设计

**职责**：展示知识库仪表盘（解析 index.md + raw-registry.md）。

**适用范围**：见 scaffold-design §4.2 按类型分组。

### 6.1 流程步骤

1. **解析 raw-registry.md**：统计 raw 文件数量、类型分布、处理状态
2. **解析 index.md**：统计 wiki 文档数量、分类分布、最近修改时间
3. **查找最近活动**：
   - 最近修改 wiki：从 index.md 各 section 获取最新更新时间
   - 最近预处理 raw：从 raw-registry.md 获取最新处理日期
4. **查找待处理文件**：从 raw-registry.md
   - 预处理状态为"未处理"
   - 编译状态为"未编译"或"部分编译"
5. **格式化输出**：调用 format_dashboard.py 生成文本仪表盘

### 6.2 信息来源

| 信息 | 来源 | 说明 |
|------|------|------|
| raw 文件统计 | raw-registry.md | 数量、类型、状态 |
| wiki 文档统计 | index.md | 数量、分类（不扫描 wiki 目录） |
| 最近修改 wiki | index.md | 各 entry 的更新时间 |
| 最近预处理 | raw-registry.md | 最近处理日期字段 |

### 6.3 输出格式

```
Knowledge Base Dashboard: my-kb/

┌─────────────────────────────────────────────────┐
│ Overview                                         │
├─────────────────────────────────────────────────┤
│ Raw Files:         42 (markdown: 28, pdf: 8, image: 6) │
│ Wiki Documents:    156 (entities: 98, concepts: 34, synthesis: 24) │
│ Pending Ingest:    5 files                       │
│ Pending Compile:   12 files                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Recent Activity                                   │
├─────────────────────────────────────────────────┤
│ Latest Compiled:   [[刘邦]] (2026-04-17)     │
│ Latest Archived:   [[刘邦关系网络]] (2026-04-16) │
│ Latest Ingested:   raw/史记/本纪/项羽本纪.md (2026-04-17) │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Pending Files                                     │
├─────────────────────────────────────────────────┤
│ raw/史记/列传/张良传.md         (未处理)          │
│ raw/史记/列传/韩信传.md         (未处理)          │
│ raw/某书/chapter2.pdf          (已处理, 未编译)   │
│ ...                                              │
│ (显示前 10 个，另有 X 个待处理)                   │
└─────────────────────────────────────────────────┘
```

### 6.4 scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_registry.py | 解析 raw-registry.md | 步骤 1：统计 raw 文件状态 | 必须 |
| read_index.py | 解析 index.md | 步骤 2：统计 wiki 文档状态 | 必须 |
| format_dashboard.py | 格式化仪表盘输出 | 步骤 5：生成仪表盘 | 必须 |
